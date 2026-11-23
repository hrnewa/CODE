import os
from docx import Document

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
main_path = os.path.join(base, "manuscript/SR/返修工作/926Niu_Delayed entry into tuberculosis_Revised_clean.docx")
supp_path = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised_clean.docx")
resp_path = os.path.join(base, "manuscript/SR/返修工作/Response_to_Reviewers_DRAFT.md")

pairs = [
    ("cross-validation-derived Youden-index threshold", "training-set Youden-index threshold"),
    ("cross-validated training predictions", "training-set predictions"),
    ("cross-validated predictions in the training data", "training-set predictions"),
    ("from cross-validated predictions", "from training-set predictions"),
]

for path in [main_path, supp_path]:
    doc = Document(path)
    for p in doc.paragraphs:
        for old, new in pairs:
            if old in p.text:
                p.text = p.text.replace(old, new)
    doc.save(path)

with open(resp_path, encoding="utf-8") as f:
    txt = f.read()
txt = txt.replace("threshold was selected from cross-validated training predictions",
                  "threshold was selected from training-set predictions")
with open(resp_path, "w", encoding="utf-8") as f:
    f.write(txt)

# Methods threshold selection sentence
doc = Document(main_path)
for p in doc.paragraphs:
    if "Five-fold stratified cross-validation within the training set was used for hyperparameter tuning, model comparison, and threshold selection" in p.text:
        p.text = p.text.replace(
            "Five-fold stratified cross-validation within the training set was used for hyperparameter tuning, model comparison, and threshold selection; the held-out test set was not used for tuning or model selection.",
            "Five-fold stratified cross-validation within the training set was used for hyperparameter tuning and model comparison. The classification threshold was selected from training-set predictions by maximizing Youden's index; the held-out test set was not used for tuning, model selection, or threshold selection.")
doc.save(main_path)

# Supplement pseudocode and note
doc = Document(supp_path)
for p in doc.paragraphs:
    if "Select the probability threshold by maximizing Youden's index on cross-validated training predictions" in p.text:
        p.text = p.text.replace("on cross-validated training predictions", "on training-set predictions")
doc.save(supp_path)
print("patched threshold wording")
