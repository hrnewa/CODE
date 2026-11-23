import os
import shutil
import zipfile

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
src = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised_clean.docx")
tmp = src + ".tmp"
resdir = os.path.join(base, "ml_results/revision_clean")

mapping = {
    "word/media/image1.png": os.path.join(resdir, "Figure1_flow_clean.png"),
    "word/media/image2.png": os.path.join(resdir, "Figure2_ROC.png"),
    "word/media/image3.png": os.path.join(resdir, "Figure3_calibration.png"),
    "word/media/image4.png": os.path.join(resdir, "Figure4_SHAP_beeswarm.png"),
}

with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename in mapping:
            with open(mapping[item.filename], "rb") as f:
                data = f.read()
        zout.writestr(item, data)

shutil.move(tmp, src)
print("replaced images")
