import csv
import os
import shutil
from docx import Document

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
src = os.path.join(base, "manuscript/SR/返修工作/926Niu_Delayed entry into tuberculosis_Revised.docx")
dst = os.path.join(base, "manuscript/SR/返修工作/926Niu_Delayed entry into tuberculosis_Revised_clean.docx")
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
    n = 0
    for p in doc.paragraphs:
        if replace_in_paragraph(p, old, new):
            n += 1
    return n


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


# ---------- global numeric replacements ----------
global_pairs = [
    ("60,778", "60,476"),
    ("38,590", "38,370"),
    ("22,188", "22,106"),
    ("4,604", "4,593"),
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
    ("0.727", "0.726"),
    ("0.874", "0.875"),
    ("73.9%", "74.1%"),
    ("0.648", "0.731"),
    ("0.676", "0.587"),
    ("84.0%", "85.5%"),
    ("0.194", "0.187"),
    ("0.198", "0.187"),
    ("0.039 for treat-all", "0.025 for treat-all"),
    ("0.545 vs 0.544", "0.544 vs 0.543"),
    ("0.2031", "0.204"),
    ("0.2029", "0.204"),
    ("Δ -0.0002", "Δ -0.0003"),
    ("0.117", "0.113"),
    ("0.037", "0.035"),
    ("0.018 (95% CI 0.016-0.020)", "0.016 (95% CI 0.013-0.019)"),
    ("0.020; 95% CI 0.018-0.022", "0.017; 95% CI 0.015-0.019"),
    ("0.688 to 0.706", "0.671 to 0.705"),
    ("0.74, sensitivity", "0.703, sensitivity"),
    ("0.31", "0.30"),
    ("0.187 vs 0.039", "0.187 vs 0.025"),
    ("0.187 at 0.62", "0.187 at 0.625"),
    ("(Δ 0.001)", "(Δ 0.002)"),
    ("Δ -0.0003, 95% CI -0.0009 to 0.0005", "Δ -0.0003, 95% CI -0.0011 to 0.0004"),
    ("ΔROC-AUC 0.002)", "ΔROC-AUC 0.003)"),
    ("n = 2,089, 3.4%", "n = 2,089, 3.5%"),
    ("ΔROC-AUC 0.002, 95% CI -0.001 to 0.005", "ΔROC-AUC 0.003, 95% CI -0.001 to 0.006"),
    ("Δ 0.001, 95% CI -0.001 to 0.004", "Δ 0.002, 95% CI -0.001 to 0.005"),
    ("Δ -0.0002, 95% CI -0.0009 to 0.0005", "Δ -0.0003, 95% CI -0.0011 to 0.0004"),
    ("DeLong P = 0.29", "DeLong P = 0.09"),
    ("operating threshold of 0.62", "operating threshold of 0.625"),
    ("0.194 vs 0.039", "0.187 vs 0.025"),
    ("2126 seconds (IQR 1262-3469)", "2214.5 seconds (IQR 1215.0-3532.2)"),
    ("2035.5 seconds (IQR 1205.75-3199)", "1993.5 seconds (IQR 1190.2-3224.0)"),
    ("90.5 seconds", "221 seconds"),
    ("15,024 metres (IQR 6946-34,016.75)", "16,249 metres (IQR 6691-34,757)"),
    ("12,448 metres (IQR 6491-30,531.75)", "11,981.5 metres (IQR 6375.2-30,948.2)"),
    ("2,576 metres", "4,267.5 metres"),
]
for old, new in global_pairs:
    replace_all(old, new)

# ---------- targeted paragraph rewrites ----------
p32_old = ("The source dataset contained 67,371 pulmonary TB records from Guangxi and Guizhou. "
           "The cohort was restricted to newly registered patients (n = 61,040), because the "
           "patient-delay interval is not comparably defined for retreatment episodes. The raw "
           "new-patient file contained 564 records (0.92%) with negative patient-delay values. "
           "Date-order checks corrected 430 of these; the remaining 134 were excluded. Together "
           "with 128 records with missing residential coordinates required for geographic "
           "accessibility computation or unresolvable identifier conflicts across data sources, "
           "262 records were excluded. The final analytic cohort comprised 60,476 patients "
           "(22,106 non-delayed and 38,370 delayed).")
p32_new = ("The source dataset contained 67,371 pulmonary TB records from Guangxi and Guizhou. "
           "The cohort was restricted to newly registered patients (n = 61,040), because the "
           "patient-delay interval is not comparably defined for retreatment episodes. The raw "
           "new-patient file contained 564 records (0.92%) with negative patient-delay values; "
           "these records were excluded because the recorded first-visit date preceded the "
           "recorded symptom-onset date and the date order could not be reliably resolved. "
           "The final analytic cohort comprised 60,476 patients (22,106 non-delayed and "
           "38,370 delayed).")
for p in doc.paragraphs:
    if p32_old in p.text:
        p.runs[0].text = p.text.replace(p32_old, p32_new)
        for r in p.runs[1:]:
            r.text = ""
        break

p50_old = ("XGBoost showed nearly identical discrimination (ROC-AUC 0.698), and the difference "
           "between the two gradient-boosting models was small and did not provide evidence of "
           "superiority.")
p50_new = ("XGBoost showed nearly identical discrimination (ROC-AUC 0.698); the difference was "
           "statistically detectable but very small (ΔROC-AUC 0.001, 95% CI 0.0003-0.0019; "
           "DeLong P = 0.008) and not clinically meaningful.")
for p in doc.paragraphs:
    if p50_old in p.text:
        replace_in_paragraph(p, p50_old, p50_new)
        break

p101_old1 = ("Seventh, the primary validation used a random held-out split, which may allow "
             "location memorisation because patients from the same village share identical "
             "geographic values; temporal validation showed limited transportability (ROC-AUC "
             "0.568, calibration slope 0.30); a spatial block cross-validation using "
             "accessibility-profile clusters was close to the random-split estimate (ROC-AUC "
             "0.692), but county-level validation and province-stratified performance could not "
             "be reported because county and province identifiers were not retained in the "
             "de-identified analysis file.")
p101_new1 = ("Seventh, the primary validation used a random held-out split, which may allow "
             "location memorisation because patients from the same village share identical "
             "geographic values; temporal validation showed limited transportability (ROC-AUC "
             "0.568, calibration slope 0.30), and province-stratified discrimination was lower in "
             "Guangxi (ROC-AUC 0.681) than in Guizhou (0.707); a spatial block cross-validation "
             "using accessibility-profile clusters was close to the random-split estimate "
             "(ROC-AUC 0.692). County identifiers were available only for Guangxi, so county-level "
             "validation was restricted to that province.")
for p in doc.paragraphs:
    if p101_old1 in p.text:
        replace_in_paragraph(p, p101_old1, p101_new1)
        break

p101_old2 = ("Fifth, insurance values were partly imputed, and key-population Unknown categories "
             "were frequent and apparently patterned by data-system changes, so these domains "
             "should not be interpreted as individual risk factors.")
p101_new2 = ("Fifth, insurance values were imputed from residence and occupation for 90.1% of "
             "patients (100% in Guangxi and 46.6% in Guizhou), and key-population Unknown "
             "categories were frequent and apparently patterned by data-system changes, so these "
             "domains should not be interpreted as individual risk factors.")
for p in doc.paragraphs:
    if p101_old2 in p.text:
        replace_in_paragraph(p, p101_old2, p101_new2)
        break

p89_old = ("Insurance values were missing for a substantial minority of patients and were "
           "imputed from residence and occupation, so insurance-related findings should be "
           "interpreted cautiously.")
p89_new = ("Insurance values were imputed from residence and occupation for 90.1% of patients "
           "(100% in Guangxi and 46.6% in Guizhou), so insurance-related findings should be "
           "interpreted cautiously.")
for p in doc.paragraphs:
    if p89_old in p.text:
        replace_in_paragraph(p, p89_old, p89_new)
        break

# ---------- Table 0 baseline ----------
base_rows = {r["variable"] + "|" + r["level"]: r for r in read_csv("baseline_characteristics_clean.csv")}
t0 = doc.tables[0]
label_map = {
    "Age, years": ("age", "NA"),
    "Nearest road-network travel time": ("nearest_road_time", "NA"),
    "Average road-network travel time": ("avg_road_time", "NA"),
    "Nearest road-network distance": ("nearest_road_dist", "NA"),
    "Average road-network distance": ("avg_road_dist", "NA"),
    "Sex: Male": ("gender_clean", "男"),
    "Sex: Female": ("gender_clean", "女"),
    "Farmers": ("occupation_group", "农民"),
    "Homemakers or unemployed": ("occupation_group", "家务及待业"),
    "Officials, employees or retirees": ("occupation_group", "干部职员/离退人员"),
    "Other": ("occupation_group", "其他"),
    "Students": ("occupation_group", "学生"),
    "Service workers": ("occupation_group", "服务业"),
    "Industrial workers": ("occupation_group", "工人"),
    "Professional or technical workers": ("occupation_group", "专业技术人员"),
    "Ethnic minority status: No": ("is_minority", "0"),
    "Ethnic minority status: Yes": ("is_minority", "1"),
    "Local": ("户籍地址类别", "本地"),
    "Intra-city migrant": ("户籍地址类别", "市内流动"),
    "Inter-city migrant within province": ("户籍地址类别", "市间流动（省内流动）"),
    "Inter-provincial migrant": ("户籍地址类别", "省间流动"),
    "Local resident insurance": ("险种类型_final", "本地居民"),
    "Non-local resident insurance": ("险种类型_final", "异地居民"),
    "Local employee insurance": ("险种类型_final", "本地职工"),
    "Non-local employee insurance": ("险种类型_final", "异地职工"),
}
for row in t0.rows[1:]:
    label = row.cells[0].text.strip()
    if label in label_map:
        key = "|".join(label_map[label])
        if key in base_rows:
            r = base_rows[key]
            set_cell(row.cells[1], r["Overall"])
            set_cell(row.cells[2], r["No"])
            set_cell(row.cells[3], r["Yes"])

# ---------- Table 1 model performance ----------
metrics = {r["model"]: r for r in read_csv("model_metrics.csv")}
ens = read_csv("ensemble_metrics.csv")[0]
t1 = doc.tables[1]
perf_map = {
    "LightGBM": ("LightGBM", metrics["LightGBM"]),
    "XGBoost": ("XGBoost", metrics["XGBoost"]),
    "MeanEnsemble": ("MeanEnsemble", ens),
    "RandomForest": ("Random forest", metrics["Random forest"]),
    "ElasticNet": ("Elastic net", metrics["Elastic net"]),
}
for row in t1.rows[1:]:
    label = row.cells[0].text.strip()
    if label in perf_map:
        _, r = perf_map[label]
        thr_txt = "0.50" if label == "MeanEnsemble" else f"{float(r['threshold']):.3f}".rstrip("0").rstrip(".")
        set_cell(row.cells[1], thr_txt)
        for j, key in zip(range(2, 9), ["roc_auc", "pr_auc", "accuracy", "sensitivity", "specificity", "ppv", "npv"]):
            set_cell(row.cells[j], f"{float(r[key]):.3f}")

# ---------- Table 2 DCA ----------
nb = {f"{float(r['threshold']):.3f}": r for r in read_csv("net_benefit_comparison.csv")}
t2 = doc.tables[2]
for row in t2.rows[1:]:
    thr = row.cells[0].text.strip()
    if thr == "0.62":
        set_cell(row.cells[0], "0.625")
        thr = "0.625"
    key = f"{float(thr):.3f}"
    if key in nb:
        r = nb[key]
        set_cell(row.cells[1], f"{float(r['full']):.3f}")
        set_cell(row.cells[2], f"{float(r['no_geo']):.3f}")
        set_cell(row.cells[3], f"{float(r['treat_all']):.3f}")

# ---------- Table 3 seven-day ----------
s7 = read_csv("seven_day_metrics.csv")[0]
t3 = doc.tables[3]
row = t3.rows[1]
set_cell(row.cells[2], f"{float(s7['threshold']):.3f}".rstrip("0").rstrip("."))
set_cell(row.cells[3], f"{float(s7['event_rate']):.3f}")
for j, key in zip(range(4, 11), ["roc_auc", "pr_auc", "accuracy", "sensitivity", "specificity", "ppv", "npv"]):
    set_cell(row.cells[j], f"{float(s7[key]):.3f}")

doc.save(dst)
print("saved", dst)
