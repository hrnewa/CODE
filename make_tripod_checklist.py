from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import sys

OUT_DOCX = sys.argv[1]
OUT_MD = sys.argv[2]

TITLE = ("Predicting Delayed Entry into TB-Designated Care in Mountainous, Multi-Ethnic China: "
         "A Retrospective Prediction-Modelling Study Incorporating Fine-Scale Geographic Accessibility")

rows = [
    ("TITLE", "Title", "1", "D;E",
     "Identify the study as developing or evaluating the performance of a multivariable prediction model, the target population, and the outcome to be predicted",
     "Main p1"),
    ("ABSTRACT", "Abstract", "2", "D;E",
     "See TRIPOD+AI for Abstracts checklist",
     "Main p1-2 (structured Background, Methods, Results, Conclusions); all 13 abstract items addressed"),
    ("INTRODUCTION", "Background", "3a", "D;E",
     "Explain the healthcare context (including whether diagnostic or prognostic) and rationale for developing or evaluating the prediction model, including references to existing models",
     "Main p2-4 (Background)"),
    ("", "", "3b", "D;E",
     "Describe the target population and the intended purpose of the prediction model in the context of the care pathway, including its intended users (e.g., healthcare professionals, patients, public)",
     "Main p3-4 (aims; retrospective risk characterisation and area-level planning); p6-7 (model development); p13-17 (Discussion)"),
    ("", "", "3c", "D;E",
     "Describe any known health inequalities between sociodemographic groups",
     "Main p3 (ethnic diversity and uneven access); p16-17 (ethnicity, migration and social interpretation); Suppl S12 p37 (age, sex, residence subgroups); S21 p44 (province)"),
    ("", "Objectives", "4", "D;E",
     "Specify the study objectives, including whether the study describes the development or validation of a prediction model (or both)",
     "Main p3 (final Background paragraph); p6-7 (development plus internal, temporal and spatial evaluation)"),
    ("METHODS", "Data", "5a", "D;E",
     "Describe the sources of data separately for the development and evaluation datasets (e.g., randomised trial, cohort, routine care or registry data), the rationale for using these data, and representativeness of the data",
     "Main p4-5 (three linked routine data sources plus Baidu Maps); Suppl Methods 1 p4; S4 p30"),
    ("", "", "5b", "D;E",
     "Specify the dates of the collected participant data, including start and end of participant accrual; and, if applicable, end of follow-up",
     "Main p4 (registration 20 September 2017-31 December 2024); Suppl Methods 1-2 p4-5"),
    ("", "Participants", "6a", "D;E",
     "Specify key elements of the study setting (e.g., primary care, secondary care, general population) including the number and location of centres",
     "Main p4-5 (Guangxi and Guizhou, China; 199 TB-designated facilities in the 2024 registries); Suppl S1 p18-24"),
    ("", "", "6b", "D;E",
     "Describe the eligibility criteria for study participants",
     "Main p4-5 (newly registered pulmonary TB patients; exclusions); Figure 1 p4; Suppl S3 p29"),
    ("", "", "6c", "D;E",
     "Give details of any treatments received, and how they were handled during model development or evaluation, if relevant",
     "Not applicable. Observational prediction study; no study treatment was administered or evaluated, and TB treatment initiation occurs after the predicted outcome (Main p5)."),
    ("", "Data preparation", "7", "D;E",
     "Describe any data pre-processing and quality checking, including whether this was similar across relevant sociodemographic groups",
     "Main p5-6; Suppl Methods 1 p4 and 6 p12-13; S2 p25-28; S3 p29"),
    ("", "Outcome", "8a", "D;E",
     "Clearly define the outcome that is being predicted and the time horizon, including how and when assessed, the rationale for choosing this outcome, and whether the method of outcome assessment is consistent across sociodemographic groups",
     "Main p1-2 and p5 (symptom onset to first recorded visit to a TB-designated facility; 14-day horizon); Suppl Methods 3 p6-7; S3 p29"),
    ("", "", "8b", "D;E",
     "If outcome assessment requires subjective interpretation, describe the qualifications and demographic characteristics of the outcome assessors",
     "Not applicable. The outcome is derived from recorded symptom-onset and first-visit dates in routine surveillance data, without subjective assessor judgement (Main p5)."),
    ("", "", "8c", "D;E",
     "Report any actions to blind assessment of the outcome to be predicted",
     "Not applicable. Retrospective analysis of de-identified routine records; outcome was computed from date fields before modelling and no human outcome assessor was involved (Main p5)."),
    ("", "Predictors", "9a", "D",
     "Describe the choice of initial predictors (e.g., literature, previous models, all available predictors) and any pre-selection of predictors before model building",
     "Main p5-6; Suppl Methods 4 p8-11"),
    ("", "", "9b", "D;E",
     "Clearly define all predictors, including how and when they were measured (and any actions to blind assessment of predictors for the outcome and other predictors)",
     "Main p5-6 (nine domains; registration-time measurement); Suppl S2 p25-28; S3 p29; Methods 4.1-4.5 p10-11"),
    ("", "", "9c", "D;E",
     "If predictor measurement requires subjective interpretation, describe the qualifications and demographic characteristics of the predictor assessors",
     "Not applicable. Predictors were extracted from routine administrative, surveillance, insurance and geographic records; none required subjective assessor interpretation (Main p5-6)."),
    ("", "Sample size", "10", "D;E",
     "Explain how the study size was arrived at (separately for development and evaluation), and justify that the study size was sufficient to answer the research question. Include details of any sample size calculation",
     "Main p5 (all eligible records; no formal sample-size calculation); Suppl Methods 2 p5. Final cohort n = 60,476; training 42,333; test 18,143."),
    ("", "Missing data", "11", "D;E",
     "Describe how missing data were handled. Provide reasons for omitting any data",
     "Main p6; Suppl Methods 5 p12; S3 p29"),
    ("", "Analytical methods", "12a", "D",
     "Describe how the data were used (e.g., for development and evaluation of model performance) in the analysis, including whether the data were partitioned, considering any sample size requirements",
     "Main p6-7 (stratified 70:30 split; five-fold CV in training; held-out test); Suppl Methods 6 p12-13; Methods 11 p16"),
    ("", "", "12b", "D",
     "Depending on the type of model, describe how predictors were handled in the analyses (functional form, rescaling, transformation, or any standardisation)",
     "Main p5-6 (log(x+1), splines, encoding, pooling); Suppl Methods 6 p12-13; S2 p25-28"),
    ("", "", "12c", "D",
     "Specify the type of model, rationale, all model-building steps, including any hyperparameter tuning, and method for internal validation",
     "Main p6-7; Suppl Methods 7 p13-14; S14 p39 (search ranges and selected values)"),
    ("", "", "12d", "D;E",
     "Describe if and how any heterogeneity in estimates of model parameter values and model performance was handled and quantified across clusters (e.g., hospitals, countries)",
     "Main p13; Suppl S19 p43 (temporal), S20 p43 (spatial block CV), S21 p44 (province). No cluster-random-effects model; heterogeneity assessed by stratified validation."),
    ("", "", "12e", "D;E",
     "Specify all measures and plots used (and their rationale) to evaluate model performance (e.g., discrimination, calibration, clinical utility) and, if relevant, to compare multiple models",
     "Main p7 and p8-13; Tables 2-4; Figures 2-4; Suppl S7-S12 p35-37 and S15-S27 p40-48"),
    ("", "", "12f", "E",
     "Describe any model updating (e.g., recalibration) arising from the model evaluation, either overall or for particular sociodemographic groups or settings",
     "No model updating was performed. Temporal validation was used only as a transportability check (Main p13; Suppl S19 p43)."),
    ("", "", "12g", "E",
     "For model evaluation, describe how the model predictions were calculated (e.g., formula, code, object, application programming interface)",
     "Main p7 and p18 (fitted LightGBM; predictions generated in R); Suppl Methods 11 p16 (pseudocode). Full analysis code available from the corresponding author on reasonable request."),
    ("", "Class imbalance", "13", "D;E",
     "If class imbalance methods were used, state why and how this was done, and any subsequent methods to recalibrate the model or the model predictions",
     "Main p6-7 (outcome-stratified split; PR-AUC reported); Suppl Methods 8 p15. No resampling or threshold recalibration; Youden-index threshold used."),
    ("", "Fairness", "14", "D;E",
     "Describe any approaches that were used to address model fairness and their rationale",
     "Main p13 and p16-17 (age, sex, residence and province subgroup performance; cautious interpretation of ethnicity and migration); Suppl S12 p37; S21 p44. No formal fairness mitigation was applied."),
    ("", "Model output", "15", "D",
     "Specify the output of the prediction model (e.g., probabilities, classification). Provide details and rationale for any classification and how the thresholds were identified",
     "Main p7 (predicted probability; Youden-index threshold from training predictions); Table 2 p9; Suppl S10 p36"),
    ("", "Training versus evaluation", "16", "D;E",
     "Identify any differences between the development and evaluation data in healthcare setting, eligibility criteria, outcome, and predictors",
     "Main p6-7 (random split within the same cohort); p13 (temporal validation uses later onset years); Suppl S19 p43"),
    ("", "Ethical approval", "17", "D;E",
     "Name the institutional research board or ethics committee that approved the study and describe the participant-informed consent or the ethics committee waiver of informed consent",
     "Main p5 (Biomedical Ethics Review Committee, Tongji Medical College, HUST; S058, 23 April 2025; consent waived); p18 (Declarations)"),
    ("OPEN SCIENCE", "Funding", "18a", "D;E",
     "Give the source of funding and the role of the funders for the present study",
     "Main p18 (Funding: no specific grant from any funding agency)"),
    ("", "Conflicts of interest", "18b", "D;E",
     "Declare any conflicts of interest and financial disclosures for all authors",
     "Main p19 (Competing interests: none declared)"),
    ("", "Protocol", "18c", "D;E",
     "Indicate where the study protocol can be accessed or state that a protocol was not prepared",
     "Main p19 (no separate study protocol was prepared)"),
    ("", "Registration", "18d", "D;E",
     "Provide registration information for the study, including register name and registration number, or state that the study was not registered",
     "Main p19 (not prospectively registered); p18 (clinical trial number: not applicable)"),
    ("", "Data sharing", "18e", "D;E",
     "Provide details of the availability of the study data",
     "Main p18 (data available from the named provincial data holders under licence; not publicly available)"),
    ("", "Code sharing", "18f", "D;E",
     "Provide details of the availability of the analytical code",
     "Main p18 (analysis code as pseudocode and available from the corresponding author on reasonable request); Suppl Methods 11 p16"),
    ("", "Patient & public involvement", "19", "D;E",
     "Provide details of any patient and public involvement during the design, conduct, reporting, interpretation, or dissemination of the study or state no involvement",
     "Main p19 (no patient or public involvement)"),
    ("RESULTS", "Participants", "20a", "D;E",
     "Describe the flow of participants through the study, including the number of participants with and without the outcome and, if applicable, a summary of the follow-up time. A diagram may be helpful",
     "Main p5 and Figure 1 p4; Suppl S3 p29"),
    ("", "", "20b", "D;E",
     "Report the characteristics overall and, where applicable, for each data source or setting, including the key dates, key predictors (including demographics), treatments received, sample size, number of outcome events, follow-up time, and amount of missing data. A table may be helpful. Report any differences across key demographic groups",
     "Main p7 and Table 1 p7; Suppl S1 p18-24; S2 p25-28; S3 p29"),
    ("", "", "20c", "E",
     "For model evaluation, show a comparison with the development data of the distribution of important predictors (demographics, predictors, and outcome)",
     "Main p13; Suppl S19 p43 (temporal) and S21 p44 (province). Predictor distributions across evaluation strata are not tabulated separately."),
    ("", "Model development", "21", "D;E",
     "Specify the number of participants and outcome events in each analysis (e.g., for model development, hyperparameter tuning, model evaluation)",
     "Main p5-9; Suppl Methods 2 p5 and 6 p12-13; S18 p42; S19 p43"),
    ("", "Model specification", "22", "D",
     "Provide details of the full prediction model (e.g., formula, code, object, application programming interface) to allow predictions in new individuals and to enable third-party evaluation and implementation, including any restrictions to access or re-use",
     "Hyperparameters in Suppl S14 p39; pseudocode in Suppl Methods 11 p16; full fitted model and analysis code available from the corresponding author (Main p18). No public model object or repository."),
    ("", "Model performance", "23a", "D;E",
     "Report model performance estimates with confidence intervals, including for any key subgroups (e.g., sociodemographic). Consider plots to aid presentation",
     "Main p8-13; Tables 2-4; Figures 2-4; Suppl S7-S12 p35-37 and S15-S27 p40-48 (bootstrap CIs in S27 p47)"),
    ("", "", "23b", "D;E",
     "If examined, report results of any heterogeneity in model performance across clusters",
     "Main p13; Suppl S19-S21 p43-44"),
    ("", "Model updating", "24", "E",
     "Report the results from any model updating, including the updated model and subsequent performance",
     "Not applicable; no model updating was performed."),
    ("DISCUSSION", "Interpretation", "25", "D;E",
     "Give an overall interpretation of the main results, including issues of fairness in the context of the objectives and previous studies",
     "Main p13-17 (Discussion, including ethnicity/migration and fairness cautions)"),
    ("", "Limitations", "26", "D;E",
     "Discuss any limitations of the study (such as a non-representative sample, sample size, overfitting, missing data) and their effects on any biases, statistical uncertainty, and generalizability",
     "Main p16-17 (Strengths and limitations)"),
    ("", "Usability of the model in the context of current care", "27a", "D",
     "Describe how poor quality or unavailable input data (e.g., predictor values) should be assessed and handled when implementing the prediction model",
     "Main p6 (missingness handling) and p16-17 (data-quality limitations); Suppl S3 p29"),
    ("", "", "27b", "D",
     "Specify whether users will be required to interact in the handling of the input data or use of the model, and what level of expertise is required of users",
     "Main p3-4 (intended users and planning use) and p13-17 (not for individual pre-delay screening); implementation would require analytical and programme expertise."),
    ("", "", "27c", "D;E",
     "Discuss any next steps for future research, with a specific view to applicability and generalizability of the model",
     "Main p17-18 (Conclusions: external, prospective and spatial validation before programme use)"),
]

doc = Document()
sec = doc.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
for attr in ("top_margin", "bottom_margin"):
    setattr(sec, attr, Cm(1.4))
for attr in ("left_margin", "right_margin"):
    setattr(sec, attr, Cm(1.4))

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(8)
normal.paragraph_format.space_after = Pt(0)
normal.paragraph_format.line_spacing = 1.0

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("TRIPOD+AI Checklist")
r.bold = True
r.font.size = Pt(16)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Reporting checklist for prediction-model studies using regression or machine learning")
r.italic = True
r.font.size = Pt(9)

for line in [
    ("Manuscript: ", TITLE),
    ("Journal: ", "Scientific Reports (revision)"),
    ("Checklist version: ", "TRIPOD+AI, 11 January 2024 (27 items; 52 subitems)"),
    ("Prepared: ", "23 November 2026"),
    ("Page references: ", "main text PDF (21 pp) and supplementary PDF (58 pp) generated from the submitted DOCX files"),
]:
    p = doc.add_paragraph()
    r = p.add_run(line[0]); r.bold = True; r.font.size = Pt(9)
    r = p.add_run(line[1]); r.font.size = Pt(9)

p = doc.add_paragraph()
r = p.add_run("Abbreviations: D = development; E = evaluation; D;E = both. Page numbers refer to the submitted PDFs and may shift after journal typesetting.")
r.italic = True
r.font.size = Pt(8)

table = doc.add_table(rows=1, cols=5)
table.style = "Table Grid"
table.alignment = WD_TABLE_ALIGNMENT.CENTER
widths = [Cm(2.3), Cm(4.0), Cm(1.0), Cm(1.2), Cm(18.4)]
hdr = table.rows[0].cells
for i, text in enumerate(["Section / Topic", "Item", "No.", "D/E", "Checklist item and location in the revised manuscript"]):
    hdr[i].text = ""
    pp = hdr[i].paragraphs[0]
    rr = pp.add_run(text)
    rr.bold = True
    rr.font.size = Pt(8)
    pp.alignment = WD_ALIGN_PARAGRAPH.CENTER

for section, topic, num, de, item, loc in rows:
    cells = table.add_row().cells
    vals = [section, topic, num, de, item]
    for i, v in enumerate(vals):
        cells[i].text = ""
        pp = cells[i].paragraphs[0]
        rr = pp.add_run(v)
        rr.font.size = Pt(7.5)
        if i == 2 or i == 3:
            pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    lp = cells[4].add_paragraph()
    rr = lp.add_run("Reported: " + loc)
    rr.italic = True
    rr.font.size = Pt(7.5)

for row in table.rows:
    for i, cell in enumerate(row.cells):
        cell.width = widths[i]

p = doc.add_paragraph()
r = p.add_run("Notes")
r.bold = True
r.font.size = Pt(9)
notes = [
    "1. Item 2: the abstract is structured and reports the objective, data sources, participants, outcome, predictors, sample size, model type, performance, and conclusions; it follows the TRIPOD+AI for Abstracts checklist (Main p1-2).",
    "2. Items 8b, 8c, 9c and 6c are marked not applicable because the study uses de-identified routine records and date-based outcomes, with no subjective outcome or predictor assessment and no study treatment.",
    "3. The Declarations now include a funding statement (no specific grant), author contributions, a statement that no separate protocol was prepared, a statement that the study was not prospectively registered, and a statement that there was no patient or public involvement (Main p18-19).",
    "4. Item 22: the full fitted model is not publicly deposited; hyperparameters, pseudocode and an offer of the analysis code are provided. A public repository (GitHub/Zenodo) would strengthen compliance.",
    "5. This checklist was completed against the TRIPOD+AI 27-item checklist (Collins et al., BMJ 2024;385:e078378).",
]
for n in notes:
    p = doc.add_paragraph()
    r = p.add_run(n)
    r.font.size = Pt(7.5)

footer = sec.footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = fp.add_run()
fld1 = OxmlElement("w:fldSimple"); fld1.set(qn("w:instr"), "PAGE")
run._r.addnext(fld1)
r2 = fp.add_run(" / ")
fld2 = OxmlElement("w:fldSimple"); fld2.set(qn("w:instr"), "NUMPAGES")
r2._r.addnext(fld2)

doc.save(OUT_DOCX)

with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("# TRIPOD+AI Checklist\n\n")
    f.write("**Manuscript:** " + TITLE + "\n\n")
    f.write("**Journal:** Scientific Reports (revision)\n\n")
    f.write("**Checklist version:** TRIPOD+AI, 11 January 2024 (27 items; 52 subitems)\n\n")
    f.write("**Prepared:** 23 November 2026\n\n")
    f.write("**Page references:** main text PDF (21 pp) and supplementary PDF (58 pp) generated from the submitted DOCX files.\n\n")
    f.write("D = development; E = evaluation; D;E = both. Page numbers refer to the submitted PDFs and may shift after journal typesetting.\n\n")
    f.write("| Section / Topic | Item | No. | D/E | Checklist item | Reported in revised manuscript |\n")
    f.write("|---|---|---|---|---|---|\n")
    for section, topic, num, de, item, loc in rows:
        f.write("| %s | %s | %s | %s | %s | %s |\n" % (section, topic, num, de, item.replace("|", "\\|"), loc.replace("|", "\\|")))
    f.write("\n## Notes\n\n")
    for n in notes:
        f.write("- " + n + "\n")

print("wrote", OUT_DOCX, OUT_MD)
