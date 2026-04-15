import argparse
import hashlib
import shutil
import tempfile
from pathlib import Path

import cv2
from icrawler.builtin import BingImageCrawler, GoogleImageCrawler
from PIL import Image


DEFAULT_KEYWORDS = {
    "clear": [
        "clear skin face portrait",
        "healthy skin face close up",
        "clean skin woman face natural light",
        "clear complexion face front view",
        "human face flawless skin close up",
    ],
    "acne": [
        "severe acne face close up",
        "cystic acne face human",
        "nodular acne face close up",
        "inflammatory acne face high resolution",
        "severe pimples face portrait",
    ],
    "dark_circles": [
        "dark circles under eyes face close up",
        "under eye pigmentation human face portrait",
        "periorbital dark circles close up face",
        "tired eyes dark circles portrait",
        "eye bag dark circles face photo",
    ],
    "dark_spots": [
        "dark spots face close up human",
        "hyperpigmentation face portrait",
        "melasma face close up",
        "facial pigmentation cheek forehead close up",
        "uneven skin tone face portrait",
    ],
}

ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def file_hash(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_face(image_path: Path) -> bool:
    image = cv2.imread(str(image_path))
    if image is None:
        return False

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
    return len(faces) > 0


def existing_hashes(target_dir: Path) -> set[str]:
    hashes = set()
    for path in target_dir.iterdir():
        if path.is_file() and path.suffix.lower() in ALLOWED_SUFFIXES:
            try:
                hashes.add(file_hash(path))
            except OSError:
                continue
    return hashes


def normalize_image(source_path: Path, destination_path: Path) -> bool:
    try:
        with Image.open(source_path) as image:
            image = image.convert("RGB")
            if min(image.size) < 128:
                return False
            image.save(destination_path, format="JPEG", quality=95)
        return True
    except Exception:
        return False


def next_index(target_dir: Path, prefix: str) -> int:
    highest = -1
    for path in target_dir.glob(f"{prefix}_*.jpg"):
        try:
            highest = max(highest, int(path.stem.split("_")[-1]))
        except ValueError:
            continue
    return highest + 1


def build_crawler(provider: str, temp_dir: Path):
    storage = {"root_dir": str(temp_dir)}
    if provider == "bing":
        return BingImageCrawler(storage=storage)
    if provider == "google":
        return GoogleImageCrawler(storage=storage)
    raise ValueError(f"Unsupported provider: {provider}")


def crawl_images(
    target_dir: Path,
    keywords: list[str],
    max_images: int,
    prefix: str,
    providers: list[str],
) -> int:
    target_dir.mkdir(parents=True, exist_ok=True)
    known_hashes = existing_hashes(target_dir)
    start_index = next_index(target_dir, prefix)
    saved_count = 0

    with tempfile.TemporaryDirectory(prefix="skin_crawl_") as temp_root:
        temp_dir = Path(temp_root)

        for keyword in keywords:
            if saved_count >= max_images:
                break

            for provider in providers:
                if saved_count >= max_images:
                    break

                print(f"Searching {provider.title()} Images for: {keyword}")
                try:
                    crawler = build_crawler(provider, temp_dir)
                    crawler.crawl(keyword=keyword, max_num=max_images * 3, overwrite=True)
                except Exception as exc:
                    print(f"Skipping provider {provider}: {exc}")
                    continue

                for downloaded in list(temp_dir.iterdir()):
                    if saved_count >= max_images:
                        break
                    if not downloaded.is_file() or downloaded.suffix.lower() not in ALLOWED_SUFFIXES:
                        continue

                    normalized_path = temp_dir / f"normalized_{downloaded.stem}.jpg"
                    if not normalize_image(downloaded, normalized_path):
                        downloaded.unlink(missing_ok=True)
                        normalized_path.unlink(missing_ok=True)
                        continue

                    try:
                        image_digest = file_hash(normalized_path)
                    except OSError:
                        normalized_path.unlink(missing_ok=True)
                        downloaded.unlink(missing_ok=True)
                        continue

                    if image_digest in known_hashes:
                        normalized_path.unlink(missing_ok=True)
                        downloaded.unlink(missing_ok=True)
                        continue

                    if not detect_face(normalized_path):
                        normalized_path.unlink(missing_ok=True)
                        downloaded.unlink(missing_ok=True)
                        continue

                    final_path = target_dir / f"{prefix}_{start_index + saved_count:04d}.jpg"
                    shutil.move(str(normalized_path), final_path)
                    known_hashes.add(image_digest)
                    saved_count += 1
                    print(f"Saved {saved_count}/{max_images}: {final_path}")
                    downloaded.unlink(missing_ok=True)

                for leftover in temp_dir.iterdir():
                    if leftover.is_file():
                        leftover.unlink(missing_ok=True)

    return saved_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download and clean face images for SkinSmart dataset folders."
    )
    parser.add_argument(
        "--label",
        default="clear",
        choices=sorted(DEFAULT_KEYWORDS.keys()),
        help="Dataset class to download for.",
    )
    parser.add_argument(
        "--split",
        default="test",
        choices=["train", "test"],
        help="Dataset split folder.",
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=40,
        help="Number of new cleaned images to save.",
    )
    parser.add_argument(
        "--target-dir",
        default=None,
        help="Optional explicit target directory. Overrides --label and --split path.",
    )
    parser.add_argument(
        "--providers",
        nargs="+",
        default=["bing", "google"],
        choices=["bing", "google"],
        help="Crawler providers to use in order.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.target_dir:
        target_dir = Path(args.target_dir)
    else:
        target_dir = Path("ml") / "dataset" / args.split / args.label

    keywords = DEFAULT_KEYWORDS[args.label]
    saved_count = crawl_images(
        target_dir=target_dir,
        keywords=keywords,
        max_images=args.max_images,
        prefix=args.label,
        providers=args.providers,
    )
    print(f"Done. Saved {saved_count} new images to {target_dir}")


if __name__ == "__main__":
    main()
