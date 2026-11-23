import os
from docx import Document
from docx.shared import Pt

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
path = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised_clean.docx")
doc = Document(path)


def set_cell(cell, text):
    p = cell.paragraphs[0]
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run(text)


def add_note(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = True
    r.font.size = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    return p

# front flow table
t1 = doc.tables[1]
for row in t1.rows:
    label = row.cells[0].text.strip()
    if label == "Negative delay exclusion":
        set_cell(row.cells[2], "Invalid date order; first-visit date preceded symptom-onset date")
        set_cell(row.cells[3], "564 records excluded after new-patient restriction")
    if label == "Final analytical cohort":
        set_cell(row.cells[3], "60,476 records")

# outcome counts table
t4 = doc.tables[4]
for row in t4.rows:
    label = row.cells[0].text.strip()
    if label.startswith("No delay"):
        set_cell(row.cells[1], "22,106")
        set_cell(row.cells[2], "36.5")
    if label.startswith("Patient delay"):
        set_cell(row.cells[1], "38,370")
        set_cell(row.cells[2], "63.5")

# feature engineering symptom row
t5 = doc.tables[5]
for row in t5.rows:
    if row.cells[0].text.strip() == "Symptoms":
        set_cell(row.cells[2], "Symptom flags derived from available text and the structured severity field; missing symptom text was not assumed to indicate absence of symptoms.")

# notes after new tables
notes = [
    "Note. Test-set performance was computed separately within Guangxi and Guizhou. Discrimination was lower in Guangxi (ROC-AUC 0.681) than in Guizhou (0.707), but event prevalence differed substantially (66.7% vs 49.3%), so PR-AUC is not directly comparable across provinces.",
    "Note. Models replaced the six distance and travel-time variables with administrative location identifiers (prefecture, urban/rural proxy, city, or both). Location identifiers performed at least as well as the six geographic variables, indicating that the distance variables do not capture all location-related information.",
    "Note. Key-population Unknown counts increased sharply from 2022 and were universal in Guizhou during 2022-2024, consistent with a data-system or form-version change rather than patient-level risk.",
    "Note. Several subtype indicators share identical Unknown totals (for example, 28,579 for custodial personnel, livestock workers, and nursing-home residents), indicating block missingness across subtype fields.",
    "Note. Insurance type was fully imputed in Guangxi and imputed for 46.6% of patients in Guizhou; insurance-related estimates should therefore be interpreted as descriptive.",
    "Note. Area-level agreement was high (weighted correlation 0.957 across prefectures and 0.984 across counties), although the slope exceeded 1 and the intercept was negative, indicating some regression-to-the-mean and regional recalibration.",
    "Note. Confidence intervals are percentile bootstrap intervals (1,000 resamples). The DeLong test compares LightGBM and XGBoost ROC-AUC; the difference was statistically detectable but very small.",
]
for i, note in enumerate(notes):
    tbl = doc.tables[28 + i]
    p = add_note(note)
    tbl._tbl.addnext(p._p)

doc.save(path)
print("patched front tables and added notes")
