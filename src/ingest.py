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

    # Split by IS standard headers. BIS SP 21 format:
    # "IS 269 : 1989", "IS 2185 (Part 2) : 1983", etc.
    # We capture the full standard ID including optional Part and year.
    pattern = r"(IS\s+\d+(?:\s*\(Part\s*\d+\))?(?:\s*:\s*\d{4})?)"
    parts = re.split(pattern, full_text)
    
    chunks = []
    
    # parts[0] is everything before the first IS standard
    for i in range(1, len(parts), 2):
        is_num_raw = parts[i].strip()
        # Normalize spacing in standard_id: "IS 269 : 1989" -> "IS 269: 1989"
        # Keep the year — it's part of the real IS number format
        standard_id = re.sub(r'\s*:\s*', ': ', is_num_raw).strip()
        standard_id = re.sub(r'\s+', ' ', standard_id)  # collapse extra spaces
        
        # The content following this IS number
        content = parts[i+1].strip() if i+1 < len(parts) else ""
        
        # Assume first line of content is the title
        lines = content.split('\n')
        title = lines[0].strip() if lines else "Unknown Title"
        
        # Extract scope: roughly first 500 characters
        scope = content[:500].replace('\n', ' ').strip()
        
        # Full chunk text for embedding
        full_chunk_text = f"{standard_id}\n{content}"
        
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
    """Fallback chunks matching real BIS SP 21 IS number format (with year)."""
    return [
        {
            "standard_id": "IS 269: 1989",
            "title": "Specification for Ordinary Portland Cement, 33 Grade",
            "category": "Cement",
            "scope": "This standard covers the manufacture and chemical and physical requirements of 33 grade ordinary Portland cement.",
            "keywords": ["cement", "portland", "opc", "33 grade", "compressive", "strength"],
            "full_text": "IS 269: 1989 Specification for Ordinary Portland Cement, 33 Grade. Covers chemical and physical requirements for OPC 33 grade cement."
        },
        {
            "standard_id": "IS 8112: 1989",
            "title": "Specification for 43 Grade Ordinary Portland Cement",
            "category": "Cement",
            "scope": "Covers requirements for 43 grade ordinary portland cement.",
            "keywords": ["cement", "portland", "43 grade", "opc"],
            "full_text": "IS 8112: 1989 Specification for 43 Grade Ordinary Portland Cement. Chemical and physical requirements for OPC 43 grade."
        },
        {
            "standard_id": "IS 12269: 1987",
            "title": "Specification for 53 Grade Ordinary Portland Cement",
            "category": "Cement",
            "scope": "Covers requirements for 53 grade ordinary portland cement.",
            "keywords": ["cement", "portland", "53 grade", "opc", "high strength"],
            "full_text": "IS 12269: 1987 Specification for 53 Grade Ordinary Portland Cement. Chemical and physical requirements for OPC 53 grade."
        },
        {
            "standard_id": "IS 383: 1970",
            "title": "Specification for Coarse and Fine Aggregates from Natural Sources for Concrete",
            "category": "Concrete",
            "scope": "Specification for coarse and fine aggregates from natural sources for concrete.",
            "keywords": ["aggregates", "coarse", "fine", "concrete", "sand", "gravel"],
            "full_text": "IS 383: 1970 Specification for Coarse and Fine Aggregates from Natural Sources for Concrete. Covers grading, quality, and testing of natural aggregates."
        },
        {
            "standard_id": "IS 458: 2003",
            "title": "Specification for Precast Concrete Pipes (With and Without Reinforcement)",
            "category": "Pipes",
            "scope": "Covers precast concrete pipes with and without reinforcement for water mains and sewers.",
            "keywords": ["concrete", "pipes", "precast", "reinforcement", "water mains"],
            "full_text": "IS 458: 2003 Specification for Precast Concrete Pipes (With and Without Reinforcement). Covers dimensions, testing, and quality for precast pipes."
        },
        {
            "standard_id": "IS 455: 1989",
            "title": "Specification for Portland Slag Cement",
            "category": "Cement",
            "scope": "Covers manufacture and requirements for Portland slag cement.",
            "keywords": ["cement", "portland", "slag", "psc"],
            "full_text": "IS 455: 1989 Specification for Portland Slag Cement. Covers chemical, physical requirements and manufacture of Portland slag cement."
        },
        {
            "standard_id": "IS 1489 (Part 1): 1991",
            "title": "Specification for Portland Pozzolana Cement: Flyash Based",
            "category": "Cement",
            "scope": "Covers flyash based portland pozzolana cement requirements.",
            "keywords": ["cement", "pozzolana", "flyash", "ppc"],
            "full_text": "IS 1489 (Part 1): 1991 Specification for Portland Pozzolana Cement: Flyash Based."
        },
        {
            "standard_id": "IS 1489 (Part 2): 1991",
            "title": "Specification for Portland Pozzolana Cement: Calcined Clay Based",
            "category": "Cement",
            "scope": "Covers calcined clay based portland pozzolana cement.",
            "keywords": ["cement", "pozzolana", "calcined clay", "ppc"],
            "full_text": "IS 1489 (Part 2): 1991 Specification for Portland Pozzolana Cement: Calcined Clay Based."
        },
        {
            "standard_id": "IS 2185 (Part 1): 1979",
            "title": "Specification for Concrete Masonry Units: Hollow and Solid Concrete Blocks",
            "category": "Concrete",
            "scope": "Covers hollow and solid concrete blocks for masonry.",
            "keywords": ["concrete", "blocks", "masonry", "hollow", "solid"],
            "full_text": "IS 2185 (Part 1): 1979 Specification for Concrete Masonry Units: Hollow and Solid Concrete Blocks."
        },
        {
            "standard_id": "IS 2185 (Part 2): 1983",
            "title": "Specification for Concrete Masonry Units: Hollow and Solid Lightweight Concrete Blocks",
            "category": "Concrete",
            "scope": "Covers lightweight hollow and solid concrete masonry blocks, dimensions and physical requirements.",
            "keywords": ["concrete", "blocks", "masonry", "hollow", "lightweight"],
            "full_text": "IS 2185 (Part 2): 1983 Specification for Concrete Masonry Units: Hollow and Solid Lightweight Concrete Blocks. Dimensions and physical requirements."
        },
        {
            "standard_id": "IS 459: 1992",
            "title": "Specification for Corrugated and Semi-Corrugated Asbestos Cement Sheets",
            "category": "Other Building Materials",
            "scope": "Covers corrugated and semi-corrugated asbestos cement sheets for roofing and cladding.",
            "keywords": ["asbestos", "cement", "sheets", "corrugated", "roofing", "cladding"],
            "full_text": "IS 459: 1992 Specification for Corrugated and Semi-Corrugated Asbestos Cement Sheets. Covers manufacture, dimensions, and testing for roofing sheets."
        },
        {
            "standard_id": "IS 3466: 1988",
            "title": "Specification for Masonry Cement",
            "category": "Cement",
            "scope": "Covers masonry cement for general use in mortars, not for structural concrete.",
            "keywords": ["masonry", "cement", "mortar", "general purpose"],
            "full_text": "IS 3466: 1988 Specification for Masonry Cement. Covers masonry cement for use in mortar for masonry work, not for structural concrete."
        },
        {
            "standard_id": "IS 6909: 1990",
            "title": "Specification for Supersulphated Cement",
            "category": "Cement",
            "scope": "Covers supersulphated cement for marine works and aggressive conditions.",
            "keywords": ["supersulphated", "cement", "marine", "sulfate", "aggressive"],
            "full_text": "IS 6909: 1990 Specification for Supersulphated Cement. Covers composition, manufacture, and testing for marine and aggressive water conditions."
        },
        {
            "standard_id": "IS 8042: 1989",
            "title": "Specification for White Portland Cement",
            "category": "Cement",
            "scope": "Covers white portland cement for architectural and decorative purposes.",
            "keywords": ["white", "portland", "cement", "decorative", "architectural"],
            "full_text": "IS 8042: 1989 Specification for White Portland Cement. Covers physical and chemical requirements for white portland cement used in architectural finishes."
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
