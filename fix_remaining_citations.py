import sys
from docx import Document

path = sys.argv[1]
doc = Document(path)


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
            n += 1
            continue
        if si == ei:
            t = texts[si]
            p.runs[si].text = t[:idx - starts[si]] + new + t[end - starts[si]:]
        else:
            p.runs[si].text = texts[si][:idx - starts[si]] + new
            for j in range(si + 1, ei):
                p.runs[j].text = ""
            p.runs[ei].text = texts[ei][end - starts[ei]:]
        n += 1
    return n


repls = [
("Patient delay is both a clinical problem and a population-level public-health concern[4\u20136].",
 "Patient delay is both a clinical problem and a population-level public-health concern[4,5]. Late presentation can also result in severe disseminated disease and high mortality[6]."),
("and patient source[11,12], as well as spatial determinants such as straight-line distance and travel time to health facilities[13,33,34].",
 "and patient source[11], as well as spatial determinants such as straight-line distance and travel time to health facilities[12,13,33,34]."),
("after temporal features and demographics[15,16].",
 "after temporal features and demographics, consistent with previous TB delay research[15,16]."),
("A total of 70 non-zero coefficients were retained.",
 "A total of 64 non-zero coefficients were retained (excluding the intercept)."),
("The probability threshold was selected using Youden\u2019s index from training-set predictions and then applied to the held-out test set.",
 "Thresholds for LightGBM, XGBoost, Random Forest, and Elastic Net were selected using Youden\u2019s index from training-set predictions. The mean-probability ensemble used a fixed threshold of 0.50. All thresholds were applied to the held-out test set."),
]
count = 0
for p in doc.paragraphs:
    for old, new in repls:
        count += replace_in_paragraph(p, old, new)
print("main replacements", count)
doc.save(path)
