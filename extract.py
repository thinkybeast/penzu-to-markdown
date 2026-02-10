#!/usr/bin/env python3
"""Extract Penzu journal entries from PDF to Obsidian markdown files."""

import re
from pathlib import Path
from pypdf import PdfReader


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def parse_date(date_str: str) -> str:
    """Convert M/D/YYYY to YYYY-MM-DD."""
    month, day, year = date_str.split('/')
    return f"{year}-{int(month):02d}-{int(day):02d}"


def dedupe_lines(text: str) -> str:
    """Remove consecutive duplicate lines (PDF extraction artifact)."""
    lines = text.split('\n')
    deduped = []
    prev = None
    for line in lines:
        if line != prev:
            deduped.append(line)
            prev = line
    return '\n'.join(deduped)


def extract_entries(pdf_path: str) -> list[dict]:
    """Extract all journal entries from PDF."""
    reader = PdfReader(pdf_path)

    # Concatenate all pages
    full_text = ""
    for page in reader.pages:
        text = page.extract_text() or ""
        full_text += text + "\n"

    # Remove duplicate lines from PDF extraction
    full_text = dedupe_lines(full_text)

    # Pattern: Title + "by Max Hawkins" + Day. M/D/YYYY
    pattern = r'(.+?)\s+by Max Hawkins\s+(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\.\s+(\d{1,2}/\d{1,2}/\d{4})'

    # Find all matches with positions
    matches = list(re.finditer(pattern, full_text))

    entries = []
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        date_str = match.group(3)

        # Dedupe title if repeated
        words = title.split()
        if len(words) >= 2:
            mid = len(words) // 2
            first_half = ' '.join(words[:mid])
            second_half = ' '.join(words[mid:])
            if first_half == second_half:
                title = first_half

        # Get content: from end of this match to start of next (or end of text)
        content_start = match.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        content = full_text[content_start:content_end].strip()

        entries.append({
            'title': title,
            'date': parse_date(date_str),
            'content': content
        })

    return entries


def write_markdown(entries: list[dict], output_dir: Path):
    """Write entries to markdown files."""
    output_dir.mkdir(exist_ok=True)

    # Track dates for handling duplicates
    date_counts = {}

    for entry in entries:
        date = entry['date']
        slug = slugify(entry['title'])[:50]  # Limit slug length

        # Handle duplicate dates
        if date in date_counts:
            date_counts[date] += 1
            filename = f"{date}-{slug}-{date_counts[date]}.md"
        else:
            date_counts[date] = 0
            filename = f"{date}-{slug}.md"

        filepath = output_dir / filename

        content = f"""---
date: {date}
---

# {entry['title']}

{entry['content']}
"""
        filepath.write_text(content)
        print(f"Wrote: {filename}")


def main():
    pdf_path = Path("data/Penzu_Export_1770755734_Feb2026.pdf")
    output_dir = Path("posts")

    print(f"Extracting from: {pdf_path}")
    entries = extract_entries(str(pdf_path))
    print(f"Found {len(entries)} entries")

    write_markdown(entries, output_dir)
    print(f"Done! Files written to {output_dir}/")


if __name__ == "__main__":
    main()
