from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
import os
import re
from clip_service import calculate_clip_similarity

app = Flask(__name__)

load_dotenv()

API_KEY = os.environ.get("API_KEY")


@app.route("/")
def hello_world():
    return render_template(
        "contence.html",
        title="Where’s Waldo?"
    )

@app.route("/clip-score", methods=["POST"])
def clip_score():

    data = request.get_json(silent=True) or {}

    target = data.get("target", "").strip()
    filed = data.get("filed", "").strip()

    if not target or not filed:
        return jsonify({
            "error": "targetとfiledの両方を入力してください。"
        }), 400

    try:
        score = calculate_clip_similarity(
            filed=filed,
            target=target
        )

        return jsonify({
            "score": round(score, 3)
        })

    except Exception as error:
        print(f"CLIP error: {error}")

        return jsonify({
            "error": str(error)
        }), 500


@app.route("/generate-image", methods=["POST"])
def generate_image():

    data = request.json

    target = data.get("target")
    filed = data.get("filed")

    print(f"Target is  {target}")
    print(f"in {filed} ")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-image-1",
        "prompt": f"""
        
Create a highly detailed hidden-object puzzle illustration.

Create approximately 300 {filed}.

Each {filed} should occupy roughly 2–6% of the image width.

Vary their size, pose, rotation, and orientation.

About 30% should face sideways.
About 20% should face away from the viewer.
About 20% should be sitting or resting.
About 10% should be partially hidden by other {filed}.

Add exactly one {target}.

The {target} should be the same size as the surrounding {filed}, naturally blended into the crowd, partially hidden, and difficult to distinguish.

Avoid empty areas and fill the entire image with objects.

The result should resemble a classic hidden-object puzzle.

    """,
        "size": "1024x1024",
        "quality": "medium",
        "n": 1
    }

    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        json=payload,
        headers=headers
    )

    response_data = response.json()

    print(response_data)

    if response.status_code == 200:

        image_base64 = response_data["data"][0]["b64_json"]

        image_url = (
            f"data:image/png;base64,{image_base64}"
        )

        return jsonify({
            "image_url": image_url
        })

    return jsonify(
        response_data
    ), response.status_code


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