# ==========================================================
# CatLoaf AI Bakery V3
# rss_reader.py
# RSS Reader & Article Ranking
# ==========================================================

import re
import html

import feedparser


# --------------------------------------------------
# Constants
# --------------------------------------------------

MAX_ARTICLES_PER_FEED = 5


# --------------------------------------------------
# Image Extraction Helpers
# --------------------------------------------------

IMG_REGEX = re.compile(
    r'<img[^>]+src=["\']([^"\']+)["\']',
    re.IGNORECASE
)


def extract_html_image(text):

    if not text:

        return ""

    match = IMG_REGEX.search(text)

    if match:

        return html.unescape(match.group(1))

    return ""


def extract_image(entry):

    """
    Attempts every common RSS image format.
    Returns the first usable image URL.
    """

    # ------------------------------------
    # media:content
    # ------------------------------------

    if getattr(entry, "media_content", None):

        for media in entry.media_content:

            url = media.get("url")

            if url:

                return url

    # ------------------------------------
    # media:thumbnail
    # ------------------------------------

    if getattr(entry, "media_thumbnail", None):

        for media in entry.media_thumbnail:

            url = media.get("url")

            if url:

                return url

    # ------------------------------------
    # enclosures / links
    # ------------------------------------

    if getattr(entry, "links", None):

        for link in entry.links:

            href = link.get("href", "")

            if not href:

                continue

            if (

                link.get("rel") == "enclosure"

                or link.get("type", "").startswith("image/")

            ):

                return href

    # ------------------------------------
    # content blocks
    # ------------------------------------

    if getattr(entry, "content", None):

        for block in entry.content:

            image = extract_html_image(

                block.get("value", "")

            )

            if image:

                return image

    # ------------------------------------
    # summary
    # ------------------------------------

    image = extract_html_image(

        entry.get("summary", "")

    )

    if image:

        return image

    # ------------------------------------
    # description
    # ------------------------------------

    image = extract_html_image(

        entry.get("description", "")

    )

    if image:

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

    # --------------------------------------------------
    # Read Every Feed
    # --------------------------------------------------

    for feed_url in feeds:

        try:

            print("Feed:", feed_url)

            feed = feedparser.parse(feed_url)

            source = feed.feed.get(

                "title",

                feed_url

            )

            for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:

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

    seen_titles = set()

    seen_links = set()

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

    print("=" * 60)
    print(f"Loaded {len(unique)} unique articles.")
    print("=" * 60)

    return unique[:max_articles]

# --------------------------------------------------
# Article Scoring
# --------------------------------------------------

def score_articles(articles):

    KEYWORDS = {

        # Core Solana
        "solana": 30,
        "validator": 20,
        "firedancer": 25,
        "jupiter": 22,
        "raydium": 22,
        "pump.fun": 22,
        "phantom": 20,
        "backpack": 20,
        "kamino": 20,
        "drift": 20,
        "sanctum": 18,
        "helius": 18,
        "marinade": 18,

        # Builders
        "builder": 15,
        "developer": 15,
        "ecosystem": 15,
        "infrastructure": 15,
        "rpc": 12,
        "sdk": 12,

        # Trading
        "listing": 15,
        "launch": 15,
        "integration": 15,
        "upgrade": 15,
        "airdrop": 12,
        "volume": 10,
        "liquidity": 10,

        # Memecoins
        "memecoin": 12,
        "meme": 10,
        "community": 8,

        # Security
        "hack": 25,
        "exploit": 25,
        "security": 20,

        # Institutional
        "etf": 20,
        "institutional": 18,
        "adoption": 15,
        "stablecoin": 15,
        "payments": 12

    }

    TRUSTED = [

        "solana",
        "coindesk",
        "cointelegraph",
        "decrypt",
        "blockworks",
        "the block",
        "messari",
        "helius",
        "raydium",
        "jupiter",
        "phantom"

    ]

    IMPACT = [

        "breaking",
        "major",
        "launch",
        "released",
        "upgrade",
        "integration",
        "partnership",
        "record",
        "new"

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

        # ----------------------------
        # Keyword score
        # ----------------------------

        for word, value in KEYWORDS.items():

            if word in text:

                score += value

        # ----------------------------
        # Trusted source
        # ----------------------------

        if any(

            trusted in source

            for trusted in TRUSTED

        ):

            score += 6

        # ----------------------------
        # Image bonus
        # ----------------------------

        if article.get("image"):

            score += 5

        # ----------------------------
        # Longer titles tend to
        # contain better context.
        # ----------------------------

        title = article.get(

            "title",

            ""

        )

        if len(title) > 45:

            score += 2

        # ----------------------------
        # High-impact wording
        # ----------------------------

        for word in IMPACT:

            if word in text:

                score += 3

        # ----------------------------
        # Heavy Solana bonus
        # ----------------------------

        if "solana" in text:

            score += 10

        # ----------------------------
        # Skip weak articles
        # ----------------------------

        if score < 8:

            continue

        article["score"] = score

        scored.append(article)

    scored.sort(

        key=lambda x: (

            x["score"],

            bool(x.get("image")),

            len(x.get("summary", ""))

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

    for index, article in enumerate(articles[:limit], start=1):

        print(f"#{index}")

        print(

            "Score :",

            article.get("score", 0)

        )

        print(

            "Image :",

            "YES" if article.get("image") else "NO"

        )

        print(

            "Source:",

            article.get("source", "Unknown")

        )

        print(

            "Title :",

            article.get("title", "")

        )

        if article.get("published"):

            print(

                "Date  :",

                article.get("published")

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

    articles = get_latest_news(

        feed_file=feed_file,

        max_articles=max_articles

    )

    ranked = score_articles(articles)

    print_top_articles(ranked)

    return ranked