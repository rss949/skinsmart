import cv2
import numpy as np
import tensorflow as tf
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- LOAD MODEL ----------------
MODEL_CANDIDATES = [
    os.path.join(BASE_DIR, "ml", "model", "best_model.h5"),
    os.path.join(BASE_DIR, "ml", "model", "skin_model.h5"),
]
MODEL_PATH = next((p for p in MODEL_CANDIDATES if os.path.exists(p)), MODEL_CANDIDATES[-1])
model = tf.keras.models.load_model(MODEL_PATH)

CLASS_NAMES = [
    "Pimples / Acne",
    "Clear Skin",
    "Dark Spots",
    "Dark Circles"
]

IMG_SIZE = 224
CONFIDENCE_THRESHOLD = 0.45
MARGIN_THRESHOLD = 0.06
BLUR_THRESHOLD = 45.0
MIN_BRIGHTNESS = 45.0
MAX_BRIGHTNESS = 215.0
RECOVERABLE_CONFIDENCE_THRESHOLD = 0.34
RECOVERABLE_SIGNAL_THRESHOLD = 0.30

# ---------------- FACE DETECTOR ----------------
FACE_CASCADE_PATHS = [
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml",
    cv2.data.haarcascades + "haarcascade_frontalface_alt.xml",
    cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml",
]
face_cascades = [
    cv2.CascadeClassifier(path)
    for path in FACE_CASCADE_PATHS
    if os.path.exists(path)
]
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)


def _largest_face(faces):
    return max(faces, key=lambda f: f[2] * f[3])


def _collect_faces(gray):
    candidates = []
    for cascade in face_cascades:
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )
        for x, y, w, h in faces:
            area = w * h
            duplicate = False
            for ex, ey, ew, eh in candidates:
                inter_x1 = max(x, ex)
                inter_y1 = max(y, ey)
                inter_x2 = min(x + w, ex + ew)
                inter_y2 = min(y + h, ey + eh)
                inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
                union_area = area + (ew * eh) - inter_area
                if union_area and (inter_area / union_area) > 0.45:
                    duplicate = True
                    break
            if not duplicate:
                candidates.append((x, y, w, h))
    return candidates


def _expand_bbox(x, y, w, h, width, height, pad_ratio=0.23):
    pad_w = int(w * pad_ratio)
    pad_h = int(h * pad_ratio)

    x1 = max(0, x - pad_w)
    y1 = max(0, y - pad_h)
    x2 = min(width, x + w + pad_w)
    y2 = min(height, y + h + pad_h)
    return x1, y1, x2, y2


def _is_blurry(gray_face):
    return cv2.Laplacian(gray_face, cv2.CV_64F).var() < BLUR_THRESHOLD


def _bad_lighting(gray_face):
    brightness = float(np.mean(gray_face))
    return brightness < MIN_BRIGHTNESS or brightness > MAX_BRIGHTNESS


def _clahe_bgr(face_img):
    lab = cv2.cvtColor(face_img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    merged = cv2.merge((l, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def _enhance_face(face_img):
    softened = cv2.bilateralFilter(face_img, 7, 45, 45)
    return _clahe_bgr(softened)


def _prepare_input(face_img):
    resized = cv2.resize(face_img, (IMG_SIZE, IMG_SIZE))
    return resized.astype("float32") / 255.0


def _predict_with_tta(face_img):
    original = _prepare_input(face_img)
    flipped = cv2.flip(original, 1)
    enhanced = _prepare_input(_enhance_face(face_img))

    batch = np.stack([original, flipped, enhanced], axis=0)
    preds = model.predict(batch, verbose=0)
    return np.mean(preds, axis=0)


def _clamp01(value):
    return float(np.clip(value, 0.0, 1.0))


def _find_eyes(gray_face):
    upper = gray_face[: int(gray_face.shape[0] * 0.62), :]
    eyes = eye_cascade.detectMultiScale(
        upper,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(22, 22)
    )
    if len(eyes) >= 2:
        eyes = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)[:2]
        eyes = sorted(eyes, key=lambda e: e[0])  # left, right
        return eyes
    return []


def _default_eye_boxes(w, h):
    eye_w = int(0.16 * w)
    eye_h = int(0.10 * h)
    y = int(0.28 * h)
    left_x = int(0.24 * w)
    right_x = int(0.60 * w)
    return [(left_x, y, eye_w, eye_h), (right_x, y, eye_w, eye_h)]


def _compute_dark_circle_signal(face_bgr, gray_face):
    h, w = gray_face.shape[:2]
    eyes = _find_eyes(gray_face)
    if len(eyes) < 2:
        eyes = _default_eye_boxes(w, h)

    deltas = []
    for x, y, ew, eh in eyes:
        under_y1 = min(h - 1, y + int(0.85 * eh))
        under_y2 = min(h, under_y1 + max(6, int(0.75 * eh)))
        under_x1 = max(0, x - int(0.1 * ew))
        under_x2 = min(w, x + ew + int(0.1 * ew))
        if under_y2 <= under_y1 or under_x2 <= under_x1:
            continue

        cheek_y1 = min(h - 1, under_y2 + int(0.15 * eh))
        cheek_y2 = min(h, cheek_y1 + max(6, int(0.90 * eh)))
        cheek_x1 = under_x1
        cheek_x2 = under_x2
        if cheek_y2 <= cheek_y1:
            continue

        under_mean = float(np.mean(gray_face[under_y1:under_y2, under_x1:under_x2]))
        cheek_mean = float(np.mean(gray_face[cheek_y1:cheek_y2, cheek_x1:cheek_x2]))
        if cheek_mean <= 1:
            continue
        delta = (cheek_mean - under_mean) / cheek_mean
        deltas.append(delta)

    if not deltas:
        return 0.0
    # 0.08 starts mild, 0.30+ strong dark-circle contrast.
    return _clamp01((float(np.mean(deltas)) - 0.08) / 0.22)


def _skin_mask_ycrcb(face_bgr):
    ycrcb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2YCrCb)
    lower = np.array([0, 133, 77], dtype=np.uint8)
    upper = np.array([255, 173, 127], dtype=np.uint8)
    mask = cv2.inRange(ycrcb, lower, upper)
    mask = cv2.medianBlur(mask, 5)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    return mask


def _compute_acne_signal(face_bgr, skin_mask):
    b, g, r = cv2.split(face_bgr)
    hsv = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2HSV)
    s = hsv[:, :, 1]

    red_pixels = (
        (r > (g + 14)) &
        (r > (b + 14)) &
        (s > 55) &
        (skin_mask > 0)
    )
    red_ratio = float(np.mean(red_pixels)) if red_pixels.size else 0.0

    binary = (red_pixels.astype(np.uint8) * 255)
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    blob_count = 0
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if 6 <= area <= 220:
            blob_count += 1
    blob_density = blob_count / 120.0

    signal = 0.72 * red_ratio * 16.0 + 0.28 * blob_density
    return _clamp01(signal)


def _compute_dark_spot_signal(face_bgr, gray_face, skin_mask):
    v = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2HSV)[:, :, 2]
    mean_v = float(np.mean(v[skin_mask > 0])) if np.any(skin_mask > 0) else float(np.mean(v))
    threshold = max(35, int(mean_v - 28))
    dark_pixels = ((v < threshold) & (skin_mask > 0))
    dark_ratio = float(np.mean(dark_pixels)) if dark_pixels.size else 0.0

    binary = (dark_pixels.astype(np.uint8) * 255)
    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    blob_count = 0
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if 8 <= area <= 280:
            blob_count += 1
    blob_density = blob_count / 140.0

    signal = 0.65 * dark_ratio * 14.0 + 0.35 * blob_density
    return _clamp01(signal)


def _compute_cv_signals(face_bgr, gray_face):
    skin_mask = _skin_mask_ycrcb(face_bgr)
    dark_circle = _compute_dark_circle_signal(face_bgr, gray_face)
    acne = _compute_acne_signal(face_bgr, skin_mask)
    dark_spot = _compute_dark_spot_signal(face_bgr, gray_face, skin_mask)
    return {
        "Dark Circles": dark_circle,
        "Pimples / Acne": acne,
        "Dark Spots": dark_spot
    }


def _fuse_model_and_cv(preds, cv_signals):
    model_scores = {CLASS_NAMES[i]: float(preds[i]) for i in range(len(CLASS_NAMES))}

    fused = {}
    fused["Pimples / Acne"] = 0.78 * model_scores["Pimples / Acne"] + 0.22 * cv_signals["Pimples / Acne"]
    fused["Dark Spots"] = 0.78 * model_scores["Dark Spots"] + 0.22 * cv_signals["Dark Spots"]
    fused["Dark Circles"] = 0.78 * model_scores["Dark Circles"] + 0.22 * cv_signals["Dark Circles"]

    cv_pressure = max(cv_signals.values()) if cv_signals else 0.0
    fused_clear = model_scores["Clear Skin"] - (0.35 * cv_pressure)
    fused["Clear Skin"] = max(0.01, fused_clear)

    total = sum(fused.values())
    if total <= 0:
        return {k: 0.25 for k in fused}
    return {k: fused[k] / total for k in fused}


def _build_result(face_img, gray_face, quality_ok, quality_warning=None):
    preds = _predict_with_tta(face_img)
    cv_signals = _compute_cv_signals(face_img, gray_face)
    fused_scores = _fuse_model_and_cv(preds, cv_signals)

    ranked = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    skin_concern = ranked[0][0]
    confidence = float(ranked[0][1])
    sorted_preds = np.array([score for _, score in ranked], dtype=np.float32)
    margin = float(sorted_preds[0] - sorted_preds[1]) if len(sorted_preds) > 1 else 0.0

    low_confidence = confidence < CONFIDENCE_THRESHOLD or margin < MARGIN_THRESHOLD

    best_non_clear = max(
        ["Pimples / Acne", "Dark Spots", "Dark Circles"],
        key=lambda c: fused_scores[c]
    )
    best_non_clear_score = float(fused_scores[best_non_clear])

    if (
        skin_concern == "Clear Skin"
        and low_confidence
        and best_non_clear_score >= 0.24
        and (fused_scores["Clear Skin"] - best_non_clear_score) <= 0.10
    ):
        skin_concern = best_non_clear
        confidence = best_non_clear_score

    analysis_ok = True
    analysis_warning = ""
    analysis_message = "Analysis completed successfully."

    if not quality_ok:
        recoverable = confidence >= RECOVERABLE_CONFIDENCE_THRESHOLD or best_non_clear_score >= RECOVERABLE_SIGNAL_THRESHOLD
        if recoverable:
            analysis_warning = (
                quality_warning
                or "Lighting or sharpness was not ideal, so this result should be treated as a guided estimate."
            )
            analysis_message = "Analysis completed with image-quality fallback."
        else:
            analysis_ok = False
            analysis_message = (
                quality_warning
                or "Image quality is too low for a reliable result. Please retake the photo in bright light."
            )

    if skin_concern not in {"Pimples / Acne", "Dark Spots", "Dark Circles", "Clear Skin"}:
        skin_concern = "Clear Skin"

    scores = {
        k: round(float(v) * 100, 2)
        for k, v in fused_scores.items()
    }

    return {
        "face_detected": True,
        "quality_ok": quality_ok,
        "analysis_ok": analysis_ok,
        "age_ok": True,
        "age": 22,
        "skin_concern": skin_concern,
        "confidence": round(confidence * 100, 2),
        "low_confidence": low_confidence,
        "scores": scores,
        "cv_signals": {k: round(v * 100, 2) for k, v in cv_signals.items()},
        "analysis_message": analysis_message,
        "analysis_warning": analysis_warning,
    }


def analyze_skin_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = _collect_faces(gray)

    if len(faces) == 0:
        return {"face_detected": False}

    x, y, w, h = _largest_face(faces)
    x1, y1, x2, y2 = _expand_bbox(x, y, w, h, gray.shape[1], gray.shape[0])
    face_img = img[y1:y2, x1:x2]
    gray_face = gray[y1:y2, x1:x2]

    blurry = _is_blurry(gray_face)
    bad_lighting = _bad_lighting(gray_face)
    quality_ok = not blurry and not bad_lighting

    if quality_ok:
        return _build_result(face_img, gray_face, quality_ok=True)

    enhanced_face = _enhance_face(face_img)
    enhanced_gray = cv2.cvtColor(enhanced_face, cv2.COLOR_BGR2GRAY)
    quality_reasons = []
    if blurry:
        quality_reasons.append("the photo appears blurry")
    if bad_lighting:
        quality_reasons.append("lighting is uneven")
    warning = (
        "We detected a face, but "
        + " and ".join(quality_reasons)
        + ". The result below is a best-effort estimate."
    )
    return _build_result(
        enhanced_face,
        enhanced_gray,
        quality_ok=False,
        quality_warning=warning
    )
