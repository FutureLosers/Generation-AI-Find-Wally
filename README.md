# Generation-AI-Find-Wally ver2

AIを利用して、「ウォーリーをさがせ」のような隠し絵クイズを自動生成する実験プロジェクトです。

ユーザーが次の2つを入力すると、AIが隠し絵を生成します。

* `target`：探す対象
* `filed`：大量に配置する対象

例：

```text
target: cat
filed: dog
```

この場合、「大量の犬の中から猫を探す」問題を生成します。

> `filed` は本来 `field` が自然な表記ですが、既存コードとの互換性のため、現在は `filed` を使用しています。

---

## ver2について

ver2では、ver2preで実験していた複数の生成方法を整理し、正式に使用するプログラムを `app.py` に統合しました。

ver2preでは、次の実験用プログラムを使用していました。

* `app1.py`
* `app2.py`
* `app3.py`
* `Cat and Dog Extra .py`

ver2では、ver2preの `app3.py` を正式版として採用し、ファイル名を次のように変更しています。

```text
app3.py
↓
app.py
```

以下の実験用ファイルは、ver2には引き継いでいません。

```text
app1.py
app2.py
Cat and Dog Extra .py
```

過去の実験内容については、GitHubのコミット履歴または `ver2pre` のタグから確認できます。

---

## ver2preについて

ver2preは、画像生成方法やプロンプトの違いを比較するための実験段階のバージョンです。

ver2preでは、主に次の内容を検証しました。

* 一般的な画像生成プロンプト
* 白黒イラストによる対象の明確化
* ウォーリー風の高密度な隠し絵生成
* 既存画像を利用した画像編集
* 犬の中から猫を探す問題
* 横縞と縦縞など、属性の違いによる問題
* Visionによる答えの座標取得

これらの実験結果を踏まえ、ver2では `app3.py` の処理を基礎として `app.py` に統合しました。

---

## ver2の主な変更点

* `app3.py` を `app.py` に変更
* 実験用プログラムを整理
* ウォーリー風の高密度な画像生成を正式採用
* CLIPによる対象同士の類似度計算を追加
* CLIP類似度を画面上に表示
* GPT Imageによる画像生成
* `gpt-4.1-mini` による対象位置の推定
* クリック位置による正解判定

---

## CLIPとは

CLIPは、画像と文章を数値ベクトルへ変換し、それぞれがどの程度似ているかを計算するモデルです。

本プロジェクトでは、入力された `filed` と `target` の文章特徴量を比較し、コサイン類似度を計算します。

例：

```text
filed: dog
target: cat
```

この2つをCLIPで計算すると、次のような類似度が表示されます。

```text
CLIP similarity: 0.912
```

数値が1に近いほど、CLIP上では似た対象として判断されています。

ただし、CLIP類似度は、画像生成が成功するかどうかを完全に判定するものではありません。

画像生成AIの傾向を予測するための参考値として使用しています。

---

## CLIP類似度の目安

現在の実験では、次のような傾向が確認されています。

### 0.85以下

問題としては比較的単純になりますが、探す対象は明確に生成されやすく、ほぼ確実にクイズとして成立します。

例：

```text
rabbit → dragon
```

対象同士の特徴が大きく異なるため、見つけやすい問題になりやすいです。

---

### 0.85以上、0.90未満

生成結果によっては、探す対象の表現が少し曖昧になる場合があります。

一方で、対象同士が適度に似ているため、隠し絵として程よい難易度になることもあります。

例：

```text
watch → compass
snake → lizard
```

現在のところ、最もゲームとして面白い問題が生成されやすい範囲です。

---

### 0.90以上

対象同士の類似度が非常に高く、現状の画像生成AIでは、探す対象を明確に描き分けることが難しい場合があります。

例：

```text
dog → cat
horizontal stripes → vertical stripes
```

対象が周囲の特徴に引っ張られ、別の対象として明確に生成されないことがあります。

0.90以上の場合は、単語だけで指定するのではなく、探す対象の特徴を補足することを推奨します。

例：

```text
cat
```

ではなく、

```text
a small cat with pointed ears, whiskers and a long curved tail
```

のように、副次的な特徴を追加します。

これにより、CLIP類似度が変化し、画像生成AIが対象を描き分けやすくなる場合があります。

---

## 使用例

### 比較的簡単な問題

```text
target: dragon
filed: rabbit
```

### 適度な難易度の問題

```text
target: compass
filed: watch
```

### 生成が難しい問題

```text
target: cat
filed: dog
```

犬と猫はCLIP上で高い類似度になるため、猫が犬に近い姿で生成される場合があります。

この場合は、次のように対象を詳しく指定します。

```text
target:
a small cat with pointed ears, whiskers and a long curved tail
```

---

## 動作環境

* Python 3.11
* Flask
* OpenAI API
* PyTorch
* torchvision
* Pillow
* transformers
* python-dotenv
* requests
* translate
* inflection

---

## インストール

仮想環境を作成します。

```bash
python -m venv .venv
```

Windowsの場合：

```powershell
.venv\Scripts\activate
```

必要なライブラリをインストールします。

```bash
python -m pip install flask requests python-dotenv translate inflection
python -m pip install torch torchvision pillow transformers
```

---

## APIキーの設定

プロジェクト直下に `.env` を作成し、OpenAI APIキーを設定します。

```env
API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
```

`.env` はGitHubへ公開しないでください。

`.gitignore` には次の内容を設定します。

```gitignore
.env
.venv/
.idea/
__pycache__/
```

---

## 実行方法

次のコマンドを実行します。

```bash
python app.py
```

起動後、ブラウザで次のURLを開きます。

```text
http://127.0.0.1:5000
```

初回起動時は、Hugging FaceからCLIPモデルをダウンロードするため、少し時間がかかる場合があります。

---

## 処理の流れ

```text
targetとfiledを入力
        ↓
CLIP類似度を計算
        ↓
類似度を画面に表示
        ↓
GPT Imageで隠し絵を生成
        ↓
gpt-4.1-miniで対象位置を推定
        ↓
ユーザーが画像をクリック
        ↓
座標範囲内なら正解表示
```

---

## 現状の課題

* 犬の中から猫を探す問題では、猫が明確に生成されない場合がある
* 横縞と縦縞など、属性だけが異なる対象は生成が不安定
* 画像生成AIが指定した個数を正確に描くとは限らない
* CLIP類似度だけでは生成結果を完全には予測できない
* Visionによる座標取得には誤差が発生する場合がある
* 生成対象と推定座標が少しずれる場合がある

---

## 今後の予定

* CLIP類似度に応じた生成ルートの分岐
* 0.90以上の組み合わせに対する補足説明の自動生成
* 対象の視覚的特徴を追加するプロンプト改善
* 生成結果とCLIP類似度の関係を記録
* 問題生成の成功率を蓄積
* 難易度の自動判定
* ComfyUIやLoRAとの連携
* Visionによる座標推定精度の改善

---

## ライセンス

MIT License
