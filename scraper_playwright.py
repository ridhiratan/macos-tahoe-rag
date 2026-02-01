#!/usr/bin/env python3
"""
Playwright-based scraper for JS-rendered Apple Developer documentation.
"""

import asyncio
import re
import time
from pathlib import Path
from playwright.async_api import async_playwright

# JS-rendered Apple Developer documentation URLs
URLS = [
    ("release_notes_26", "https://developer.apple.com/documentation/macos-release-notes/macos-26-release-notes"),
    ("release_notes_26_1", "https://developer.apple.com/documentation/macos-release-notes/macos-26_1-release-notes"),
    ("release_notes_26_2", "https://developer.apple.com/documentation/macos-release-notes/macos-26_2-release-notes"),
    ("whats_new_macos26", "https://developer.apple.com/documentation/macos-release-notes/macos-26-release-notes#Whats-New"),
]

DOCS_DIR = Path(__file__).parent / "docs"


def clean_text(text: str) -> str:
    """Clean extracted text."""
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines).strip()


async def scrape_with_playwright(name: str, url: str) -> tuple[bool, str]:
    """Scrape a JS-rendered page using Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print(f"  Loading: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # Wait for content to render
            await page.wait_for_timeout(2000)

            # Get title
            title = await page.title()

            # Try to get main content
            content = ""

            # Try different selectors for Apple Developer docs
            selectors = [
                "main",
                ".documentation-content",
                "#main-content",
                "article",
                "[role='main']",
            ]

            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        content = await element.inner_text()
                        if len(content) > 200:  # Got meaningful content
                            break
                except:
                    continue

            # Fallback to body
            if not content or len(content) < 200:
                content = await page.inner_text("body")

            await browser.close()

            if not content or len(content) < 100:
                return False, "No meaningful content extracted"

            content = clean_text(content)

            doc = f"""# {title}

Source: {url}
Scraped: {time.strftime('%Y-%m-%d %H:%M:%S')}
Method: Playwright (JS-rendered)

---

{content}
"""
            return True, doc

        except Exception as e:
            await browser.close()
            return False, f"Error: {e}"


async def main():
    """Main scraper function."""
    print("Apple Developer Docs Scraper (Playwright)")
    print("=" * 50)

    DOCS_DIR.mkdir(exist_ok=True)

    success_count = 0
    fail_count = 0

    for name, url in URLS:
        print(f"\n[{name}]")
        success, result = await scrape_with_playwright(name, url)

        if success:
            file_path = DOCS_DIR / f"{name}.txt"
            file_path.write_text(result, encoding='utf-8')
            print(f"  ✓ Saved to {file_path.name} ({len(result)} chars)")
            success_count += 1
        else:
            print(f"  ✗ Failed: {result}")
            fail_count += 1

    print("\n" + "=" * 50)
    print(f"Done! Success: {success_count}, Failed: {fail_count}")


if __name__ == "__main__":
    asyncio.run(main())
