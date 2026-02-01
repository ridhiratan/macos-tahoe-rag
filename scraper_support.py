#!/usr/bin/env python3
"""
Scraper for additional Apple Support articles using Playwright.
"""

import asyncio
import re
import time
from pathlib import Path
from playwright.async_api import async_playwright

# Additional Apple Support URLs for troubleshooting and how-to content
URLS = [
    # What's new in Tahoe (detailed guide)
    ("whats_new_tahoe_guide", "https://support.apple.com/guide/mac-help/whats-new-in-macos-tahoe-apd07d671600/mac"),

    # Troubleshooting
    ("startup_issues", "https://support.apple.com/en-us/123922"),
    ("diagnose_problems", "https://support.apple.com/guide/mac-help/diagnose-problems-mh35727/mac"),

    # System Settings
    ("system_settings", "https://support.apple.com/guide/mac-help/change-system-settings-mh15217/mac"),

    # Battery
    ("battery_drain_fix", "https://support.apple.com/guide/mac-help/if-your-battery-runs-out-of-charge-quickly-mh27540/mac"),
    ("battery_settings", "https://support.apple.com/guide/mac-help/change-battery-settings-mchlfc3b7879/mac"),
    ("battery_condition", "https://support.apple.com/guide/mac-help/check-the-condition-of-your-computers-battery-mh20865/mac"),
    ("battery_not_charging", "https://support.apple.com/guide/mac-help/if-your-battery-status-is-not-charging-mh20876/mac"),

    # Security
    ("security_content", "https://support.apple.com/en-us/125110"),

    # Performance & Storage
    ("storage_mac", "https://support.apple.com/guide/mac-help/free-up-storage-space-on-your-mac-mchl43d7b4e0/mac"),
    ("slow_mac", "https://support.apple.com/guide/mac-help/if-your-mac-runs-slowly-mh27606/mac"),

    # Wi-Fi & Connectivity
    ("wifi_issues", "https://support.apple.com/guide/mac-help/if-your-mac-doesnt-connect-to-the-internet-mchlp1498/mac"),

    # Updates
    ("software_update", "https://support.apple.com/guide/mac-help/get-macos-updates-mchlpx1065/mac"),

    # Backup
    ("time_machine", "https://support.apple.com/guide/mac-help/back-up-your-mac-with-time-machine-mh35860/mac"),
]

DOCS_DIR = Path(__file__).parent / "docs"


def clean_text(text: str) -> str:
    """Clean extracted text."""
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines).strip()


async def scrape_page(name: str, url: str) -> tuple[bool, str]:
    """Scrape a page using Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print(f"  Loading: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(2000)

            title = await page.title()

            # Try different selectors
            content = ""
            selectors = [
                "main",
                "article",
                ".main-content",
                "#main-content",
                ".article-content",
                "#content",
                "[role='main']",
            ]

            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        content = await element.inner_text()
                        if len(content) > 200:
                            break
                except:
                    continue

            if not content or len(content) < 200:
                content = await page.inner_text("body")

            await browser.close()

            if not content or len(content) < 100:
                return False, "No meaningful content extracted"

            content = clean_text(content)

            doc = f"""# {title}

Source: {url}
Scraped: {time.strftime('%Y-%m-%d %H:%M:%S')}
Type: Apple Support Article

---

{content}
"""
            return True, doc

        except Exception as e:
            await browser.close()
            return False, f"Error: {e}"


async def main():
    """Main scraper function."""
    print("Apple Support Articles Scraper")
    print("=" * 50)

    DOCS_DIR.mkdir(exist_ok=True)

    success_count = 0
    fail_count = 0

    for name, url in URLS:
        print(f"\n[{name}]")
        success, result = await scrape_page(name, url)

        if success:
            file_path = DOCS_DIR / f"{name}.txt"
            file_path.write_text(result, encoding='utf-8')
            print(f"  ✓ Saved to {file_path.name} ({len(result)} chars)")
            success_count += 1
        else:
            print(f"  ✗ Failed: {result}")
            fail_count += 1

        await asyncio.sleep(1)

    print("\n" + "=" * 50)
    print(f"Done! Success: {success_count}, Failed: {fail_count}")
    print(f"\nTotal docs in folder: {len(list(DOCS_DIR.glob('*.txt')))}")


if __name__ == "__main__":
    asyncio.run(main())
