from extractor import extract_all
from pathlib import Path


def build_events(images_data):
    sorted_data = sorted(images_data, key=lambda x: x.get("datetime") or "")
    events_html = ""

    for img in sorted_data:
        filename = img.get("filename", "")
        image_path = f"../images/nigga/{filename}"

        events_html += f"""
<div class="event">

<div class="date">
{img.get('datetime', 'N/A')}
</div>

<img src="{image_path}" class="photo" alt="{filename}">

<div>
<span class="label">Device:</span>
{img.get('camera_model', 'Unknown')}
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
    base_dir = Path(__file__).resolve().parent.parent
    images_path = base_dir / "images" / "ready"

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