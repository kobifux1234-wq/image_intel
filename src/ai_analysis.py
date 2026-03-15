import base64, io, requests, os, json
from flask import jsonify
from PIL import Image, ImageOps

# Ensure the SCHEMA is defined or imported
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "trust_score": {"type": "integer"},
        "inconsistencies": {"type": "string"},
        "analysis": {"type": "string"}
    },
    "required": ["trust_score", "inconsistencies", "analysis"]
}


def process_and_encode_image(pil_img):
    try:
        img = ImageOps.exif_transpose(pil_img)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img = ImageOps.autocontrast(img)
        img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error processing: {e}")
        return None


def analayze(image_data, user_key):
    if len(user_key) < 30 or not user_key.startswith("AIza"):
        return jsonify({"error": "Invalid API key"}), 400

    MODEL = "gemini-2.5-flash"
    URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={user_key}"

    # Start parts with general prompt
    prompt_parts = [{
        "text": "Perform a professional photo forensics analysis. Compare visual content with EXIF. Return valid JSON."
    }]

    # Loop adds each image and its metadata into Parts
    for img_info in image_data:
        # Path must be exact to cache directory
        img_path = os.path.join("cache", img_info['filename'])
        try:
            if os.path.exists(img_path):
                with Image.open(img_path) as pil_img:
                    encoded = process_and_encode_image(pil_img)
                    if encoded:
                        # Add image metadata text
                        prompt_parts.append(
                            {"text": f"Image Filename: {img_info['filename']}. Metadata: {json.dumps(img_info)}"})
                        # Add the image itself
                        prompt_parts.append({
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": encoded
                            }
                        })
        except Exception as e:
            print(f"Could not process {img_info['filename']}: {e}")

    if len(prompt_parts) <= 1:
        return jsonify({"error": "Failed to process any images"}), 400

    # Build the payload with all collected parts
    payload = {
        "contents": [{"parts": prompt_parts}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseJsonSchema": RESPONSE_SCHEMA,
            "temperature": 0.1
        }
    }

    try:
        response = requests.post(URL, json=payload, timeout=60)

        if response.status_code != 200:
            # Print Google's exact error to the terminal
            print(f"Google API Error: {response.text}")
            return jsonify(
                {"error": f"API Error {response.status_code}", "details": response.json()}), response.status_code

        result = response.json()

        if 'candidates' in result and result['candidates']:
            # Extract the JSON that the AI generated
            ai_raw_response = result['candidates'][0]['content']['parts'][0]['text']
            print(ai_raw_response)
            return jsonify(json.loads(ai_raw_response))

        return jsonify({"error": "No candidates returned from AI"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
