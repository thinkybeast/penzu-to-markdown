# Penzu to Obsidian

Extracts journal entries from a Penzu PDF export into individual Markdown files for Obsidian.

## Usage

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Place your Penzu PDF export in data/
# Update the filename in extract.py if needed

# Run
python extract.py
```

Output goes to `posts/` as individual `.md` files.

## Output Format

Each entry becomes a file like `2021-06-05-im-an-angelino-now.md`:

```markdown
---
date: 2021-06-05
---

# i'm an angelino now

[journal content]
```

## How It Works

1. Extracts text from all PDF pages
2. Finds entries using pattern: `Title` + `by [Author]` + `Day. M/D/YYYY`
3. Deduplicates lines (PDF extraction artifact)
4. Writes each entry to `posts/YYYY-MM-DD-slugified-title.md`

## Requirements

- Python 3.10+
- pypdf
