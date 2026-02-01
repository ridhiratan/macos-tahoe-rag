"""Test WebBaseLoader on Apple release notes."""
from langchain_community.document_loaders import WebBaseLoader

# Test with the release notes URL
urls = [
    "https://developer.apple.com/documentation/macos-release-notes/macos-26-release-notes",
    "https://support.apple.com/en-us/122868",  # What's new (this worked before)
]

for url in urls:
    print(f"\n{'='*60}")
    print(f"URL: {url}")
    print('='*60)

    loader = WebBaseLoader(web_paths=[url])
    docs = loader.load()

    if docs:
        content = docs[0].page_content[:1000]  # First 1000 chars
        print(f"Content length: {len(docs[0].page_content)} chars")
        print(f"Preview:\n{content}...")
    else:
        print("No documents loaded")
