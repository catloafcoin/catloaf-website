import os
import time

from supabase import create_client


# --------------------------------------------------
# Environment
# --------------------------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)


print("=" * 60)
print("CONNECTING TO SUPABASE")
print("=" * 60)

print(
    "SUPABASE_URL               :",
    bool(SUPABASE_URL)
)

print(
    "SUPABASE_SERVICE_ROLE_KEY  :",
    bool(SUPABASE_KEY)
)


if not SUPABASE_URL:

    raise RuntimeError(
        "SUPABASE_URL environment variable is missing."
    )


if not SUPABASE_KEY:

    raise RuntimeError(
        "SUPABASE_SERVICE_ROLE_KEY environment variable is missing."
    )


try:

    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )

    # Simple connection test

    supabase.table("queue") \
        .select("id") \
        .limit(1) \
        .execute()

    print("✓ Connected to Supabase")

except Exception as e:

    print("=" * 60)
    print("SUPABASE CONNECTION FAILED")
    print(e)
    print("=" * 60)

    raise

# --------------------------------------------------
# Queue
# --------------------------------------------------

def add_queue(item):

    if not item:

        raise ValueError(
            "Cannot add an empty queue item."
        )

    try:

        print(
            f"Adding to queue: {item.get('id', 'unknown')}"
        )

        supabase.table("queue").upsert(item).execute()

        print("✓ Queue item saved")

    except Exception as e:

        print("=" * 60)
        print("QUEUE INSERT FAILED")
        print(e)
        print("=" * 60)

        raise


def get_queue():

    try:

        result = (
            supabase.table("queue")
            .select("*")
            .execute()
        )

        data = result.data or []

        print(f"Queue contains {len(data)} item(s).")

        return data

    except Exception as e:

        print("=" * 60)
        print("QUEUE LOAD FAILED")
        print(e)
        print("=" * 60)

        return []

# --------------------------------------------------
# Pending Posts
# --------------------------------------------------

def add_pending(post_id):

    try:

        supabase.table(
            "pending_posts"
        ).upsert({

            "id": post_id

        }).execute()

        print(
            f"✓ Pending added: {post_id}"
        )

    except Exception as e:

        print(
            f"Failed adding pending {post_id}:",
            e
        )


def remove_pending(post_id):

    try:

        supabase.table(
            "pending_posts"
        ).delete().eq(
            "id",
            post_id
        ).execute()

        print(
            f"✓ Pending removed: {post_id}"
        )

    except Exception as e:

        print(
            f"Failed removing pending {post_id}:",
            e
        )

# --------------------------------------------------
# Posted Posts
# --------------------------------------------------

def add_posted(post_id):

    try:

        supabase.table(
            "posted_posts"
        ).upsert({

            "id": post_id

        }).execute()

        print(
            f"✓ Posted: {post_id}"
        )

    except Exception as e:

        print(
            f"Failed adding posted {post_id}:",
            e
        )


def is_posted(post_id):

    try:

        result = (

            supabase.table(
                "posted_posts"
            )

            .select("id")

            .eq(
                "id",
                post_id
            )

            .limit(1)

            .execute()

        )

        return bool(result.data)

    except Exception as e:

        print(
            f"Failed checking posted {post_id}:",
            e
        )

        return False


# --------------------------------------------------
# Queue Removal
# --------------------------------------------------

def remove_queue(post_id):

    try:

        supabase.table(
            "queue"
        ).delete().eq(
            "id",
            post_id
        ).execute()

        print(
            f"✓ Queue removed: {post_id}"
        )

    except Exception as e:

        print(
            f"Failed removing queue item {post_id}:",
            e
        )