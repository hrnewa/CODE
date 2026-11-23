import os
from docx import Document

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
main_path = os.path.join(base, "manuscript/SR/返修工作/926Niu_Delayed entry into tuberculosis_Revised_clean.docx")
supp_path = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised_clean.docx")


def set_cell(cell, text):
    p = cell.paragraphs[0]
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run(text)


# main
doc = Document(main_path)
for p in doc.paragraphs:
    if "with an event rate of 74.1% (Table 4)" in p.text:
        p.text = p.text.replace(
            "with an event rate of 74.1% (Table 4). At the Youden-index threshold of 0.703, sensitivity was 0.731 and specificity was 0.587.",
            "with an event rate of 73.8% (Table 4). At the Youden-index threshold of 0.732, sensitivity was 0.678 and specificity was 0.656.")
t = doc.tables[3]
row = t.rows[1]
set_cell(row.cells[2], "0.732")
set_cell(row.cells[3], "0.738")
set_cell(row.cells[4], "0.726")
set_cell(row.cells[5], "0.875")
set_cell(row.cells[6], "0.672")
set_cell(row.cells[7], "0.678")
set_cell(row.cells[8], "0.656")
set_cell(row.cells[9], "0.847")
set_cell(row.cells[10], "0.419")
doc.save(main_path)

# supplement
doc = Document(supp_path)
for p in doc.paragraphs:
    if "the event rate was 74.1%" in p.text:
        p.text = p.text.replace("the event rate was 74.1%", "the event rate was 73.8%")
t = doc.tables[16]
row = t.rows[1]
set_cell(row.cells[2], "0.732")
set_cell(row.cells[3], "0.738")
set_cell(row.cells[4], "0.726")
set_cell(row.cells[5], "0.875")
set_cell(row.cells[6], "0.672")
set_cell(row.cells[7], "0.678")
set_cell(row.cells[8], "0.656")
set_cell(row.cells[9], "0.847")
set_cell(row.cells[10], "0.419")

# S10 threshold table
t17 = doc.tables[17]
vals = [
    ("0.732", "0.432"), ("0.731", "0.432"), ("0.730", "0.432"),
    ("0.729", "0.432"), ("0.728", "0.432"), ("0.727", "0.432"),
    ("0.726", "0.432"), ("0.725", "0.432"),
]
for i, (thr, j) in enumerate(vals, start=1):
    if i < len(t17.rows):
        set_cell(t17.rows[i].cells[0], thr)
        set_cell(t17.rows[i].cells[1], "j_index")
        set_cell(t17.rows[i].cells[2], "binary")
        set_cell(t17.rows[i].cells[3], j)
doc.save(supp_path)
print("patched 7-day final")
