from flask import Flask, render_template, request, jsonify
import requests, base64, json, io, os, shutil, tempfile, atexit, ctypes
from flask import send_from_directory

app = Flask(__name__)

# הגדרת נתיב לתיקייה זמנית בתוך הפרויקט
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')

def hide_path(path):
    if os.name == 'nt':
        FILE_ATTRIBUTE_HIDDEN = 0x02
        ctypes.windll.kernel32.SetFileAttributesW(path, FILE_ATTRIBUTE_HIDDEN)

if os.path.exists(CACHE_DIR):
    shutil.rmtree(CACHE_DIR)
os.makedirs(CACHE_DIR)
hide_path(CACHE_DIR)

@app.route('/cache/<filename>')
def serve_temp_image(filename):
    return send_from_directory(CACHE_DIR, filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_images():
    if 'photos' not in request.files:
        return "לא נשלחו תמונות", 400

    files = request.files.getlist('photos')

    if not files or files[0].filename == '':
        return "לא נבחרו קבצים", 400

    # 2. הכנת התיקייה הזמנית (מחיקה ויצירה מחדש)
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
    os.makedirs(CACHE_DIR)
    hide_path(CACHE_DIR)

    # 3. שמירת הקבצים פיזית לדיסק
    # זה השלב הקריטי שמאפשר למודולים שלך לקרוא את הקבצים
    for file in files:
        file_path = os.path.join(CACHE_DIR, file.filename)
        file.save(file_path)

    # עכשיו יש לנו נתיב אמיתי בשרת שאפשר לעבוד איתו!
    folder_path = CACHE_DIR

    use_extended = request.form.get('extended_search') == 'on'
    user_api_key = request.form.get('gemini_key')
    if use_extended:
        if not user_api_key:
            return jsonify({"error": "בחרת בחיפוש מורחב אך לא הזנת מפתח API"}), 400

    try:
        # שלב 1: שליפת נתונים
        from extractor import extract_all
        images_data = extract_all(folder_path)

        # שלב 2: יצירת מפה
        from map_view import create_map
        map_html = create_map(images_data)

        # שלב 3: ציר זמן
        from timeline import create_timeline
        timeline_html = create_timeline(images_data)

        # שלב 4: ניתוח
        from analyzer import analyze_data
        analysis = analyze_data(images_data)

        if use_extended:
            from ai_analysis import analayze
            ai_analyze= analayze(images_data,user_api_key)
        else:
            ai_analyze=""
        # שלב 5: הרכבת דו"ח
        from report import create_report
        return create_report(images_data, map_html, timeline_html, analysis,ai_analyze)

    except Exception as e:
        return f"שגיאה בעיבוד הנתונים: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
