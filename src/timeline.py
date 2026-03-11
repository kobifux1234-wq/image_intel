from extractor import extract_all
from pathlib import Path


def clean_text(value, default="Unknown"):
    if not value:
        return default
    return str(value).replace("\x00", "").strip()


def format_datetime(value):
    if not value:
        return "N/A"
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


def build_events(images_data):
    sorted_data = sorted(images_data, key=lambda x: x.get("datetime") or "")
    events_html = ""

    for img in sorted_data:
        filename = img.get("filename", "")
        image_path = f"../images/nigga/{filename}"

        device_name = build_device_name(img)
        location_text = format_location(img.get("location"))
        date_text = format_datetime(img.get("datetime"))

        events_html += f"""
<div class="event">

<div class="date">
{date_text}
</div>

<img src="{image_path}" class="photo" alt="{filename}">

<div>
<span class="label">Device:</span>
{device_name}
</div>

<div>
<span class="label">Location:</span>
{location_text}
</div>

</div>
"""

    return events_html


def generate_timeline_html(images_data):
    src_dir = Path(__file__).resolve().parent
    template_path = src_dir / "templates" / "timeline_template.html"

    with open(template_path, "r", encoding="utf-8") as f:
        template_html = f.read()

    events_html = build_events(images_data)
    final_html = template_html.replace("{{ EVENTS }}", events_html)

    return final_html


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    images_path = BASE_DIR / "images" / "nigga"

    print("Extracting data...")
    extracted_data = extract_all(str(images_path))

    print("Generating timeline...")
    final_html = generate_timeline_html(extracted_data)

    output_dir = BASE_DIR / "output"
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "timeline.html"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_html)

    print("-" * 40)
    print("SUCCESS!")
    print(f"Timeline created at: {output_file}")
    print("-" * 40)