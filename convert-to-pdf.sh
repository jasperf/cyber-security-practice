#!/bin/bash
# Convert all session .md files to PDFs using pandoc
# Output goes to material/paper-based-tests/
# Requires: pandoc, xelatex (from MacTeX/TeX Live)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/material/paper-based-tests"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Find all session markdown files in s1-s5 directories
SESSION_MD_FILES=(
  "s1-cryptography/session1-cryptography.md"
  "s2-networking/session2-networking.md"
  "s3-red-teaming/session3-red-teaming.md"
  "s4-forensics/session4-forensics.md"
  "s5-misc-ctf/session5-misc-ctf.md"
)

echo "Converting markdown files to PDF..."
echo "Output directory: $OUTPUT_DIR"
echo ""

for md_file in "${SESSION_MD_FILES[@]}"; do
  # Get the base filename without extension
  base_name=$(basename "$md_file" .md)
  pdf_file="${OUTPUT_DIR}/${base_name}.pdf"
  
  echo "Converting $md_file -> $pdf_file"
  
  pandoc -f gfm "$md_file" -o "$pdf_file" \
    --pdf-engine=xelatex \
    -V geometry:margin=2.2cm \
    -V fontsize=11pt \
    -V colorlinks=true
  
  echo "  ✓ Created $pdf_file"
done

echo ""
echo "All PDFs generated successfully in $OUTPUT_DIR/"
