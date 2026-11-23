import os
from docx import Document

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
path = os.path.join(base, "manuscript/SR/返修工作/926Niu_Delayed entry into tuberculosis_Revised_clean.docx")
doc = Document(path)


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


for p in doc.paragraphs:
    if "n = 2,089, 3.4%" in p.text:
        rep(p, "n = 2,089, 3.4%", "n = 2,089, 3.5%")

p72_old = ("In a spatial block cross-validation using 20 accessibility-profile clusters, ROC-AUC "
           "was 0.692, close to the random-split estimate (Supplementary Table S20).")
p72_new = ("In a spatial block cross-validation using 20 accessibility-profile clusters, ROC-AUC "
           "was 0.692, close to the random-split estimate (Supplementary Table S20). "
           "Province-stratified test performance was lower in Guangxi (ROC-AUC 0.681) than in "
           "Guizhou (0.707), and area-level predicted and observed delay proportions were highly "
           "correlated across prefectures (weighted r = 0.957) and counties in Guangxi (0.984) "
           "(Supplementary Tables S21 and S26). Replacing the six geographic variables with "
           "prefecture or urban/rural identifiers yielded ROC-AUC values of 0.709 to 0.711, "
           "slightly higher than the full model (0.699), indicating that administrative location "
           "captures additional information beyond the distance variables (Supplementary Table "
           "S22). A sensitivity model removing duplicate encodings yielded ROC-AUC 0.694 "
           "(Supplementary Table S18).")
for p in doc.paragraphs:
    if p72_old in p.text:
        rep(p, p72_old, p72_new)
        break

p101_old1 = ("Fifth, insurance values were imputed from residence and occupation for 90.1% of "
             "patients (100% in Guangxi and 46.6% in Guizhou), and key-population Unknown "
             "categories were frequent and apparently patterned by data-system changes, so these "
             "domains should not be interpreted as individual risk factors.")
p101_new1 = ("Fifth, insurance values were imputed from residence and occupation for 90.1% of "
             "patients (100% in Guangxi and 46.6% in Guizhou), and key-population Unknown "
             "categories increased sharply after 2022 and were universal in Guizhou during "
             "2022-2024, consistent with data-system changes (Supplementary Tables S23-S24); these "
             "domains should not be interpreted as individual risk factors.")
for p in doc.paragraphs:
    if p101_old1 in p.text:
        rep(p, p101_old1, p101_new1)
        break

p101_old2 = ("County identifiers were available only for Guangxi, so county-level validation was "
             "restricted to that province.")
p101_new2 = ("County identifiers were available only for Guangxi, so county-level validation was "
             "restricted to that province; administrative location identifiers performed slightly "
             "better than the six distance variables (ROC-AUC 0.709-0.711), so the geographic "
             "domain should not be interpreted as capturing all spatial information.")
for p in doc.paragraphs:
    if p101_old2 in p.text:
        rep(p, p101_old2, p101_new2)
        break

doc.save(path)
print("patched main extra")
