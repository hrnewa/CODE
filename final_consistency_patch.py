import os
import re
import shutil
import sys
import datetime
from docx import Document

MAIN = sys.argv[1]
SUPP = sys.argv[2]
RESP = sys.argv[3]
BACKUP_DIR = sys.argv[4]


def backup(path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    name = os.path.basename(path)
    stem, ext = os.path.splitext(name)
    dst = os.path.join(BACKUP_DIR, stem + "_pre_final" + ext)
    shutil.copy2(path, dst)
    return dst


def containers(doc):
    yield from doc.paragraphs
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                yield from cell.paragraphs


def replace_in_paragraph(p, old, new):
    n = 0
    while old in p.text:
        texts = [r.text for r in p.runs]
        full = "".join(texts)
        idx = full.find(old)
        if idx < 0:
            break
        end = idx + len(old)
        starts = []
        pos = 0
        for t in texts:
            starts.append(pos)
            pos += len(t)
        si = None
        for i, s in enumerate(starts):
            if s <= idx < s + len(texts[i]) or (s == idx and len(texts[i]) == 0):
                si = i
                break
        ei = None
        for i, s in enumerate(starts):
            if s < end <= s + len(texts[i]):
                ei = i
                break
        if si is None or ei is None:
            p.runs[0].text = full.replace(old, new, 1)
            for r in p.runs[1:]:
                r.text = ""
            n += 1
            continue
        if si == ei:
            t = texts[si]
            p.runs[si].text = t[: idx - starts[si]] + new + t[end - starts[si] :]
        else:
            p.runs[si].text = texts[si][: idx - starts[si]] + new
            for j in range(si + 1, ei):
                p.runs[j].text = ""
            p.runs[ei].text = texts[ei][end - starts[ei] :]
        n += 1
    return n


def apply(doc, old, new, expected=None):
    total = 0
    for p in containers(doc):
        total += replace_in_paragraph(p, old, new)
    print("replace %r -> %r : %d" % (old[:60], new[:60], total))
    if expected is not None and total != expected:
        raise SystemExit("Expected %d replacements, got %d for %r" % (expected, total, old))
    return total


main_bak = backup(MAIN)
supp_bak = backup(SUPP)
print("backups:", main_bak, supp_bak)

doc = Document(MAIN)
apply(doc, "63.5%", "63.4%", 2)
apply(doc, "prefecture or urban/rural identifiers yielded ROC-AUC values of 0.709 to 0.711",
      "prefecture, city, or urban/rural identifiers yielded ROC-AUC values of 0.702 to 0.711", 1)
apply(doc, "(ROC-AUC 0.709-0.711)", "(ROC-AUC 0.702-0.711)", 1)
doc.save(MAIN)

doc = Document(SUPP)
apply(doc, "63.5%", "63.4%", 1)
t4 = doc.tables[4]
cell = t4.rows[2].cells[2]
if cell.text.strip() != "63.5":
    raise SystemExit("Unexpected outcome-count cell: %r" % cell.text)
cell.paragraphs[0].runs[0].text = "63.4"
for r in cell.paragraphs[0].runs[1:]:
    r.text = ""
print("table S1 event rate 63.5 -> 63.4")
apply(doc, "74.1%", "73.8%", 1)
apply(doc, "missing symptom text coded as not recorded; model without symptom-onset year.",
      "model without symptom-onset year; and a model with duplicate encodings removed.", 1)
apply(doc, "spatially grouped cross-validation by county",
      "spatially grouped cross-validation by accessibility-profile cluster", 1)
apply(doc, "bootstrap 95% confidence intervals (2,000 resamples)",
      "bootstrap 95% confidence intervals (1,000 resamples for main test-set metrics; 2,000 for incremental comparisons)", 1)
apply(doc, "Location identifiers performed at least as well as the six geographic variables, indicating that the distance variables do not capture all location-related information.",
      "Location identifiers performed at least as well as the six geographic variables: prefecture and city identifiers reached ROC-AUC 0.709-0.711, and the urban/rural proxy alone reached 0.702, indicating that the distance variables do not capture all location-related information. The no-geography refit in this table is a separate model fit from that in Supplementary Table S15; small differences (<=0.001 in AUC) reflect fit-to-fit variation.", 1)

stripped = []
for p in doc.paragraphs:
    txt = p.text.strip()
    if txt.startswith("Supplementary Table S") and txt.endswith("."):
        old = p.text
        new = old.rstrip()
        new = new[:-1] if new.endswith(".") else new
        if replace_in_paragraph(p, old, new):
            stripped.append(old)
print("stripped heading periods:", len(stripped))
doc.save(SUPP)

with open(RESP, "r", encoding="utf-8") as f:
    text = f.read()
old_text = text
text, n1 = re.subn(r"0\.709[\u2013-]0\.711", "0.702\u20130.711", text)
print("response comparator range replacements:", n1)
if n1 != 1:
    raise SystemExit("Expected 1 comparator range replacement in response letter, got %d" % n1)
with open(RESP, "w", encoding="utf-8") as f:
    f.write(text)

print("done", datetime.datetime.now().isoformat(timespec="seconds"))
