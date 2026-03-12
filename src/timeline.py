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
        return '<img src="../src/static/logos/samsung.png" class="device-logo" alt="Samsung logo">'

    if "canon" in text:
        return '<img src="../src/static/logos/Canon.png" class="device-logo" alt="Canon logo">'

    if "sony" in text:
        return '<img src="../src/static/logos/sony.png" class="device-logo" alt="Sony logo">'

    if "lg" in text:
        return '<img src="../src/static/logos/lg.png" class="device-logo" alt="LG logo">'

    if "xiaomi" in text or "redmi" in text:
        return '<img src="../src/static/logos/xiaomi.png" class="device-logo" alt="Xiaomi logo">'

    return '<span class="device-emoji" aria-label="camera">📷</span>'


def build_events(images_data):
    sorted_data = sorted(
        images_data,
        key=lambda x: (x.get("datetime") is None, x.get("datetime") or "")
    )

    events_html = ""

    for img in sorted_data:
        filename = img.get("filename", "")
        image_path = f"../images/nigga/{filename}"

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


def generate_timeline_html(images_data):
    events_html = build_events(images_data)

    # Hardcoded HTML template with Heebo font and your original CSS
    final_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Photo Intelligence Timeline</title>

    <!-- Google Fonts: Heebo -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com" rel="stylesheet">

    <style>
    body{{
        font-family: 'Heebo', sans-serif; /* Applied Heebo here */
        background: #eef2f3;
        padding: 40px;
    }}

    h1{{
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }}

    .timeline{{
        border-left: 4px solid #3498db;
        margin-left: 40px;
        padding-left: 25px;
    }}

    .event{{
        position: relative;
        background: white;
        padding: 18px;
        margin-bottom: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        width: 420px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .event:hover{{
        transform: translateY(-4px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.18);
    }}

    .event::before{{
        content: "";
        position: absolute;
        left: -33px;
        top: 20px;
        width: 14px;
        height: 14px;
        background: #3498db;
        border-radius: 50%;
    }}

    .date{{
        font-weight: bold;
        color: #2980b9;
        margin-bottom: 10px;
    }}

    .photo{{
        width: 100%;
        height: 220px;
        object-fit: cover;
        border-radius: 8px;
        margin: 10px 0;
        display: block;
    }}

    .label{{
        font-weight: bold;
        color: #555;
    }}

    .device{{
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 8px;
        margin-bottom: 8px;
        flex-wrap: wrap;
    }}

    .device-logo{{
        width: 42px;
        height: 24px;
        object-fit: contain;
        display: block;
    }}

    .device-emoji{{
        font-size: 24px;
        line-height: 1;
        display: inline-block;
    }}

    .location{{
        margin-top: 6px;
        line-height: 1.5;
        word-break: break-word;
    }}

    a{{
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


def main():
    base_dir = Path(__file__).resolve().parent.parent
    images_path = base_dir / "images" / "sample_data"

    print("Extracting data...")
    extracted_data = extract_all(str(images_path))

    print("Generating timeline...")
    final_html = generate_timeline_html(extracted_data)

    output_dir = base_dir / "output"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "timeline.html"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_html)

    print("-" * 40)
    print("SUCCESS!")
    print(f"Timeline created at: {output_file}")
    print("-" * 40)


if __name__ == "__main__":
    main()