
from flask import (
    Flask, render_template, abort, redirect,
    request, url_for, send_from_directory
)
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename
from datetime import date

import qrcode
import io
import sqlite3
import os
import uuid

app = Flask(__name__)

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(BASE_DIR, "database", "lost_found.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
QR_FOLDER = os.path.join(BASE_DIR, "qr_codes")

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

GOOGLE_FORM_URL = "https://forms.gle/YOUR_FORM_LINK"

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}


# DATABASE CONNECTION

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# DATABASE INITIALIZATION

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(QR_FOLDER, exist_ok=True)

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            location TEXT,
            date_found TEXT,
            status TEXT DEFAULT 'Available'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS report_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            image_filename TEXT NOT NULL,
            image_source TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    sample_items = [
        ("ITEM001", "Laptop", "Black laptop found in classroom.",
         "Computer Lab", "2026-11-12", "Available"),
        ("ITEM002", "Wallet", "Brown wallet found near the library.",
         "Library", "2026-11-12", "Available"),
        ("ITEM003", "Water Bottle", "Blue water bottle.",
         "College Canteen", "2026-11-12", "Available"),
        ("ITEM004", "ID Card", "Student ID card found.",
         "Main Building", "2026-11-12", "Available")
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO items
        (id, name, description, location, date_found, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, sample_items)

    conn.commit()
    conn.close()


# HOMEPAGE

@app.route("/")
def home():
    conn = get_db()

    items = conn.execute("""
        SELECT * FROM items
        ORDER BY date_found DESC, id DESC
    """).fetchall()

    conn.close()

    return render_template("index.html", items=items)


# ITEM DETAILS

@app.route("/item/<item_id>")
def item_details(item_id):
    conn = get_db()

    item = conn.execute("""
        SELECT * FROM items WHERE id = ?
    """, (item_id,)).fetchone()

    conn.close()

    if item is None:
        abort(404)

    return render_template(
        "item.html",
        item=item,
        form_url=GOOGLE_FORM_URL
    )


# VIEW GENERATED QR CODE

@app.route("/qr/<item_id>")
def qr_code(item_id):
    filename = f"{item_id}.png"

    if not os.path.isfile(os.path.join(QR_FOLDER, filename)):
        abort(404)

    return send_from_directory(
        QR_FOLDER,
        filename,
        mimetype="image/png"
    )


# REPORT A NEW ITEM

@app.route("/report", methods=["GET", "POST"])
def report_item():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        image_source = request.form.get("image_source", "")
        photo = request.files.get("photo")

        errors = []

        if not name:
            errors.append("Please enter the item name.")
        elif len(name) > 100:
            errors.append("Item name must be 100 characters or fewer.")

        if not location:
            errors.append("Please enter where the item was found.")
        elif len(location) > 150:
            errors.append("Location must be 150 characters or fewer.")

        if not description:
            errors.append("Please describe the item.")
        elif len(description) > 2000:
            errors.append("Description must be 2000 characters or fewer.")

        if image_source not in {"camera", "upload"}:
            errors.append("Please choose camera or upload a photo.")

        if photo is None or not photo.filename:
            errors.append("Please select or capture a photo.")

        extension = ""

        if photo is not None and photo.filename:
            safe_name = secure_filename(photo.filename)

            if "." not in safe_name:
                errors.append("Invalid image filename.")
            else:
                extension = safe_name.rsplit(".", 1)[-1].lower()

                if extension not in ALLOWED_IMAGE_EXTENSIONS:
                    errors.append("Use JPG, JPEG, PNG, or WebP images.")
                else:
                    try:
                        image = Image.open(io.BytesIO(photo.read()))
                        image.verify()

                        if image.format not in ALLOWED_IMAGE_FORMATS:
                            errors.append("Unsupported image format.")

                    except (
                        Image.DecompressionBombError,
                        UnidentifiedImageError,
                        OSError,
                        SyntaxError
                    ):
                        errors.append("The selected file is not a valid image.")
                    finally:
                        photo.seek(0)

        if errors:
            return render_template(
                "report.html",
                submitted=False,
                errors=errors,
                name=name,
                location=location,
                description=description,
                image_source=image_source
            ), 400

        # Create unique item ID
        item_id = "ITEM" + uuid.uuid4().hex[:8].upper()

        # Create filenames
        filename = f"{uuid.uuid4().hex}.{extension}"
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        qr_path = os.path.join(QR_FOLDER, f"{item_id}.png")

        # Save photo and QR code
        photo.save(image_path)

        try:
            qr = qrcode.make(item_id)
            qr.save(qr_path)

            conn = get_db()

            try:
                conn.execute("""
                    INSERT INTO items
                    (id, name, description, location, date_found, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item_id,
                    name,
                    description,
                    location,
                    date.today().isoformat(),
                    "Available"
                ))

                conn.execute("""
                    INSERT INTO report_submissions
                    (description, image_filename, image_source)
                    VALUES (?, ?, ?)
                """, (
                    description,
                    filename,
                    image_source
                ))

                conn.commit()

            finally:
                conn.close()

        except Exception:
            if os.path.exists(image_path):
                os.remove(image_path)

            if os.path.exists(qr_path):
                os.remove(qr_path)

            raise

        return redirect(
            url_for("report_item", submitted="1", item_id=item_id)
        )

    return render_template(
        "report.html",
        submitted=request.args.get("submitted") == "1",
        item_id=request.args.get("item_id", ""),
        errors=[],
        name="",
        location="",
        description="",
        image_source="upload"
    )


# FILE SIZE ERROR

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template(
        "report.html",
        submitted=False,
        errors=["Photo must be 10 MB or smaller."],
        name="",
        location="",
        description="",
        image_source="upload"
    ), 413


# PAGE NOT FOUND

@app.errorhandler(404)
def page_not_found(error):
    return """
    <h1>404 - Item Not Found</h1>
    <p>The requested item does not exist.</p>
    <a href="/">Back to Homepage</a>
    """, 404


# START APPLICATION

if __name__ == "__main__":
    init_db()

    print("----------------------------------")
    print(" SMART LOST & FOUND SYSTEM")
    print("----------------------------------")
    print("Website: http://127.0.0.1:5001")
    print("Database: SQLite")
    print("QR Scanner: Ready")
    print("----------------------------------")

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )

