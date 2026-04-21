"""
Autonomous Substack drafter — polls for login, inserts draft, exits.

Usage:
    python3 drafts/post_substack_auto.py

Behavior:
    1. Opens Chromium to the Substack publish URL.
    2. If the page redirects to signin, polls every 3s for up to 240s
       for the user to complete login in the visible browser window.
    3. Once the publish editor is detected, types title/subtitle/body
       from drafts/launch-post.md.
    4. Waits for Substack's autosave (3s).
    5. Closes browser. Draft persists in the user's Substack account.

Unlike post_to_substack.py, this has NO input() pauses — safe for
non-interactive execution (e.g. invoked from an agent).
"""

import re
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

SLUG = "minyansh"
PROFILE = Path.home() / ".playwright-profiles" / f"substack-{SLUG}"
PUBLISH_URL = f"https://{SLUG}.substack.com/publish/post?type=newsletter"
MAX_LOGIN_WAIT = 240  # seconds

TITLE_SEL = 'div[contenteditable="true"][data-placeholder="Title"], textarea[placeholder="Title"]'
SUBTITLE_SEL = 'div[contenteditable="true"][data-placeholder*="subtitle" i], textarea[placeholder*="subtitle" i]'
BODY_SEL = 'div[contenteditable="true"][data-placeholder*="story" i], div.tiptap[contenteditable="true"]'


def parse_draft(md_path: Path):
    text = md_path.read_text()
    m = re.search(r"## Substack Post(.*?)(?=^## |\Z)", text, re.DOTALL | re.MULTILINE)
    if not m:
        raise ValueError("No '## Substack Post' section in draft")
    section = m.group(1)

    title = re.search(r"### Title\s*\n(.+?)(?=\n###|\Z)", section, re.DOTALL)
    subtitle = re.search(r"### Subtitle\s*\n(.+?)(?=\n###|\Z)", section, re.DOTALL)
    body = re.search(r"### Body\s*\n(.+?)(?=\n##|\Z)", section, re.DOTALL)

    if not title or not body:
        raise ValueError("Missing Title or Body")

    return {
        "title": title.group(1).strip(),
        "subtitle": subtitle.group(1).strip() if subtitle else "",
        "body": body.group(1).strip(),
    }


def wait_for_editor(page, max_wait: int) -> bool:
    """
    Poll for the publish editor to become visible. CRITICAL: we do NOT
    re-navigate during polling — re-navigation kicks the user out of the
    login form mid-entry (the "flashing" bug). We simply wait.

    After login, Substack auto-redirects back to /publish/post and the
    Title field appears.
    """
    start = time.time()
    last_url = None
    while time.time() - start < max_wait:
        elapsed = int(time.time() - start)

        # Probe for the title field without re-navigating
        try:
            if page.locator(TITLE_SEL).first.is_visible(timeout=1000):
                print(f"  [auth] {elapsed}s  editor ready ✓", flush=True)
                return True
        except Exception:
            pass

        try:
            url = page.url
            if url != last_url:
                print(f"  [auth] {elapsed}s  url now: {url[:100]}", flush=True)
                last_url = url
            elif elapsed % 30 == 0:
                print(f"  [auth] {elapsed}s  still on: {url[:100]}", flush=True)
        except Exception as e:
            print(f"  [auth] {elapsed}s  page inaccessible: {e}", flush=True)
            return False

        time.sleep(3)
    return False


def insert_draft(page, draft: dict):
    print("  [write] clicking title field...", flush=True)
    page.click(TITLE_SEL)
    page.keyboard.type(draft["title"], delay=8)
    print(f"  [write] title typed ({len(draft['title'])} chars)", flush=True)

    if draft["subtitle"]:
        try:
            page.click(SUBTITLE_SEL, timeout=5000)
            page.keyboard.type(draft["subtitle"], delay=8)
            print(f"  [write] subtitle typed ({len(draft['subtitle'])} chars)", flush=True)
        except PWTimeout:
            print("  [write] subtitle field not found, skipping", flush=True)

    print("  [write] clicking body field...", flush=True)
    page.click(BODY_SEL)
    paragraphs = [p.strip() for p in draft["body"].split("\n\n") if p.strip()]
    for i, para in enumerate(paragraphs, 1):
        page.keyboard.type(para, delay=3)
        page.keyboard.press("Enter")
        page.keyboard.press("Enter")
        print(f"  [write] para {i}/{len(paragraphs)} ({len(para)} chars)", flush=True)


def main():
    draft_path = Path("drafts/launch-post.md")
    if not draft_path.exists():
        print(f"ERROR: {draft_path} not found", file=sys.stderr)
        sys.exit(1)

    draft = parse_draft(draft_path)
    print(f"[plan] title:    {draft['title']}")
    print(f"[plan] subtitle: {draft['subtitle'][:70]}")
    print(f"[plan] body:     {len(draft['body'])} chars")
    print(f"[plan] profile:  {PROFILE}")
    print()

    with sync_playwright() as pw:
        print("[launch] opening Chromium with persistent profile...", flush=True)
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            headless=False,
        )
        page = ctx.new_page()
        print(f"[nav] navigating to {PUBLISH_URL}", flush=True)
        page.goto(PUBLISH_URL, wait_until="domcontentloaded")

        print()
        print("=" * 70)
        print("  A browser window should have opened on your screen.")
        print("  IF YOU SEE A LOGIN PAGE: log into Substack now.")
        print(f"  I will wait up to {MAX_LOGIN_WAIT}s for the editor to load.")
        print("=" * 70)
        print()

        if not wait_for_editor(page, MAX_LOGIN_WAIT):
            print(f"[fail] editor never loaded after {MAX_LOGIN_WAIT}s", file=sys.stderr)
            ctx.close()
            sys.exit(2)

        try:
            insert_draft(page, draft)
        except Exception as e:
            print(f"[fail] insert error: {e}", file=sys.stderr)
            ctx.close()
            sys.exit(3)

        print("[wait] letting Substack autosave...", flush=True)
        page.wait_for_timeout(4000)

        # Verify by reading the title back
        try:
            title_elem = page.query_selector(TITLE_SEL)
            if title_elem:
                current_title = title_elem.inner_text()
                print(f"[verify] title on page: {current_title[:80]}", flush=True)
        except Exception:
            pass

        print("[done] draft inserted. Closing browser.")
        print(f"[done] check your drafts: https://{SLUG}.substack.com/publish/posts?type=drafts")
        ctx.close()


if __name__ == "__main__":
    main()
