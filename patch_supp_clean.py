import os
from docx import Document

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
src = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised_clean.docx")
doc = Document(src)


def rep(p, old, new):
    if old not in p.text:
        return False
    for r in p.runs:
        if old in r.text:
            r.text = r.text.replace(old, new)
            return True
    full = p.text.replace(old, new)
    if p.runs:
        p.runs[0].text = full
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run(full)
    return True


def replace_all(old, new):
    for p in doc.paragraphs:
        rep(p, old, new)


def set_cell(cell, text):
    p = cell.paragraphs[0]
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run(text)


replace_all("n = 56,174", "n = 55,883")
replace_all("ROC-AUC 0.686", "ROC-AUC 0.687")
replace_all("n = 58,556", "n = 58,266")
replace_all("ROC-AUC 0.691", "ROC-AUC 0.687")
replace_all("ROC-AUC 0.671", "ROC-AUC 0.667")
replace_all("n = 42,068", "n = 41,811")
replace_all("n = 18,710", "n = 18,665")
replace_all("PR-AUC 0.789", "PR-AUC 0.787")
replace_all("73.9%", "74.1%")
replace_all("retaining 70 non-zero coefficients", "retaining 64 non-zero coefficients")

p96_old = ("Note. This table separates implausible outcome values from predictor missingness "
           "and documents the rule used for each major variable group. In the raw new-patient "
           "file, 564 of 61,040 records (0.92%) had negative patient_delay values; 430 were "
           "corrected by date-order checks and 134 (0.22%) were excluded.")
p96_new = ("Note. This table separates implausible outcome values from predictor missingness "
           "and documents the rule used for each major variable group. In the raw new-patient "
           "file, 564 of 61,040 records (0.92%) had negative patient_delay values; these records "
           "were excluded because the recorded first-visit date preceded the recorded "
           "symptom-onset date and the date order could not be reliably resolved.")
for p in doc.paragraphs:
    if p96_old in p.text:
        rep(p, p96_old, p96_new)
        break

p113_old = ("Interpretation. At thresholds from 0.10 to 0.50, the model showed higher net "
            "benefit than the treat-none strategy but no meaningful benefit over the treat-all "
            "strategy at low thresholds (0.594 vs 0.594 at 0.10; 0.544 vs 0.543 at 0.20). The "
            "incremental advantage over treat-all became apparent only at higher thresholds "
            "(0.30-0.50), and the operating threshold of 0.625 was not evaluated in this table. "
            "These results do not support strong claims of clinical utility; they are consistent "
            "with a role in risk stratification for planning rather than individual "
            "decision-making.")
p113_new = ("Interpretation. At thresholds from 0.10 to 0.50, the model showed higher net "
            "benefit than the treat-none strategy but no meaningful benefit over the treat-all "
            "strategy at low thresholds (0.594 vs 0.594 at 0.10; 0.544 vs 0.543 at 0.20). Net "
            "benefit exceeded treat-all at higher thresholds, including the operating threshold "
            "of 0.625 (0.187 vs 0.025); the no-geography model was essentially identical at this "
            "threshold (0.187). These results do not support strong claims of clinical utility; "
            "they are consistent with a role in risk stratification for planning rather than "
            "individual decision-making.")
for p in doc.paragraphs:
    if p113_old in p.text:
        rep(p, p113_old, p113_new)
        break

# Table 10 >365 row
t10 = doc.tables[10]
for row in t10.rows[1:]:
    if row.cells[0].text.strip() == "patient_delay >365 days":
        set_cell(row.cells[1], "3.45% after new-patient restriction")

# Table 14 ensemble threshold
t14 = doc.tables[14]
for row in t14.rows[1:]:
    if row.cells[0].text.strip() == "MeanEnsemble":
        set_cell(row.cells[1], "0.50")

# Table 22 formatting
t22 = doc.tables[22]
for row in t22.rows[1:]:
    label = row.cells[0].text.strip()
    if label == "ROC-AUC":
        set_cell(row.cells[3], "0.003 (-0.0005 to 0.0056)")
    if label == "PR-AUC":
        set_cell(row.cells[3], "0.002 (-0.0004 to 0.0048)")
    if label == "Brier score":
        set_cell(row.cells[3], "-0.0003 (-0.0011 to 0.0004)")

doc.save(src)
print("patched", src)
