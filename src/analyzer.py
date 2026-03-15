from datetime import datetime
from geopy.distance import geodesic
import pprint
from extractor import *

def analyze_data(data):
    # אם אין נתונים, נחזיר מילון ריק כדי שהקוד לא יקרוס
    if not data:
        return {"total_images": 0, "insights": ["לא נמצאו נתונים לניתוח"]}

    imgs_with_date = []
    for i in data:
        if i.get("datetime"):
            imgs_with_date.append(i)

    imgs_with_date.sort(key=lambda x: x["datetime"])

    # 2. חישוב סטטיסטיקות בסיסיות (כמו שזוג B התבקש)
    cameras = []
    gps_count = 0
    for i in data:
        model = i.get("camera_model")
        if model and model not in cameras:
            cameras.append(model)
        if i.get("has_gps"):
            gps_count += 1

    # מציאת טווח תאריכים (רק תאריך בלי שעה)
    start_date = imgs_with_date[0]["datetime"].split(" ")[0] if imgs_with_date else "N/A"
    end_date = imgs_with_date[-1]["datetime"].split(" ")[0] if imgs_with_date else "N/A"

    insights = []

    # 3. ניתוח דפוסים (החלפות, פערי זמן, מיקומים)

    # א. בדיקת החלפות מכשיר
    if len(cameras) > 1:
        insights.append(f"נמצאו {len(cameras)} מכשירים שונים - ייתכן שהסוכן החליף מכשירים")

    for i in range(1, len(imgs_with_date)):
        prev, curr = imgs_with_date[i - 1], imgs_with_date[i]

        # זיהוי החלפת מכשיר
        if prev.get("camera_model") != curr.get("camera_model"):
            date_only = curr["datetime"].split(" ")[0]
            insights.append(f"ב-{date_only} הסוכן עבר ממכשיר {prev['camera_model']} ל-{curr['camera_model']}")

        # ב. בדיקת פערי זמן (מעל 12 שעות)
        t1 = datetime.fromisoformat(prev["datetime"])
        t2 = datetime.fromisoformat(curr["datetime"])
        gap = (t2 - t1).total_seconds() / 3600
        if gap > 12:
            insights.append(f"פער זמן של {int(gap)} שעות בין {prev['filename']} ל-{curr['filename']}")

    # ג. בדיקת מיקום (ריכוז וחזרה)
    gps_imgs = [i for i in data if i.get("has_gps")]
    for i in range(len(gps_imgs)):
        for j in range(i + 1, len(gps_imgs)):
            dist = geodesic((gps_imgs[i]["latitude"], gps_imgs[i]["longitude"]),
                            (gps_imgs[j]["latitude"], gps_imgs[j]["longitude"])).km

            if dist < 1.0:
                time1 = datetime.fromisoformat(gps_imgs[i]["datetime"])
                time2 = datetime.fromisoformat(gps_imgs[j]["datetime"])
                time_gap = abs((time2 - time1).total_seconds() / 3600)

                if time_gap > 3:
                    insights.append(
                        f"חזרה למיקום: הסוכן חזר לאזור של {gps_imgs[i]['filename']} כעבור {int(time_gap)} שעות")
                else:
                    insights.append(f"ריכוז גיאוגרפי: {gps_imgs[i]['filename']} ו-{gps_imgs[j]['filename']} קרובות")

    # 4. הפלט הסופי בפורמט המדויק שנדרש מזוג B
    return {
        "total_images": len(data),
        "images_with_gps": gps_count,
        "images_with_datetime": len(imgs_with_date),
        "unique_cameras": cameras,
        "date_range": {"start": start_date, "end": end_date},
        "insights": insights
    }


if __name__ == "__main__":
    from pathlib import Path


    base_path = Path(__file__).resolve().parent.parent
    images_path = base_path / "images" / "nigga"

    extracted_data = extract_all(str(images_path))

    if not extracted_data:
        print("אזהרה: עדיין לא נמצאו תמונות. וודא שהתמונות בפורמט .jpg ונמצאות במיקום הנכון.")

    payoff = analyze_data(extracted_data)
    pprint.pprint(payoff, sort_dicts=False)