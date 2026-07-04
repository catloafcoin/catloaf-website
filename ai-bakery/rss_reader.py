# ==========================================================
# CatLoaf AI Bakery V3
# rss_reader.py
# RSS Reader & Smart Ranking Engine
# ==========================================================

import re
import html
import time
from datetime import datetime, timezone

import feedparser


# --------------------------------------------------
# Constants
# --------------------------------------------------

MAX_ARTICLES_PER_FEED = 5

MAX_ARTICLE_AGE_DAYS = 7

IMG_REGEX = re.compile(
    r'<img[^>]+src=["\']([^"\']+)["\']',
    re.IGNORECASE
)

BAD_IMAGE_PATTERNS = [

    "avatar",
    "profile",
    "icon",
    "favicon",
    "emoji",
    "logo",
    "placeholder",
    "default",
    "blank",
    "pixel",
    "spacer"

]


# --------------------------------------------------
# Date Helpers
# --------------------------------------------------

def parse_article_time(entry):

    """
    Converts RSS published date into datetime.
    """

    if getattr(entry, "published_parsed", None):

        try:

            return datetime.fromtimestamp(
                time.mktime(entry.published_parsed),
                tz=timezone.utc
            )

        except Exception:

            pass

    if getattr(entry, "updated_parsed", None):

        try:

            return datetime.fromtimestamp(
                time.mktime(entry.updated_parsed),
                tz=timezone.utc
            )

        except Exception:

            pass

    return None


def article_age_days(dt):

    if dt is None:

        return 999

    return (

        datetime.now(timezone.utc) - dt

    ).days


# --------------------------------------------------
# HTML Image Extraction
# --------------------------------------------------

def extract_html_image(text):

    if not text:

        return ""

    match = IMG_REGEX.search(text)

    if not match:

        return ""

    return html.unescape(

        match.group(1)

    )


# --------------------------------------------------
# Image Validation
# --------------------------------------------------

def image_is_valid(url):

    if not url:

        return False

    url = url.lower()

    if not (

        url.startswith("http://")

        or url.startswith("https://")

    ):

        return False

    for bad in BAD_IMAGE_PATTERNS:

        if bad in url:

            return False

    return True


# --------------------------------------------------
# RSS Image Extraction
# --------------------------------------------------

def extract_image(entry):

    """
    Attempts every known RSS image format.
    Returns the first usable image.
    """

    # --------------------------
    # media_content
    # --------------------------

    if getattr(entry, "media_content", None):

        for media in entry.media_content:

            url = media.get("url", "")

            if image_is_valid(url):

                return url

    # --------------------------
    # media_thumbnail
    # --------------------------

    if getattr(entry, "media_thumbnail", None):

        for media in entry.media_thumbnail:

            url = media.get("url", "")

            if image_is_valid(url):

                return url

    # --------------------------
    # links
    # --------------------------

    if getattr(entry, "links", None):

        for link in entry.links:

            href = link.get("href", "")

            if image_is_valid(href):

                if (

                    link.get("rel") == "enclosure"

                    or link.get("type", "").startswith("image/")

                ):

                    return href

    # --------------------------
    # content blocks
    # --------------------------

    if getattr(entry, "content", None):

        for block in entry.content:

            image = extract_html_image(

                block.get("value", "")

            )

            if image_is_valid(image):

                return image

    # --------------------------
    # summary
    # --------------------------

    image = extract_html_image(

        entry.get("summary", "")

    )

    if image_is_valid(image):

        return image

    # --------------------------
    # description
    # --------------------------

    image = extract_html_image(

        entry.get("description", "")

    )

    if image_is_valid(image):

        return image

    return ""

# --------------------------------------------------
# RSS Reader
# --------------------------------------------------

def get_latest_news(

    feed_file="rss_feeds.txt",

    max_articles=20

):

    articles = []

    try:

        with open(

            feed_file,

            "r",

            encoding="utf-8"

        ) as f:

            feeds = [

                line.strip()

                for line in f

                if line.strip()

            ]

    except FileNotFoundError:

        print(

            f"RSS feed file not found: {feed_file}"

        )

        return []

    print("=" * 60)
    print("READING RSS FEEDS")
    print("=" * 60)

    for feed_url in feeds:

        try:

            print("Feed:", feed_url)

            feed = feedparser.parse(feed_url)

            source = feed.feed.get(

                "title",

                feed_url

            )

            for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:

                published_dt = parse_article_time(entry)

                age_days = article_age_days(published_dt)

                article = {

                    "title":

                        entry.get(

                            "title",

                            ""

                        ).strip(),

                    "summary":

                        entry.get(

                            "summary",

                            entry.get(

                                "description",

                                ""

                            )

                        ),

                    "link":

                        entry.get(

                            "link",

                            ""

                        ),

                    "source":

                        source,

                    "published":

                        entry.get(

                            "published",

                            ""

                        ),

                    "published_dt":

                        published_dt,

                    "age_days":

                        age_days,

                    "image":

                        extract_image(entry)

                }

                articles.append(article)

        except Exception as e:

            print("=" * 60)
            print("RSS ERROR")
            print(feed_url)
            print(e)
            print("=" * 60)

    # --------------------------------------------------
    # Remove Duplicates
    # --------------------------------------------------

    unique = []

    seen_links = set()

    seen_titles = set()

    for article in articles:

        title = (

            article.get(

                "title",

                ""

            )

            .strip()

            .lower()

        )

        link = (

            article.get(

                "link",

                ""

            )

            .strip()

        )

        if title in seen_titles:

            continue

        if link and link in seen_links:

            continue

        seen_titles.add(title)

        if link:

            seen_links.add(link)

        unique.append(article)

    # --------------------------------------------------
    # Freshness Sort
    # --------------------------------------------------

    unique.sort(

        key=lambda article: (

            article.get(

                "age_days",

                999

            ),

            not bool(

                article.get(

                    "image"

                )

            )

        )

    )

    print("=" * 60)
    print(

        f"Loaded {len(unique)} unique articles."

    )

    print("=" * 60)

    return unique[:max_articles]

# --------------------------------------------------
# Article Scoring
# --------------------------------------------------

def score_articles(articles):

    KEYWORDS = {

        # Core Solana
        "solana": 35,
        "validator": 24,
        "firedancer": 28,
        "jupiter": 24,
        "raydium": 24,
        "pump.fun": 22,
        "phantom": 20,
        "backpack": 20,
        "kamino": 20,
        "drift": 20,
        "helius": 20,
        "marinade": 18,
        "sanctum": 18,

        # Infrastructure
        "rpc": 16,
        "sdk": 16,
        "developer": 18,
        "builder": 18,
        "infrastructure": 18,
        "ecosystem": 15,

        # DeFi
        "liquidity": 12,
        "dex": 12,
        "staking": 12,
        "yield": 10,

        # Security
        "hack": 30,
        "exploit": 30,
        "security": 24,
        "audit": 16,

        # Adoption
        "stablecoin": 16,
        "payments": 15,
        "adoption": 16,
        "institutional": 18,
        "etf": 20,

        # Community
        "memecoin": 14,
        "community": 10,
        "governance": 12

    }

    TRUSTED = [

        "solana",
        "helius",
        "jupiter",
        "raydium",
        "phantom",
        "backpack",
        "messari",
        "blockworks",
        "coindesk",
        "cointelegraph",
        "decrypt",
        "the block"

    ]

    IMPACT = [

        "breaking",
        "major",
        "launch",
        "released",
        "upgrade",
        "integration",
        "record",
        "new",
        "mainnet",
        "proposal"

    ]

    scored = []

    for article in articles:

        score = 0

        text = (

            article.get("title", "")

            + " "

            + article.get("summary", "")

        ).lower()

        source = article.get(

            "source",

            ""

        ).lower()

        # -------------------------
        # Keyword Score
        # -------------------------

        for word, value in KEYWORDS.items():

            if word in text:

                score += value

        # -------------------------
        # Trusted Source
        # -------------------------

        if any(

            s in source

            for s in TRUSTED

        ):

            score += 8

        # -------------------------
        # Solana Bonus
        # -------------------------

        if "solana" in text:

            score += 12

        # -------------------------
        # High Impact Words
        # -------------------------

        for word in IMPACT:

            if word in text:

                score += 4

        # -------------------------
        # Freshness Bonus
        # -------------------------

        age = article.get(

            "age_days",

            999

        )

        if age <= 0:

            score += 18

        elif age == 1:

            score += 14

        elif age <= 3:

            score += 8

        elif age <= 7:

            score += 2

        else:

            score -= 12

        # -------------------------
        # Image Bonus
        # -------------------------

        if image_is_valid(

            article.get("image", "")

        ):

            score += 8

        # -------------------------
        # Better Titles
        # -------------------------

        title = article.get(

            "title",

            ""

        )

        if len(title) > 50:

            score += 2

        # -------------------------
        # Weak Article Filter
        # -------------------------

        if score < 10:

            continue

        article["score"] = score

        scored.append(article)

    scored.sort(

        key=lambda article: (

            article["score"],

            -article.get(

                "age_days",

                999

            ),

            bool(

                article.get(

                    "image"

                )

            ),

            len(

                article.get(

                    "summary",

                    ""

                )

            )

        ),

        reverse=True

    )

    return scored

# --------------------------------------------------
# Debug Helpers
# --------------------------------------------------

def print_top_articles(articles, limit=10):

    print("\n" + "=" * 60)
    print("TOP SCORED ARTICLES")
    print("=" * 60)

    if not articles:

        print("No scored articles.")
        print("=" * 60)
        return

    for index, article in enumerate(

        articles[:limit],

        start=1

    ):

        age = article.get(

            "age_days",

            "?"

        )

        print(f"#{index}")

        print(

            "Score :",

            article.get(

                "score",

                0

            )

        )

        print(

            "Age   :",

            f"{age} day(s)"

        )

        print(

            "Image :",

            "YES"

            if article.get("image")

            else "NO"

        )

        print(

            "Source:",

            article.get(

                "source",

                "Unknown"

            )

        )

        print(

            "Title :",

            article.get(

                "title",

                ""

            )

        )

        if article.get("published"):

            print(

                "Date  :",

                article.get(

                    "published"

                )

            )

        print("-" * 60)

    print("=" * 60)

# --------------------------------------------------
# Convenience Wrapper
# --------------------------------------------------

def get_ranked_articles(

    feed_file="rss_feeds.txt",

    max_articles=20

):

    # Load extra articles so duplicates can be filtered
    articles = get_latest_news(

        feed_file=feed_file,

        max_articles=max_articles * 2

    )

    if not articles:

        return []

    ranked = score_articles(articles)

    # Fallback if every article scores too low
    if not ranked:

        print("=" * 60)
        print("No high-scoring articles found.")
        print("Falling back to newest articles.")
        print("=" * 60)

        ranked = sorted(

            articles,

            key=lambda article: (

                article.get("age_days", 999),

                not bool(article.get("image"))

            )

        )

    # --------------------------------------
    # Diversity Filter
    # --------------------------------------

    final = []

    seen_topics = set()

    for article in ranked:

        title = article.get(

            "title",

            ""

        ).lower()

        topic = " ".join(

            title.split()[:4]

        )

        if topic in seen_topics:

            continue

        seen_topics.add(topic)

        final.append(article)

        if len(final) >= max_articles:

            break

    print_top_articles(final)

    print("=" * 60)
    print("SMART ARTICLE SUMMARY")
    print("=" * 60)

    for index, article in enumerate(final[:5], start=1):

        print(

            f"{index}. "

            f"[{article.get('score', 0)}] "

            f"{article.get('title', '')}"

        )

        print(

            f"   Age    : {article.get('age_days', '?')} day(s)"

        )

        print(

            f"   Image  : {'YES' if article.get('image') else 'NO'}"

        )

        print(

            f"   Source : {article.get('source', '')}"

        )

        print()

    print("=" * 60)

    return final