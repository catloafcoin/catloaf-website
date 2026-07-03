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
    supabase.table("pending_posts").upsert({
        "id": post_id
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
    supabase.table("posted_posts").upsert({
        "id": post_id
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

    score = 50

    telegram = item.get("telegram", {})

    text = (
        telegram.get("opening", "")
        + " "
        + " ".join(telegram.get("bullets", []))
        + " "
        + telegram.get("why", "")
        + " "
        + telegram.get("question", "")
    ).lower()

    keywords = [
        "solana",
        "jupiter",
        "phantom",
        "pump.fun",
        "raydium",
        "drift",
        "sanctum",
        "backpack",
        "meme",
        "airdrop",
        "defi",
        "token",
        "launch",
        "listing",
        "partnership",
        "volume",
        "record",
        "breaking"
    ]

    for word in keywords:
        if word in text:
            score += 5

    if item.get("meme"):
        score += 10

    if item.get("poll"):
        score += 10

    return min(score, 100)
