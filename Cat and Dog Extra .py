from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
import os
import re
import base64
from io import BytesIO
app = Flask(__name__)

load_dotenv()

API_KEY = os.environ.get("API_KEY")


@app.route("/")
def hello_world():
    return render_template(
        "contence.html",
        title="Where’s Waldo?"
    )


@app.route("/generate-image", methods=["POST"])
def generate_image():

    data = request.json

    target = data.get("target")
    filed = data.get("filed")

    print(f"Target is {target}")
    print(f"in {filed}")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content - Type": "application / json"
    }

    files = {
        "image": ("sample.png", open("sample.png", "rb"), "image/png")
    }

    data = {
        "model": "gpt-image-1",
        "prompt": f"""
    Create hundreds of {filed} while preserving the overall composition of this image.

    Keep the same art style.

    Do not add any {target}.
    """,
        "size": "1024x1024",
        "quality": "medium"
    }

    base_response = requests.post(
        "https://api.openai.com/v1/images/edits",
        headers=headers,
        files=files,
        data=data
    )

    base_data = base_response.json()
    print(base_data)

    if base_response.status_code != 200:
        return jsonify(base_data), base_response.status_code

    base64_image = base_data["data"][0]["b64_json"]
    image_bytes = base64.b64decode(base64_image)

    edit_files = {
        "image": ("base.png", BytesIO(image_bytes), "image/png")
    }

    edit_data_payload = {
        "model": "gpt-image-1",
        "prompt": f"""
    Edit this image. Keep almost everything unchanged.

    Choose exactly one clearly visible small dog near the center of the image and replace only that dog with one small cat.

    The cat must be recognizable as a cat, with pointed ears, cat face, whiskers, and a long curved tail.

    Do not create another dog in that spot.

    Do not change the rest of the image.

    Do not add circles, arrows, labels, text, or markers.
    """,
        "size": "1024x1024",
        "quality": "medium",
        "n": "1"
    }

    edit_response = requests.post(
        "https://api.openai.com/v1/images/edits",
        headers={"Authorization": f"Bearer {API_KEY}"},
        files=edit_files,
        data=edit_data_payload
    )


    edit_data = edit_response.json()
    print(edit_data)

    if edit_response.status_code != 200:
        return jsonify(edit_data), edit_response.status_code

    final_base64 = edit_data["data"][0]["b64_json"]

    image_url = f"data:image/png;base64,{final_base64}"

    return jsonify({
        "image_url": image_url
    })

@app.route("/answer", methods=["POST"])
def answer():

    data = request.json

    target = data.get("target")
    filed = data.get("filed")
    image_url = data.get("image_url")

    plot = f"""
Find the single {target} among many {filed}s.

Return ONLY the bounding box.

Format:
x1,y1,x2,y2

Do not explain.
Do not output any other text.
"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": plot
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        "max_tokens": 100
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload
    )

    response_data = response.json()

    print(response_data)

    try:
        answer_text = (
            response_data["choices"][0]
            ["message"]["content"]
        )

        print(answer_text)

        point = re.findall(
            r"\d+",
            answer_text
        )

        if not point:
            return jsonify({
                "answer": answer_text
            })

        answerpoint = [
            int(num)
            for num in point
        ]

        print(answerpoint)

        return jsonify(
            answerpoint
        )

    except Exception as e:

        print(response_data)

        return jsonify({
            "error": str(e),
            "response": response_data
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )