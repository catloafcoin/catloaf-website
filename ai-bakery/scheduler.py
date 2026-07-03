from database import supabase
import json
import os

DAILY_FILE = "daily_content.json"


def save_daily(data):
    with open(DAILY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_daily():
    if not os.path.exists(DAILY_FILE):
        return {}

    with open(DAILY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def add_to_queue(item):
    supabase.table("queue").upsert(item).execute()


def add_queue(item):
    add_to_queue(item)


def get_queue():
    return supabase.table("queue").select("*").execute().data


def remove_by_id(post_id):
    supabase.table("queue").delete().eq("id", post_id).execute()


def clear_queue():
    supabase.table("queue").delete().neq("id", "").execute()


def remove_first():
    queue = get_queue()

    if queue:
        remove_by_id(queue[0]["id"])


def add_pending(post_id):
    supabase.table("pending_posts").upsert({
        "id": post_id
    }).execute()


def mark_pending(post_id):
    add_pending(post_id)


def remove_pending(post_id):
    supabase.table("pending_posts").delete().eq(
        "id", post_id
    ).execute()


def mark_posted(post_id):
    supabase.table("posted_posts").upsert({
        "id": post_id
    }).execute()


def is_posted(post_id):
    result = (
        supabase.table("posted_posts")
        .select("id")
        .eq("id", post_id)
        .execute()
    )

    return len(result.data) > 0


def should_post_now():
    return True


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
