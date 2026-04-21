"""
MindSpace OS — Substack draft inserter via Playwright.

Opens Substack's post editor, fills title/subtitle/body, saves as DRAFT.
Leaves the final "Publish" click to the human for review.

Prerequisites:
    pip install playwright
    playwright install chromium

Usage:
    # First time: log in manually so the session cookie is saved
    python post_to_substack.py --login

    # Then: save a draft
    python post_to_substack.py --draft drafts/launch-post.md

Design notes:
    - Uses a PERSISTENT browser context (user-data-dir) so your Substack
      login survives between runs. Playwright reuses the cookie.
    - DOES NOT click Publish — only "Save draft". Review in browser first.
    - Substack's editor is a Slate.js rich-text field; we type into it
      rather than setting innerHTML (setting HTML silently fails).
    - Selectors are based on current Substack UI (April 2026). If they
      break, open the page and re-inspect.
"""

import argparse
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

SUBSTACK_PUB = "minyansh"
PUBLISH_URL = f"https://{SUBSTACK_PUB}.substack.com/publish/post?type=newsletter"
HOME_URL = f"https://{SUBSTACK_PUB}.substack.com/publish/home"
USER_DATA_DIR = Path.home() / ".playwright-substack-profile"


def parse_draft(md_path: Path):
    """Extract title, subtitle, and body from the launch-post.md file."""
    text = md_path.read_text()

    # Pull the Substack section
    m = re.search(r"## Substack Post(.*?)(?=^## )", text, re.DOTALL | re.MULTILINE)
    if not m:
        raise ValueError("No '## Substack Post' section found in draft file")
    section = m.group(1)

    title_m = re.search(r"### Title\s*\n(.+?)(?=\n###|\Z)", section, re.DOTALL)
    subtitle_m = re.search(r"### Subtitle\s*\n(.+?)(?=\n###|\Z)", section, re.DOTALL)
    body_m = re.search(r"### Body\s*\n(.+?)(?=\n##|\Z)", section, re.DOTALL)

    if not (title_m and body_m):
        raise ValueError("Missing Title or Body in draft file")

    return {
        "title": title_m.group(1).strip(),
        "subtitle": (subtitle_m.group(1).strip() if subtitle_m else ""),
        "body": body_m.group(1).strip(),
    }


def login_flow():
    """Open Substack login so the user authenticates once. Session persists."""
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
        )
        page = ctx.new_page()
        page.goto(HOME_URL)
        print("=" * 60)
        print("Log in to Substack in the browser window.")
        print("Navigate to your publication dashboard to confirm login.")
        print("Then press ENTER here to save the session and exit.")
        print("=" * 60)
        input()
        ctx.close()


def save_draft(draft: dict):
    """Insert the draft into Substack's editor and save (NOT publish)."""
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,  # keep visible so you can verify
        )
        page = ctx.new_page()
        page.goto(PUBLISH_URL, wait_until="domcontentloaded")

        # Detect login wall
        if "signin" in page.url or "sign-in" in page.url:
            print("ERROR: not logged in. Run with --login first.", file=sys.stderr)
            ctx.close()
            sys.exit(1)

        # Title field — Substack uses a contenteditable div with a placeholder.
        # Match by placeholder text or aria-label.
        print("Filling title...")
        title_sel = 'div[contenteditable="true"][data-placeholder="Title"], textarea[placeholder="Title"]'
        page.wait_for_selector(title_sel, timeout=15000)
        page.click(title_sel)
        page.keyboard.type(draft["title"], delay=10)

        # Subtitle
        if draft["subtitle"]:
            print("Filling subtitle...")
            subtitle_sel = 'div[contenteditable="true"][data-placeholder*="subtitle" i], textarea[placeholder*="subtitle" i]'
            try:
                page.click(subtitle_sel, timeout=5000)
                page.keyboard.type(draft["subtitle"], delay=10)
            except PWTimeout:
                print("  (subtitle field not found, skipping)")

        # Body — click into the editor area and type. Substack's editor strips
        # most pasted HTML, so we type line-by-line and use Enter for paragraphs.
        print("Filling body...")
        body_sel = 'div[contenteditable="true"][data-placeholder*="story" i], div.tiptap[contenteditable="true"]'
        page.click(body_sel)

        for para in draft["body"].split("\n\n"):
            para = para.strip()
            if not para:
                continue
            page.keyboard.type(para, delay=5)
            page.keyboard.press("Enter")
            page.keyboard.press("Enter")

        # Substack autosaves; give it a beat.
        page.wait_for_timeout(2000)

        print("=" * 60)
        print("Draft inserted. Review in the browser.")
        print("When ready, click 'Continue' > 'Send' to publish manually.")
        print("Press ENTER here to close the browser.")
        print("=" * 60)
        input()
        ctx.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--login", action="store_true", help="Log in once; session persists")
    ap.add_argument("--draft", type=Path, default=Path("drafts/launch-post.md"))
    args = ap.parse_args()

    if args.login:
        login_flow()
        return

    if not args.draft.exists():
        print(f"ERROR: draft file not found: {args.draft}", file=sys.stderr)
        sys.exit(1)

    draft = parse_draft(args.draft)
    print(f"Title:    {draft['title']}")
    print(f"Subtitle: {draft['subtitle'][:60]}{'...' if len(draft['subtitle']) > 60 else ''}")
    print(f"Body:     {len(draft['body'])} chars")
    print()

    save_draft(draft)


if __name__ == "__main__":
    main()
