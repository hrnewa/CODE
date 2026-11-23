import csv
import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
path = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised_clean.docx")
resdir = os.path.join(base, "ml_results/revision_clean")
doc = Document(path)


def read_csv(name):
    with open(os.path.join(resdir, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def set_cell(cell, text, bold=False, size=8):
    cell.text = ""
    p = cell.paragraphs[0]
    run = p.add_run(str(text))
    run.bold = bold
    run.font.size = Pt(size)


def add_caption(text):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(9)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)
    return p


def add_table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    for j, h in enumerate(headers):
        set_cell(t.rows[0].cells[j], h, bold=True, size=8)
    for row in rows:
        cells = t.add_row().cells
        for j, val in enumerate(row):
            set_cell(cells[j], val, size=8)
    return t


anchor = None
for p in doc.paragraphs:
    if "III. Supplementary Figures" in p.text:
        anchor = p._p
        break
if anchor is None:
    raise RuntimeError("anchor not found")

new_items = []

# S21 province-stratified performance
sub = read_csv("subgroup_performance.csv")
rows = []
for r in sub:
    if r["model"] == "LightGBM" and r["group"] == "Province":
        rows.append([r["level"], f"{int(r['n']):,}", f"{int(r['events']):,}",
                     f"{100*float(r['event_rate']):.1f}%", f"{float(r['roc_auc']):.3f}",
                     f"{float(r['pr_auc']):.3f}", f"{float(r['brier']):.3f}",
                     f"{float(r['cal_intercept']):.3f}", f"{float(r['cal_slope']):.3f}"])
new_items.append(add_caption("Supplementary Table S21. Province-stratified test-set performance of the final LightGBM model."))
new_items.append(add_table(["Province", "n", "Events", "Event rate", "ROC-AUC", "PR-AUC",
                            "Brier score", "Calibration intercept", "Calibration slope"], rows))

# S22 location comparator
comp = read_csv("location_comparator_models.csv")
rows = []
for r in comp:
    rows.append([r["model"], f"{int(float(r['n_predictors']))}", f"{float(r['roc_auc']):.3f}",
                 f"{float(r['pr_auc']):.3f}", f"{float(r['brier']):.3f}",
                 f"{float(r['cal_intercept']):.3f}", f"{float(r['cal_slope']):.3f}"])
new_items.append(add_caption("Supplementary Table S22. Location-identifier comparator models fitted with the same split, preprocessing, and LightGBM hyperparameters."))
new_items.append(add_table(["Model", "Predictors", "ROC-AUC", "PR-AUC", "Brier score",
                            "Calibration intercept", "Calibration slope"], rows))

# S23 key-pop unknown by year and province
kp = read_csv("keypop_unknown_by_year_province_compact.csv")
rows = []
for r in kp:
    n = int(r["n"]); anyu = int(r["any_unknown"])
    rows.append([r["symptom_year"], r["province"], f"{n:,}",
                 f"{anyu:,} ({100*anyu/n:.1f}%)", f"{int(r['close_contact']):,}",
                 f"{int(r['custodial']):,}", f"{int(r['livestock']):,}",
                 f"{int(r['nursing_home']):,}"])
new_items.append(add_caption("Supplementary Table S23. Key-population \u201cUnknown\u201d missingness by calendar year and province."))
new_items.append(add_table(["Onset year", "Province", "n", "Any subtype unknown",
                            "Close contact", "Custodial", "Livestock", "Nursing home"], rows))

# S24 subtype totals
sub_tot = read_csv("keypop_unknown_subtype_totals.csv")
sub_prov = {r["subtype"]: r for r in read_csv("keypop_unknown_subtype_by_province.csv")}
name_map = {
    "重点人群-A.密切接触者_final": "Close contact",
    "重点人群-D.医务人员_final": "Health-care worker",
    "重点人群-E.学校托幼机构人员_final": "School/kindergarten personnel",
    "重点人群-F.监管人员_final": "Custodial personnel",
    "重点人群-G.养殖人员_final": "Livestock worker",
    "重点人群-H.接尘人员/尘肺病患者_final": "Dust-exposed worker",
    "重点人群-I.精神病院患者_final": "Psychiatric-hospital patient",
    "重点人群-J.养老院居住者_final": "Nursing-home resident",
    "重点人群-K.福利院居住者_final": "Welfare-institution resident",
    "重点人群-L.其他人群聚集场所人员_final": "Other congregate setting",
}
rows = []
for r in sub_tot:
    st = r["subtype"]
    p = sub_prov.get(st, {})
    rows.append([name_map.get(st, st), f"{int(r['unknown_n']):,} ({float(r['pct']):.1f}%)",
                 f"{int(p.get('Guangxi', 0)):,}", f"{int(p.get('Guizhou', 0)):,}"])
new_items.append(add_caption("Supplementary Table S24. Key-population subtype \u201cUnknown\u201d totals overall and by province."))
new_items.append(add_table(["Subtype", "Overall n (%)", "Guangxi n", "Guizhou n"], rows))

# S25 insurance imputation
ins = read_csv("insurance_imputation_summary.csv")
rows = []
total_n = sum(int(r["n"]) for r in ins)
total_imp = sum(int(r["imputed"]) for r in ins)
for r in ins:
    rows.append([r["province"], f"{int(r['n']):,}", f"{int(r['imputed']):,} ({float(r['imputed_pct']):.1f}%)",
                 f"{int(r['n']) - int(r['imputed']):,} ({100 - float(r['imputed_pct']):.1f}%)"])
rows.append(["Overall", f"{total_n:,}", f"{total_imp:,} ({100*total_imp/total_n:.1f}%)",
             f"{total_n-total_imp:,} ({100*(total_n-total_imp)/total_n:.1f}%)"])
new_items.append(add_caption("Supplementary Table S25. Insurance-type imputation from residence and occupation."))
new_items.append(add_table(["Province", "n", "Imputed n (%)", "Recorded n (%)"], rows))

# S26 area-level calibration
area = read_csv("area_level_calibration.csv")
rows = []
for r in area:
    rows.append([r["group"], f"{int(r['n_areas'])}", f"{float(r['weighted_r']):.3f}",
                 f"{float(r['slope']):.2f}", f"{float(r['intercept']):.3f}",
                 f"{float(r['mean_abs_diff']):.3f}"])
new_items.append(add_caption("Supplementary Table S26. Area-level agreement between predicted and observed delay proportions."))
new_items.append(add_table(["Area level", "n areas", "Weighted correlation", "Slope", "Intercept",
                            "Mean absolute difference"], rows))

# S27 bootstrap CIs
boot = read_csv("bootstrap_metrics.csv")
label_map = {
    "lgb_auc": "LightGBM ROC-AUC", "lgb_pr": "LightGBM PR-AUC", "lgb_brier": "LightGBM Brier score",
    "xgb_auc": "XGBoost ROC-AUC", "xgb_pr": "XGBoost PR-AUC", "xgb_brier": "XGBoost Brier score",
    "d_auc": "Difference in ROC-AUC (LightGBM - XGBoost)",
    "d_pr": "Difference in PR-AUC (LightGBM - XGBoost)",
    "d_brier": "Difference in Brier score (LightGBM - XGBoost)",
    "lgb_acc": "LightGBM accuracy",
}
rows = []
for r in boot:
    p = r["p_value"]
    rows.append([label_map.get(r["metric"], r["metric"]), f"{float(r['estimate']):.3f}",
                 f"{float(r['ci_low']):.3f} to {float(r['ci_high']):.3f}",
                 f"{float(p):.3f}" if p not in ("", "NA") else "\u2014"])
new_items.append(add_caption("Supplementary Table S27. Bootstrap confidence intervals and DeLong test for test-set performance."))
new_items.append(add_table(["Metric", "Estimate", "95% CI", "P value"], rows))

for el in new_items:
    anchor.addprevious(el._p if hasattr(el, "_p") else el._tbl)

# update S20 note
for p in doc.paragraphs:
    if p.text.startswith("Note. County identifiers were not retained"):
        p.text = ("Note. County identifiers were available only for Guangxi; spatial blocks were defined "
                  "by k-means clustering of the six log-transformed accessibility variables, and "
                  "fivefold group cross-validation was performed. This is not equivalent to holding out "
                  "whole counties.")
        break

doc.save(path)
print("added new tables")
