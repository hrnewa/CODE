import csv
import os
from docx import Document

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
path = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised_clean.docx")
resdir = os.path.join(base, "ml_results/revision_clean")
doc = Document(path)

with open(os.path.join(resdir, "baseline_characteristics_clean.csv"), encoding="utf-8-sig") as f:
    rows = {r["variable"] + "|" + r["level"]: r for r in csv.DictReader(f)}


def set_cell(cell, text):
    p = cell.paragraphs[0]
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run(text)


res_map = {
    "Local": "本地", "Intra-city migrant": "市内流动",
    "Inter-city migrant within province": "市间流动（省内流动）",
    "Inter-provincial migrant": "省间流动", "Foreign national": "外籍",
    "Hong Kong/Macau/Taiwan": "港澳台",
}
ins_map = {
    "Local resident insurance": "本地居民", "Non-local resident insurance": "异地居民",
    "Local employee insurance": "本地职工", "Non-local employee insurance": "异地职工",
}

t = doc.tables[8]
for row in t.rows[1:]:
    var_label = row.cells[1].text.strip()
    level_label = row.cells[2].text.strip()
    var = level = None
    if var_label == "Residence status" and level_label in res_map:
        var, level = "户籍地址类别", res_map[level_label]
    elif var_label == "Insurance type" and level_label in ins_map:
        var, level = "险种类型_final", ins_map[level_label]
    if var:
        r = rows.get(var + "|" + level)
        if r:
            set_cell(row.cells[3], r["Overall"])
            set_cell(row.cells[4], r["No"])
            set_cell(row.cells[5], r["Yes"])

doc.save(path)
print("patched baseline residence/insurance")
