import os
from docx import Document

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
path = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised_clean.docx")
doc = Document(path)

for p in doc.paragraphs:
    if p.text.startswith("Note. The primary outcome was delayed entry into TB-designated care"):
        p.text = ("Note. The primary outcome was delayed entry into TB-designated care (≥14 days). "
                  "The classification threshold was selected using Youden's index from training-set "
                  "predictions; the test set was not used for threshold selection. A fivefold "
                  "cross-validation threshold was 0.651 (sensitivity 0.611, specificity 0.667); the "
                  "training-set threshold was used for consistency across models.")
        break

doc.save(path)
print("patched S7 note")
