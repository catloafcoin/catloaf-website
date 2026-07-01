import os
import requests

HF_API_KEY = os.getenv("HUGGINGFACE")

MODEL = (
    "https://router.huggingface.co/hf-inference/models/"
MODEL = (
    "https://router.huggingface.co/hf-inference/models/"
    "black-forest-labs/FLUX.1-dev"
)

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}"
}

def generate_image(prompt, filename="art.png"):

    print("Generating AI artwork...")

    response = requests.post(
        MODEL,
        headers=HEADERS,
        json={
            "inputs": prompt
        },
        timeout=300
    )

    if response.status_code != 200:
        raise Exception(response.text)

    with open(filename, "wb") as f:
        f.write(response.content)

    print("✓ Image generated")

    return filename


if __name__ == "__main__":

    generate_image(
        "A majestic orange loaf cat sitting on a throne made of glowing Solana coins, ultra detailed digital art, cinematic lighting, fantasy, masterpiece",
        "test_art.png"
    )
