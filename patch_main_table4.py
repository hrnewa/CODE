import os
from docx import Document

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
path = os.path.join(base, "manuscript/SR/返修工作/926Niu_Delayed entry into tuberculosis_Revised_clean.docx")
doc = Document(path)

for p in doc.paragraphs:
    if "with an event rate of 74.1%. At the Youden-index threshold" in p.text:
        p.text = p.text.replace("with an event rate of 74.1%. At the Youden-index threshold",
                                "with an event rate of 74.1% (Table 4). At the Youden-index threshold")
    if "ranging approximately from 0.671 to 0.705 and overlapping confidence intervals (Table 4)." in p.text:
        p.text = p.text.replace(
            "ranging approximately from 0.671 to 0.705 and overlapping confidence intervals (Table 4).",
            "ranging approximately from 0.671 to 0.705 and overlapping confidence intervals (Supplementary Table S12).")

doc.save(path)
print("patched Table 4 references")
