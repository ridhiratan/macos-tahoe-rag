#!/usr/bin/env python3
"""
Scraper for macOS Tahoe documentation from Apple's official pages.

Targets specific Apple pages about macOS Tahoe and saves content as text files
for use in RAG (Retrieval Augmented Generation).
"""

import os
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

# macOS Tahoe specific URLs to scrape
URLS = [
    # Main macOS page
    ("macos_main", "https://www.apple.com/macos/"),

    # Support articles
    ("whats_new_updates", "https://support.apple.com/en-us/122868"),
    ("how_to_upgrade", "https://support.apple.com/en-us/122727"),
    ("compatible_computers", "https://support.apple.com/en-us/122867"),
    ("enterprise_features", "https://support.apple.com/en-us/124963"),

    # Newsroom
    ("announcement", "https://www.apple.com/newsroom/2025/06/macos-tahoe-26-makes-the-mac-more-capable-productive-and-intelligent-than-ever/"),
    ("release_announcement", "https://www.apple.com/newsroom/2025/09/new-versions-of-apples-software-platforms-are-available-today/"),

    # Developer documentation
    ("release_notes", "https://developer.apple.com/documentation/macos-release-notes/macos-26-release-notes"),
    ("release_notes_26_2", "https://developer.apple.com/documentation/macos-release-notes/macos-26_2-release-notes"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

DOCS_DIR = Path(__file__).parent.parent / "docs"


def clean_text(text: str) -> str:
    """Clean extracted text by removing extra whitespace."""
    # Replace multiple newlines with double newline
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    # Strip lines
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines).strip()


def extract_content(soup: BeautifulSoup, url: str) -> str:
    """Extract main content from the page."""
    # Remove script, style, nav, footer elements
    for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        element.decompose()

    # Try to find main content area
    main_content = None

    # Different selectors for different Apple page types
    selectors = [
        'main',
        'article',
        '.main-content',
        '#main-content',
        '.article-content',
        '#content',
        '.gb-localnav-content',
        'div[role="main"]',
    ]

    for selector in selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break

    if not main_content:
        main_content = soup.body

    if main_content:
        text = main_content.get_text(separator='\n')
        return clean_text(text)

    return ""


def scrape_url(name: str, url: str) -> tuple[bool, str]:
    """Scrape a single URL and return (success, content/error)."""
    try:
        print(f"  Fetching: {url}")
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title = soup.title.string if soup.title else name

        # Extract content
        content = extract_content(soup, url)

        if not content:
            return False, "No content extracted"

        # Format document
        doc = f"""# {title}

Source: {url}
Scraped: {time.strftime('%Y-%m-%d %H:%M:%S')}

---

{content}
"""
        return True, doc

    except requests.RequestException as e:
        return False, f"Request error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Main scraper function."""
    print("macOS Tahoe Documentation Scraper")
    print("=" * 50)

    DOCS_DIR.mkdir(exist_ok=True)

    success_count = 0
    fail_count = 0

    for name, url in URLS:
        print(f"\n[{name}]")
        success, result = scrape_url(name, url)

        if success:
            # Save to file
            file_path = DOCS_DIR / f"{name}.txt"
            file_path.write_text(result, encoding='utf-8')
            print(f"  ✓ Saved to {file_path.name}")
            success_count += 1
        else:
            print(f"  ✗ Failed: {result}")
            fail_count += 1

        # Be polite - wait between requests
        time.sleep(1)

    print("\n" + "=" * 50)
    print(f"Done! Success: {success_count}, Failed: {fail_count}")
    print(f"Documents saved to: {DOCS_DIR}")


if __name__ == "__main__":
    main()
