import requests
import urllib.parse
import time


def generate_image(prompt, filename="art.png"):

    print("Generating AI artwork...")

if isinstance(prompt, dict):
    prompt = prompt.get("prompt", "")

if not prompt:
    raise Exception("Image prompt is empty.")

prompt = urllib.parse.quote(prompt)

    url = f"https://image.pollinations.ai/prompt/{prompt}?width=768&height=768&model=flux&enhance=true"

    for attempt in range(3):

        try:

            response = requests.get(
                url,
                timeout=180
            )

            if response.status_code == 200:

                with open(filename, "wb") as f:
                    f.write(response.content)

                print("✓ Image generated")

                return filename

            print(f"Attempt {attempt+1} failed: {response.status_code}")

        except Exception as e:
            print(e)

        time.sleep(15)

    print("⚠ Pollinations unavailable. Skipping image.")

    return None


if __name__ == "__main__":

    generate_image(
        "A majestic orange loaf cat sitting on a throne made of glowing Solana coins, cinematic digital art",
        "test_art.png"
    )
