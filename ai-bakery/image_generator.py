import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_image(prompt, output_file="catloaf.png"):
    response = client.models.generate_images(
        model="gemini-2.5-flash-image-preview",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1
        )
    )

    image = response.generated_images[0].image
    image.save(output_file)

    return output_file
