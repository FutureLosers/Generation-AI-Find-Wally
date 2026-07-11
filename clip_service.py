import torch
import torch.nn.functional as F
from transformers import CLIPModel, CLIPTokenizer


MODEL_NAME = "openai/clip-vit-base-patch32"

# GPUが利用できればGPU、なければCPU
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"CLIP device: {DEVICE}")
print("Loading CLIP model...")


# CLIPモデルはアプリ起動時に1回だけ読み込む
clip_model = CLIPModel.from_pretrained(
    MODEL_NAME
).to(DEVICE)

clip_tokenizer = CLIPTokenizer.from_pretrained(
    MODEL_NAME
)

clip_model.eval()

print("CLIP model loaded.")


def create_clip_prompt(word: str) -> str:
    """
    単語を、今回の隠し絵ゲームに近い文章へ変換する。
    """

    return (
        f"a small clearly recognizable {word} "
        "in a detailed hidden-object puzzle illustration"
    )


def get_text_features(texts: list[str]) -> torch.Tensor:
    """
    文章をCLIP特徴量へ変換する。
    """

    inputs = clip_tokenizer(
        texts,
        padding=True,
        truncation=True,
        return_tensors="pt"
    )

    inputs = {
        key: value.to(DEVICE)
        for key, value in inputs.items()
    }

    with torch.no_grad():
        text_outputs = clip_model.text_model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"]
        )

        pooled_output = text_outputs.pooler_output

        features = clip_model.text_projection(
            pooled_output
        )

    # ベクトルの長さを1にそろえる
    features = F.normalize(
        features,
        p=2,
        dim=-1
    )

    return features


def calculate_clip_similarity(
    filed: str,
    target: str
) -> float:
    """
    filedとtargetのCLIP類似度を計算する。
    """

    filed = filed.strip()
    target = target.strip()

    if not filed or not target:
        raise ValueError(
            "filedとtargetの両方を入力してください。"
        )

    filed_prompt = create_clip_prompt(filed)
    target_prompt = create_clip_prompt(target)

    features = get_text_features(
        [filed_prompt, target_prompt]
    )

    similarity = torch.sum(
        features[0] * features[1]
    ).item()

    return similarity