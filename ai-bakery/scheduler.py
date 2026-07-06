from database import supabase
import json
import os

DAILY_FILE = "daily_content.json"


# --------------------------------------------------
# Daily Content
# --------------------------------------------------

def save_daily(data):
    with open(DAILY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_daily():
    if not os.path.exists(DAILY_FILE):
        return {}

    try:
        with open(DAILY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(f"Failed to load daily content: {e}")
        return {}


# --------------------------------------------------
# Queue
# --------------------------------------------------

def add_to_queue(item):

    if "id" not in item:
        raise Exception("Queue item is missing an ID.")

    clean_item = dict(item)

    # Preserve all metadata
    clean_item.setdefault("image", None)
    clean_item.setdefault("source_title", "")
    clean_item.setdefault("source_url", "")
    clean_item.setdefault("persona", "")
    clean_item.setdefault("category", "")
    clean_item.setdefault("title", "")
    clean_item.setdefault("caption", "")
    clean_item.setdefault("quote", "")
    clean_item.setdefault("cta", "")
    from datetime import datetime, timezone

    clean_item.setdefault(
        "created_at",
        datetime.now(timezone.utc).isoformat()
    )

    supabase.table("queue").upsert(clean_item).execute()


def add_queue(item):
    add_to_queue(item)

def get_queue():
    result = (
        supabase.table("queue")
        .select("*")
        .execute()
    )

    return result.data

def remove_by_id(post_id):
    supabase.table("queue").delete().eq(
        "id", post_id
    ).execute()


def clear_queue():
    supabase.table("queue").delete().neq(
        "id", ""
    ).execute()


def remove_first():
    queue = get_queue()

    if queue:
        remove_by_id(queue[0]["id"])


# --------------------------------------------------
# Pending
# --------------------------------------------------

def add_pending(post_id):

    from datetime import datetime, timezone

    supabase.table("pending_posts").upsert({

        "id": post_id,

        "created_at": datetime.now(
            timezone.utc
        ).isoformat()

    }).execute()


def mark_pending(post_id):
    add_pending(post_id)


def load_pending():
    result = (
        supabase.table("pending_posts")
        .select("id")
        .execute()
    )

    return [row["id"] for row in result.data]


def remove_pending(post_id):
    supabase.table("pending_posts").delete().eq(
        "id", post_id
    ).execute()


# --------------------------------------------------
# Posted
# --------------------------------------------------

def mark_posted(post_id):

    from datetime import datetime, timezone

    supabase.table("posted_posts").upsert({

        "id": post_id,

        "created_at": datetime.now(
            timezone.utc
        ).isoformat()

    }).execute()

def load_posted():
    result = (
        supabase.table("posted_posts")
        .select("id")
        .execute()
    )

    return [row["id"] for row in result.data]


def is_posted(post_id):
    result = (
        supabase.table("posted_posts")
        .select("id")
        .eq("id", post_id)
        .execute()
    )

    return len(result.data) > 0


# --------------------------------------------------
# Scheduler
# --------------------------------------------------

def should_post_now():
    return True


# --------------------------------------------------
# Content Score
# --------------------------------------------------

def calculate_score(item):

    score = 0

    telegram = item.get("telegram", {})

    # --------------------------------------------------
    # Telegram Quality
    # --------------------------------------------------

    opening = telegram.get("opening", "")
    bullets = telegram.get("bullets", [])
    why = telegram.get("why", "")
    hot_take = telegram.get("question", "")

    if opening:
        score += 10

    if len(bullets) == 3:
        score += 15

    if why:
        score += 10

    if hot_take:
        score += 10

    # --------------------------------------------------
    # Images
    # --------------------------------------------------

    if item.get("art_image"):
        score += 10

    if telegram.get("header_image"):
        score += 10

    # --------------------------------------------------
    # Engagement
    # --------------------------------------------------

    if item.get("poll"):
        score += 10

    if item.get("meme"):
        score += 10

    x_posts = item.get("x_posts", [])

    if len(x_posts) >= 3:
        score += 15

    # --------------------------------------------------
    # News Relevance
    # --------------------------------------------------

    text = (
        opening
        + " "
        + " ".join(bullets)
        + " "
        + why
        + " "
        + hot_take
    ).lower()

    important = [
        "solana",
        "pump.fun",
        "raydium",
        "jupiter",
        "phantom",
        "backpack",
        "validator",
        "builder",
        "ecosystem",
        "defi",
        "launch",
        "listing"
    ]

    score += min(
        10,
        sum(
            1
            for word in important
            if word in text
        )
    )

    return min(score, 100)
