# ==========================================================
# CatLoaf AI Bakery V3
# image_generator.py
# AI Artwork Generator
# ==========================================================

import os
import time
import uuid
import random
import urllib.parse

import requests

from storage import upload_image


# --------------------------------------------------
# Character Identity (Never Changes)
# --------------------------------------------------

BASE_CHARACTER = """
CatLoaf mascot,
freshly baked orange loaf-shaped cat,
golden toasted bread body,
soft fluffy orange fur,
bright emerald green eyes,
rounded loaf silhouette,
small ears,
tiny paws,
small tail,
cute expressive face,
premium digital illustration,
consistent mascot design,
single character,
adorable,
clean composition,
high detail,
masterpiece,
no text,
no logo,
no watermark,
no speech bubbles,
no UI,
no extra characters
"""


# --------------------------------------------------
# Style Rotation
# --------------------------------------------------

ART_STYLES = [

    "editorial illustration",
    "storybook illustration",
    "premium poster illustration",
    "comic illustration",
    "animated movie concept art",
    "cinematic digital painting",
    "stylised concept art",
    "collectible sticker artwork",
    "high-end splash art",
    "digital painting"

]


CAMERA_ANGLES = [

    "close-up",
    "wide shot",
    "portrait composition",
    "three-quarter view",
    "top-down view",
    "low angle",
    "dynamic perspective",
    "isometric view"

]


LIGHTING = [

    "warm bakery lighting",
    "soft morning light",
    "golden sunrise",
    "dramatic rim lighting",
    "cinematic lighting",
    "volumetric lighting",
    "soft sunset glow",
    "cozy indoor lighting"

]


MOODS = [

    "wholesome",
    "heroic",
    "playful",
    "curious",
    "relaxed",
    "cozy",
    "cheerful",
    "adventurous"

]


COLOR_PALETTES = [

    "warm oranges and cream",
    "golden bakery colours",
    "soft pastel palette",
    "rich autumn colours",
    "bright vibrant colours",
    "warm cinematic colours"

]


# --------------------------------------------------
# Prompt Builder
# --------------------------------------------------

def build_prompt(prompt):

    if isinstance(prompt, dict):

        prompt = prompt.get("prompt", "")

    elif prompt is None:

        prompt = ""

    return ", ".join([

        BASE_CHARACTER,

        prompt,

        random.choice(ART_STYLES),

        random.choice(CAMERA_ANGLES),

        random.choice(LIGHTING),

        random.choice(MOODS),

        random.choice(COLOR_PALETTES),

        "ultra detailed",

        "professional illustration",

        "sharp focus",

        "8k quality",

        "beautiful composition"

    ])

# --------------------------------------------------
# Pollinations Image Generator
# --------------------------------------------------

def generate_image(prompt, filename=None):

    if filename is None:

        filename = f"{uuid.uuid4().hex}.png"

    final_prompt = build_prompt(prompt)

    encoded_prompt = urllib.parse.quote(final_prompt)

    seed = random.randint(1, 999999999)

    url = (
        "https://image.pollinations.ai/prompt/"
        f"{encoded_prompt}"
        "?width=1024"
        "&height=1024"
        "&model=flux"
        "&enhance=true"
        "&nologo=true"
        f"&seed={seed}"
    )

    print("=" * 60)
    print("GENERATING CATLOAF ARTWORK")
    print("=" * 60)
    print("Seed :", seed)
    print("Prompt:")
    print(final_prompt)
    print("=" * 60)

    for attempt in range(1, 4):

        try:

            response = requests.get(
                url,
                timeout=180
            )

            if response.status_code != 200:

                print(
                    f"Attempt {attempt} failed:",
                    response.status_code
                )

                time.sleep(10)

                continue

            if len(response.content) < 5000:

                print(
                    f"Attempt {attempt}: image too small."
                )

                time.sleep(10)

                continue

            with open(filename, "wb") as f:

                f.write(response.content)

            print("✓ Image generated")
            print(filename)

            print("=" * 60)
            print("UPLOADING TO SUPABASE")
            print("=" * 60)

            public_url = upload_image(filename)

            if public_url:

                print("✓ Upload successful")
                print(public_url)

                try:

                    os.remove(filename)

                    print("✓ Local image removed")

                except Exception:

                    pass

                return public_url

            print("⚠ Upload failed.")
            print("Using local image.")

            return filename

        except Exception as e:

            print(
                f"Attempt {attempt} exception:"
            )

            print(e)

            time.sleep(10)

    print("=" * 60)
    print("IMAGE GENERATION FAILED")
    print("=" * 60)

    return None

# --------------------------------------------------
# Batch Generator
# --------------------------------------------------

def generate_images(prompts):

    """
    Generates multiple images.

    Returns a list of image URLs.
    """

    results = []

    if not prompts:

        return results

    for prompt in prompts:

        image = generate_image(prompt)

        if image:

            results.append(image)

    return results


# --------------------------------------------------
# Image Validator
# --------------------------------------------------

def image_exists(image):

    if not image:

        return False

    # Public URL
    if (
        isinstance(image, str)
        and (
            image.startswith("http://")
            or image.startswith("https://")
        )
    ):

        return True

    # Local file
    return os.path.exists(image)


# --------------------------------------------------
# Standalone Test
# --------------------------------------------------

if __name__ == "__main__":

    test_prompt = {
        "prompt":
        (
            "CatLoaf inspecting fresh Solana alpha "
            "inside a futuristic bakery full of warm "
            "bread, glowing monitors and cozy lighting."
        )
    }

    image = generate_image(test_prompt)

    print("=" * 60)

    if image:

        print("SUCCESS")
        print(image)

    else:

        print("FAILED")

    print("=" * 60)