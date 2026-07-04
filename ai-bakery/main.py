from scheduler import (
    add_to_queue,
    save_daily,
    calculate_score
)

from image_generator import generate_image

from rss_reader import (
    get_latest_news,
    score_articles
)

from poster import process_queue

from modules import (
    load_text,
    load_json,
    validate_json
)

import os
import json
import uuid
import google.generativeai as genai

print("=" * 50)
print("🍞 Starting CatLoaf AI Bakery V2")
print("=" * 50)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

config = load_json("config.json")

RUN_ID = uuid.uuid4().hex[:8]

API_KEYS = [
    os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4")
]

if not API_KEYS[0]:
    raise Exception("Missing GEMINI_API_KEY")

print("✓ Configuration Loaded")

# --------------------------------------------------
# Prompt Files
# --------------------------------------------------

brand = load_text("brand.txt")
prompt_template = load_text("prompt.txt")
history = load_text("history.txt")

print("✓ Prompt Loaded")

# --------------------------------------------------
# RSS
# --------------------------------------------------

print("Fetching RSS...")

articles = score_articles(
    get_latest_news()
)

if not articles:
    raise Exception("No RSS articles found.")

articles = sorted(
    articles,
    key=lambda x: x.get("score", 0),
    reverse=True
)

articles = articles[:12]

print("\nTop Articles\n")

for article in articles[:5]:

    print(
        article.get("score", 0),
        "-",
        article.get("title", "")
    )

# --------------------------------------------------
# News Mode
# --------------------------------------------------

highest_score = max(
    article.get("score", 0)
    for article in articles
)

if highest_score >= 25:

    news_mode = "breaking"

elif highest_score >= 15:

    news_mode = "trending"

else:

    news_mode = "fallback"

print(f"Highest Score : {highest_score}")
print(f"News Mode     : {news_mode}")

# --------------------------------------------------
# Build Gemini Context
# --------------------------------------------------

news_text = ""

for article in articles:

    news_text += f"""

TITLE:
{article.get('title','')}

SUMMARY:
{article.get('summary','')}

SOURCE:
{article.get('source','')}

URL:
{article.get('link','')}
"""

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

# --------------------------------------------------
# Gemini
# --------------------------------------------------

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json"
}

response = None
last_error = None

for key in API_KEYS:

    if not key:
        continue

    try:

        genai.configure(api_key=key)

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

data = validate_json(response.text)

required = [
    "telegram",
    "art_image",
    "meme",
    "poll",
    "x_posts",
    "best_time"
]

for key in required:

    if key not in data:
        raise Exception(f"Missing {key}")

print("✓ JSON Valid")

score = calculate_score(data)

print(f"Content Score: {score}")

if score >= 80:

    save_daily(data)

    print("✓ Daily Saved")

else:

    print("Skipped Daily Save")

# --------------------------------------------------
# Article Selection
# --------------------------------------------------

def article_has_image(article):

    return bool(article.get("image"))


def choose_hot_loaf_article(articles):

    print("\nSelecting Hot Loaf article...\n")

    with_image = [
        a for a in articles
        if article_has_image(a)
    ]

    if with_image:

        article = max(
            with_image,
            key=lambda x: x.get("score", 0)
        )

        print("✓ Hot Loaf uses RSS image")

    else:

        article = max(
            articles,
            key=lambda x: x.get("score", 0)
        )

        print("✓ Hot Loaf will use AI header")

    return article


def choose_secondary_article(articles, exclude_id):

    remaining = [

        a for a in articles

        if a.get("link") != exclude_id

    ]

    if not remaining:

        return choose_hot_loaf_article(articles)

    return max(
        remaining,
        key=lambda x: x.get("score", 0)
    )


# --------------------------------------------------
# Pick Articles
# --------------------------------------------------

hot_article = choose_hot_loaf_article(articles)

secondary_article = choose_secondary_article(
    articles,
    hot_article.get("link")
)

print("=" * 60)
print("HOT LOAF ARTICLE")
print("=" * 60)
print(hot_article.get("title"))
print(hot_article.get("link"))
print("=" * 60)

print("=" * 60)
print("SECONDARY ARTICLE")
print("=" * 60)
print(secondary_article.get("title"))
print(secondary_article.get("link"))
print("=" * 60)

# --------------------------------------------------
# Hot Loaf Sources
# --------------------------------------------------

source_title = hot_article.get("title", "")
source_url = hot_article.get("link", "")
rss_image = hot_article.get("image", "")

# --------------------------------------------------
# Secondary Sources
# --------------------------------------------------

secondary_title = secondary_article.get("title", "")
secondary_url = secondary_article.get("link", "")
secondary_image = secondary_article.get("image", "")

# --------------------------------------------------
# Telegram Message Builder
# --------------------------------------------------

def divider():
    return "━━━━━━━━━━━━━━━━━━━━━━"


tg = data["telegram"]

persona = tg.get("persona", "CatLoaf")
category = tg.get("category", "Community")
headline = tg.get("headline", "TODAY'S HOT LOAF")

loaf_score = tg.get("loaf_score", {})

overall = loaf_score.get("overall", "-")
market = loaf_score.get("market_impact", "-")
builder = loaf_score.get("builder_interest", "-")
urgency = loaf_score.get("urgency", "-")

telegram_message = f"""
🔥 <b>{headline}</b>

{divider()}

🍞 <i>Fresh from today's oven...</i>

{tg.get("opening","")}

🔥 <b>Fresh Alpha</b>
"""

for bullet in tg.get("bullets", []):

    telegram_message += f"\n• {bullet}"

telegram_message += "\n\n🧈 <b>Why It Matters</b>\n\n"
telegram_message += tg.get("why", "")

telegram_message += "\n\n📊 <b>Loaf Score</b>\n"

if str(overall).isdigit():
    telegram_message += f"\n🍞 Overall: {overall}/100"
else:
    telegram_message += f"\n🍞 Overall: {overall}"

telegram_message += f"""

📈 Market Impact: {market}

🏗 Builder Interest: {builder}

⚡ Urgency: {urgency}

🥖 <b>Hot Take</b>

{tg.get("question","")}

{divider()}

📰 Source:
{source_title}

🔗 {source_url}

🐱 @CatLoafCoin
"""

# --------------------------------------------------
# Images
# --------------------------------------------------

meme = data["meme"]
art = data["art_image"]
header = tg.get("header_image", {})

print("=" * 60)
print("IMAGE SELECTION")
print("=" * 60)

if rss_image:

    print("Using RSS image for Hot Loaf.")
    hot_loaf_image = rss_image

else:

    print("Generating AI Hot Loaf image.")
    hot_loaf_image = generate_image(header)

print("Generating AI artwork...")
art_image = generate_image(art)

x_news_image = secondary_image or hot_loaf_image
x_funny_image = art_image
x_education_image = hot_loaf_image

# --------------------------------------------------
# Art Message
# --------------------------------------------------

meme_message = f"""
🎨 <b>$CLOAF ART FOR YOU ❤️</b>

{divider()}

<b>{art.get('title','Art')}</b>

<i>"{meme.get('quote','')}"</i>

{art.get('caption','')}

🥖 {meme.get('cta','')}
"""

# --------------------------------------------------
# Queue Objects
# --------------------------------------------------

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

# --------------------------------------------------
# Queue
# --------------------------------------------------

add_to_queue(hot_loaf)
add_to_queue(art_post)
add_to_queue(poll_post)
add_to_queue(x_viral)
add_to_queue(x_funny)
add_to_queue(x_educational)

print("✓ Queue Updated")

# --------------------------------------------------
# Best Time
# --------------------------------------------------

best = data.get("best_time", {})

print("\n" + "=" * 60)
print("BEST TIME TO POST")
print("=" * 60)
print("UTC      :", best.get("utc", "Anytime"))
print("Reason   :", best.get("reason", "No recommendation"))
print("Audience :", best.get("audience", "Crypto Community"))

# --------------------------------------------------
# History
# --------------------------------------------------

history_entry = {

    "headline": headline,

    "theme": news_mode,

    "source": source_title,

    "meme": meme.get("quote", "")[:50],

    "poll": data["poll"]["question"][:50],

    "cta": meme.get("cta", "")[:50]

}

history_lines = []

for line in history.splitlines():

    line = line.strip()

    if line:

        history_lines.append(line)

history_lines.append(

    json.dumps(

        history_entry,

        ensure_ascii=False

    )

)

history_lines = history_lines[-10:]

with open(

    "history.txt",

    "w",

    encoding="utf-8"

) as f:

    f.write(

        "\n".join(history_lines)

    )

print("✓ History Updated")

# --------------------------------------------------
# Summary
# --------------------------------------------------

print("\n" + "=" * 60)
print("🍞 DAILY CONTENT SUMMARY")
print("=" * 60)

print(f"Headline          : {headline}")
print(f"News Mode         : {news_mode}")
print(f"Primary Article   : {source_title}")
print(f"Secondary Article : {secondary_title}")
print(f"RSS Image         : {'Yes' if rss_image else 'No'}")
print(f"Hot Loaf Image    : {'RSS' if rss_image else 'AI'}")
print(f"Art Image         : {'Generated' if art_image else 'Missing'}")
print(f"Posts Queued      : 6")

print("=" * 60)

for item in [

    hot_loaf,

    art_post,

    poll_post,

    x_viral,

    x_funny,

    x_educational

]:

    print(

        f"{item['type']:15} -> {item['id']}"

    )

print("=" * 60)

# --------------------------------------------------
# Approval Queue
# --------------------------------------------------

print("\nStarting Approval Queue...\n")

try:

    process_queue()

    print("\n✓ Approval Queue Finished")

except Exception as e:

    print("=" * 60)
    print("APPROVAL ERROR")
    print(e)
    print("=" * 60)

print("=" * 60)
print("🍞 CatLoaf AI Bakery Complete")
print("=" * 60)