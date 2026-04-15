import os 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'
import os
import json
import hashlib
import html
import re
import secrets
import smtplib
import urllib.parse
import urllib.request
from functools import wraps
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

from flask import Flask, render_template, redirect, url_for, session, request, flash, Response, jsonify
import cv2
import numpy as np
import mysql.connector
from dotenv import load_dotenv
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash

from ai_skin import analyze_skin_image
from ai_routine import generate_skincare_routine, ALL_BRANDS


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "skinsmart_secret_key")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

CONCERN_ORDER = ["Dark Circles", "Dark Spots", "Pimples / Acne"]
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
BRAND_SHOWCASE = [
    {"name": "Mamaearth", "accent": "#33a66f"},
    {"name": "Foxtale", "accent": "#f18421"},
    {"name": "Dot & Key", "accent": "#db4d83"},
    {"name": "The Derma Co", "accent": "#2f7fd6"},
    {"name": "Minimalist", "accent": "#1f2937"},
    {"name": "Cetaphil", "accent": "#2d6cb5"},
    {"name": "Himalaya", "accent": "#2f8f5b"},
    {"name": "Plix", "accent": "#f05d5e"},
]


_IMAGE_PROXY_CACHE = {}
_IMAGE_PROXY_TTL_SECONDS = 6 * 60 * 60


def _fallback_svg(brand, product):
    brand_color = {
        "Cetaphil": "#2d6cb5",
        "Himalaya": "#2f8f5b",
        "Plix": "#8a2ea6",
    }.get(brand, "#4b5563")
    safe_brand = html.escape(brand or "SkinSmart")
    safe_product = html.escape(product or "Product")
    return (
        "<svg xmlns='http://www.w3.org/2000/svg' width='600' height='600' viewBox='0 0 600 600'>"
        "<rect width='600' height='600' fill='#f8fafc'/>"
        f"<rect x='36' y='36' width='528' height='528' rx='28' fill='white' stroke='{brand_color}' stroke-width='6'/>"
        f"<circle cx='300' cy='220' r='82' fill='{brand_color}' opacity='0.12'/>"
        f"<rect x='220' y='150' width='160' height='170' rx='28' fill='{brand_color}' opacity='0.9'/>"
        "<rect x='245' y='115' width='110' height='50' rx='18' fill='#dbeafe'/>"
        f"<text x='300' y='392' text-anchor='middle' font-family='Arial, sans-serif' font-size='34' font-weight='700' fill='{brand_color}'>{safe_brand}</text>"
        f"<text x='300' y='440' text-anchor='middle' font-family='Arial, sans-serif' font-size='23' fill='#334155'>{safe_product}</text>"
        "<text x='300' y='486' text-anchor='middle' font-family='Arial, sans-serif' font-size='18' fill='#64748b'>Image unavailable</text>"
        "</svg>"
    )


def _brand_logo_svg(brand_name):
    brand_entry = next((item for item in BRAND_SHOWCASE if item["name"] == brand_name), None)
    accent = (brand_entry or {}).get("accent", "#4b5563")
    wordmark = (brand_entry or {}).get("wordmark_color", "#1f2937")
    safe_brand = html.escape(brand_name or "Brand")
    font_size = 58 if len(safe_brand) < 10 else 48 if len(safe_brand) < 14 else 40
    return (
        "<svg xmlns='http://www.w3.org/2000/svg' width='640' height='240' viewBox='0 0 640 240'>"
        "<rect width='640' height='240' rx='32' fill='white'/>"
        f"<rect x='18' y='18' width='604' height='204' rx='26' fill='white' stroke='{accent}' stroke-opacity='0.18' stroke-width='2'/>"
        f"<circle cx='92' cy='120' r='38' fill='{accent}' fill-opacity='0.12'/>"
        f"<circle cx='92' cy='120' r='22' fill='{accent}'/>"
        f"<text x='150' y='135' font-family='Georgia, Times New Roman, serif' font-size='{font_size}' font-weight='700' fill='{wordmark}'>{safe_brand}</text>"
        "</svg>"
    )


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "skinsmart_db"),
    )


@app.route("/product-image")
def product_image():
    src = (request.args.get("src") or "").strip()
    if not src.lower().startswith(("http://", "https://")):
        return Response(status=404)

    parsed = urllib.parse.urlparse(src)
    referer = f"{parsed.scheme}://{parsed.netloc}/" if parsed.scheme and parsed.netloc else src

    now = datetime.now().timestamp()
    cached = _IMAGE_PROXY_CACHE.get(src)
    if cached and (now - cached["ts"]) < _IMAGE_PROXY_TTL_SECONDS:
        return Response(cached["body"], mimetype=cached["content_type"])

    try:
        req = urllib.request.Request(
            src,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0 Safari/537.36"
                ),
                "Referer": referer,
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read()
            content_type = resp.headers.get_content_type() or "image/jpeg"
            if not content_type.startswith("image/"):
                return Response(status=404)

        _IMAGE_PROXY_CACHE[src] = {
            "ts": now,
            "body": body,
            "content_type": content_type,
        }
        return Response(body, mimetype=content_type)
    except Exception:
        return Response(status=404)


@app.route("/product-fallback")
def product_fallback():
    brand = (request.args.get("brand") or "SkinSmart").strip()
    product = (request.args.get("product") or "Product").strip()
    return Response(_fallback_svg(brand, product), mimetype="image/svg+xml")


@app.route("/brand-logo")
def brand_logo():
    brand = (request.args.get("brand") or "Brand").strip()
    return Response(_brand_logo_svg(brand), mimetype="image/svg+xml")


def ensure_db_schema(conn):
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(255) NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            detected_concern VARCHAR(80) NOT NULL,
            age INT NULL,
            skin_type VARCHAR(30) NULL,
            selected_brand VARCHAR(80) NULL,
            routine_json LONGTEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_history_user_time (user_id, created_at),
            CONSTRAINT fk_history_user FOREIGN KEY (user_id)
                REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            token_hash CHAR(64) NOT NULL UNIQUE,
            expires_at DATETIME NOT NULL,
            used_at DATETIME NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_password_reset_user (user_id),
            CONSTRAINT fk_reset_user FOREIGN KEY (user_id)
                REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            rating INT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'users'
          AND COLUMN_NAME = 'email'
        """
    )
    if cursor.fetchone()[0] == 0:
        cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255) NULL UNIQUE")
    conn.commit()
    cursor.close()


def _utc_now():
    return datetime.now(timezone.utc)


def _hash_reset_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _normalize_email(value):
    return (value or "").strip().lower()


def _is_valid_email(value):
    return bool(EMAIL_REGEX.match(_normalize_email(value)))


def _is_valid_username(value):
    return 3 <= len((value or "").strip()) <= 50


def _is_valid_password(value):
    return len(value or "") >= 8


def _admin_email():
    return _normalize_email(os.getenv("ADMIN_EMAIL", "rss029993@gmail.com"))


def _admin_password():
    return os.getenv("ADMIN_PASSWORD", "dhiraj2003")


def _admin_password_hash():
    return os.getenv("ADMIN_PASSWORD_HASH")


def _clear_admin_otp_session():
    session.pop("admin_pending_email", None)
    session.pop("admin_otp_hash", None)
    session.pop("admin_otp_expires_at", None)


def _issue_admin_otp():
    otp = f"{secrets.randbelow(900000) + 100000:06d}"
    session["admin_pending_email"] = _admin_email()
    session["admin_otp_hash"] = hashlib.sha256(otp.encode("utf-8")).hexdigest()
    session["admin_otp_expires_at"] = int((_utc_now() + timedelta(minutes=10)).timestamp())
    return otp


def _admin_otp_is_valid(otp):
    expected_hash = session.get("admin_otp_hash")
    expires_at = session.get("admin_otp_expires_at")
    if not expected_hash or not expires_at:
        return False
    if int(_utc_now().timestamp()) > int(expires_at):
        return False
    return hashlib.sha256((otp or "").strip().encode("utf-8")).hexdigest() == expected_hash


def _serialize_feedback_row(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "message": row["message"],
        "rating": row["rating"],
    }


def get_feedback_entries():
    conn = get_db_connection()
    try:
        ensure_db_schema(conn)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, name, message, rating
            FROM feedback
            ORDER BY id DESC
            """
        )
        rows = cursor.fetchall()
        cursor.close()
        return [_serialize_feedback_row(row) for row in rows]
    finally:
        conn.close()


def _smtp_configured():
    required = ("SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "MAIL_FROM")
    return all(os.getenv(name) for name in required)


def send_password_reset_email(to_email, username, reset_url):
    if not _smtp_configured():
        raise RuntimeError("SMTP is not configured")

    message = EmailMessage()
    message["Subject"] = "Reset your SkinSmart password"
    message["From"] = os.getenv("MAIL_FROM")
    message["To"] = to_email
    message.set_content(
        (
            f"Hi {username},\n\n"
            "We received a request to reset your SkinSmart password.\n"
            f"Reset it here: {reset_url}\n\n"
            "This link expires in 30 minutes. If you did not request this, "
            "you can safely ignore this email."
        )
    )

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() != "false"

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
        server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
        server.send_message(message)


def send_admin_otp_email(to_email, otp):
    if not _smtp_configured():
        raise RuntimeError("SMTP is not configured")

    message = EmailMessage()
    message["Subject"] = "Your SkinSmart admin OTP"
    message["From"] = os.getenv("MAIL_FROM")
    message["To"] = to_email
    message.set_content(
        (
            "SkinSmart admin login requested.\n\n"
            f"Use this one-time password to continue: {otp}\n\n"
            "This OTP expires in 10 minutes. If this was not you, please change the admin password immediately."
        )
    )

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() != "false"

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
        server.ehlo()
        if use_tls:
            server.starttls()
            server.ehlo()
        server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
        server.send_message(message)


def create_password_reset_token(user_id):
    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_reset_token(raw_token)
    expires_at = _utc_now() + timedelta(minutes=30)

    conn = get_db_connection()
    try:
        ensure_db_schema(conn)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM password_reset_tokens WHERE user_id = %s OR expires_at < UTC_TIMESTAMP()",
            (user_id,),
        )
        cursor.execute(
            """
            INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
            VALUES (%s, %s, %s)
            """,
            (user_id, token_hash, expires_at.replace(tzinfo=None)),
        )
        conn.commit()
        cursor.close()
    finally:
        conn.close()

    return raw_token


def get_reset_token_record(raw_token):
    conn = get_db_connection()
    try:
        ensure_db_schema(conn)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT prt.id, prt.user_id, prt.expires_at, prt.used_at, u.username, u.email
            FROM password_reset_tokens prt
            JOIN users u ON u.id = prt.user_id
            WHERE prt.token_hash = %s
            """,
            (_hash_reset_token(raw_token),),
        )
        record = cursor.fetchone()
        cursor.close()
        return record
    finally:
        conn.close()


def mark_reset_token_used(token_id, password_hash):
    conn = get_db_connection()
    try:
        ensure_db_schema(conn)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id FROM password_reset_tokens WHERE id = %s FOR UPDATE",
            (token_id,),
        )
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            cursor.close()
            return False

        cursor.execute(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (password_hash, row[0]),
        )
        cursor.execute(
            "UPDATE password_reset_tokens SET used_at = UTC_TIMESTAMP() WHERE id = %s",
            (token_id,),
        )
        cursor.execute(
            "DELETE FROM password_reset_tokens WHERE user_id = %s AND id <> %s",
            (row[0], token_id),
        )
        conn.commit()
        cursor.close()
        return True
    finally:
        conn.close()


def save_history_entry(user_id, detected_concern, age, skin_type, selected_brand, routine):
    conn = get_db_connection()
    try:
        ensure_db_schema(conn)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO analysis_history
            (user_id, detected_concern, age, skin_type, selected_brand, routine_json)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                detected_concern,
                age,
                skin_type,
                selected_brand,
                json.dumps(routine),
            ),
        )
        conn.commit()
        cursor.close()
    finally:
        conn.close()


def _pdf_safe_text(value):
    text = str(value or "")
    text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _build_simple_pdf(title, lines):
    content_lines = [
        "BT",
        "/F1 12 Tf",
        "14 TL",
        "50 800 Td",
        f"({_pdf_safe_text(title)}) Tj",
        "T*",
    ]

    for line in lines[:45]:
        content_lines.append(f"({_pdf_safe_text(line)}) Tj")
        content_lines.append("T*")

    content_lines.append("ET")
    content = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        (
            b"5 0 obj\n<< /Length "
            + str(len(content)).encode("ascii")
            + b" >>\nstream\n"
            + content
            + b"\nendstream\nendobj\n"
        ),
    ]

    pdf = b"%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj

    xref_pos = len(pdf)
    pdf += b"xref\n0 6\n0000000000 65535 f \n"
    for idx in range(1, 6):
        pdf += f"{offsets[idx]:010} 00000 n \n".encode("ascii")
    pdf += b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n"
    pdf += str(xref_pos).encode("ascii")
    pdf += b"\n%%EOF"
    return pdf


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_authenticated"):
            flash("Please log in as admin to continue.", "error")
            return redirect(url_for("admin_login"))
        return view_func(*args, **kwargs)

    return wrapped_view


def _severity_from_score(score):
    if score >= 65:
        return "HIGH", "High severity"
    if score >= 45:
        return "MODERATE", "Moderate severity"
    if score >= 28:
        return "MILD", "Mild severity"
    return "", "Not detected"


def _build_detected_concerns(scores):
    concern_rows = []
    for concern in CONCERN_ORDER:
        score = float(scores.get(concern, 0.0))
        tag, detail = _severity_from_score(score)
        concern_rows.append(
            {
                "name": "Acne" if concern == "Pimples / Acne" else concern,
                "key": concern,
                "score": round(score, 2),
                "tag": tag,
                "detail": detail,
                "detected": bool(tag)
            }
        )
    return concern_rows


def _assessment_copy(primary_concern, confidence, concern_rows):
    active = [row["name"].lower() for row in concern_rows if row["detected"]]

    if primary_concern == "Clear Skin" and confidence >= 55:
        overall_title = "Healthy"
        overall_subtitle = "Overall Skin Health"
        text = (
            "Your skin appears mostly clear in this image. Maintain a gentle, "
            "consistent routine and daily sunscreen to protect long-term skin health."
        )
        return overall_subtitle, overall_title, text

    overall_title = "Needs Attention"
    overall_subtitle = "Overall Skin Health"
    if active:
        joined = ", ".join(active)
        text = (
            f"Your skin image shows signs of {joined}. With a targeted routine and "
            "consistent care, these concerns can improve over time."
        )
    else:
        text = (
            "The model detected subtle signs of skin stress in this image. "
            "Retake in bright light for a more reliable concern breakdown."
        )
    return overall_subtitle, overall_title, text


@app.route("/")
def home():
    return render_template("index.html", brand_cards=BRAND_SHOWCASE)


@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    message = (payload.get("message") or "").strip()
    rating = payload.get("rating")

    if not name or not message:
        return jsonify({"success": False, "error": "Name and message are required."}), 400

    if len(name) > 255:
        return jsonify({"success": False, "error": "Name must be 255 characters or fewer."}), 400

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Rating must be a number between 1 and 5."}), 400

    if rating < 1 or rating > 5:
        return jsonify({"success": False, "error": "Rating must be between 1 and 5."}), 400

    try:
        conn = get_db_connection()
        ensure_db_schema(conn)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            INSERT INTO feedback (name, message, rating)
            VALUES (%s, %s, %s)
            """,
            (name, message, rating),
        )
        feedback_id = cursor.lastrowid
        conn.commit()
        cursor.execute(
            """
            SELECT id, name, message, rating
            FROM feedback
            WHERE id = %s
            """,
            (feedback_id,),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
    except mysql.connector.Error:
        return jsonify({"success": False, "error": "Could not save feedback right now."}), 500

    feedback_item = _serialize_feedback_row(row)
    socketio.emit("new_feedback", feedback_item)
    return jsonify({"success": True, "feedback": feedback_item}), 201


@app.route("/get_feedback")
def get_feedback():
    try:
        feedback_items = get_feedback_entries()
    except mysql.connector.Error:
        return jsonify({"success": False, "error": "Could not load feedback right now."}), 500
    return jsonify(feedback_items)


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("analyze_skin"))

    if request.method == "POST":
        email = _normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("login.html")

        if not _is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return render_template("login.html")

        try:
            conn = get_db_connection()
            ensure_db_schema(conn)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, username, email, password_hash FROM users WHERE email = %s",
                (email,),
            )
            user = cursor.fetchone()
            cursor.close()
            conn.close()
        except mysql.connector.Error:
            flash("We could not reach the database right now. Please try again in a moment.", "error")
            return render_template("login.html")

        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session["user_id"] = user["id"]
        session["user_name"] = user["username"]
        session["user_email"] = user["email"]
        flash("Login successful.", "success")
        return redirect(url_for("analyze_skin"))

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("analyze_skin"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = _normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password or not confirm_password:
            flash("All fields are required.", "error")
            return render_template("signup.html", form_data={"username": username, "email": email})

        if len(username) < 3 or len(username) > 50:
            flash("Username must be between 3 and 50 characters.", "error")
            return render_template("signup.html", form_data={"username": username, "email": email})

        if not _is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return render_template("signup.html", form_data={"username": username, "email": email})

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("signup.html", form_data={"username": username, "email": email})

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("signup.html", form_data={"username": username, "email": email})

        password_hash = generate_password_hash(password)

        try:
            conn = get_db_connection()
            ensure_db_schema(conn)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                cursor.close()
                conn.close()
                flash("That username or email is already in use.", "error")
                return render_template("signup.html", form_data={"username": username, "email": email})

            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash),
            )
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error:
            flash("We could not create your account right now. Please try again shortly.", "error")
            return render_template("signup.html", form_data={"username": username, "email": email})

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html", form_data={"username": "", "email": ""})


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = _normalize_email(request.form.get("email", ""))
        if not _is_valid_email(email):
            flash("Enter the email address linked to your account.", "error")
            return render_template("forgot_password.html", form_data={"email": email})

        try:
            conn = get_db_connection()
            ensure_db_schema(conn)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, username, email FROM users WHERE email = %s",
                (email,),
            )
            user = cursor.fetchone()
            cursor.close()
            conn.close()
        except mysql.connector.Error:
            flash("We could not process password reset right now. Please try again shortly.", "error")
            return render_template("forgot_password.html", form_data={"email": email})

        if user:
            try:
                token = create_password_reset_token(user["id"])
                reset_url = url_for("reset_password", token=token, _external=True)
                send_password_reset_email(user["email"], user["username"], reset_url)
            except Exception:
                flash(
                    "We found your account, but the reset email could not be sent. "
                    "Check SMTP settings and try again.",
                    "error",
                )
                return render_template("forgot_password.html", form_data={"email": email})

        flash(
            "If an account exists for that email, a password reset link has been sent.",
            "success",
        )
        return redirect(url_for("login"))

    return render_template("forgot_password.html", form_data={"email": ""})


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        record = get_reset_token_record(token)
    except mysql.connector.Error:
        flash("We could not validate that reset link right now. Please try again later.", "error")
        return redirect(url_for("forgot_password"))

    if not record:
        flash("That reset link is invalid.", "error")
        return redirect(url_for("forgot_password"))

    expires_at = record["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.replace(tzinfo=timezone.utc) < _utc_now():
        flash("That reset link has expired. Request a new one.", "error")
        return redirect(url_for("forgot_password"))

    if record.get("used_at"):
        flash("That reset link has already been used. Request a new one.", "error")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("reset_password.html", token=token)

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("reset_password.html", token=token)

        try:
            updated = mark_reset_token_used(record["id"], generate_password_hash(password))
        except mysql.connector.Error:
            flash("We could not update your password right now. Please try again.", "error")
            return render_template("reset_password.html", token=token)

        if not updated:
            flash("That reset link is no longer valid. Request a new one.", "error")
            return redirect(url_for("forgot_password"))

        flash("Your password has been updated. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", token=token)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_authenticated"):
        return redirect(url_for("admin_dashboard"))

    otp_stage = bool(session.get("admin_pending_email"))

    if request.method == "POST":
        step = request.form.get("step", "credentials")

        if step == "otp":
            otp = request.form.get("otp", "").strip()
            if not otp:
                flash("OTP is required.", "error")
                return render_template("admin_login.html", otp_stage=True, admin_email=session.get("admin_pending_email", _admin_email()))
            if not _admin_otp_is_valid(otp):
                if session.get("admin_otp_expires_at") and int(_utc_now().timestamp()) > int(session.get("admin_otp_expires_at")):
                    _clear_admin_otp_session()
                    flash("OTP expired. Please sign in again.", "error")
                    return render_template("admin_login.html", otp_stage=False, admin_email=_admin_email())
                flash("Invalid OTP.", "error")
                return render_template("admin_login.html", otp_stage=True, admin_email=session.get("admin_pending_email", _admin_email()))

            session["admin_authenticated"] = True
            session["admin_name"] = "Administrator"
            session["admin_email"] = session.get("admin_pending_email", _admin_email())
            _clear_admin_otp_session()
            flash("Admin login successful.", "success")
            return redirect(url_for("admin_dashboard"))

        email = _normalize_email(request.form.get("email", ""))
        password = request.form.get("password", "")

        if not email or not password:
            flash("Admin email and password are required.", "error")
            return render_template("admin_login.html", otp_stage=False, admin_email=_admin_email())

        if email != _admin_email():
            flash("Invalid admin credentials.", "error")
            return render_template("admin_login.html", otp_stage=False, admin_email=_admin_email())

        admin_password_hash = _admin_password_hash()
        if admin_password_hash:
            password_ok = check_password_hash(admin_password_hash, password)
        else:
            password_ok = password == _admin_password()

        if not password_ok:
            flash("Invalid admin credentials.", "error")
            return render_template("admin_login.html", otp_stage=False, admin_email=_admin_email())

        try:
            otp = _issue_admin_otp()
            send_admin_otp_email(email, otp)
        except Exception:
            _clear_admin_otp_session()
            flash("Admin OTP could not be sent. Check SMTP settings and try again.", "error")
            return render_template("admin_login.html", otp_stage=False, admin_email=_admin_email())

        flash("An OTP has been sent to the admin email.", "success")
        return render_template("admin_login.html", otp_stage=True, admin_email=email)

    return render_template("admin_login.html", otp_stage=otp_stage, admin_email=session.get("admin_pending_email", _admin_email()) if otp_stage else _admin_email())


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_authenticated", None)
    session.pop("admin_name", None)
    session.pop("admin_email", None)
    _clear_admin_otp_session()
    flash("Admin logged out.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    stats = {
        "total_users": 0,
        "total_analyses": 0,
        "active_users": 0,
        "last_analysis_at": None,
    }
    users = []
    feedback_entries = []
    try:
        conn = get_db_connection()
        ensure_db_schema(conn)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        stats["total_users"] = cursor.fetchone().get("total_users", 0)

        cursor.execute("SELECT COUNT(*) AS total_analyses FROM analysis_history")
        stats["total_analyses"] = cursor.fetchone().get("total_analyses", 0)

        cursor.execute("SELECT COUNT(DISTINCT user_id) AS active_users FROM analysis_history")
        stats["active_users"] = cursor.fetchone().get("active_users", 0)

        cursor.execute("SELECT MAX(created_at) AS last_analysis_at FROM analysis_history")
        stats["last_analysis_at"] = cursor.fetchone().get("last_analysis_at")

        cursor.execute(
            """
            SELECT
                u.id,
                u.username,
                u.email,
                u.created_at,
                COUNT(h.id) AS analyses_count,
                MAX(h.created_at) AS last_analysis_at
            FROM users u
            LEFT JOIN analysis_history h ON h.user_id = u.id
            GROUP BY u.id, u.username, u.email, u.created_at
            ORDER BY u.created_at DESC
            LIMIT 100
            """
        )
        users = cursor.fetchall()

        cursor.execute(
            """
            SELECT id, name, message, rating
            FROM feedback
            ORDER BY id DESC
            LIMIT 100
            """
        )
        feedback_entries = cursor.fetchall()
        cursor.close()
        conn.close()
    except mysql.connector.Error:
        flash("Could not load admin dashboard data.", "error")

    return render_template(
        "admin_dashboard.html",
        stats=stats,
        users=users,
        feedback_entries=feedback_entries,
    )


@app.route("/admin/users/create", methods=["POST"])
@admin_required
def admin_create_user():
    username = request.form.get("username", "").strip()
    email = _normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not username or not email or not password or not confirm_password:
        flash("All fields are required to add a user.", "error")
        return redirect(url_for("admin_dashboard"))

    if not _is_valid_username(username):
        flash("Username must be between 3 and 50 characters.", "error")
        return redirect(url_for("admin_dashboard"))

    if not _is_valid_email(email):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("admin_dashboard"))

    if not _is_valid_password(password):
        flash("Password must be at least 8 characters.", "error")
        return redirect(url_for("admin_dashboard"))

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        conn = get_db_connection()
        ensure_db_schema(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            flash("That username or email is already in use.", "error")
            return redirect(url_for("admin_dashboard"))

        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username, email, generate_password_hash(password)),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error:
        flash("Could not add the user right now. Please try again.", "error")
        return redirect(url_for("admin_dashboard"))

    flash(f"User '{username}' was added successfully.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    try:
        conn = get_db_connection()
        ensure_db_schema(conn)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            flash("User not found.", "error")
            return redirect(url_for("admin_dashboard"))

        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error:
        flash("Could not delete that user right now.", "error")
        return redirect(url_for("admin_dashboard"))

    flash(f"User '{user['username']}' was deleted.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/feedback/<int:feedback_id>/delete", methods=["POST"])
@admin_required
def admin_delete_feedback(feedback_id):
    try:
        conn = get_db_connection()
        ensure_db_schema(conn)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, message FROM feedback WHERE id = %s", (feedback_id,))
        feedback = cursor.fetchone()

        if not feedback:
            cursor.close()
            conn.close()
            flash("Feedback not found.", "error")
            return redirect(url_for("admin_dashboard"))

        cursor.execute("DELETE FROM feedback WHERE id = %s", (feedback_id,))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error:
        flash("Could not delete that feedback right now.", "error")
        return redirect(url_for("admin_dashboard"))

    flash(f"Feedback from '{feedback['name']}' was deleted.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/analyze-skin")
@login_required
def analyze_skin():
    return render_template("analyze_skin.html")


@app.route("/analysis", methods=["POST"])
@login_required
def analysis():
    file = request.files.get("skin_image")

    if not file or file.filename == "":
        flash("No image uploaded", "error")
        return redirect(url_for("analyze_skin"))

    allowed_ext = {"jpg", "jpeg", "png"}
    if "." not in file.filename:
        flash("Invalid image file", "error")
        return redirect(url_for("analyze_skin"))

    ext = file.filename.rsplit(".", 1)[1].lower()
    if ext not in allowed_ext:
        flash("Only JPG, JPEG, PNG images are allowed", "error")
        return redirect(url_for("analyze_skin"))

    image_bytes = file.read()
    if not image_bytes:
        flash("The uploaded image was empty. Please choose a valid photo.", "error")
        return redirect(url_for("analyze_skin"))

    if len(image_bytes) > 10 * 1024 * 1024:
        flash("Please upload an image smaller than 10MB.", "error")
        return redirect(url_for("analyze_skin"))

    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        flash("Invalid image file", "error")
        return redirect(url_for("analyze_skin"))

    try:
        result = analyze_skin_image(img)
    except Exception:
        flash(
            "We hit an unexpected issue while analyzing that photo. "
            "Please try again with a clear front-facing image.",
            "error"
        )
        return redirect(url_for("analyze_skin"))

    if not result.get("face_detected"):
        flash(
            "We could not confidently analyze this photo. "
            "Please upload a clear, front-facing human face photo with the full face visible.",
            "error"
        )
        return redirect(url_for("analyze_skin"))

    if not result.get("analysis_ok", True):
        flash(
            result.get(
                "analysis_message",
                "We could not confidently analyze this photo. Please retake it in brighter light."
            ),
            "error"
        )
        return redirect(url_for("analyze_skin"))

    skin_concern = result.get("skin_concern", "Clear Skin")
    if skin_concern not in {"Dark Circles", "Pimples / Acne", "Dark Spots", "Clear Skin"}:
        skin_concern = "Clear Skin"

    session["skin_concern"] = skin_concern
    session["age"] = result.get("age")
    session["analysis_confidence"] = result.get("confidence", 0.0)
    session["analysis_scores"] = result.get("scores", {})
    session["analysis_message"] = result.get("analysis_message", "")
    session["analysis_warning"] = result.get("analysis_warning", "")
    session.pop("last_saved_signature", None)

    if result.get("analysis_warning"):
        flash(result["analysis_warning"], "error")
    elif result.get("low_confidence"):
        flash(
            "The model confidence is low for this image. Result may be less accurate.",
            "error"
        )

    return redirect(url_for("show_concern"))


@app.route("/show-concern")
@login_required
def show_concern():
    concern = session.get("skin_concern", "Clear Skin")
    confidence = float(session.get("analysis_confidence", 0.0))
    scores = session.get("analysis_scores", {}) or {}
    concern_rows = _build_detected_concerns(scores)
    active_targets = [row["name"].lower() for row in concern_rows if row["detected"]]
    summary_targets = ", ".join(active_targets) if active_targets else "overall skin health"
    overall_subtitle, overall_title, assessment_text = _assessment_copy(
        concern,
        confidence,
        concern_rows
    )

    return render_template(
        "skin_concern.html",
        concern=concern,
        confidence=confidence,
        concern_rows=concern_rows,
        summary_targets=summary_targets,
        overall_subtitle=overall_subtitle,
        overall_title=overall_title,
        assessment_text=assessment_text,
        analysis_message=session.get("analysis_message", ""),
        analysis_warning=session.get("analysis_warning", "")
    )


@app.route("/details", methods=["GET", "POST"])
@login_required
def details():
    if request.method == "POST":
        age_raw = request.form.get("age", "").strip()
        try:
            age = int(age_raw)
        except ValueError:
            flash("Please enter a valid age.", "error")
            return redirect(url_for("details"))

        if age < 18 or age > 50:
            flash("Age must be between 18 and 50.", "error")
            return redirect(url_for("details"))

        session["age"] = age
        session["skin_type"] = request.form["skin_type"]
        session["preferred_brand"] = request.form["preferred_brand"]
        return redirect(url_for("results"))

    return render_template("details.html", all_brands=ALL_BRANDS)


@app.route("/results")
@login_required
def results():
    brand_override = request.args.get("brand", "").strip()
    if brand_override in ALL_BRANDS:
        session["preferred_brand"] = brand_override

    routine = generate_skincare_routine(
        skin_concern=session.get("skin_concern"),
        age=session.get("age"),
        skin_type=session.get("skin_type"),
        lifestyle=session.get("lifestyle"),
        preferred_brand=session.get("preferred_brand")
    )

    user_id = session.get("user_id")
    concern = session.get("skin_concern", "Clear Skin")
    age = session.get("age")
    skin_type = session.get("skin_type")
    selected_brand = routine.get("selected_brand")

    signature = f"{concern}|{age}|{skin_type}|{selected_brand}"
    if user_id and session.get("last_saved_signature") != signature:
        try:
            save_history_entry(
                user_id=user_id,
                detected_concern=concern,
                age=age,
                skin_type=skin_type,
                selected_brand=selected_brand,
                routine=routine,
            )
            session["last_saved_signature"] = signature
        except mysql.connector.Error:
            flash("Could not save analysis history right now.", "error")

    return render_template(
        "results.html",
        routine=routine,
        all_brands=ALL_BRANDS
    )


@app.route("/history")
@login_required
def history():
    entries = []
    try:
        conn = get_db_connection()
        ensure_db_schema(conn)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, detected_concern, age, skin_type, selected_brand, routine_json, created_at
            FROM analysis_history
            WHERE user_id = %s
            ORDER BY created_at DESC, id DESC
            LIMIT 25
            """,
            (session.get("user_id"),),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        for row in rows:
            try:
                routine = json.loads(row.get("routine_json") or "{}")
            except json.JSONDecodeError:
                routine = {}

            row["routine"] = routine
            entries.append(row)
    except mysql.connector.Error:
        flash("Could not load history right now.", "error")

    return render_template("history.html", entries=entries)


@app.route("/history/download/<int:entry_id>")
@login_required
def download_history_pdf(entry_id):
    try:
        conn = get_db_connection()
        ensure_db_schema(conn)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, detected_concern, age, skin_type, selected_brand, routine_json, created_at
            FROM analysis_history
            WHERE id = %s AND user_id = %s
            """,
            (entry_id, session.get("user_id")),
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
    except mysql.connector.Error:
        flash("Could not generate PDF right now.", "error")
        return redirect(url_for("history"))

    if not row:
        flash("History record not found.", "error")
        return redirect(url_for("history"))

    try:
        routine = json.loads(row.get("routine_json") or "{}")
    except json.JSONDecodeError:
        routine = {}

    lines = [
        f"User: {session.get('user_name', '')}",
        f"Generated: {row.get('created_at')}",
        f"Detected concern: {row.get('detected_concern', 'Clear Skin')}",
        f"Age: {row.get('age')}",
        f"Skin type: {row.get('skin_type')}",
        f"Brand: {row.get('selected_brand')}",
        "",
        "Morning Routine:",
    ]
    for idx, item in enumerate(routine.get("morning", []), start=1):
        lines.append(f"{idx}. {item.get('display_step', 'Step')} - {item.get('product', '')} ({item.get('brand', '')})")
        lines.append(f"   Buy: {item.get('buy_url', '')}")

    lines.append("")
    lines.append("Evening Routine:")
    for idx, item in enumerate(routine.get("evening", []), start=1):
        lines.append(f"{idx}. {item.get('display_step', 'Step')} - {item.get('product', '')} ({item.get('brand', '')})")
        lines.append(f"   Buy: {item.get('buy_url', '')}")

    pdf_bytes = _build_simple_pdf("SkinSmart Recommendation Report", lines)
    filename = f"skinsmart-history-{entry_id}.pdf"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.route("/history/delete/<int:entry_id>", methods=["POST"])
@login_required
def delete_history_entry(entry_id):
    try:
        conn = get_db_connection()
        ensure_db_schema(conn)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM analysis_history WHERE id = %s AND user_id = %s",
            (entry_id, session.get("user_id")),
        )
        conn.commit()
        deleted_count = cursor.rowcount
        cursor.close()
        conn.close()
    except mysql.connector.Error:
        flash("Could not delete history entry right now.", "error")
        return redirect(url_for("history"))

    if deleted_count:
        flash("History entry deleted.", "success")
    else:
        flash("History entry not found.", "error")
    return redirect(url_for("history"))


@app.route("/history/delete-all", methods=["POST"])
@login_required
def delete_all_history():
    try:
        conn = get_db_connection()
        ensure_db_schema(conn)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM analysis_history WHERE user_id = %s",
            (session.get("user_id"),),
        )
        conn.commit()
        deleted_count = cursor.rowcount
        cursor.close()
        conn.close()
    except mysql.connector.Error:
        flash("Could not delete history right now.", "error")
        return redirect(url_for("history"))

    if deleted_count:
        flash(f"Deleted {deleted_count} history entries.", "success")
    else:
        flash("No history entries to delete.", "error")
    return redirect(url_for("history"))


@app.errorhandler(404)
def page_not_found(_error):
    return render_template(
        "error_state.html",
        title="Page Not Found",
        message="The page you were looking for does not exist or may have moved.",
        action_url=url_for("home"),
        action_label="Back to Home",
    ), 404


@app.errorhandler(413)
def file_too_large(_error):
    return render_template(
        "error_state.html",
        title="File Too Large",
        message="Please upload an image smaller than 10MB and try again.",
        action_url=url_for("analyze_skin") if session.get("user_id") else url_for("home"),
        action_label="Try Again",
    ), 413


@app.errorhandler(500)
def internal_error(_error):
    return render_template(
        "error_state.html",
        title="Something Went Wrong",
        message="An unexpected error occurred. Please try again in a moment.",
        action_url=url_for("home"),
        action_label="Back to Home",
    ), 500


if __name__ == "__main__":
    socketio.run(app, debug=True)
