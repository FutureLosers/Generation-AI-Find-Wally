from flask import Flask,render_template, request, jsonify
import requests
from dotenv import load_dotenv
import os
import re
from translate import Translator
import inflection as i

app = Flask(__name__)

load_dotenv()  # .envファイルから環境変数を読み込む

API_KEY = os.environ.get("API_KEY")

@app.route("/")
def hello_world():

    return render_template('contence.html', title='ウォーリーを探せ')

@app.route('/generate-image', methods=['POST'])
def generate_image():
    # リクエストからプロンプトを取得
    data = request.json
    before_target = data.get('target')
    before_filed=data.get('filed')
    translator = Translator(from_lang="ja", to_lang="en")
    target = translator.translate(before_target)
    filed= translator.translate(i.pluralize(before_filed))

    print(f"探すものは{target}")
    print(f"{filed}に隠します")


    # OpenAIのAPIリクエストの設定
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': "dall-e-3",
        'prompt': "This illustration has a high contrast style with many "+filed+" shots taken from a high perspective. There is only one small "+target+". Draw "+target+" small to make it less noticeable. Please choose a scenery where "+target+" is difficult to find among "+filed+".",
        'size': "1024x1024",
        'quality': "standard",
        'n': 1
    }

    # APIリクエストの送信
    response = requests.post('https://api.openai.com/v1/images/generations', json=payload, headers=headers)
    response_data = response.json()
    print(response_data)

    if response.status_code == 200:
        # 成功した場合、画像のURLを返す
        response_data = response.json()
        image_url = response_data['data'][0]['url']
        return jsonify({'image_url': image_url})
    else:
        # 失敗した場合、APIのエラーレスポンスをそのまま返す
        return jsonify(response.json()), response.status_code

@app.route('/answer', methods=['POST'])


def answer():
    # リクエストからプロンプトを取得

    data = request.json
    target = data.get('target')
    filed=data.get('filed')
    image_url=data.get('image_url')
    plot = r"There are many {}s here. This is one {}. Where is it located? Please respond in the format '(\d+,\d+)~(\d+,\d+)'. If multiple answers are visible, choose the one that seems most like a {}.".format(
        filed, target,target)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Bearer {API_KEY}',
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": plot},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        }
                    }
                ]
            }
        ],
        "max_tokens": 100
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    response_data = response.json()

    print(response_data)
    answer = response_data['choices'][0]['message']['content']
    print(answer)
    point = re.findall(r"\d+", answer)
    print(point)
    if not point:
        return answer  # 数値が見つからない場合は回答文を返す
    else:
        answerpoint = [int(num) for num in point]
        print(answerpoint)
        return answerpoint  # 数値が見つかった場合は座標を返す

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)