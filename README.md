# Generation-AI-Find-Wally (ver2pre)

AIを利用して「ウォーリーをさがせ」のような隠し絵ゲームを自動生成する実験プロジェクトです。

本バージョンは **ver2pre** であり、画像生成方法や難易度調整を検証するための試作版です。

---

## 動作環境

- Python 3.11
- Flask
- OpenAI API
- python-dotenv
- requests
- translate
- inflection

APIキーは `.env` に設定してください。

```env
API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 実行方法

それぞれ独立した実験プログラムになっています。

### app1.py

初期版

- GPT Imageによる画像生成
- `gpt-4.1-mini` による答えの座標取得

```bash
python app1.py
```

---

### app2.py

プロンプト改善版

- 白黒のイラストを生成
- 探す対象を明確にするためのプロンプト調整

```bash
python app2.py
```

---

### app3.py

最新版（ver2pre）

- ウォーリー風の隠し絵生成
- Visionによる位置推定
- 難易度向上の実験

```bash
python app3.py
```

---

### Cat and Dog Extra.py

「犬の中から猫を探す」という、類似した対象を使った追加実験です。

- 事前に作成した画像を元に画像編集を実行
- 現在は「犬」と「猫」の組み合わせに対応
- `sample.png` を元画像として使用

```bash
python "Cat and Dog Extra.py"
```

---

## 現状の課題

現在確認している問題：

- 犬の中に猫を生成する場合、犬の特徴が優先され、猫が明確に生成されないことがある
- 横縞・縦縞など、属性のみが異なる対象の生成は不安定
- Visionによる座標取得には誤差が発生することがある

---

## 今後の予定（ver3）

- CLIPによる対象同士の類似度測定
- 類似度と画像生成結果の関係を検証
- CLIP類似度による生成ルート分岐の検討
- 画像編集APIを利用した生成方法との比較
- 難易度の自動調整

---

## ライセンス

MIT License