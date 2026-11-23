import sys
from docx import Document

path = sys.argv[1]
out = sys.argv[2]
doc = Document(path)

with open(out, "w", encoding="utf-8") as f:
    f.write("=== PARAGRAPHS ===\n")
    for i, p in enumerate(doc.paragraphs):
        txt = p.text.strip()
        if txt:
            f.write(f"[P{i}] {txt}\n")
    f.write("\n=== TABLES ===\n")
    for ti, table in enumerate(doc.tables):
        f.write(f"\n--- TABLE {ti} ({len(table.rows)}x{len(table.columns)}) ---\n")
        for ri, row in enumerate(table.rows):
            cells = [c.text.replace("\n", " ").strip() for c in row.cells]
            f.write(f"R{ri}: " + " | ".join(cells) + "\n")
print("dumped", out)
