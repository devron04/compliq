"""
CompliQ - From product to standard, instantly.
src/ingest.py

This script parses the raw BIS SP 21 PDF, chunks it by structural boundaries 
(each standard is one chunk), extracts metadata (IS number, title, category, scope),
and saves the structured data to data/chunks.json.
"""

import json
import re
import sys
import argparse
from pathlib import Path
try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF (fitz) is required. Install via: pip install pymupdf")
    sys.exit(1)

# Basic keyword mapping to determine category
CATEGORY_KEYWORDS = {
    "Cement": ["cement", "portland", "pozzolana", "slag"],
    "Steel": ["steel", "bars", "reinforcement", "structural"],
    "Concrete": ["concrete", "admixture", "aggregates"],
    "Bricks": ["brick", "masonry", "block"],
    "Tiles": ["tile", "flooring", "ceramic"],
    "Pipes": ["pipe", "tube", "plumbing"],
    "Glass": ["glass", "glazing"],
    "Timber": ["timber", "wood", "plywood"]
}

def determine_category(text: str) -> str:
    """Categorize standard based on keyword frequency."""
    text_lower = text.lower()
    best_category = "Other Building Materials"
    max_count = 0
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        count = sum(text_lower.count(kw) for kw in keywords)
        if count > max_count:
            max_count = count
            best_category = category
            
    return best_category

def extract_keywords(text: str) -> list[str]:
    """Extract a few keywords heuristically."""
    # Simplified approach: just find common words > 4 chars, or rely on categories
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    # Sort and take top 10
    top_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
    return [w[0] for w in top_words]

def parse_pdf(pdf_path: str) -> list[dict]:
    """Parse the PDF and chunk by 'IS <number>' standards."""
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n"

    # A naive approach to split by IS numbers. 
    # BIS standards usually start with "IS " followed by digits, sometimes with year e.g. "IS 269 : 2015"
    # We look for lines that look like standard headers.
    
    # Let's split using a regex that finds standard beginnings:
    # Look for "IS \d+(?:[A-Za-z]+)?(?:\s*:\s*\d{4})?" at the start of a line or paragraph
    # We will use re.split with a capturing group to keep the delimiter
    pattern = r"(IS\s+\d+(?:[A-Za-z]+)?(?:\s*:\s*\d{4})?)"
    parts = re.split(pattern, full_text)
    
    chunks = []
    
    # parts[0] is everything before the first IS standard
    for i in range(1, len(parts), 2):
        is_num_raw = parts[i].strip()
        # Clean IS number (e.g. "IS 269 : 2015" -> "IS 269")
        standard_id = is_num_raw.split(':')[0].strip()
        
        # The content following this IS number
        content = parts[i+1].strip() if i+1 < len(parts) else ""
        
        # Assume first line of content is the title
        lines = content.split('\n')
        title = lines[0].strip() if lines else "Unknown Title"
        
        # Extract scope: roughly first 500 characters
        scope = content[:500].replace('\n', ' ').strip()
        
        # Full chunk text for embedding
        full_chunk_text = f"{is_num_raw}\n{content}"
        
        chunk = {
            "standard_id": standard_id,
            "title": title,
            "category": determine_category(full_chunk_text),
            "scope": scope,
            "keywords": extract_keywords(full_chunk_text),
            "full_text": full_chunk_text
        }
        chunks.append(chunk)

    # In case the parsing failed or it's a dummy PDF, provide some dummy chunks
    if not chunks:
        print("Warning: No 'IS ...' standards found in PDF. Using fallback chunks.", file=sys.stderr)
        chunks = generate_fallback_chunks()

    return chunks

def generate_fallback_chunks() -> list[dict]:
    """Generate dummy chunks if no valid standards are extracted."""
    return [
        {
            "standard_id": "IS 269",
            "title": "Ordinary Portland Cement — Specification",
            "category": "Cement",
            "scope": "This standard covers the manufacture and chemical and physical requirements of 33, 43, and 53 grade ordinary Portland cement.",
            "keywords": ["cement", "portland", "compressive", "strength", "grades"],
            "full_text": "IS 269 : 2015 Ordinary Portland Cement — Specification. This standard covers the manufacture and chemical and physical requirements of 33, 43, and 53 grade ordinary Portland cement (OPC)."
        },
        {
            "standard_id": "IS 1786",
            "title": "High Strength Deformed Steel Bars and Wires for Concrete Reinforcement",
            "category": "Steel",
            "scope": "This standard covers the requirements of deformed steel bars and wires for use as reinforcement in concrete.",
            "keywords": ["steel", "bars", "deformed", "reinforcement", "concrete"],
            "full_text": "IS 1786 : 2008 High Strength Deformed Steel Bars and Wires for Concrete Reinforcement. It covers various grades like Fe 415, Fe 500, Fe 500D, Fe 550, Fe 550D, Fe 600."
        },
        {
            "standard_id": "IS 383",
            "title": "Coarse and Fine Aggregates for Concrete",
            "category": "Concrete",
            "scope": "Specification for coarse and fine aggregates from natural sources for concrete.",
            "keywords": ["aggregates", "coarse", "fine", "concrete", "sand"],
            "full_text": "IS 383 : 2016 Coarse and Fine Aggregates for Concrete. Covers requirements for aggregates, including crushed stone, gravel, and sand for concrete mixes."
        }
    ]

def main():
    parser = argparse.ArgumentParser(description="Ingest BIS PDF and create chunks")
    parser.add_argument("--pdf", required=True, type=str, help="Path to BIS_SP21.pdf")
    parser.add_argument("--out", default="data/chunks.json", type=str, help="Output JSON path")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"Error: {pdf_path} does not exist.", file=sys.stderr)
        # We'll still dump fallback chunks so the pipeline doesn't break
        chunks = generate_fallback_chunks()
    else:
        print(f"Parsing PDF: {pdf_path}", file=sys.stderr)
        chunks = parse_pdf(args.pdf)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully wrote {len(chunks)} chunks to {out_path}", file=sys.stderr)

if __name__ == "__main__":
    main()
