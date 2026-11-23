import sys
from docx import Document

path = sys.argv[1]
doc = Document(path)


def replace_in_paragraph(p, old, new):
    for _ in range(20):
        if old not in p.text:
            return 0
        texts = [r.text for r in p.runs]
        full = "".join(texts)
        idx = full.find(old)
        if idx < 0:
            return 0
        end = idx + len(old)
        starts = []
        pos = 0
        for t in texts:
            starts.append(pos)
            pos += len(t)
        si = ei = None
        for i, s in enumerate(starts):
            if s <= idx < s + len(texts[i]) or (s == idx and len(texts[i]) == 0):
                si = i
                break
        for i, s in enumerate(starts):
            if s < end <= s + len(texts[i]):
                ei = i
                break
        if si is None or ei is None:
            p.runs[0].text = full.replace(old, new, 1)
            for r in p.runs[1:]:
                r.text = ""
        elif si == ei:
            t = texts[si]
            p.runs[si].text = t[:idx - starts[si]] + new + t[end - starts[si]:]
        else:
            p.runs[si].text = texts[si][:idx - starts[si]] + new
            for j in range(si + 1, ei):
                p.runs[j].text = ""
            p.runs[ei].text = texts[ei][end - starts[ei]:]
    return 0


para_repls = [
("Supplementary Table S5. Retained predictor domains from Elastic Net logistic regression",
 "Supplementary Table S5. Predictor domains represented in the Elastic Net model"),
("A total of 70 non-zero coefficients were retained.",
 "A total of 64 non-zero coefficients were retained (excluding the intercept)."),
("retaining 64 non-zero coefficients", "with 64 non-zero coefficients (excluding the intercept)"),
("The table summarizes retained predictor domains rather than serving as the variable-selection basis for the final LightGBM model.",
 "The table summarizes predictor domains represented in the Elastic Net model rather than serving as the variable-selection basis for the final LightGBM model."),
("The Elastic Net comparator retained predictors from the same broad domains",
 "The Elastic Net comparator included predictors from the same broad domains"),
("Test-set performance was computed separately within Guangxi and Guizhou. Discrimination was lower in Guangxi (ROC-AUC 0.681) than in Guizhou (0.707), but event prevalence differed substantially (66.7% vs 49.3%), so PR-AUC is not directly comparable across provinces.",
 "Test-set performance was computed separately within Guangxi and Guizhou. Discrimination was lower in Guangxi (ROC-AUC 0.681) than in Guizhou (0.707), but event prevalence differed substantially (66.7% vs 49.3%), so PR-AUC is not directly comparable across provinces. In the full cohort, 49,224 patients were from Guangxi (32,862 delayed, 66.8%) and 11,252 from Guizhou (5,508 delayed, 49.0%)."),
]
n = 0
for p in doc.paragraphs:
    for old, new in para_repls:
        n += 1 if (old in p.text and (replace_in_paragraph(p, old, new) >= 0)) else 0

cell_repls = {
"Representative retained predictors": "Representative predictors",
"Spatial-access variables were retained by the regularized linear model, consistent with the tree-based model importance ranking.": "Spatial-access variables had non-zero coefficients, consistent with the tree-based model importance ranking.",
"Occupation and nonlinear age patterns were retained as relevant predictors.": "Occupation and nonlinear age patterns had non-zero coefficients.",
"Comorbidity-related variables were retained after diagnosis-code enrichment and missingness coding.": "Comorbidity-related variables had non-zero coefficients after diagnosis-code enrichment and missingness coding.",
"Patient source and referral pathway variables were retained, consistent with care-seeking pathway relevance.": "Patient source and referral pathway variables had non-zero coefficients, consistent with care-seeking pathway relevance.",
"Several key-population subtype variables were retained, although individual dummy-level coefficients should be interpreted cautiously.": "Several key-population subtype variables had non-zero coefficients, although individual dummy-level coefficients should be interpreted cautiously.",
}
m = 0
t = doc.tables[12]
for row in t.rows:
    for cell in row.cells:
        txt = cell.text.strip()
        if txt in cell_repls:
            new = cell_repls[txt]
            p = cell.paragraphs[0]
            if p.runs:
                p.runs[0].text = new
                for r in p.runs[1:]:
                    r.text = ""
            else:
                p.add_run(new)
            m += 1
print("paragraph candidates", n, "cell replacements", m)
doc.save(path)
