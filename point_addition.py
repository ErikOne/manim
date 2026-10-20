"""Scene 4: Point addition on an elliptic curve (secant and tangent rule)."""
from manim import *
from curve_utils import curve_points, third_intersection
import numpy as np


class PointAddition(Scene):
    def construct(self):
        title = Text("Adding Points on an Elliptic Curve", font_size=38)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        axes = Axes(
            x_range=[-3, 3.5, 1],
            y_range=[-4, 4, 1],
            x_length=6.5,
            y_length=6,
            axis_config={"include_tip": True},
        ).shift(DOWN * 0.3)
        self.play(Create(axes))

        xs, ys_top, ys_bot = curve_points()
        top = VMobject(color=YELLOW).set_points_smoothly([axes.c2p(x, y) for x, y in zip(xs, ys_top)])
        bot = VMobject(color=YELLOW).set_points_smoothly([axes.c2p(x, y) for x, y in zip(xs, ys_bot)])
        self.play(Create(top), Create(bot))

        rule = MathTex(
            r"P + Q = \text{reflect}(R)\ \text{across the x-axis}",
            font_size=32,
        ).to_edge(DOWN)
        self.play(Write(rule))

        # --- Part A: P + Q via secant line ---
        x1, y1 = 0.0, 1.0
        x2, y2 = 1.0, 1.0
        x3, y3, _ = third_intersection(x1, y1, x2, y2)

        P, Q, R = axes.c2p(x1, y1), axes.c2p(x2, y2), axes.c2p(x3, y3)
        dotP, dotQ = Dot(P, color=RED), Dot(Q, color=RED)
        labP = MathTex("P", color=RED, font_size=32).next_to(dotP, UP)
        labQ = MathTex("Q", color=RED, font_size=32).next_to(dotQ, UP)
        self.play(FadeIn(dotP), FadeIn(dotQ), Write(labP), Write(labQ))

        direction = (np.array(Q) - np.array(P))
        direction = direction / np.linalg.norm(direction)
        line = Line(np.array(P) - direction * 6, np.array(P) + direction * 6, color=GREEN)
        self.play(Create(line))

        dotR = Dot(R, color=ORANGE)
        labR = MathTex("R", color=ORANGE, font_size=32).next_to(dotR, DOWN)
        self.play(FadeIn(dotR), Write(labR))

        sum_point = axes.c2p(x3, -y3)
        reflect_line = DashedLine(R, sum_point, color=GRAY)
        dotSum = Dot(sum_point, color=BLUE)
        labSum = MathTex("P+Q", color=BLUE, font_size=32).next_to(dotSum, DOWN)
        self.play(Create(reflect_line))
        self.play(FadeIn(dotSum), Write(labSum))
        self.wait(1.5)

        self.play(*[FadeOut(m) for m in [dotP, dotQ, labP, labQ, line, dotR, labR,
                                          reflect_line, dotSum, labSum]])

        # --- Part B: doubling P via tangent line ---
        rule2 = MathTex(r"2P = \text{reflect}(R)\ \text{using the tangent at } P", font_size=32)
        rule2.to_edge(DOWN)
        self.play(Transform(rule, rule2))

        xt, yt = 1.0, 1.0
        xr, yr, slope = third_intersection(xt, yt, xt, yt)
        Pt = axes.c2p(xt, yt)
        dotPt = Dot(Pt, color=RED)
        labPt = MathTex("P", color=RED, font_size=32).next_to(dotPt, UP)
        self.play(FadeIn(dotPt), Write(labPt))

        tangent_dir = np.array([1, slope, 0])
        tangent_dir = tangent_dir / np.linalg.norm(tangent_dir)
        tangent = Line(np.array(Pt) - tangent_dir * 6, np.array(Pt) + tangent_dir * 6, color=GREEN)
        self.play(Create(tangent))

        Rt = axes.c2p(xr, yr)
        dotRt = Dot(Rt, color=ORANGE)
        labRt = MathTex("R", color=ORANGE, font_size=32).next_to(dotRt, DOWN)
        self.play(FadeIn(dotRt), Write(labRt))

        double_point = axes.c2p(xr, -yr)
        reflect2 = DashedLine(Rt, double_point, color=GRAY)
        dot2P = Dot(double_point, color=BLUE)
        lab2P = MathTex("2P", color=BLUE, font_size=32).next_to(dot2P, UP)
        self.play(Create(reflect2))
        self.play(FadeIn(dot2P), Write(lab2P))
        self.wait(2)
