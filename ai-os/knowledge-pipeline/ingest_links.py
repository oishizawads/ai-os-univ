import os
import requests
from bs4 import BeautifulSoup
import yaml
from pathlib import Path

# Placeholder for LLM integration
def summarize_with_llm(content, url):
    # In a real scenario, this would call /gemini-coder or /codex-coder or an API
    # For now, we create a structured template
    return f"""---
title: "Summary of {url}"
source: "{url}"
type: "raw_ingested"
---

## Raw Content Snippet
{content[:1000]}...

## TODO
- [ ] Principle extraction
- [ ] Playbook conversion
"""

def ingest_url(url, output_dir):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Simple extraction: title and text
        title = soup.title.string if soup.title else url
        text = soup.get_text(separator='\n')
        
        summary = summarize_with_llm(text, url)
        
        # Save to raw/ in obsidian-vault (relative path for now)
        filename = "".join(x for x in title if x.isalnum())[:50] + ".md"
        filepath = Path(output_dir) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        print(f"Ingested: {url} -> {filepath}")
    except Exception as e:
        print(f"Failed to ingest {url}: {e}")

if __name__ == "__main__":
    # Example usage
    links = [
        "https://github.com/Abruptive/Ankh.md",
        "https://github.com/google-research/timesfm"
    ]
    vault_raw = "ai-os/obsidian-vault/raw"
    for link in links:
        ingest_url(link, vault_raw)
