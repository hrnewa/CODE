from PIL import Image, ImageDraw, ImageFont

src = r"D:/橡树湾资料/小论文/结核病延迟ML/ml_results/incremental_reanalysis/Figure1_flow_revised.png"
dst = r"D:/橡树湾资料/小论文/结核病延迟ML/ml_results/revision_clean/Figure1_flow_clean.png"

im = Image.open(src).convert("RGB")
d = ImageDraw.Draw(im)
white = (255, 255, 255)
black = (35, 35, 35)
font_path = r"C:/Windows/Fonts/calibri.ttf"
f20 = ImageFont.truetype(font_path, 21)
f18 = ImageFont.truetype(font_path, 18)

def center_text(lines, box, font, gap=28):
    x0, y0, x1, y1 = box
    total = len(lines) * gap
    yy = y0 + ((y1 - y0) - total) / 2 + 4
    for line in lines:
        w = d.textlength(line, font=font)
        d.text(((x0 + x1 - w) / 2, yy), line, font=font, fill=black)
        yy += gap

# final cohort box
d.rectangle((200, 570, 645, 660), fill=white)
center_text(["Final analytical cohort for model", "development", "60476 records"],
            (195, 565, 650, 665), f20, gap=28)

# exclusion box: clear interior and redraw border
d.rectangle((750, 456, 1195, 544), fill=white)
d.rectangle((740, 546, 1210, 575), fill=white)
d.rectangle((744, 452, 1201, 548), outline=black, width=2)
center_text(["Excluded during outcome cleaning",
             "564 records with negative delay (0.92%)"],
            (750, 458, 1195, 542), f18, gap=28)

# training and test boxes
d.rectangle((55, 1180, 385, 1275), fill=white)
center_text(["Training set", "42333 records"], (50, 1175, 390, 1280), f20, gap=30)
d.rectangle((515, 1180, 815, 1275), fill=white)
center_text(["test set", "18143 records"], (510, 1175, 820, 1280), f20, gap=30)

im.save(dst)
print("saved", dst)
