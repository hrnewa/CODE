import sys
from docx import Document

path = sys.argv[1]
doc = Document(path)

mapping = {
    "户籍地址类别": "Household registration category",
    "`重点人群-E.学校托幼机构人员_final_未知`": "`Key population E: school/kindergarten personnel_final_Unknown`",
    "hiv_aids_final_未知": "hiv_aids_final_Unknown",
    "diabetes_final_否": "diabetes_final_No",
    "hiv_aids_final_否": "hiv_aids_final_No",
    "is_key_population_final_否": "is_key_population_final_No",
    "`重点人群-I.精神病院患者_final_other`": "`Key population I: psychiatric-hospital patient_final_other`",
    "`重点人群-A.密切接触者_final_other`": "`Key population A: close contact_final_other`",
    "`重点人群-G.养殖人员_final_否`": "`Key population G: livestock worker_final_No`",
    "`重点人群-G.养殖人员_final_未知`": "`Key population G: livestock worker_final_Unknown`",
    "`重点人群-J.养老院居住者_final_否`": "`Key population J: nursing-home resident_final_No`",
    "is_key_population_final_是": "is_key_population_final_Yes",
    "`重点人群-J.养老院居住者_final_未知`": "`Key population J: nursing-home resident_final_Unknown`",
    "`重点人群-L.其他人群聚集场所人员_final_未知`": "`Key population L: other congregate-setting population_final_Unknown`",
    "diabetes_final_是": "diabetes_final_Yes",
    "重点人群-E.学校托幼机构人员_final_否": "Key population E: school/kindergarten personnel_final_No",
    "重点人群-A.密切接触者_final_未知": "Key population A: close contact_final_Unknown",
    "险种类型_final": "Insurance type_final",
}

n = 0
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            text = cell.text.strip()
            if text in mapping:
                new = mapping[text]
                p = cell.paragraphs[0]
                if p.runs:
                    p.runs[0].text = new
                    for r in p.runs[1:]:
                        r.text = ""
                else:
                    p.add_run(new)
                n += 1
doc.save(path)
print("translated cells:", n)
