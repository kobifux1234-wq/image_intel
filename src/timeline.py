from extractor import extract_all
from pathlib import Path
from datetime import datetime


def clean_text(value, default="Unknown"):
    if not value:
        return default
    return str(value).replace("\x00", "").strip()


def format_datetime(value):
    if not value:
        return "N/A"

    try:
        dt = datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y • %H:%M")
    except Exception:
        return str(value)


def format_location(value):
    if not value:
        return "Location does not exist."
    return str(value)


def build_device_name(img):
    make = clean_text(img.get("camera_make"), "")
    model = clean_text(img.get("camera_model"), "")

    full_name = f"{make} {model}".strip()

    if not full_name:
        return "Unknown"
    return full_name


def get_device_logo_html(img):
    make = clean_text(img.get("camera_make"), "").lower()
    model = clean_text(img.get("camera_model"), "").lower()
    text = f"{make} {model}"

    if "apple" in text or "iphone" in text:
        return '<img src="../src/static/logos/apple.png" class="device-logo" alt="Apple logo">'

    if "samsung" in text or "galaxy" in text or "sm-" in text:
        return '<img src="/static/logos/samsung.png" class="device-logo" alt="Samsung logo">'

    if "canon" in text:
        return '<img src="/static/logos/Canon.png" class="device-logo" alt="Canon logo">'

    if "sony" in text:
        return '<img src="/static/logos/sony.png" class="device-logo" alt="Sony logo">'

    if "lg" in text:
        return '<img src="/static/logos/lg.png" class="device-logo" alt="LG logo">'

    if "xiaomi" in text or "redmi" in text:
        return '<img src="/static/logos/xiaomi.png" class="device-logo" alt="Xiaomi logo">'

    return '<span class="device-emoji" aria-label="camera">📷</span>'


def build_events(images_data):
    sorted_data = sorted(
        images_data,
        key=lambda x: (x.get("datetime") is None, x.get("datetime") or "")
    )

    events_html = ""

    for img in sorted_data:
        filename = img.get("filename", "")
        image_path = f"/cache/{img['filename']}"

        device_name = build_device_name(img)
        device_logo_html = get_device_logo_html(img)
        location_text = format_location(img.get("location"))
        date_text = format_datetime(img.get("datetime"))

        events_html += f"""
<div class="event">

    <div class="date">
        {date_text}
    </div>

    <a href="{image_path}" target="_blank">
        <img src="{image_path}" class="photo" alt="{filename}">
    </a>

    <div class="device">
        {device_logo_html}
        <span class="label">Device:</span>
        <span>{device_name}</span>
    </div>

    <div class="location">
        <span class="label">📍 Location:</span>
        <span>{location_text}</span>
    </div>

</div>
"""

    return events_html


def create_timeline(images_data):
    # קריאה לפונקציית העזר
    events_html = build_events(images_data)

    final_html = f"""
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Photo Intelligence Timeline</title>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&display=swap" rel="stylesheet">

    <style>
    body {{
        font-family: 'Heebo', sans-serif;
        background: #eef2f3;
        padding: 40px;
        direction: rtl;    /* תיקון כיוון */
        text-align: right; /* יישור לימין */
    }}

    h1 {{
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }}

    /* --- תיקון הקו הכחול לימין --- */
    .timeline {{
        border-right: 4px solid #1a73e8; 
        border-left: none;
        padding-right: 40px;
        padding-left: 0;
        margin-right: 25px;
        margin-left: 0;
    }}

    .event {{
        position: relative;
        background: white;
        padding: 18px;
        margin-bottom: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        width: 420px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .event:hover {{
        transform: translateY(-4px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.18);
    }}

    /* --- תיקון הנקודה הכחולה לימין --- */
    .event::before {{
        content: "";
        position: absolute;
        right: -50px;  /* זז ימינה כדי לשבת על הקו */
        left: auto;    /* ביטול ה-left הישן */
        top: 20px;
        width: 14px;
        height: 14px;
        background: #3498db;
        border-radius: 50%;
        border: 3px solid #eef2f3;
    }}

    .date {{
        font-weight: bold;
        color: #2980b9;
        margin-bottom: 10px;
        text-align: left; /* תאריך באנגלית נראה טוב יותר משמאל */
    }}

    .photo {{
        width: 100%;
        height: 220px;
        object-fit: cover;
        border-radius: 8px;
        margin: 10px 0;
        display: block;
    }}
    .device-logo {{
        height: 24px;
        width: auto;
        object-fit: contain;
    }}
    .label {{
        font-weight: bold;
        color: #555;
        margin-left: 5px; /* רווח משמאל לנקודותיים */
    }}

    .device, .location {{
        display: flex;
        align-items: center;
        gap: 5px;
        margin-top: 8px;
        margin-bottom: 8px;
        flex-wrap: wrap;
    }}

    a {{
        text-decoration: none;
        color: inherit;
    }}
    </style>
</head>
<body>

<h1>Photo Timeline</h1>

<div class="timeline">
{events_html}
</div>

</body>
</html>
"""
    return final_html
