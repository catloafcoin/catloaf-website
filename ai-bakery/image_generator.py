import requests
import urllib.parse


def generate_image(prompt, filename="art.png"):

    print("Generating AI artwork...")

    prompt = urllib.parse.quote(prompt)

    url = f"https://image.pollinations.ai/prompt/{prompt}"

    response = requests.get(
        url,
        timeout=180
    )

    if response.status_code != 200:
        raise Exception(response.text)

    with open(filename, "wb") as f:
        f.write(response.content)

    print("✓ Image generated")

    return filename


if __name__ == "__main__":

    generate_image(
        "A majestic orange loaf cat sitting on a throne made of glowing Solana coins, cinematic digital art",
        "test_art.png"
    )
