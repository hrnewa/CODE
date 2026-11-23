import os
from docx import Document

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
path = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised_clean.docx")
doc = Document(path)

for p in doc.paragraphs:
    if p.text.startswith("Because county identifiers were available only for Guangxi"):
        p.text = ("Because county identifiers were available only for Guangxi, we approximated spatial "
                  "validation by grouping patients into 20 spatial blocks using k-means on the six "
                  "log-transformed accessibility variables and performing fivefold group "
                  "cross-validation. Discrimination was close to the random-split estimate (ROC-AUC "
                  "0.692, PR-AUC 0.787), suggesting that location memorisation did not materially "
                  "inflate performance (Supplementary Table S20). Province-stratified test performance "
                  "is reported separately in Supplementary Table S21. This is not equivalent to holding "
                  "out whole counties, and county-level validation remains desirable.")
        break

# insert a summary paragraph after P84
anchor = None
for p in doc.paragraphs:
    if p.text.startswith("Because county identifiers were available only for Guangxi"):
        anchor = p._p
        break
if anchor is not None:
    newp = doc.add_paragraph()
    newp.add_run("In addition, province-stratified performance, location-identifier comparator models, "
                 "area-level calibration, key-population missingness by year and province, insurance "
                 "imputation, bootstrap confidence intervals, and a sensitivity model removing "
                 "duplicate encodings are reported in Supplementary Tables S21-S27.")
    anchor.addnext(newp._p)

doc.save(path)
print("patched section 10")
