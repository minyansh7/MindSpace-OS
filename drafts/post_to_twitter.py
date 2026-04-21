"""
MindSpace OS — Twitter/X poster via Playwright (no API, no fees).

Same pattern as post_to_substack.py:
    - Persistent browser profile → log in once, session reused
    - Drives x.com's UI directly → bypasses the paid API entirely
    - Parses drafts/launch-post.md so copy lives in one place

Prerequisites:
    pip install playwright
    playwright install chromium

Usage:
    # First time only — log into X in the opened browser, then Enter
    python post_to_twitter.py --login

    # Post a single tweet (default: option A)
    python post_to_twitter.py
    python post_to_twitter.py --option B
    python post_to_twitter.py --option C

    # Post the full thread (option C opener + follow-ups)
    python post_to_twitter.py --thread

    # Dry-run: fill the box but STOP before clicking Post
    python post_to_twitter.py --review

Design notes:
    - Auto-clicks "Post" by default. Use --review for a safety pause.
    - Thread mode uses x.com's "Add" button to chain tweets in a single
      compose session — posts atomically when you click Post All.
    - 280-char guard: refuses to send tweets over the limit.
    - Selectors are x.com circa April 2026. Fallbacks included; if they
      break, open DevTools on /compose/post and update TWEET_TEXTAREA.
"""

import argparse
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

COMPOSE_URL = "https://x.com/compose/post"
HOME_URL = "https://x.com/home"
USER_DATA_DIR = Path.home() / ".playwright-twitter-profile"
TWEET_LIMIT = 280

# x.com selectors (as of April 2026). These are the stable test-ids.
TWEET_TEXTAREA = 'div[data-testid^="tweetTextarea_"][contenteditable="true"]'
POST_BUTTON = 'button[data-testid="tweetButton"], button[data-testid="tweetButtonInline"]'
ADD_TO_THREAD = 'button[data-testid="addButton"]'


# ---------- draft parsing ----------

def _extract_code_block(text: str) -> str:
    """Given a chunk containing a ``` fenced block, return the block contents."""
    m = re.search(r"```[^\n]*\n(.*?)\n```", text, re.DOTALL)
    return m.group(1).strip() if m else ""


def parse_drafts(md_path: Path):
    """Pull options A/B/C and thread follow-ups from launch-post.md."""
    text = md_path.read_text()

    # Everything under "## Twitter / X Posts"
    m = re.search(r"## Twitter / X Posts(.*)", text, re.DOTALL)
    if not m:
        raise ValueError("No '## Twitter / X Posts' section in draft file")
    twitter_section = m.group(1)

    def grab_option(letter: str) -> str:
        pattern = rf"### Option {letter}[^\n]*\n(.*?)(?=\n### |\Z)"
        mm = re.search(pattern, twitter_section, re.DOTALL)
        if not mm:
            return ""
        return _extract_code_block(mm.group(1))

    # Thread follow-ups: all code blocks under "Follow-up tweets"
    thread_tail = []
    follow = re.search(
        r"\*\*Follow-up tweets[^*]*\*\*(.*)", twitter_section, re.DOTALL
    )
    if follow:
        for block in re.findall(r"```[^\n]*\n(.*?)\n```", follow.group(1), re.DOTALL):
            t = block.strip()
            if t:
                thread_tail.append(t)

    return {
        "A": grab_option("A"),
        "B": grab_option("B"),
        "C": grab_option("C"),
        "thread_tail": thread_tail,
    }


# ---------- playwright flows ----------

def login_flow():
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
        )
        page = ctx.new_page()
        page.goto(HOME_URL)
        print("=" * 60)
        print("Log into X in the browser window.")
        print("Once you see your home timeline, press ENTER here.")
        print("=" * 60)
        input()
        ctx.close()


def _type_into_compose(page, text: str):
    """Click the compose area and type. Preserves newlines via Shift+Enter."""
    page.click(TWEET_TEXTAREA)
    # Split on newlines so blank lines become actual line breaks in the tweet.
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line:
            page.keyboard.type(line, delay=8)
        if i < len(lines) - 1:
            # Shift+Enter = newline within the same tweet (Enter would submit)
            page.keyboard.press("Shift+Enter")


def _check_length(text: str, label: str = "tweet"):
    # X counts URLs as 23 chars regardless of actual length; our drafts use
    # placeholder "[link]" so this is a conservative check.
    if len(text) > TWEET_LIMIT:
        print(
            f"ERROR: {label} is {len(text)} chars (limit {TWEET_LIMIT}). "
            f"Trim the draft in launch-post.md.",
            file=sys.stderr,
        )
        sys.exit(1)


def post_single(text: str, review: bool):
    _check_length(text)

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
        )
        page = ctx.new_page()
        page.goto(COMPOSE_URL, wait_until="domcontentloaded")

        if "login" in page.url or "i/flow/login" in page.url:
            print("ERROR: not logged in. Run with --login first.", file=sys.stderr)
            ctx.close()
            sys.exit(1)

        page.wait_for_selector(TWEET_TEXTAREA, timeout=15000)
        _type_into_compose(page, text)
        page.wait_for_timeout(500)

        if review:
            print("=" * 60)
            print("Tweet composed. REVIEW MODE — not clicking Post.")
            print("Click Post manually in the browser, or close to discard.")
            print("Press ENTER to close this script.")
            print("=" * 60)
            input()
            ctx.close()
            return

        print("Clicking Post...")
        page.click(POST_BUTTON)
        # Wait for navigation away from compose OR for the dialog to close.
        try:
            page.wait_for_url(lambda u: "compose/post" not in u, timeout=10000)
        except PWTimeout:
            pass
        page.wait_for_timeout(1500)
        print("Posted.")
        ctx.close()


def post_thread(tweets: list[str], review: bool):
    if not tweets:
        print("ERROR: no tweets to post.", file=sys.stderr)
        sys.exit(1)
    for i, t in enumerate(tweets):
        _check_length(t, f"tweet {i + 1}")

    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
        )
        page = ctx.new_page()
        page.goto(COMPOSE_URL, wait_until="domcontentloaded")

        if "login" in page.url or "i/flow/login" in page.url:
            print("ERROR: not logged in. Run with --login first.", file=sys.stderr)
            ctx.close()
            sys.exit(1)

        page.wait_for_selector(TWEET_TEXTAREA, timeout=15000)

        for i, tweet in enumerate(tweets):
            if i > 0:
                # Click + to add another tweet to the thread
                page.click(ADD_TO_THREAD)
                page.wait_for_timeout(400)
                # Focus the newly-created textarea (it becomes the Nth one)
                textareas = page.locator(TWEET_TEXTAREA)
                textareas.nth(i).click()
            else:
                page.click(TWEET_TEXTAREA)
            _type_into_compose_at_focus(page, tweet)

        page.wait_for_timeout(800)

        if review:
            print("=" * 60)
            print(f"Thread of {len(tweets)} tweets composed. REVIEW MODE.")
            print("Click 'Post all' manually, or close to discard.")
            print("Press ENTER to close this script.")
            print("=" * 60)
            input()
            ctx.close()
            return

        print(f"Posting thread ({len(tweets)} tweets)...")
        page.click(POST_BUTTON)
        try:
            page.wait_for_url(lambda u: "compose/post" not in u, timeout=15000)
        except PWTimeout:
            pass
        page.wait_for_timeout(1500)
        print("Thread posted.")
        ctx.close()


def _type_into_compose_at_focus(page, text: str):
    """Type into whatever textarea currently has focus (for thread mode)."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line:
            page.keyboard.type(line, delay=8)
        if i < len(lines) - 1:
            page.keyboard.press("Shift+Enter")


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", action="store_true", help="Log in once; session persists")
    ap.add_argument("--draft", type=Path, default=Path("drafts/launch-post.md"))
    ap.add_argument("--option", choices=["A", "B", "C"], default="A",
                    help="Which single-tweet option to post (default A)")
    ap.add_argument("--thread", action="store_true",
                    help="Post the full thread (option C + follow-ups)")
    ap.add_argument("--review", action="store_true",
                    help="Fill the compose box but do NOT click Post")
    ap.add_argument("--link", type=str, default=None,
                    help="Replace all '[link]' placeholders with this URL before posting")
    args = ap.parse_args()

    if args.login:
        login_flow()
        return

    if not args.draft.exists():
        print(f"ERROR: draft file not found: {args.draft}", file=sys.stderr)
        sys.exit(1)

    drafts = parse_drafts(args.draft)

    def apply_link(s: str) -> str:
        return s.replace("[link]", args.link) if args.link else s

    if args.thread:
        tweets = [drafts["C"]] + drafts["thread_tail"]
        if not drafts["C"]:
            print("ERROR: option C (thread opener) not found in draft file.", file=sys.stderr)
            sys.exit(1)
        tweets = [apply_link(t) for t in tweets]
        print(f"Thread: {len(tweets)} tweets")
        for i, t in enumerate(tweets, 1):
            preview = t.replace("\n", " ")[:80]
            print(f"  {i}. ({len(t)} chars) {preview}{'...' if len(t) > 80 else ''}")
        print()
        post_thread(tweets, review=args.review)
    else:
        text = apply_link(drafts[args.option])
        if not text:
            print(f"ERROR: option {args.option} not found in draft file.", file=sys.stderr)
            sys.exit(1)
        print(f"Option {args.option} ({len(text)} chars):")
        print("-" * 60)
        print(text)
        print("-" * 60)
        print()
        post_single(text, review=args.review)


if __name__ == "__main__":
    main()
