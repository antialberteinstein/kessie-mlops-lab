"""Interactive generation from a trained checkpoint."""

import torch

from config import DATA, MODEL, TRAIN
from model import load_trained_model


def main():
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(TRAIN.output_dir, trust_remote_code=True)
    model = load_trained_model(tokenizer, TRAIN.output_dir, MODEL, DATA)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model = model.to(device=device, dtype=dtype)
    model.eval()

    while True:
        text = input("> ").strip()
        if not text:
            break
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        with torch.inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=True,
                temperature=0.8,
                top_p=0.95,
                pad_token_id=tokenizer.pad_token_id,
            )
        print(tokenizer.decode(output[0], skip_special_tokens=True))


if __name__ == "__main__":
    main()
