"""Hello, Circle! A simple 'Hello, World!' scene: a unit circle is rolled out onto a number line
(length 2*pi), the line is folded into a square and into an equilateral triangle of the same
perimeter, and finally a point travels along all four at the same pace.

    manim -ql hello_circle.py HelloCircle
"""
from manim import *
import numpy as np

R = 1.0
P = 2 * PI * R          # common perimeter
LINE_Y = -1.8
SLOT_Y = 1.7
SLOTS = [np.array([x, SLOT_Y, 0.0]) for x in (-4.5, 0.0, 4.5)]
N = 240                 # divisible by 3 and 4, so square and triangle corners are sample points


def polygon_fn(verts):
    """Point at fraction t of the perimeter of a closed polygon (equal-length sides)."""
    verts = [np.array(v, dtype=float) for v in verts]
    n = len(verts)

    def f(t):
        s = min(max(t, 0.0), 1.0) * n
        i = min(int(s), n - 1)
        u = s - i
        return verts[i] * (1 - u) + verts[(i + 1) % n] * u
    return f


def circle_fn(c):
    return lambda t: c + R * np.array([np.cos(-PI / 2 + 2 * PI * t), np.sin(-PI / 2 + 2 * PI * t), 0.0])


def square_fn(c):
    a = P / 4
    return polygon_fn([c + np.array(v) for v in
                       [(-a / 2, -a / 2, 0), (a / 2, -a / 2, 0), (a / 2, a / 2, 0), (-a / 2, a / 2, 0)]])


def triangle_fn(c):
    b = P / 3
    h = b * np.sqrt(3) / 2
    return polygon_fn([c + np.array(v) for v in
                       [(-b / 2, -h / 3, 0), (b / 2, -h / 3, 0), (0, 2 * h / 3, 0)]])


def outline(fn, color):
    """Sample a perimeter function so shapes with equal N morph by arc length."""
    m = VMobject(color=color, stroke_width=6)
    m.set_points_as_corners([fn(i / N) for i in range(N + 1)])
    return m


class HelloCircle(Scene):
    def construct(self):
        # ---------------------------------------------------------- hello
        hello = Text("Hello, World!", font_size=84)
        self.play(Write(hello), run_time=2)
        self.wait(0.5)
        self.play(hello.animate.scale(0.4).to_corner(UL, buff=0.3))

        # ---------------------------------------------------------- circle, radius 1
        circle = Circle(radius=R, color=BLUE, stroke_width=6)
        spoke = Line(ORIGIN, RIGHT * R, color=YELLOW)
        r_lbl = MathTex("r = 1", font_size=36).next_to(spoke, DOWN, buff=0.15)
        self.play(Create(circle), run_time=1.5)
        self.play(Create(spoke), FadeIn(r_lbl))
        self.wait(0.5)
        self.play(FadeOut(spoke), FadeOut(r_lbl), circle.animate.move_to(SLOTS[0]))

        # ---------------------------------------------------------- number line
        nl = NumberLine(x_range=[0, 7, 1], length=7, include_numbers=True, font_size=28)
        nl.move_to([0, LINE_Y, 0])
        nl.shift(UP * (LINE_Y - nl.n2p(0)[1]))  # move_to centres the labels too; put the axis itself on LINE_Y
        x0 = nl.n2p(0)[0]
        line_fn = lambda t: np.array([x0 + P * t, LINE_Y, 0.0])
        self.play(Create(nl))

        # a copy of the circle rolls out on the number line
        centre0 = np.array([x0, LINE_Y + R, 0.0])
        bottom = SLOTS[0] + DOWN * R
        wheel = VGroup(Circle(radius=R, color=BLUE, stroke_width=6).move_to(SLOTS[0]),
                       Line(SLOTS[0], bottom, color=YELLOW, stroke_width=5),
                       Dot(bottom, color=YELLOW, radius=0.07))
        self.add(wheel)
        self.play(wheel.animate.move_to(centre0), run_time=1.5)

        seg = Line([x0, LINE_Y, 0], [x0 + 1e-3, LINE_Y, 0], color=RED, stroke_width=8)
        self.add(seg)
        base = wheel.copy()

        def roll_wheel(m, a):
            m.become(base).rotate(-2 * PI * a, about_point=centre0).shift(RIGHT * P * a)

        def grow_seg(m, a):
            m.become(Line([x0, LINE_Y, 0], [x0 + max(P * a, 1e-3), LINE_Y, 0], color=RED, stroke_width=8))

        self.play(UpdateFromAlphaFunc(wheel, roll_wheel), UpdateFromAlphaFunc(seg, grow_seg),
                  run_time=4, rate_func=smooth)
        brace = Brace(seg, DOWN, buff=0.55, color=RED)
        brace_lbl = brace.get_tex(r"2\pi r = 2\pi", buff=0.1).set_color(RED)
        self.play(GrowFromCenter(brace), FadeIn(brace_lbl))
        self.wait(1)

        # ---------------------------------------------------------- line -> square
        self.play(FadeOut(wheel), FadeOut(brace), FadeOut(brace_lbl))
        self.play(Transform(seg, outline(square_fn(SLOTS[1]), GREEN)), run_time=3)
        square = seg
        self.wait(0.5)

        # ---------------------------------------------------------- square -> line -> triangle
        # a copy of the square moves down onto the number line (bottom-left corner at 0) and unrolls there,
        # to stress the equal perimeter: its bottom side already lies on the line, the other three fold open
        tri_copy = square.copy()
        self.add(tri_copy)
        a = P / 4
        self.play(tri_copy.animate.move_to([x0 + a / 2, LINE_Y + a / 2, 0]), run_time=1.5)
        self.wait(0.5)
        self.play(Transform(tri_copy, outline(line_fn, RED)), run_time=3)
        brace = Brace(tri_copy, DOWN, buff=0.55, color=RED)
        brace_lbl = brace.get_tex(r"2\pi", buff=0.1).set_color(RED)
        self.play(GrowFromCenter(brace), FadeIn(brace_lbl))
        self.wait(1)
        self.play(FadeOut(brace), FadeOut(brace_lbl))
        self.play(Transform(tri_copy, outline(triangle_fn(SLOTS[2]), ORANGE)), run_time=3)
        triangle = tri_copy

        caption = Text("Circle, square and triangle: all with perimeter 2π", font_size=30, color=GRAY_B)
        caption.move_to([0, -3.5, 0])
        self.play(FadeIn(caption, shift=UP * 0.2))
        self.wait(1)

        # ---------------------------------------------------------- a point travelling along all four
        fns = [line_fn, circle_fn(SLOTS[0]), square_fn(SLOTS[1]), triangle_fn(SLOTS[2])]
        tr = ValueTracker(0)
        ref = outline(line_fn, RED).set_stroke(width=8)
        self.play(FadeIn(ref))
        dots = VGroup(*[Dot(fn(0), color=YELLOW, radius=0.11).set_z_index(5) for fn in fns])
        for d, fn in zip(dots, fns):
            d.add_updater(lambda m, f=fn: m.move_to(f(tr.get_value())))
        s_lbl = VGroup(MathTex("s =", font_size=36),
                       DecimalNumber(0, num_decimal_places=2, font_size=36))
        s_lbl.arrange(RIGHT, buff=0.15).move_to([5.3, LINE_Y, 0])
        s_lbl[1].add_updater(lambda m: m.set_value(P * tr.get_value()).next_to(s_lbl[0], RIGHT, buff=0.15))
        self.play(FadeIn(dots), FadeIn(s_lbl))
        self.play(tr.animate.set_value(1), run_time=8, rate_func=linear)
        self.wait(2)
