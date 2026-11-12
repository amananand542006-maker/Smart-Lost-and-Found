# Smart Lost & Found

Smart Lost & Found is a Flask-based web application for managing lost and found items in a campus or workplace setting. It allows users to browse available items, report new finds, upload photos, and generate QR codes for rapid item lookup.

## Overview

The system is designed around a simple workflow:

- A user reports a found item through a form.
- The item is stored in a SQLite database.
- A unique ID is generated for the item.
- A QR code is created for quick identification.
- Other users can scan the QR code or browse the home page to view item details.

## Features

- Responsive item listing page
- Item detail page with description and metadata
- Report form with validation for name, location, and description
- Photo upload support or camera capture from the browser
- QR code generation for each item
- SQLite database for persistent storage
- Optional webcam-based QR-scanning utility for quick access to item pages
- Sample seed data for initial testing and demos

## Tech Stack

- Python 3
- Flask
- SQLite
- Pillow
- qrcode
- OpenCV
- HTML/CSS templates

## Project Structure

```text
Smart-Lost-and-Found/
├── app.py                  # Main Flask app and database setup
├── scanner.py              # Webcam QR scanner utility
├── generate_qr.py          # Generates QR codes for existing items
├── requirements.txt        # Python dependencies
├── database/
│   └── lost_found.db      # SQLite database (created at runtime)
├── qr_codes/              # Generated QR code images
├── static/
│   ├── css/
│   ├── uploads/
│   └── ...
├── templates/
│   ├── index.html
│   ├── item.html
│   └── report.html
└── README.md
```

## Installation

1. Open a terminal in the project folder.
2. Create and activate a virtual environment:

```bash
cd Smart-Lost-and-Found
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the application:

```bash
python app.py
```

The app runs by default at:

```text
http://127.0.0.1:5001
```

## Running the App

Once the server is running, you can:

- Open the homepage to browse all items.
- Click an item to view its details.
- Submit a new lost/found item report from the report page.

## QR Code Support

The project includes two QR-related utilities:

### Generate QR codes for all items

```bash
python generate_qr.py
```

This creates QR images in the `qr_codes/` folder.

### Scan QR codes with a webcam

```bash
python scanner.py
```

The scanner uses the webcam to detect QR codes and opens the matching item page in the browser.

## Database

The application creates a SQLite database at `database/lost_found.db` when it starts. The database stores:

- `items`: item information such as ID, name, description, location, date, and status
- `report_submissions`: image submission data and timestamps

The app also seeds a few sample items automatically when the database is initialized.

## Notes

- The `GOOGLE_FORM_URL` in `app.py` is currently a placeholder and should be replaced with the real form link if you want item claims to redirect to a Google Form.
- The app is intended for local development and demonstration use, but it can be extended for production deployment with proper authentication, validation, and deployment configuration.

## Development Notes

This project is a compact, full-stack Python app with a simple front-end and database-backed backend. It is especially suitable as a student project, campus utility, or prototype for a real lost-and-found system.
