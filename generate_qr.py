
import qrcode
import sqlite3
import os

os.makedirs("qr_codes", exist_ok=True)

conn = sqlite3.connect("database/lost_found.db")

items = conn.execute(
    "SELECT id, name FROM items"
).fetchall()

conn.close()

for item_id, name in items:
    qr = qrcode.make(item_id)

    filename = f"qr_codes/{item_id}.png"
    qr.save(filename)

    print(f"QR generated: {name} -> {filename}")
