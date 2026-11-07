"""Builds manim_intro.pptx: six English slides introducing Manim (history, 3Blue1Brown, install).

    pip install python-pptx
    python make_manim_slides.py
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

BG = RGBColor(0x0D, 0x0D, 0x12)
PANEL = RGBColor(0x1C, 0x1C, 0x24)
WHITE = RGBColor(0xF2, 0xF2, 0xF2)
GRAY = RGBColor(0x9A, 0x9A, 0xA6)
YELLOW = RGBColor(0xF7, 0xD9, 0x6F)
BLUE = RGBColor(0x58, 0xC4, 0xDD)
GREEN = RGBColor(0x83, 0xC1, 0x67)
ORANGE = RGBColor(0xFF, 0x86, 0x2F)
RED = RGBColor(0xFC, 0x62, 0x55)
BODY, MONO = "Calibri", "Consolas"
STILL = "media/images/hello_circle/HelloCircle_ManimCE_v0.22.1.png"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def new_slide(title, notes):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    if title:
        text(s, title, 0.7, 0.4, 11.9, 0.9, size=36, color=YELLOW, bold=True)
        bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(1.25), Inches(1.6), Inches(0.06))
        bar.fill.solid(); bar.fill.fore_color.rgb = BLUE; bar.line.fill.background()
    n = len(prs.slides)
    text(s, f"Manim  ·  {n}", 11.4, 7.0, 1.5, 0.3, size=11, color=GRAY, align=PP_ALIGN.RIGHT)
    s.notes_slide.notes_text_frame.text = notes
    return s


def text(s, t, x, y, w, h, size=22, color=WHITE, bold=False, align=PP_ALIGN.LEFT, font=BODY,
         anchor=MSO_ANCHOR.TOP):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = t
    f = r.font
    f.size, f.bold, f.name = Pt(size), bold, font
    f.color.rgb = color
    return tb


def bullets(s, items, x, y, w, h, size=22, gap=10):
    """items: str or (str, level). A hanging bullet is set through the paragraph XML."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        t, lvl = (it, 0) if isinstance(it, str) else it
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        pPr = p._p.get_or_add_pPr()
        pPr.set("marL", str(int(Inches(0.35 + 0.35 * lvl))))
        pPr.set("indent", str(-int(Inches(0.3))))
        for tag, attrs in (("a:buClr", None), ("a:buChar", {"char": "•" if lvl == 0 else "–"})):
            el = etree.SubElement(pPr, qn(tag))
            if attrs:
                for k, v in attrs.items():
                    el.set(k, v)
            else:
                c = etree.SubElement(el, qn("a:srgbClr")); c.set("val", "58C4DD")
        r = p.add_run()
        r.text = t
        r.font.size, r.font.name = Pt(size - 3 * lvl), BODY
        r.font.color.rgb = WHITE if lvl == 0 else GRAY
    return tb


def panel(s, x, y, w, h, line=GRAY):
    r = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    r.adjustments[0] = 0.04
    r.fill.solid(); r.fill.fore_color.rgb = PANEL
    r.line.color.rgb = line; r.line.width = Pt(1.25)
    r.shadow.inherit = False
    return r


def code(s, lines, x, y, w, h, size=15):
    """Code panel; everything after '#' on a line is grey."""
    panel(s, x, y, w, h)
    tb = s.shapes.add_textbox(Inches(x + 0.2), Inches(y + 0.12), Inches(w - 0.4), Inches(h - 0.24))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        body, _, com = ln.partition("#")
        for part, col in ((body, WHITE), (("#" + com) if _ else "", GRAY)):
            if part:
                r = p.add_run(); r.text = part
                r.font.size, r.font.name = Pt(size), MONO
                r.font.color.rgb = col
    return tb


def link(s, label, url, x, y, w, color=BLUE, size=20):
    tb = text(s, label, x, y, w, 0.4, size=size, color=color)
    tb.click_action.hyperlink.address = url   # on the shape: a run link would take the theme's dark blue
    return tb


# ============================================================ 1. title
s = new_slide(None, "Manim: a Python library that turns code into explanatory math animations. "
                    "Everything in the videos you saw today was made with it. The three shapes on the right "
                    "are the circle, square and triangle from our Hello World video.")
text(s, "Manim", 0.9, 2.0, 8, 1.6, size=88, color=WHITE, bold=True)
text(s, "Animating mathematics with code", 0.95, 3.7, 8.5, 0.7, size=32, color=YELLOW)
text(s, "Python  ·  open source  ·  the engine behind 3Blue1Brown", 0.95, 4.5, 9, 0.5, size=20, color=GRAY)
for shp, col, x, y, w in ((MSO_SHAPE.OVAL, BLUE, 9.3, 1.6, 1.6), (MSO_SHAPE.RECTANGLE, GREEN, 9.3, 3.5, 1.6),
                          (MSO_SHAPE.ISOSCELES_TRIANGLE, ORANGE, 9.3, 5.4, 1.6)):
    sh = s.shapes.add_shape(shp, Inches(x + 0.8), Inches(y), Inches(w), Inches(w))
    sh.fill.background(); sh.line.color.rgb = col; sh.line.width = Pt(5); sh.shadow.inherit = False

# ============================================================ 2. 3b1b
s = new_slide("3Blue1Brown and Grant Sanderson",
              "3Blue1Brown is Grant Sanderson's YouTube channel: visual, intuitive explanations of mathematics. "
              "He wrote Manim to make those animations: instead of drawing by hand, every frame is computed by code, "
              "so it is exact and reproducible. Manim stands for 'mathematical animation engine'. "
              "Famous series: Essence of Linear Algebra, Essence of Calculus, the neural network series.")
bullets(s, [
    "3Blue1Brown: a YouTube channel with visual explanations of mathematics",
    "Created by Grant Sanderson (Stanford mathematics graduate, formerly at Khan Academy)",
    "Known for: linear algebra, calculus, neural networks, Fourier transform, ...",
    "Every animation is generated by his own Python code: Manim, the mathematical animation engine",
    "Precise, reproducible, and easy to adapt: change a number and re-render",
], 0.7, 1.7, 7.4, 5, size=23, gap=16)
panel(s, 8.6, 1.9, 4.0, 3.6, line=BLUE)
text(s, "Links", 8.9, 2.05, 3.4, 0.5, size=24, color=YELLOW, bold=True)
link(s, "3blue1brown.com", "https://www.3blue1brown.com", 8.9, 2.75, 3.5)
link(s, "youtube.com/@3blue1brown", "https://www.youtube.com/@3blue1brown", 8.9, 3.35, 3.7, size=19)
link(s, "github.com/3b1b/manim", "https://github.com/3b1b/manim", 8.9, 3.95, 3.5)
text(s, "(the original source code)", 8.9, 4.4, 3.5, 0.4, size=15, color=GRAY)

# ============================================================ 3. history
s = new_slide("From one person's tool to a community project",
              "Manim started as Grant's personal tool, around 2015, built for his own videos. It is open source, but it "
              "changed constantly and was not documented for outsiders. In 2020 a group of users forked it as Manim "
              "Community Edition: stable releases, tests, documentation. Both versions live on. Important practical point: "
              "'pip install manim' is the community edition; the original is 'pip install manimgl'.")
events = [
    ("2015", "Grant Sanderson starts 3Blue1Brown and writes Manim for his own videos", BLUE),
    ("GitHub", "The code is published on GitHub as 3b1b/manim, and others start using it", BLUE),
    ("2020", "A community fork appears: Manim Community Edition (ManimCE), with stable releases, tests and documentation", GREEN),
    ("2021", "Grant's Summer of Math Exposition (SoME) encourages many new creators to make Manim videos", GREEN),
    ("today", "ManimCE is at v0.22; Grant keeps developing his own version for his videos", ORANGE),
]
y0 = 1.75
line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.55), Inches(y0 + 0.2), Inches(0.05), Inches(4.0))
line.fill.solid(); line.fill.fore_color.rgb = GRAY; line.line.fill.background()
for i, (when, what, col) in enumerate(events):
    y = y0 + i * 0.95
    text(s, when, 0.7, y, 1.7, 0.5, size=22, color=col, bold=True, align=PP_ALIGN.RIGHT)
    d = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(2.45), Inches(y + 0.1), Inches(0.25), Inches(0.25))
    d.fill.solid(); d.fill.fore_color.rgb = col; d.line.fill.background()
    text(s, what, 3.0, y, 9.6, 0.8, size=21)
panel(s, 0.7, 6.15, 11.9, 0.8, line=YELLOW)
text(s, "Two versions:   pip install manim  =  Community Edition   |   pip install manimgl  =  Grant's original",
     0.95, 6.3, 11.5, 0.5, size=20, color=YELLOW, font=BODY)

# ============================================================ 4. how it works
s = new_slide("How Manim works",
              "You write a Scene class in Python; construct() is the script of the video. self.play() runs an "
              "animation. Manim computes every frame, draws it with Cairo, and encodes the frames into an MP4 with FFmpeg. "
              "The still on the right is from our own Hello Circle video.")
steps = [("Python script", BLUE, "your code"),
         ("Scene.construct()", BLUE, "the script of the video (MovingCameraScene: with a zoomable camera)"),
         ("Cairo draws frames", GREEN, "draws every frame as 2D vector graphics (text: Pango)"),
         ("FFmpeg → MP4", ORANGE, "glues the frames into a video file")]
for i, (lbl, col, sub) in enumerate(steps):
    text(s, sub, 0.7 + i * 3.05, 2.48, 2.6, 0.6, size=12, color=GRAY, align=PP_ALIGN.CENTER)
    x = 0.7 + i * 3.05
    b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.7), Inches(2.5), Inches(0.75))
    b.fill.solid(); b.fill.fore_color.rgb = PANEL; b.line.color.rgb = col; b.line.width = Pt(2); b.shadow.inherit = False
    tf = b.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = lbl; r.font.size = Pt(18); r.font.name = BODY; r.font.color.rgb = WHITE
    if i < 3:
        a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 2.58), Inches(1.9), Inches(0.38), Inches(0.35))
        a.fill.solid(); a.fill.fore_color.rgb = GRAY; a.line.fill.background()
code(s, [
    "from manim import *",
    "",
    "class SquareToCircle(Scene):",
    "    def construct(self):",
    "        square = Square()",
    "        circle = Circle(color=BLUE)",
    "        self.play(Create(square))",
    "        self.play(Transform(square, circle))",
    "        self.play(FadeOut(square))",
], 0.7, 3.2, 6.6, 2.85, size=15)
code(s, ["$ manim -ql example.py SquareToCircle"], 0.7, 6.2, 6.6, 0.6, size=15)
pic = s.shapes.add_picture(STILL, Inches(7.65), Inches(3.2), width=Inches(5.0))
pic.line.color.rgb = GRAY; pic.line.width = Pt(1)
text(s, "A frame from our Hello Circle video: ~200 lines of Python", 7.65, 6.05, 5.0, 0.4, size=14, color=GRAY)

# ============================================================ 5. building blocks
s = new_slide("The building blocks we used in the ECC videos",
              "These are the Manim features behind our elliptic curve videos. Text/MathTex/Write for titles and formulas; "
              "Axes and ParametricFunction for the curve; ValueTracker with updaters for everything that moves "
              "together (the line through P and Q and the third point R follow automatically); "
              "MovingCameraScene to zoom out to the whole curve and follow R; UpdateFromAlphaFunc for custom motion "
              "(rolling circle, folding line); LaggedStart, Succession and Indicate for rhythm and highlights. "
              "The Hello World videos demonstrate each of them in a few lines.")
blocks = [
    ("Text, MathTex, Write", "words and LaTeX formulas, written on screen", "titles, y² = x³ + ax + b"),
    ("Axes, c2p, ParametricFunction", "coordinate system and your own curves", "the elliptic curve"),
    ("ValueTracker + updaters", "one number drives everything that depends on it", "P slides, line and R follow"),
    ("MovingCameraScene", "the camera is an object: zoom, pan, follow", "zoom out to the whole curve"),
    ("Transform / ReplacementTransform", "morph one object or formula into another", "changing a and b"),
    ("UpdateFromAlphaFunc, rate_func", "your own formula per frame, and the tempo", "rolling circle, folding line"),
    ("LaggedStart, Succession, Indicate", "rhythm and highlights", "table of 5y mod 19"),
]
tbl = s.shapes.add_table(len(blocks) + 1, 3, Inches(0.7), Inches(1.6), Inches(11.9), Inches(5.0)).table
for c, w in enumerate((4.1, 4.6, 3.2)):
    tbl.columns[c].width = Inches(w)
for r_i, row in enumerate([("Manim feature", "What it does", "Where we used it")] + blocks):
    tbl.rows[r_i].height = Inches(0.58)
    for c_i, val in enumerate(row):
        cell = tbl.cell(r_i, c_i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0x2A, 0x2A, 0x36) if r_i == 0 else PANEL
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        r = cell.text_frame.paragraphs[0].add_run(); r.text = val
        r.font.size, r.font.bold = Pt(17), r_i == 0 or c_i == 0
        r.font.name = MONO if c_i == 0 and r_i else BODY
        r.font.color.rgb = YELLOW if r_i == 0 else (BLUE if c_i == 0 else (GRAY if c_i == 2 else WHITE))
    if r_i:
        tbl.cell(r_i, 0).text_frame.paragraphs[0].runs[0].font.size = Pt(15)

# ============================================================ 5. install
s = new_slide("What you need to install",
              "pip installs Manim and most dependencies. FFmpeg is used for video encoding and comes bundled through the "
              "PyAV package. Cairo and Pango draw shapes and text; on Linux install the system development packages first. "
              "LaTeX is optional, but you need it for formulas (MathTex/Tex). 'manim checkhealth' verifies the installation, "
              "including LaTeX and dvisvgm.")
rows = [
    ("Requirement", "What it is used for", "Notes"),
    ("Python ≥ 3.11", "runs Manim and your scene code", "use a virtual environment"),
    ("FFmpeg", "encodes the frames into an MP4", "bundled via the PyAV package"),
    ("Cairo + Pango", "draws shapes and text", "Linux: system dev packages needed"),
    ("LaTeX + dvisvgm", "formulas: MathTex / Tex", "optional · MiKTeX, TeX Live or MacTeX"),
]
tbl = s.shapes.add_table(len(rows), 3, Inches(0.7), Inches(1.6), Inches(11.9), Inches(2.6)).table
for c, w in enumerate((3.2, 4.4, 4.3)):
    tbl.columns[c].width = Inches(w)
for r_i, row in enumerate(rows):
    tbl.rows[r_i].height = Inches(0.52)
    for c_i, val in enumerate(row):
        cell = tbl.cell(r_i, c_i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(0x2A, 0x2A, 0x36) if r_i == 0 else PANEL
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        r = p.add_run(); r.text = val
        r.font.size, r.font.name = Pt(18), BODY
        r.font.bold = r_i == 0 or c_i == 0
        r.font.color.rgb = YELLOW if r_i == 0 else (BLUE if c_i == 0 else (GREEN if "optional" not in val else ORANGE) if c_i == 2 else WHITE)
code(s, [
    "# Ubuntu / Debian: system packages",
    "sudo apt install ffmpeg libcairo2-dev libpango1.0-dev texlive-latex-extra dvisvgm",
    "",
    "# all platforms: virtual environment + Manim",
    "python -m venv manim-env",
    "source manim-env/bin/activate        # Windows: manim-env\\Scripts\\activate",
    "pip install manim",
    "manim checkhealth                    # verify the installation",
], 0.7, 4.45, 11.9, 2.4, size=15)

# ============================================================ 6. first render + resources
s = new_slide("Your first video, and where to learn more",
              "Save the SquareToCircle example as example.py and run the command. -ql renders quickly in low quality "
              "(480p15) while you work; use -qh for the final 1080p version. If you do not want to install anything, "
              "try.manim.community runs Manim in the browser. The docs gallery has many examples to copy from.")
code(s, [
    "manim -pql example.py SquareToCircle      # preview, low quality (fast)",
    "manim -qh  example.py SquareToCircle      # final 1080p60",
    "manim -s   example.py SquareToCircle      # only the last frame (a still)",
], 0.7, 1.7, 11.9, 1.3, size=16)
text(s, "Useful flags", 0.7, 3.25, 5, 0.5, size=24, color=YELLOW, bold=True)
bullets(s, [
    "-p  open the video when it is finished",
    "-ql / -qm / -qh  low, medium or high quality",
    "-s  render only the final frame",
    "-n 12  start at animation number 12",
], 0.7, 3.85, 5.8, 3, size=20, gap=8)
panel(s, 7.0, 3.25, 5.6, 3.55, line=BLUE)
text(s, "Resources", 7.3, 3.35, 4, 0.5, size=24, color=YELLOW, bold=True)
link(s, "docs.manim.community", "https://docs.manim.community", 7.3, 4.0, 5, size=19)
text(s, "documentation, tutorials, example gallery", 7.3, 4.38, 5.2, 0.4, size=14, color=GRAY)
link(s, "try.manim.community", "https://try.manim.community", 7.3, 4.85, 5, size=19)
text(s, "run Manim in your browser, nothing to install", 7.3, 5.23, 5.2, 0.4, size=14, color=GRAY)
link(s, "manim.community/discord", "https://manim.community/discord", 7.3, 5.7, 5, size=19)
text(s, "community help  ·  also r/manim on Reddit", 7.3, 6.08, 5.2, 0.4, size=14, color=GRAY)

prs.save("manim_intro.pptx")
print("saved manim_intro.pptx,", len(prs.slides), "slides")
