from PIL import Image
from PIL.ExifTags import TAGS
from pathlib import Path
from geopy.geocoders import Nominatim
from datetime import datetime
import re

"""
extractor.py - שליפת EXIF מתמונות
צוות 1, זוג A

ראו docs/api_contract.md לפורמט המדויק של הפלט.
"""

geolocator = Nominatim(user_agent="image_intel")


def convert_to_degrees(value):
    try:
        return float(value[0] + (value[1] / 60) + (value[2] / 3600))
    except Exception:
        return None


def get_gps_decimal(exif_data):
    if not exif_data or 'GPSInfo' not in exif_data:
        return None, None

    gps_info = exif_data['GPSInfo']

    try:
        lat = convert_to_degrees(gps_info[2])
        lon = convert_to_degrees(gps_info[4])

        if gps_info.get(1) == 'S': lat = -lat
        if gps_info.get(3) == 'W': lon = -lon

        return lat, lon
    except:
        return None, None

def datatime(data: dict):
    try:
        return data['DateTimeOriginal'].replace(':', "-", 2)
    except Exception:
        return None


def camera_make(data: dict):
    try:
        return data['Make']
    except Exception:
        return None


def camera_model(data: dict):
    try:
        return data['Model']
    except Exception:
        return None


def location(lat, lon):
    try:
        if lat is None or lon is None:
            return None

        my_location = geolocator.reverse((lat, lon), language='en')

        if my_location is None:
            return None

        address = my_location.raw.get("address", {})

        city = (
            address.get("city")
            or address.get("town")
            or address.get("village")
            or address.get("municipality")
        )

        extra_place = (
            address.get("road")
            or address.get("suburb")
            or address.get("neighbourhood")
            or address.get("quarter")
        )

        if city and extra_place:
            return f"{city} - {extra_place}"

        if city:
            return city

        return None

    except Exception:
        return None


import re
from datetime import datetime


def extract_date_from_filename(filename):
    filename = filename.replace('\u200e', '').replace('\u200f', '')

    patterns = [
        (r"(\d{4}-\d{2}-\d{2}).*?(\d{2}\.\d{2}\.\d{2})", "WhatsApp"),
        # Samsung/Android
        (r"(\d{8}_\d{6})", "%Y%m%d_%H%M%S"),
    ]

    for pattern, label in patterns:
        match = re.search(pattern, filename)
        if match:
            try:
                if label == "WhatsApp":
                    date_part = match.group(1)
                    time_part = match.group(2).replace(".", ":")
                    combined = f"{date_part} {time_part}"
                    return datetime.strptime(combined, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
                else:
                    return datetime.strptime(match.group(1), label).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
    return None



def extract_metadata(image_path):
    """
    שולף EXIF מתמונה בודדת.

    Args:
        image_path: נתיב לקובץ תמונה

    Returns:
        dict עם: filename, datetime, latitude, longitude,
        camera_make, camera_model, has_gps, location
    """

    path = Path(image_path)
    raw_exif = {}

    try:
        with Image.open(image_path) as img:
            exif_raw = img._getexif()
            if exif_raw:
                for tag_id, value in exif_raw.items():
                    tag = TAGS.get(tag_id, tag_id)
                    raw_exif[tag] = value
    except:pass


    lat, lon = get_gps_decimal(raw_exif)

    dt_str = raw_exif.get('DateTimeOriginal') or raw_exif.get('DateTime')
    if dt_str:
        dt_str = dt_str.replace(':', '-', 2)  # פורמט YYYY-MM-DD
    else:
        dt_str = extract_date_from_filename(path.name)


    exif_dict = {
        "filename": path.name,
        "datetime": dt_str,
        "latitude": lat,
        "longitude": lon,
        "camera_make": camera_make(raw_exif),
        "camera_model": camera_model(raw_exif),
        "has_gps": lat is not None,
        "location": location(lat,lon)
    }
    return exif_dict


def extract_all(folder_path):
    """
    שולף EXIF מכל התמונות בתיקייה.

    Args:
        folder_path: נתיב לתיקייה

    Returns:
        list של dicts (כמו extract_metadata)
    """
    all_exif_list = []
    #extensions = ['*.jpg', '*.jpeg', '*.png']
    # folder = Path(folder_path)
    # for ext in extensions:
    #     for file_path in folder.glob(ext):
    #         all_exif_list.append(extract_metadata(file_path))
    python_files = list(Path(folder_path).glob('*.jpg'))

    for file in python_files:
        all_exif_list.append(extract_metadata(file))

    return all_exif_list