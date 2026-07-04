import requests
import urllib.parse
import time
import uuid
import random

# --------------------------------------------------
# Permanent CatLoaf Identity
# --------------------------------------------------

BASE_CHARACTER = """
CatLoaf mascot, orange loaf-shaped cat,
golden toasted bread body,
soft fluffy orange fur,
bright emerald green eyes,
rounded loaf silhouette,
tiny paws,
small tail,
cute expressive face,
premium digital illustration,
consistent mascot design,
no text,
no logo,
no watermark,
no speech bubbles,
single character,
high quality
"""

# --------------------------------------------------
# Automatic Variety
# --------------------------------------------------

STYLES = [
    "editorial illustration",
    "comic illustration",
    "storybook illustration",
    "sticker artwork",
    "cinematic digital painting",
    "animated movie concept art",
    "premium poster illustration",
    "whimsical artwork"
]

CAMERAS = [
    "close-up",
    "wide shot",
    "low angle",
    "top-down view",
    "isometric",
    "dynamic perspective",
    "three-quarter view",
    "portrait composition"
]

LIGHTING = [
    "warm bakery lighting",
    "golden sunrise",
    "soft cinematic lighting",
    "dramatic rim lighting",
    "cozy indoor lighting",
    "sunset glow",
    "soft morning light",
    "volumetric lighting"
]

MOODS = [
    "wholesome",
    "playful",
    "heroic",
    "relaxed",
    "cheerful",
    "cozy",
    "adventurous",
    "funny"
]


def build_prompt(prompt):

    if isinstance(prompt, dict):
        prompt = prompt.get("prompt", "")

    return (
        f"{BASE_CHARACTER}, "
        f"{prompt}, "
        f"{random.choice(STYLES)}, "
        f"{random.choice(CAMERAS)}, "
        f"{random.choice(LIGHTING)}, "
        f"{random.choice(MOODS)}, "
        "high detail, ultra quality, vibrant colours"
    )


def generate_image(prompt, filename=None):

    if filename is None:
        filename = f"{uuid.uuid4().hex}.png"

    print("=" * 60)
    print("Generating AI artwork...")
    print("=" * 60)

    prompt = build_prompt(prompt)

    encoded = urllib.parse.quote(prompt)

    seed = random.randint(1, 999999999)

    url = (
        "https://image.pollinations.ai/prompt/"
        f"{encoded}"
        f"?width=768"
        f"&height=768"
        f"&model=flux"
        f"&enhance=true"
        f"&seed={seed}"
    )

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
                print(filename)

                return filename

            print(
                f"Attempt {attempt + 1} failed:",
                response.status_code
            )

        except Exception as e:

            print(
                f"Attempt {attempt + 1} failed:",
                e
            )

        time.sleep(15)

    print("⚠ Pollinations unavailable.")

    return None


if __name__ == "__main__":

    generate_image(
        "CatLoaf inspecting fresh Solana alpha inside a futuristic bakery"
    )