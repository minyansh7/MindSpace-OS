"""
Autonomous Twitter/X drafter — polls for login, types tweet, WAITS for manual post.

X has no cross-browser drafts on the free tier. This script gets as close as
possible to "draft + review" by:
    1. Opening x.com/compose
    2. Polling for login (up to 240s)
    3. Typing the selected tweet (option A by default)
    4. Stopping BEFORE clicking Post — leaves the browser open for 600s
    5. User reviews in the Playwright window and clicks Post manually

Usage:
    python3 drafts/post_twitter_auto.py              # option A
    python3 drafts/post_twitter_auto.py --option B
    python3 drafts/post_twitter_auto.py --thread
    python3 drafts/post_twitter_auto.py --link https://minyansh.substack.com/p/foo

While waiting, the script polls for URL change — if the compose modal closes
(you clicked Post or dismissed), the script exits early.
"""

import argparse
import re
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

USER_DATA_DIR = Path.home() / ".playwright-profiles" / "twitter"
COMPOSE_URL = "https://x.com/compose/post"
HOME_URL = "https://x.com/home"
MAX_LOGIN_WAIT = 480  # 8 minutes — leaves room for X's login flow + captcha
POST_REVIEW_WAIT = 80  # ~1.3 min for manual review/post (bash cap is 600s total)

TWEET_TEXTAREA = 'div[data-testid^="tweetTextarea_"][contenteditable="true"]'
POST_BUTTON = 'button[data-testid="tweetButton"], button[data-testid="tweetButtonInline"]'
ADD_TO_THREAD = 'button[data-testid="addButton"]'


def _extract_code_block(text: str) -> str:
    m = re.search(r"```[^\n]*\n(.*?)\n```", text, re.DOTALL)
    return m.group(1).strip() if m else ""


def parse_drafts(md_path: Path):
    text = md_path.read_text()
    m = re.search(r"## Twitter / X Posts(.*)", text, re.DOTALL)
    if not m:
        raise ValueError("No '## Twitter / X Posts' section in draft file")
    section = m.group(1)

    def grab(letter):
        mm = re.search(
            rf"### Option {letter}[^\n]*\n(.*?)(?=\n### |\Z)",
            section, re.DOTALL,
        )
        return _extract_code_block(mm.group(1)) if mm else ""

    thread_tail = []
    follow = re.search(r"\*\*Follow-up tweets[^*]*\*\*(.*)", section, re.DOTALL)
    if follow:
        for b in re.findall(r"```[^\n]*\n(.*?)\n```", follow.group(1), re.DOTALL):
            if b.strip():
                thread_tail.append(b.strip())

    return {"A": grab("A"), "B": grab("B"), "C": grab("C"), "thread_tail": thread_tail}


def wait_for_compose(page, max_wait: int) -> bool:
    """
    Poll for the tweet textarea to become visible. CRITICAL: we do NOT
    re-navigate the page during polling — that interrupts the user's
    login flow (causing the "flashing" behavior). We just wait patiently.

    Once the user completes login, X auto-redirects back to /compose/post
    and the textarea appears — at which point we return True.
    """
    start = time.time()
    last_url = None
    while time.time() - start < max_wait:
        elapsed = int(time.time() - start)

        # Probe for the tweet textarea without re-navigating
        try:
            if page.locator(TWEET_TEXTAREA).first.is_visible(timeout=1000):
                print(f"  [auth] {elapsed}s  compose ready ✓", flush=True)
                return True
        except Exception:
            pass

        # Log URL changes only (not every tick — less noise)
        try:
            url = page.url
            if url != last_url:
                print(f"  [auth] {elapsed}s  url now: {url[:100]}", flush=True)
                last_url = url
            elif elapsed % 30 == 0:
                print(f"  [auth] {elapsed}s  still on: {url[:100]}", flush=True)
        except Exception as e:
            # Browser may have been closed by user
            print(f"  [auth] {elapsed}s  page inaccessible: {e}", flush=True)
            return False

        time.sleep(3)
    return False


def type_at_focus(page, text: str):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line:
            page.keyboard.type(line, delay=6)
        if i < len(lines) - 1:
            page.keyboard.press("Shift+Enter")


def insert_single(page, text: str):
    page.wait_for_selector(TWEET_TEXTAREA, timeout=15000)
    page.click(TWEET_TEXTAREA)
    type_at_focus(page, text)


def insert_thread(page, tweets: list):
    page.wait_for_selector(TWEET_TEXTAREA, timeout=15000)
    for i, tw in enumerate(tweets):
        if i > 0:
            page.click(ADD_TO_THREAD)
            page.wait_for_timeout(400)
            page.locator(TWEET_TEXTAREA).nth(i).click()
        else:
            page.click(TWEET_TEXTAREA)
        type_at_focus(page, tw)


def wait_for_manual_post(page, max_wait: int):
    """Poll for compose modal to close (= user clicked Post or cancelled)."""
    start = time.time()
    while time.time() - start < max_wait:
        elapsed = int(time.time() - start)
        url = page.url
        # When Post succeeds, X typically navigates away from /compose/post
        if "compose/post" not in url:
            print(f"  [review] {elapsed}s  compose closed (URL: {url[:60]})")
            return True
        # Also check if compose modal DOM has been dismissed
        try:
            visible = page.locator(TWEET_TEXTAREA).is_visible(timeout=500)
            if not visible:
                print(f"  [review] {elapsed}s  compose modal dismissed")
                return True
        except Exception:
            pass
        if elapsed % 30 == 0 and elapsed > 0:
            print(f"  [review] {elapsed}s  still composed, awaiting Post click...",
                  flush=True)
        time.sleep(2)
    print(f"  [review] {max_wait}s elapsed with no post, closing browser")
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", type=Path, default=Path("drafts/launch-post.md"))
    ap.add_argument("--option", choices=["A", "B", "C"], default="A")
    ap.add_argument("--thread", action="store_true")
    ap.add_argument("--link", type=str, default=None,
                    help="Replace all [link] with this URL")
    args = ap.parse_args()

    if not args.draft.exists():
        print(f"ERROR: {args.draft} not found", file=sys.stderr)
        sys.exit(1)

    drafts = parse_drafts(args.draft)

    def apply_link(s):
        return s.replace("[link]", args.link) if args.link else s

    if args.thread:
        tweets = [drafts["C"]] + drafts["thread_tail"]
        if not drafts["C"]:
            print("ERROR: option C missing.", file=sys.stderr)
            sys.exit(1)
        tweets = [apply_link(t) for t in tweets]
        print(f"[plan] thread with {len(tweets)} tweets")
        for i, t in enumerate(tweets, 1):
            print(f"  {i}. ({len(t)} chars) {t[:75].replace(chr(10), ' / ')}")
    else:
        single = apply_link(drafts[args.option])
        if not single:
            print(f"ERROR: option {args.option} missing.", file=sys.stderr)
            sys.exit(1)
        print(f"[plan] single tweet option {args.option} ({len(single)} chars)")
        print("-" * 60)
        print(single)
        print("-" * 60)

    print(f"[plan] profile: {USER_DATA_DIR}")
    print()

    with sync_playwright() as pw:
        print("[launch] opening Chromium for X...", flush=True)
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
        )
        page = ctx.new_page()
        print(f"[nav] navigating to {COMPOSE_URL}", flush=True)
        page.goto(COMPOSE_URL, wait_until="domcontentloaded")

        print()
        print("=" * 70)
        print("  A Chromium window should have opened on your screen.")
        print("  IF YOU SEE A LOGIN PAGE: log into X now.")
        print(f"  Waiting up to {MAX_LOGIN_WAIT}s for compose to load.")
        print("=" * 70)
        print()

        if not wait_for_compose(page, MAX_LOGIN_WAIT):
            print(f"[fail] compose never loaded after {MAX_LOGIN_WAIT}s",
                  file=sys.stderr)
            ctx.close()
            sys.exit(2)

        print()
        print("[write] inserting tweet content...")
        try:
            if args.thread:
                insert_thread(page, tweets)
            else:
                insert_single(page, single)
        except Exception as e:
            print(f"[fail] insert error: {e}", file=sys.stderr)
            ctx.close()
            sys.exit(3)

        print("[write] done. browser stays open for manual review.")
        print()
        print("=" * 70)
        print("  TWEET IS COMPOSED. Review it in the browser window.")
        print("  Click the 'Post' button yourself when ready — or close to discard.")
        print(f"  Browser will auto-close in {POST_REVIEW_WAIT}s ({POST_REVIEW_WAIT // 60} min).")
        print("=" * 70)
        print()

        posted = wait_for_manual_post(page, POST_REVIEW_WAIT)
        if posted:
            print("[done] tweet appears to have been posted or dismissed.")
        else:
            print("[done] review window elapsed. Closing.")
        ctx.close()


if __name__ == "__main__":
    main()
