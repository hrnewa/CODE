import os
import shutil
import zipfile

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
src = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised_clean.docx")
tmp = src + ".tmp"
resdir = os.path.join(base, "ml_results/revision_clean")

mapping = {
    "word/media/image2.png": os.path.join(resdir, "Figure3_calibration.png"),
    "word/media/image3.png": os.path.join(resdir, "FigureS2_DCA.png"),
    "word/media/image4.png": os.path.join(resdir, "FigureS3_variable_importance.png"),
    "word/media/image10.png": os.path.join(resdir, "FigureS8_domain_shap.png"),
    "word/media/image11.png": os.path.join(resdir, "FigureS9_PDP.png"),
}

with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename in mapping:
            with open(mapping[item.filename], "rb") as f:
                data = f.read()
        zout.writestr(item, data)

shutil.move(tmp, src)
print("replaced supplement images")
