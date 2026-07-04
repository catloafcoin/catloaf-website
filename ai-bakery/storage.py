import os
import uuid
import mimetypes

from database import supabase

BUCKET_NAME = "images"


def upload_image(image_path):

    if not image_path:
        return None

    if image_path.startswith("http://") or image_path.startswith("https://"):
        return image_path

    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return None

    filename = (
        f"{uuid.uuid4().hex}"
        f"{os.path.splitext(image_path)[1]}"
    )

    content_type = (
        mimetypes.guess_type(image_path)[0]
        or "image/png"
    )

    try:

        with open(image_path, "rb") as f:

            supabase.storage.from_(BUCKET_NAME).upload(
                path=filename,
                file=f,
                file_options={
                    "content-type": content_type,
                    "upsert": "true"
                }
            )

        public_url = (
            supabase.storage
            .from_(BUCKET_NAME)
            .get_public_url(filename)
        )

        if isinstance(public_url, dict):
            return public_url.get("publicUrl")

        return public_url

    except Exception as e:

        print("=" * 60)
        print("SUPABASE IMAGE UPLOAD FAILED")
        print(e)
        print("=" * 60)

        return None