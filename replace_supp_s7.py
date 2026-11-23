import os
import shutil
import zipfile

base = r"D:/橡树湾资料/小论文/结核病延迟ML"
src = os.path.join(base, "manuscript/SR/返修工作/Final_Supplementary Materials_Revised_clean.docx")
tmp = src + ".tmp"
newimg = os.path.join(base, "ml_results/revision_clean/FigureS7_subgroup.png")

with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == "word/media/image9.png":
            with open(newimg, "rb") as f:
                data = f.read()
        zout.writestr(item, data)

shutil.move(tmp, src)
print("replaced S7 image")
