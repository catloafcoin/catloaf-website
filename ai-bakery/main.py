# ==========================================================
# CatLoaf AI Bakery V3
# main.py
# Daily Content Engine
# ==========================================================

import os
import json
import uuid

import google.generativeai as genai

from scheduler import (
    add_to_queue,
    save_daily,
    calculate_score
)

from image_generator import generate_image

from rss_reader import (
    get_ranked_articles
)

from poster import process_queue

from modules import (
    load_text,
    load_json,
    validate_json
)

print("=" * 60)
print("🍞 Starting CatLoaf AI Bakery V3")
print("=" * 60)

# ==========================================================
# Configuration
# ==========================================================

config = load_json("config.json")

RUN_ID = uuid.uuid4().hex[:8]

API_KEYS = [

    os.getenv("GEMINI_API_KEY"),

    os.getenv("GEMINI_API_KEY_2"),

    os.getenv("GEMINI_API_KEY_3"),

    os.getenv("GEMINI_API_KEY_4")

]

if not API_KEYS[0]:

    raise RuntimeError(
        "GEMINI_API_KEY is missing."
    )

print("✓ Configuration Loaded")

# ==========================================================
# Prompt Files
# ==========================================================

brand = load_text("brand.txt")

prompt_template = load_text("prompt.txt")

history = load_text("history.txt")

print("✓ Prompt Files Loaded")

# ==========================================================
# RSS
# ==========================================================

print("=" * 60)
print("LOADING RSS ARTICLES")
print("=" * 60)

articles = get_ranked_articles()

if not articles:

    raise RuntimeError(
        "No usable RSS articles were found."
    )

articles = articles[:12]

print("=" * 60)
print("TOP ARTICLES")
print("=" * 60)

for article in articles[:5]:

    print(

        f"[{article.get('score',0):>3}]",

        article.get("title","")

    )

print("=" * 60)

# ==========================================================
# News Mode
# ==========================================================

highest_score = max(

    article.get("score", 0)

    for article in articles

)

if highest_score >= 35:

    news_mode = "breaking"

elif highest_score >= 20:

    news_mode = "trending"

else:

    news_mode = "fallback"

print("News Mode :", news_mode)
print("Top Score :", highest_score)

# ==========================================================
# Build Gemini Context
# ==========================================================

news_sections = []

for article in articles:

    news_sections.append(

f"""
TITLE:
{article.get("title","")}

SUMMARY:
{article.get("summary","")}

SOURCE:
{article.get("source","")}

URL:
{article.get("link","")}
"""

    )

news_text = "\n".join(news_sections)

prompt = f"""
{brand}

{prompt_template}
"""

prompt = (

    prompt

    .replace("{news}", news_text)

    .replace("{history}", history)

    .replace("{news_mode}", news_mode)

)

print("✓ Prompt Built")

# ==========================================================
# Gemini Generation
# ==========================================================

generation_config = {

    "temperature": 1,

    "top_p": 0.95,

    "top_k": 40,

    "max_output_tokens": 8192,

    "response_mime_type": "application/json"

}

response = None

last_error = None

for api_key in API_KEYS:

    if not api_key:

        continue

    try:

        genai.configure(

            api_key=api_key

        )

        model = genai.GenerativeModel(

            "gemini-2.5-flash"

        )

        response = model.generate_content(

            prompt,

            generation_config=generation_config

        )

        print("✓ Gemini Success")

        break

    except Exception as e:

        last_error = e

        print(e)

if response is None:

    raise last_error

data = validate_json(

    response.text

)

required = [

    "telegram",

    "art_image",

    "meme",

    "poll",

    "x_posts",

    "best_time"

]

for field in required:

    if field not in data:

        raise RuntimeError(

            f"Gemini missing: {field}"

        )

print("✓ JSON Validated")

content_score = calculate_score(data)

print(

    f"Content Score : {content_score}"

)

if content_score >= 80:

    save_daily(data)

    print("✓ Daily Saved")

else:

    print("Skipped Daily Save")


# ==========================================================
# Smart Article Selection
# ==========================================================

def article_has_image(article):

    return bool(article.get("image"))


def choose_hot_loaf_article(articles):

    """
    Picks the strongest overall article.

    Preference order:

    1. Highest score WITH image
    2. Highest score overall
    """

    print("=" * 60)
    print("SELECTING HOT LOAF ARTICLE")
    print("=" * 60)

    if not articles:

        raise RuntimeError("No articles available.")

    image_articles = [

        article

        for article in articles

        if article_has_image(article)

    ]

    if image_articles:

        selected = max(

            image_articles,

            key=lambda article: article.get("score", 0)

        )

        print("✓ RSS image available")

    else:

        selected = max(

            articles,

            key=lambda article: article.get("score", 0)

        )

        print("✓ AI header will be generated")

    return selected


def choose_secondary_article(articles, primary):

    """
    Picks the next-best article while avoiding duplicates.
    """

    candidates = []

    primary_link = primary.get("link", "")

    primary_title = primary.get("title", "").lower()

    for article in articles:

        if article.get("link") == primary_link:

            continue

        if article.get("title", "").lower() == primary_title:

            continue

        candidates.append(article)

    if not candidates:

        return primary

    return max(

        candidates,

        key=lambda article: article.get("score", 0)

    )


# ==========================================================
# Select Articles
# ==========================================================

hot_article = choose_hot_loaf_article(articles)

secondary_article = choose_secondary_article(

    articles,

    hot_article

)

print("=" * 60)
print("PRIMARY ARTICLE")
print("=" * 60)
print("Score :", hot_article.get("score", 0))
print("Title :", hot_article.get("title", ""))
print("Source:", hot_article.get("source", ""))
print("Image :", "YES" if hot_article.get("image") else "NO")
print("=" * 60)

print("=" * 60)
print("SECONDARY ARTICLE")
print("=" * 60)
print("Score :", secondary_article.get("score", 0))
print("Title :", secondary_article.get("title", ""))
print("Source:", secondary_article.get("source", ""))
print("Image :", "YES" if secondary_article.get("image") else "NO")
print("=" * 60)

# ==========================================================
# Primary Source
# ==========================================================

source_title = hot_article.get(

    "title",

    ""

)

source_url = hot_article.get(

    "link",

    ""

)

rss_image = hot_article.get(

    "image",

    ""

)

# ==========================================================
# Secondary Source
# ==========================================================

secondary_title = secondary_article.get(

    "title",

    ""

)

secondary_url = secondary_article.get(

    "link",

    ""

)

secondary_image = secondary_article.get(

    "image",

    ""

)

print("=" * 60)
print("ARTICLE SELECTION COMPLETE")
print("=" * 60)

# ==========================================================
# Telegram Message Builder
# ==========================================================

def divider():

    return "━━━━━━━━━━━━━━━━━━━━━━"


tg = data["telegram"]

persona = tg.get(

    "persona",

    "CatLoaf"

)

category = tg.get(

    "category",

    "Community"

)

headline = tg.get(

    "headline",

    "TODAY'S HOT LOAF"

)

loaf_score = tg.get(

    "loaf_score",

    {}

)

overall = loaf_score.get(

    "overall",

    "-"

)

market = loaf_score.get(

    "market_impact",

    "Medium"

)

builder = loaf_score.get(

    "builder_interest",

    "Medium"

)

urgency = loaf_score.get(

    "urgency",

    "Medium"

)

# --------------------------------------------------
# Build Telegram Message
# --------------------------------------------------

telegram_lines = [

    f"🔥 <b>{headline}</b>",

    "",

    divider(),

    "",

    "🍞 <i>Fresh from today's oven...</i>",

    "",

    tg.get("opening", ""),

    "",

    "🔥 <b>Fresh Alpha</b>",

]

# --------------------------------------------------
# Alpha Bullets
# --------------------------------------------------

for bullet in tg.get("bullets", []):

    telegram_lines.append(f"• {bullet}")

telegram_lines.extend([

    "",

    "🧈 <b>Why It Matters</b>",

    "",

    tg.get("why", ""),

    "",

    "📊 <b>Loaf Score</b>",

    ""

])

# --------------------------------------------------
# Loaf Score
# --------------------------------------------------

if str(overall).isdigit():

    telegram_lines.append(

        f"🍞 Overall: <b>{overall}/100</b>"

    )

else:

    telegram_lines.append(

        f"🍞 Overall: <b>{overall}</b>"

    )

telegram_lines.extend([

    f"📈 Market Impact: {market}",

    f"🏗 Builder Interest: {builder}",

    f"⚡ Urgency: {urgency}",

    "",

    "🥖 <b>Hot Take</b>",

    "",

    tg.get("question", ""),

    "",

    divider(),

    "",

    "📰 <b>Source</b>",

    source_title,

    source_url,

    "",

    "🐱 @CatLoafCoin"

])

telegram_message = "\n".join(

    telegram_lines

)

print("=" * 60)
print("TELEGRAM MESSAGE READY")
print("=" * 60)
print(
    telegram_message[:400]
)
print("...")
print("=" * 60)

# ==========================================================
# Image Generation
# ==========================================================

meme = data["meme"]

art = data["art_image"]

header = tg.get("header_image", {})

print("=" * 60)
print("IMAGE SELECTION")
print("=" * 60)

# ----------------------------------------------------------
# Hot Loaf Image
# ----------------------------------------------------------

if rss_image:

    print("✓ Using RSS article image.")

    hot_loaf_image = rss_image

else:

    print("✓ Generating AI Hot Loaf artwork...")

    hot_loaf_image = generate_image(header)

# ----------------------------------------------------------
# Art Post
# ----------------------------------------------------------

print("Generating daily CatLoaf artwork...")

art_image = generate_image(art)

# ----------------------------------------------------------
# X Images
# ----------------------------------------------------------

x_news_image = secondary_image or hot_loaf_image

x_funny_image = art_image if art_image else hot_loaf_image

x_education_image = hot_loaf_image

print("=" * 60)
print("IMAGE SUMMARY")
print("=" * 60)
print("Hot Loaf :", hot_loaf_image)
print("Art      :", art_image)
print("X News   :", x_news_image)
print("X Funny  :", x_funny_image)
print("X Learn  :", x_education_image)
print("=" * 60)

# ==========================================================
# Art Message
# ==========================================================

meme_message = f"""
🎨 <b>{art.get('title','Daily CatLoaf')}</b>

━━━━━━━━━━━━━━━━━━━━━━

<i>"{meme.get('quote','')}"</i>

{art.get('caption','')}

🥖 {meme.get('cta','Stay loafy!')}

🐱 @CatLoafCoin
"""

# ==========================================================
# Queue Objects
# ==========================================================

hot_loaf = {

    "id": f"hot_loaf_{RUN_ID}",
    "type": "hot_loaf",
    "text": telegram_message,
    "image": hot_loaf_image,
    "source_title": source_title,
    "source_url": source_url,
    "persona": persona,
    "category": category

}

art_post = {

    "id": f"art_{RUN_ID}",
    "type": "art",
    "text": meme_message,
    "image": art_image,
    "title": art.get("title", ""),
    "caption": art.get("caption", ""),
    "quote": meme.get("quote", ""),
    "cta": meme.get("cta", ""),
    "source_title": "",
    "source_url": ""

}

poll_post = {

    "id": f"poll_{RUN_ID}",
    "type": "what_if",
    "text": data["poll"]["question"],
    "question": data["poll"]["question"],
    "options": data["poll"]["options"],
    "image": None,
    "source_title": "",
    "source_url": ""

}

posts = data.get("x_posts", [])

while len(posts) < 3:

    posts.append({

        "type": "fallback",
        "content": "🍞 Stay loafy with $CLOAF!"

    })

x_viral = {

    "id": f"x_viral_{RUN_ID}",
    "type": "x_viral",
    "text": posts[0]["content"],
    "image": x_news_image,
    "source_title": secondary_title,
    "source_url": secondary_url

}

x_funny = {

    "id": f"x_funny_{RUN_ID}",
    "type": "x_funny",
    "text": posts[1]["content"],
    "image": x_funny_image,
    "source_title": "",
    "source_url": ""

}

x_educational = {

    "id": f"x_educational_{RUN_ID}",
    "type": "x_educational",
    "text": posts[2]["content"],
    "image": x_education_image,
    "source_title": source_title,
    "source_url": source_url

}

print("=" * 60)
print("QUEUE OBJECTS CREATED")
print("=" * 60)

for post in [

    hot_loaf,
    art_post,
    poll_post,
    x_viral,
    x_funny,
    x_educational

]:

    print(f"{post['type']:15} -> {post['id']}")

print("=" * 60)

# ==========================================================
# Add Queue
# ==========================================================

for item in [

    hot_loaf,
    art_post,
    poll_post,
    x_viral,
    x_funny,
    x_educational

]:

    add_to_queue(item)

print("=" * 60)
print("✓ Queue Updated")
print("=" * 60)

# ==========================================================
# Save History
# ==========================================================

history_entry = {

    "headline": headline,
    "theme": news_mode,
    "primary": source_title,
    "secondary": secondary_title,
    "content_score": content_score,
    "article_score": highest_score,
    "meme": meme.get("quote", "")[:80],
    "poll": data["poll"]["question"][:80]

}

history_lines = [

    line.strip()

    for line in history.splitlines()

    if line.strip()

]

history_lines.append(

    json.dumps(

        history_entry,

        ensure_ascii=False

    )

)

history_lines = history_lines[-20:]

with open(

    "history.txt",

    "w",

    encoding="utf-8"

) as f:

    f.write(

        "\n".join(history_lines)

    )

print("✓ History Updated")

# ==========================================================
# Best Time
# ==========================================================

best = data.get("best_time", {})

print("\n" + "=" * 60)
print("BEST TIME TO POST")
print("=" * 60)

print("UTC      :", best.get("utc", "Anytime"))
print("Reason   :", best.get("reason", "Highest engagement"))
print("Audience :", best.get("audience", "Crypto Community"))

# ==========================================================
# Daily Summary
# ==========================================================

print("\n" + "=" * 60)
print("🍞 DAILY CONTENT SUMMARY")
print("=" * 60)

summary = [

    ("Run ID", RUN_ID),
    ("Content Score", content_score),
    ("News Mode", news_mode),
    ("Primary Article", source_title),
    ("Secondary Article", secondary_title),
    ("Primary Score", hot_article.get("score", 0)),
    ("Secondary Score", secondary_article.get("score", 0)),
    ("RSS Image", "YES" if rss_image else "NO"),
    ("Hot Loaf Image", "RSS" if rss_image else "AI"),
    ("Artwork", "Generated" if art_image else "Missing"),
    ("Posts Queued", 6)

]

for label, value in summary:

    print(f"{label:<20}: {value}")

print("=" * 60)

print("QUEUE CONTENTS")
print("=" * 60)

for post in [

    hot_loaf,
    art_post,
    poll_post,
    x_viral,
    x_funny,
    x_educational

]:

    print(

        f"{post['type']:<18}"

        f"{post['id']}"

    )

print("=" * 60)

# ==========================================================
# Approval Queue
# ==========================================================

print()
print("=" * 60)
print("STARTING APPROVAL QUEUE")
print("=" * 60)

try:

    process_queue()

    print("=" * 60)
    print("✓ Approval Queue Finished")
    print("=" * 60)

except Exception as e:

    print("=" * 60)
    print("APPROVAL QUEUE ERROR")
    print("=" * 60)
    print(e)
    print("=" * 60)

# ==========================================================
# Finished
# ==========================================================

print("=" * 60)
print("🍞 CatLoaf AI Bakery V3 Complete")
print("=" * 60)