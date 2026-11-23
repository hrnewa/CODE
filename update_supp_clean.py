import csv
import os
import shutil
from docx import Document

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
src = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised.docx")
dst = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised_clean.docx")
resdir = os.path.join(base, "ml_results/revision_clean")

shutil.copyfile(src, dst)
doc = Document(dst)


def replace_in_paragraph(p, old, new):
    if old not in p.text:
        return False
    for run in p.runs:
        if old in run.text:
            run.text = run.text.replace(old, new)
            return True
    full = p.text.replace(old, new)
    if p.runs:
        p.runs[0].text = full
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.add_run(full)
    return True


def replace_all(old, new):
    for p in doc.paragraphs:
        replace_in_paragraph(p, old, new)


def set_cell(cell, text):
    if cell.paragraphs:
        p = cell.paragraphs[0]
        if p.runs:
            p.runs[0].text = text
            for r in p.runs[1:]:
                r.text = ""
        else:
            p.add_run(text)
        for extra in cell.paragraphs[1:]:
            for r in extra.runs:
                r.text = ""
    else:
        cell.text = text


def read_csv(name):
    with open(os.path.join(resdir, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


# global numeric replacements
pairs = [
    ("60,778", "60,476"),
    ("38,590", "38,370"),
    ("22,188", "22,106"),
    ("42,544", "42,333"),
    ("18,234", "18,143"),
    ("0.703", "0.699"),
    ("0.796", "0.793"),
    ("0.702", "0.698"),
    ("0.701", "0.696"),
    ("0.794", "0.790"),
    ("0.651", "0.649"),
    ("0.678", "0.675"),
    ("0.603", "0.605"),
    ("14.2%", "15.6%"),
    ("29.1%", "28.1%"),
    ("22.6%", "21.5%"),
    ("11.3%", "10.8%"),
    ("7.9%", "8.2%"),
    ("1.1%", "1.3%"),
    ("0.571", "0.568"),
    ("0.695", "0.692"),
    ("0.673", "0.670"),
    ("0.250", "0.252"),
    ("0.31", "0.30"),
    ("0.727", "0.726"),
    ("0.874", "0.875"),
    ("0.739", "0.741"),
    ("0.648", "0.731"),
    ("0.676", "0.587"),
    ("0.740", "0.703"),
    ("84.0%", "85.5%"),
    ("0.194", "0.187"),
    ("0.198", "0.187"),
    ("0.039", "0.025"),
    ("0.545 vs 0.544", "0.544 vs 0.543"),
    ("0.2031", "0.204"),
    ("0.2029", "0.204"),
    ("-0.0002 (-0.0009 to 0.0005)", "-0.0003 (-0.0011 to 0.0004)"),
    ("0.002 (-0.001 to 0.005)", "0.003 (-0.001 to 0.006)"),
    ("0.001 (-0.001 to 0.004)", "0.002 (-0.001 to 0.005)"),
    ("0.117", "0.113"),
    ("0.037", "0.035"),
    ("0.019 (0.018-0.022)", "0.017 (0.015-0.019)"),
    ("0.018 (0.016-0.020)", "0.016 (0.013-0.019)"),
    ("0.62", "0.625"),
]
for old, new in pairs:
    replace_all(old, new)

# targeted paragraphs
p21_old = ("Among newly registered patients, 564 records (0.92%) had negative patient_delay "
           "values in the raw file. Date-order checks corrected 430 of these; the remaining 134 "
           "records (0.22%) were treated as invalid and excluded from the analytic cohort.")
p21_new = ("Among newly registered patients, 564 records (0.92%) had negative patient_delay "
           "values in the raw file; these records were excluded because the recorded first-visit "
           "date preceded the recorded symptom-onset date and the date order could not be "
           "reliably resolved.")
for p in doc.paragraphs:
    if p21_old in p.text:
        replace_in_paragraph(p, p21_old, p21_new)
        break

p82_old = ("Additional sensitivity analyses used the same split seed and hyperparameters: "
           "excluding patients whose symptom-onset date coincided with the first-visit date "
           "(n = 56,174; ROC-AUC 0.686), excluding records with capped delay of 365 days "
           "(n = 58,556; ROC-AUC 0.691), and removing symptom-onset year from the predictor set "
           "(n = 60,476; ROC-AUC 0.667).")
p82_new = ("Additional sensitivity analyses used the same split seed and hyperparameters: "
           "excluding patients whose symptom-onset date coincided with the first-visit date "
           "(n = 55,883; ROC-AUC 0.687), excluding records with capped delay of 365 days "
           "(n = 58,266; ROC-AUC 0.687), and removing symptom-onset year from the predictor set "
           "(n = 60,476; ROC-AUC 0.667).")
for p in doc.paragraphs:
    if p82_old in p.text:
        replace_in_paragraph(p, p82_old, p82_new)
        break

p84_old = ("Because county identifiers were not retained in the de-identified analysis file, "
           "we approximated spatial validation by grouping patients into 20 spatial blocks using "
           "k-means on the six log-transformed accessibility variables and performing fivefold "
           "group cross-validation.")
p84_new = ("Because county identifiers were available only for Guangxi and province identifiers "
           "were not retained, we approximated spatial validation by grouping patients into 20 "
           "spatial blocks using k-means on the six log-transformed accessibility variables and "
           "performing fivefold group cross-validation.")
for p in doc.paragraphs:
    if p84_old in p.text:
        replace_in_paragraph(p, p84_old, p84_new)
        break

p108_old = ("The difference between LightGBM and XGBoost was small and should not be interpreted "
            "as evidence of superiority.")
p108_new = ("The difference between LightGBM and XGBoost was statistically detectable but very "
            "small (ΔROC-AUC 0.001, 95% CI 0.0003-0.0019; DeLong P = 0.008) and should not be "
            "interpreted as clinically meaningful superiority.")
for p in doc.paragraphs:
    if p108_old in p.text:
        replace_in_paragraph(p, p108_old, p108_new)
        break

# ---------- baseline table S1 ----------
base_rows = {r["variable"] + "|" + r["level"]: r for r in read_csv("baseline_characteristics_clean.csv")}
cont_map = {
    "age": "age", "symptom_year": "symptom_year", "symptom_month": "symptom_month",
    "nearest_road_time": "nearest_road_time", "avg_road_time": "avg_road_time",
    "nearest_road_dist": "nearest_road_dist", "avg_road_dist": "avg_road_dist",
    "nearest_straight_dist": "nearest_straight_dist", "avg_straight_dist": "avg_straight_dist",
}
cat_maps = {
    "gender_clean": {"Male": "男", "Female": "女"},
    "age_group": {"35-64": "35-64", ">=65": ">=65", "<35": "<35"},
    "occupation_group": {
        "Farmers": "农民", "Homemakers or unemployed": "家务及待业",
        "Officials, employees or retirees": "干部职员/离退人员", "Other": "其他",
        "Students": "学生", "Service workers": "服务业",
        "Industrial workers": "工人", "Professional or technical workers": "专业技术人员",
    },
    "ethnicity_group": {
        "Han": "汉族", "Zhuang": "壮族", "Other ethnic minorities": "其他少数民族",
        "Miao": "苗族", "Dong": "侗族", "Bouyei": "布依族", "Yi": "彝族",
    },
    "is_minority": {"0": "0", "1": "1"},
    "Residence status": {
        "Local": "本地", "Intra-city migrant": "市内流动",
        "Inter-city migrant within province": "市间流动（省内流动）",
        "Inter-provincial migrant": "省间流动", "Foreign national": "外籍",
        "Hong Kong/Macau/Taiwan": "港澳台",
    },
    "Insurance type": {
        "Local resident insurance": "本地居民", "Non-local resident insurance": "异地居民",
        "Local employee insurance": "本地职工", "Non-local employee insurance": "异地职工",
    },
    "hiv_aids_final": {"No": "否", "Unknown": "未知", "Yes": "是"},
    "diabetes_final": {"No": "否", "Unknown": "未知", "Yes": "是"},
    "symptom_season": {"Spring": "春季", "Summer": "夏季", "Winter": "冬季", "Autumn": "秋季"},
    "is_winter": {"0": "0", "1": "1"},
    "patient_source_group": {
        "Referral": "转诊类", "Direct care-seeking": "主动就医类",
        "Passive detection": "被动发现类", "Active screening": "主动筛查类", "Other": "其他",
    },
    "is_referral": {"1": "1", "0": "0"},
    "is_direct_visit": {"0": "0", "1": "1"},
    "symptom_severity_group": {
        "Asymptomatic": "无症状", "Mild": "轻度", "Moderate": "中度", "Severe": "重度",
    },
    "is_asymptomatic_final": {"1": "1", "0": "0"},
    "has_typical_symptoms_final": {"0": "0", "1": "1"},
    "is_key_population_final": {"No": "否", "Yes": "是"},
}
keypop_map = {
    "Close contact": "重点人群-A.密切接触者_final",
    "Health-care worker": "重点人群-D.医务人员_final",
    "School/kindergarten personnel": "重点人群-E.学校托幼机构人员_final",
    "Custodial personnel": "重点人群-F.监管人员_final",
    "Livestock worker": "重点人群-G.养殖人员_final",
    "Dust-exposed worker or pneumoconiosis patient": "重点人群-H.接尘人员/尘肺病患者_final",
    "Psychiatric-hospital patient": "重点人群-I.精神病院患者_final",
    "Nursing-home resident": "重点人群-J.养老院居住者_final",
    "Welfare-institution resident": "重点人群-K.福利院居住者_final",
    "Other congregate-setting population": "重点人群-L.其他人群聚集场所人员_final",
}
level_ynu = {"No": "否", "Unknown": "未知", "Yes": "是"}

t = doc.tables[8]
for row in t.rows[1:]:
    var_label = row.cells[1].text.strip()
    level_label = row.cells[2].text.strip()
    var = level = None
    if level_label == "NA" and var_label in cont_map:
        var, level = cont_map[var_label], "NA"
    elif var_label in cat_maps and level_label in cat_maps[var_label]:
        var, level = var_label, cat_maps[var_label][level_label]
    elif var_label in keypop_map and level_label in level_ynu:
        var, level = keypop_map[var_label], level_ynu[level_label]
    if var and level:
        r = base_rows.get(var + "|" + level)
        if r:
            set_cell(row.cells[3], r["Overall"])
            set_cell(row.cells[4], r["No"])
            set_cell(row.cells[5], r["Yes"])

# ---------- table S3 missing data ----------
t10 = doc.tables[10]
for row in t10.rows[1:]:
    label = row.cells[0].text.strip()
    if label == "Negative patient_delay":
        set_cell(row.cells[1], "564 of 61,040 records (0.92%) in raw new-patient file")
        set_cell(row.cells[2], "Excluded; first-visit date preceded symptom-onset date")
        set_cell(row.cells[3], "Logical date error; date order could not be reliably resolved")
    if label == "Symptom text":
        set_cell(row.cells[1], "85.5% missing")
        set_cell(row.cells[2], "Derived from available text and structured severity field; missing text not assumed to indicate absence")
        set_cell(row.cells[3], "Raw symptom text not retained; formal recoding not possible")

# ---------- table S6 Elastic Net coefficients ----------
coefs = [r for r in read_csv("elasticnet_nonzero_coefficients.csv") if r["term"] != "(Intercept)"]
coefs = coefs[:29]
t13 = doc.tables[13]
for i, r in enumerate(coefs, start=1):
    if i >= len(t13.rows):
        break
    set_cell(t13.rows[i].cells[0], r["term"])
    set_cell(t13.rows[i].cells[1], f"{float(r['estimate']):.3f}")
    set_cell(t13.rows[i].cells[2], f"{abs(float(r['estimate'])):.3f}")
    set_cell(t13.rows[i].cells[3], "Positive" if float(r["estimate"]) > 0 else "Negative")

# ---------- table S7 performance ----------
metrics = {r["model"]: r for r in read_csv("model_metrics.csv")}
ens = read_csv("ensemble_metrics.csv")[0]
t14 = doc.tables[14]
perf_map = {
    "LightGBM": metrics["LightGBM"], "XGBoost": metrics["XGBoost"],
    "MeanEnsemble": ens, "RandomForest": metrics["Random forest"],
    "ElasticNet": metrics["Elastic net"],
}
for row in t14.rows[1:]:
    label = row.cells[0].text.strip()
    if label in perf_map:
        r = perf_map[label]
        set_cell(row.cells[1], f"{float(r['threshold']):.3f}".rstrip("0").rstrip("."))
        for j, key in zip(range(2, 9), ["pr_auc", "roc_auc", "accuracy", "sensitivity", "specificity", "ppv", "npv"]):
            set_cell(row.cells[j], f"{float(r[key]):.3f}")

# ---------- table S8 DCA ----------
nb = {f"{float(r['threshold']):.3f}": r for r in read_csv("net_benefit_comparison.csv")}
t15 = doc.tables[15]
for row in t15.rows[1:]:
    thr = row.cells[0].text.strip()
    if thr == "0.62":
        set_cell(row.cells[0], "0.625"); thr = "0.625"
    key = f"{float(thr):.3f}"
    if key in nb:
        r = nb[key]
        set_cell(row.cells[1], f"{float(r['full']):.3f}")
        set_cell(row.cells[2], f"{float(r['no_geo']):.3f}")
        set_cell(row.cells[3], f"{float(r['treat_all']):.3f}")

# ---------- table S9 seven-day ----------
s7 = read_csv("seven_day_metrics.csv")[0]
t16 = doc.tables[16]
row = t16.rows[1]
set_cell(row.cells[2], f"{float(s7['threshold']):.3f}".rstrip("0").rstrip("."))
set_cell(row.cells[3], f"{float(s7['event_rate']):.3f}")
for j, key in zip(range(4, 11), ["roc_auc", "pr_auc", "accuracy", "sensitivity", "specificity", "ppv", "npv"]):
    set_cell(row.cells[j], f"{float(s7[key]):.3f}")

# ---------- table S12 subgroup ----------
sub = read_csv("subgroup_performance_with_ci.csv")
t19 = doc.tables[19]
for row in t19.rows[1:]:
    key = row.cells[0].text.strip() + "|" + row.cells[1].text.strip()
    for r in sub:
        if key == r["subgroup_type"] + "|" + r["level"]:
            set_cell(row.cells[2], f"{int(r['n'])}")
            set_cell(row.cells[3], f"{int(r['events'])}")
            set_cell(row.cells[4], f"{float(r['event_rate']):.3f}")
            set_cell(row.cells[5], f"{float(r['auc']):.3f}")
            set_cell(row.cells[6], f"{float(r['auc_low']):.3f}")
            set_cell(row.cells[7], f"{float(r['auc_high']):.3f}")

# ---------- table S13 domain SHAP ----------
dom = read_csv("shap_domain_importance_rawmodel.csv")
t20 = doc.tables[20]
for i, r in enumerate(dom, start=1):
    if i >= len(t20.rows):
        break
    set_cell(t20.rows[i].cells[0], r["domain"])
    set_cell(t20.rows[i].cells[1], f"{float(r['mean_abs_shap']):.3f}")
    set_cell(t20.rows[i].cells[2], f"{float(r['percentage']):.1f}%")
    set_cell(t20.rows[i].cells[3], f"{int(r['n_features'])}")

# ---------- table S15 incremental ----------
inc = read_csv("incremental_value_same_split.csv")
t22 = doc.tables[22]
mode_map = {
    "ROC-AUC": ("ROC-AUC full", "ROC-AUC no geo", "Delta ROC-AUC"),
    "PR-AUC": ("PR-AUC full", "PR-AUC no geo", "Delta PR-AUC"),
    "Brier score": ("Brier full", "Brier no geo", "Delta Brier"),
    "Calibration intercept": ("Calibration intercept full", "Calibration intercept no geo", None),
    "Calibration slope": ("Calibration slope full", "Calibration slope no geo", None),
}
inc_map = {r["metric"]: r for r in inc}
for row in t22.rows[1:]:
    label = row.cells[0].text.strip()
    if label in mode_map:
        f_key, n_key, d_key = mode_map[label]
        f = inc_map[f_key]
        n = inc_map[n_key]
        if label in ("ROC-AUC", "PR-AUC", "Brier score"):
            set_cell(row.cells[1], f"{float(f['value']):.3f}")
            set_cell(row.cells[2], f"{float(n['value']):.3f}")
            d = inc_map[d_key]
            set_cell(row.cells[3], f"{float(d['value']):.3f} ({float(d['ci_low']):.3f} to {float(d['ci_high']):.3f})")
            p = d["p_value"]
            set_cell(row.cells[4], f"{float(p):.2f}" if p not in ("", "NA") else "NA")
        else:
            set_cell(row.cells[1], f"{float(f['value']):.3f}")
            set_cell(row.cells[2], f"{float(n['value']):.3f}")
            set_cell(row.cells[3], f"{float(n['value']) - float(f['value']):.3f}")
            set_cell(row.cells[4], "NA")

# ---------- table S16 permutation ----------
perm = read_csv("domain_permutation_importance.csv")
t23 = doc.tables[23]
for i, r in enumerate(perm, start=1):
    if i >= len(t23.rows):
        break
    set_cell(t23.rows[i].cells[0], r["domain"])
    set_cell(t23.rows[i].cells[1], f"{int(r['n_features'])}")
    set_cell(t23.rows[i].cells[2], f"{float(r['mean_drop']):.3f} ({float(r['low']):.3f}-{float(r['high']):.3f})")

# ---------- table S17 top 20 SHAP ----------
feat = read_csv("shap_feature_importance_rawmodel.csv")[:20]
t24 = doc.tables[24]
for i, r in enumerate(feat, start=1):
    if i >= len(t24.rows):
        break
    set_cell(t24.rows[i].cells[0], str(i))
    set_cell(t24.rows[i].cells[1], r["feature"])
    set_cell(t24.rows[i].cells[2], r["domain"])
    set_cell(t24.rows[i].cells[3], f"{float(r['mean_abs_shap']):.4f}")

# ---------- table S18 sensitivity ----------
sens = read_csv("sensitivity_analyses.csv")
t25 = doc.tables[25]
main_rows = ["Main analysis", "Excluding zero-delay records",
             "Excluding delays >=365 days", "Without symptom-onset year",
             "Deduplicated encodings"]
for i, label in enumerate(main_rows, start=1):
    r = next((x for x in sens if x["analysis"].startswith(label)), None)
    if r is None:
        continue
    while i >= len(t25.rows):
        t25.add_row()
    row = t25.rows[i]
    set_cell(row.cells[0], label)
    set_cell(row.cells[1], f"{int(r['n']):,}")
    set_cell(row.cells[2], f"{int(r['events']):,}")
    set_cell(row.cells[3], f"{100*float(r['event_rate']):.1f}%")
    set_cell(row.cells[4], f"{int(r['test_n']):,}")
    set_cell(row.cells[5], f"{float(r['roc_auc']):.3f}")
    set_cell(row.cells[6], f"{float(r['pr_auc']):.3f}")
    set_cell(row.cells[7], f"{float(r['brier']):.3f}")

# ---------- table S19 temporal ----------
t26 = doc.tables[26]
row = t26.rows[1]
set_cell(row.cells[1], "41,811")
set_cell(row.cells[2], "18,665")
set_cell(row.cells[3], "11,431")
set_cell(row.cells[4], "61.2%")
set_cell(row.cells[5], "0.568")
set_cell(row.cells[6], "0.670")
set_cell(row.cells[7], "0.252")
set_cell(row.cells[8], "0.228")
set_cell(row.cells[9], "0.295")

# ---------- table S20 spatial ----------
t27 = doc.tables[27]
row = t27.rows[1]
set_cell(row.cells[1], "60,476")
set_cell(row.cells[2], "38,370")
set_cell(row.cells[3], "63.4%")
set_cell(row.cells[4], "0.692")
set_cell(row.cells[5], "0.787")
set_cell(row.cells[6], "0.206")
set_cell(row.cells[7], "-0.004")
set_cell(row.cells[8], "1.08")

doc.save(dst)
print("saved", dst)
