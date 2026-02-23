#!/usr/bin/env python3
"""Fetch up to 10000 tweets from a Twitter/X user using the GraphQL API.

Uses aiohttp with a persistent session (single TLS handshake, keep-alive)
and zero artificial delays for maximum throughput.

Setup
-----
1. Copy ``config.example.json`` → ``config.json``
2. Fill in your own user_id, auth_token, csrf_token, and cookies
3. Run:  python fetch_tweets.py            (uses config.json)
   or:   python fetch_tweets.py myconf.json (uses a custom config path)
"""

import asyncio
import json
import os
import sys
import time
import urllib.parse

import aiohttp

# ── Configuration loader ──────────────────────────────────────────────────────

DEFAULT_CONFIG_PATH = "config.json"


def load_config(path: str | None = None) -> dict:
    """Load and validate the JSON configuration file."""
    config_path = path or DEFAULT_CONFIG_PATH

    if not os.path.isfile(config_path):
        print(
            f"❌  Config file not found: {config_path}\n"
            f"    → Copy config.example.json to {config_path} and fill in your credentials."
        )
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Validate required fields
    required = ["user_id", "auth_token", "csrf_token", "cookies",
                 "bearer_token", "base_url", "features", "field_toggles"]
    missing = [k for k in required if not cfg.get(k)]
    if missing:
        print(f"❌  Missing required config keys: {', '.join(missing)}")
        sys.exit(1)

    return cfg


# ── Build headers & constants from config ─────────────────────────────────────


def make_headers(cfg: dict) -> dict:
    """Build request headers from the loaded config."""
    return {
        "accept": "*/*",
        "accept-language": "en-GB,en;q=0.5",
        "authorization": f"Bearer {cfg['bearer_token']}",
        "content-type": "application/json",
        "sec-ch-ua": '"Chromium";v="140", "Not=A?Brand";v="24", "Brave";v="140"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        ),
        "x-csrf-token": cfg["csrf_token"],
        "x-twitter-active-user": "yes",
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-client-language": "en",
    }


# ── Helpers ────────────────────────────────────────────────────────────────────


def build_url(cfg: dict, user_id: str, tweets_per_page: int, cursor: str | None = None) -> str:
    """Build the full request URL with query parameters."""
    variables: dict = {
        "userId": user_id,
        "count": tweets_per_page,
        "includePromotedContent": True,
        "withQuickPromoteEligibilityTweetFields": True,
        "withVoice": True,
    }
    if cursor:
        variables["cursor"] = cursor

    params = {
        "variables": json.dumps(variables, separators=(",", ":")),
        "features": json.dumps(cfg["features"], separators=(",", ":")),
        "fieldToggles": json.dumps(cfg["field_toggles"], separators=(",", ":")),
    }
    return f"{cfg['base_url']}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"


def extract_tweets_and_cursor(response_json: dict):
    """
    Walk the GraphQL response to pull out tweet entries and the next cursor.
    Returns (list[dict], next_cursor | None).
    """
    tweets = []
    next_cursor = None

    try:
        result = response_json["data"]["user"]["result"]
        tl = result.get("timeline_v2") or result.get("timeline")
        instructions = tl["timeline"]["instructions"]
    except (KeyError, TypeError):
        print("⚠  Unexpected response structure – could not find instructions.")
        return tweets, None

    for instruction in instructions:
        entries = instruction.get("entries") or []
        for entry in entries:
            entry_id = entry.get("entryId", "")

            # Cursor entries
            if entry_id.startswith("cursor-bottom"):
                try:
                    next_cursor = entry["content"]["value"]
                except KeyError:
                    pass
                continue

            if entry_id.startswith("cursor-top"):
                continue

            # Tweet entries
            if entry_id.startswith("tweet-") or entry_id.startswith(
                "profile-conversation-"
            ):
                try:
                    items = entry.get("content", {}).get("items")
                    if items:
                        for item in items:
                            tweet_result = (
                                item.get("item", {})
                                .get("itemContent", {})
                                .get("tweet_results", {})
                                .get("result", {})
                            )
                            if tweet_result:
                                tweets.append(tweet_result)
                    else:
                        tweet_result = (
                            entry.get("content", {})
                            .get("itemContent", {})
                            .get("tweet_results", {})
                            .get("result", {})
                        )
                        if tweet_result:
                            tweets.append(tweet_result)
                except Exception as exc:
                    print(f"⚠  Skipping entry {entry_id}: {exc}")

    return tweets, next_cursor


# ── Main loop (async) ─────────────────────────────────────────────────────────


def flush_tweets(texts: list[str], output_file: str):
    """Write the current list of tweet texts to the JSON file."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)


async def main():
    # Resolve config path (optional CLI arg)
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    cfg = load_config(config_path)

    user_id = str(cfg["user_id"])
    target_tweet_count = cfg.get("target_tweet_count")  # None → fetch all
    tweets_per_page = cfg.get("tweets_per_page", 20)
    output_file = cfg.get("output_file", "tweets.json")
    cookies = cfg["cookies"]
    headers = make_headers(cfg)

    all_texts: list[str] = []
    cursor: str | None = None
    page = 0

    # Start with an empty JSON array on disk
    flush_tweets(all_texts, output_file)

    # Build a cookie jar from COOKIES dict
    jar = aiohttp.CookieJar(unsafe=True)

    # Use a single TCPConnector with keep-alive for connection reuse
    connector = aiohttp.TCPConnector(
        limit=1,           # single connection (sequential requests)
        keepalive_timeout=60,
        enable_cleanup_closed=True,
    )

    target_label = f"{target_tweet_count}" if target_tweet_count else "ALL"
    print(f"🐦 Fetching {target_label} tweets for userId={user_id} …\n")

    async with aiohttp.ClientSession(
        headers=headers,
        cookies=cookies,
        connector=connector,
        cookie_jar=jar,
    ) as session:
        while True:
            # Stop if we've hit the target (when set)
            if target_tweet_count and len(all_texts) >= target_tweet_count:
                break

            page += 1
            url = build_url(cfg, user_id, tweets_per_page, cursor)
            print(
                f"  Page {page}: requesting {tweets_per_page} tweets "
                f"(collected so far: {len(all_texts)}) …"
            )

            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 429:
                    # Use x-rate-limit-reset to calculate exact wait time
                    reset_ts = resp.headers.get("x-rate-limit-reset")
                    if reset_ts:
                        wait_secs = max(int(reset_ts) - int(time.time()), 1) + 2  # +2s buffer
                    else:
                        wait_secs = int(resp.headers.get("retry-after", "60"))
                    body = await resp.text()
                    print(f"  ⏳ Rate-limited (429). Waiting {wait_secs}s until reset …")
                    print(f"     x-rate-limit-reset: {reset_ts}")
                    print(f"     x-rate-limit-remaining: {resp.headers.get('x-rate-limit-remaining')}")
                    print(f"     Response body: {body[:500]}")
                    await asyncio.sleep(wait_secs)
                    page -= 1  # retry the same page
                    continue

                if resp.status != 200:
                    body = await resp.text()
                    print(f"  ⚠  HTTP {resp.status}: {body[:300]}")
                    print(f"     Retrying in 30s …")
                    await asyncio.sleep(30)
                    page -= 1  # retry the same page
                    continue

                data = await resp.json()

            tweets, next_cursor = extract_tweets_and_cursor(data)

            if not tweets:
                print("  ℹ  No more tweets returned. All tweets fetched!")
                break

            # Extract text from this batch and append
            for t in tweets:
                text = t.get("legacy", {}).get("full_text", "")
                if text:
                    all_texts.append(text)

            # Flush to disk after every page so the file updates live
            flush_tweets(all_texts, output_file)
            print(f"     ↳ got {len(tweets)} tweets → {output_file} updated ({len(all_texts)} total)")

            if not next_cursor:
                print("  ℹ  No next cursor. Reached the end of the timeline.")
                break

            cursor = next_cursor
            # No artificial delay — fire the next request immediately

    # Final trim (if target was set) and write
    if target_tweet_count:
        all_texts = all_texts[:target_tweet_count]
    flush_tweets(all_texts, output_file)

    print(f"\n✅ Done. {len(all_texts)} tweet texts saved to {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
