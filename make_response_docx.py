import re
import sys
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

src, out = sys.argv[1], sys.argv[2]
lines = open(src, encoding="utf-8").read().splitlines()

doc = Document()
sec = doc.sections[0]
sec.top_margin = sec.bottom_margin = Cm(2.0)
sec.left_margin = sec.right_margin = Cm(2.2)
normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15


def add_runs(paragraph, text):
    parts = re.split(r"(\*\*.+?\*\*)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) >= 4:
            r = paragraph.add_run(part[2:-2])
            r.bold = True
        else:
            paragraph.add_run(part)


def is_sep(cells):
    return all(re.fullmatch(r":?-{2,}:?", c.strip()) for c in cells if c.strip() != "")


i = 0
while i < len(lines):
    line = lines[i].rstrip()
    s = line.strip()
    if not s:
        i += 1
        continue
    if s == "---":
        p = doc.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        pbdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "6")
        bottom.set(qn("w:space"), "1")
        bottom.set(qn("w:color"), "auto")
        pbdr.append(bottom)
        pPr.append(pbdr)
        i += 1
        continue
    if s.startswith("|"):
        table_lines = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            table_lines.append(lines[i].strip())
            i += 1
        rows = []
        for tl in table_lines:
            cells = [c.strip() for c in tl.strip("|").split("|")]
            if is_sep(cells):
                continue
            rows.append(cells)
        if rows:
            ncols = max(len(r) for r in rows)
            table = doc.add_table(rows=0, cols=ncols)
            table.style = "Table Grid"
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            for ri, r in enumerate(rows):
                cells = table.add_row().cells
                for ci in range(ncols):
                    txt = r[ci] if ci < len(r) else ""
                    p = cells[ci].paragraphs[0]
                    add_runs(p, txt)
                    for run in p.runs:
                        run.font.size = Pt(8.5)
                        if ri == 0:
                            run.bold = True
            for row in table.rows:
                trPr = row._tr.get_or_add_trPr()
                el = OxmlElement("w:cantSplit")
                trPr.append(el)
        continue
    if s.startswith("# "):
        p = doc.add_paragraph()
        r = p.add_run(s[2:])
        r.bold = True
        r.font.size = Pt(15)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(8)
        i += 1
        continue
    if s.startswith("## "):
        p = doc.add_paragraph()
        r = p.add_run(s[3:])
        r.bold = True
        r.font.size = Pt(12)
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        i += 1
        continue
    if s.startswith("- "):
        p = doc.add_paragraph(style="List Bullet")
        add_runs(p, s[2:])
        i += 1
        continue
    if re.match(r"^\d+\.\s", s):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.first_line_indent = Cm(-0.6)
        m = re.match(r"^(\d+)\.\s+(.*)$", s)
        p.add_run(m.group(1) + ". ")
        add_runs(p, m.group(2))
        i += 1
        continue
    p = doc.add_paragraph()
    add_runs(p, s)
    i += 1

footer = sec.footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fld1 = OxmlElement("w:fldSimple")
fld1.set(qn("w:instr"), "PAGE")
fp._p.append(fld1)

doc.save(out)
print("wrote", out)
