from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
import os
import re
from translate import Translator
import inflection as i

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

    print(f"Target is  {target}")
    print(f"in {filed} ")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-image-1",
        "prompt": f"""
        
This illustration has a high contrast style with many "+{filed}+" shots taken from a high perspective. There is only one small "+{target}+". Draw "+{target}+" small to make it less noticeable. Please choose a scenery where "+{target}+" is difficult to find among "+{filed}+".

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