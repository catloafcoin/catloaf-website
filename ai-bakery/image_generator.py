import os

from huggingface_hub import InferenceClient

HF_API_KEY = os.getenv("HUGGINGFACE")

client = InferenceClient(
    api_key=HF_API_KEY
)


def generate_image(prompt, filename="art.png"):

    print("Generating AI artwork...")

    image = client.text_to_image(
        prompt,
        model="black-forest-labs/FLUX.1-dev"
    )

    image.save(filename)

    print("✓ Image generated")

    return filename


if __name__ == "__main__":

    generate_image(
        "A majestic orange loaf cat sitting on a throne made of glowing Solana coins, ultra detailed digital art, cinematic lighting, masterpiece",
        "test_art.png"
    )
