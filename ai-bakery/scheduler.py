from database import supabase


def get_queue():
    return supabase.table("queue").select("*").execute().data


def add_queue(item):
    supabase.table("queue").upsert(item).execute()


def remove_by_id(post_id):
    supabase.table("queue").delete().eq("id", post_id).execute()


def add_pending(post_id):
    supabase.table("pending_posts").upsert({
        "id": post_id
    }).execute()


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
