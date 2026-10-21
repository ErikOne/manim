"""Hello, Manim! A tour of the Manim techniques used in the elliptic-curve videos,
all demonstrated on a 'Hello, World!' scene and ending with a small live elliptic curve."""
from manim import *
import numpy as np

UX, UY = 0.8, 0.22
ORIG = np.array([-0.9, 0.9, 0.0])
W0 = 14.222
TQ = -3.5
MONO = "DejaVu Sans Mono"


def xs_of(t):
    """y^2 = x^3 + 7 as a graph x(y): t = y parametrises the whole curve smoothly."""
    return np.cbrt(t * t - 7)


def third_point(tp, tq):
    xp, xq = xs_of(tp), xs_of(tq)
    if abs(xq - xp) < 1e-9:
        return None
    m = (tq - tp) / (xq - xp)
    x3 = m * m - xp - xq
    return x3, tp + m * (x3 - xp)


class HelloManim(MovingCameraScene):
    def construct(self):
        frame = self.camera.frame
        kk = lambda: frame.width / W0

        def caption(num, title, note, lines):
            head = Text(f"{num}. {title}", font_size=32, color=YELLOW).to_corner(UL, buff=0.3)
            nt = Text(note, font_size=22, color=GRAY_B).next_to(head, DOWN, buff=0.15, aligned_edge=LEFT)
            code = Text("\n".join(lines), font=MONO, font_size=19, line_spacing=0.9, color=GRAY_A)
            box = SurroundingRectangle(code, buff=0.15, corner_radius=0.1, color=GRAY,
                                       fill_color=BLACK, fill_opacity=0.92, stroke_width=1.5)
            cb = VGroup(box, code).to_edge(DOWN, buff=0.2)
            return VGroup(head, nt, cb).set_z_index(10)

        def pin(m):
            """Keep a static mobject at a fixed place and relative size inside the camera frame."""
            off, w0 = m.get_center() - frame.get_center(), m.width
            m.add_updater(lambda mm: (mm.set(width=w0 * kk()),
                                      mm.move_to(frame.get_center() + kk() * off)))

        def cap_on(cap):
            self.play(FadeIn(cap, shift=UP * 0.2), run_time=0.8)

        def cap_off(cap):
            cap.clear_updaters()
            self.play(FadeOut(cap), run_time=0.6)

        # ============================================================ intro
        hello = Text("Hello, World!", font_size=84)
        self.play(Write(hello), run_time=2)
        sub = Text("Manim techniques behind our elliptic-curve videos", font_size=28, color=GRAY_B)
        sub.next_to(hello, DOWN, buff=0.7)
        self.play(FadeIn(sub, shift=UP * 0.2))
        self.wait(2)
        self.play(FadeOut(sub), hello.animate.scale(0.75).move_to([0, 0.9, 0]))

        # ============================================================ 1. Text / MathTex / Write
        cap = caption(1, "Text, MathTex & Write", "words, LaTeX formulas, and how they appear", [
            'hello   = Text("Hello, World!")',
            'formula = MathTex(r"y^2 = x^3 + ax + b")',
            "self.play(Write(formula))",
        ])
        cap_on(cap)
        formula = MathTex(r"y^2 = x^3 + ax + b", font_size=64).move_to([0, -0.8, 0])
        self.play(Write(formula), run_time=2)
        l1 = Text("Text", font_size=24, color=BLUE).next_to(hello, RIGHT, buff=0.5)
        l2 = Text("MathTex", font_size=24, color=BLUE).next_to(formula, RIGHT, buff=0.5)
        self.play(FadeIn(l1), FadeIn(l2))
        self.wait(2.5)
        self.play(FadeOut(l1), FadeOut(l2))
        cap_off(cap)

        # ============================================================ 2. Transform
        cap = caption(2, "Transform", "one object turns into another, right in front of the viewer", [
            "self.play(ReplacementTransform(hello, formula))",
            "",
            "ring12 -> ring31     # 12 dots become 31 dots",
        ])
        cap_on(cap)
        f2 = MathTex("y^2 = x^3 + 7", font_size=72, color=ORANGE).move_to(hello)
        self.play(ReplacementTransform(hello, f2), FadeOut(formula), run_time=2)
        self.wait(1)
        self.play(FadeOut(f2))

        def ring(n, color):
            return VGroup(*[
                Dot(1.5 * np.array([np.sin(2 * PI * k / n), np.cos(2 * PI * k / n), 0]),
                    radius=0.07, color=color) for k in range(n)
            ]).move_to([0, 0.2, 0])
        r12, r31 = ring(12, BLUE), ring(31, GREEN)
        t12 = MathTex(r"\text{mod } 12", font_size=48).move_to([0, -2.0, 0])
        t31 = MathTex(r"\text{mod } 31", font_size=48).move_to([0, -2.0, 0])
        self.play(FadeIn(r12), FadeIn(t12))
        self.wait(0.8)
        self.play(ReplacementTransform(r12, r31), ReplacementTransform(t12, t31), run_time=2.5)
        self.wait(1.2)
        self.play(FadeOut(r31), FadeOut(t31))
        cap_off(cap)

        # ============================================================ 3. .animate and rate_func
        cap = caption(3, ".animate and rate_func", "the same move, three different tempos", [
            "self.play(dot.animate.move_to(END), rate_func=linear)",
            "rate_func=smooth              # default: slow - fast - slow",
            "rate_func=lambda a: a**2      # speeding up (our clock)",
        ])
        cap_on(cap)
        rows = [(1.2, "linear", linear, RED), (0.0, "smooth (default)", smooth, YELLOW),
                (-1.2, "a**2  (speeding up)", lambda a: a ** 2, GREEN)]
        dots, labs, ends = [], [], []
        for y, name, fn, col in rows:
            lab = Text(name, font=MONO, font_size=20, color=col).move_to([-5.0, y, 0])
            lab.set_x(-6.8 + lab.width / 2)
            d = Dot([-2.8, y, 0], radius=0.14, color=col)
            track = Line([-2.8, y, 0], [5.0, y, 0], color=GRAY, stroke_width=1.5)
            dots.append(d); labs.append((lab, track))
        self.play(*[FadeIn(m) for lt in labs for m in lt], *[FadeIn(d) for d in dots])
        self.play(*[d.animate(rate_func=fn, run_time=5).move_to([5.0, y, 0])
                    for d, (y, _, fn, _) in zip(dots, rows)])
        self.wait(1)
        self.play(*[FadeOut(m) for lt in labs for m in lt], *[FadeOut(d) for d in dots])
        cap_off(cap)

        # ============================================================ 4. ValueTracker + always_redraw
        cap = caption(4, "ValueTracker + always_redraw", "one number drives everything that depends on it", [
            "t    = ValueTracker(0)",
            "hand = always_redraw(lambda: Line(C, C + dir(t.get_value())))",
            "self.play(t.animate.set_value(30), rate_func=lambda a: a**2)",
        ])
        cap_on(cap)
        C = np.array([-2.5, 0.2, 0.0])
        t = ValueTracker(0)
        face = Circle(radius=1.7, color=WHITE, stroke_width=3).move_to(C)
        ticks = VGroup(*[
            Line(C + 1.5 * np.array([np.sin(2 * PI * k / 12), np.cos(2 * PI * k / 12), 0]),
                 C + 1.7 * np.array([np.sin(2 * PI * k / 12), np.cos(2 * PI * k / 12), 0]))
            for k in range(12)
        ])
        hand = always_redraw(lambda: Line(
            C, C + 1.4 * np.array([np.sin(2 * PI * t.get_value() / 12), np.cos(2 * PI * t.get_value() / 12), 0]),
            color=GREEN, stroke_width=6))
        lab_t = always_redraw(lambda: Text(f"t = {t.get_value():5.1f}", font=MONO, font_size=30)
                              .move_to([3.0, 0.8, 0]))
        lab_m = always_redraw(lambda: Text(f"t mod 12 = {t.get_value() % 12:4.1f}", font=MONO, font_size=30,
                                           color=GREEN).move_to([3.0, 0.0, 0]))
        self.play(FadeIn(face), FadeIn(ticks))
        self.add(hand, lab_t, lab_m)
        self.wait(0.8)
        self.play(t.animate.set_value(30), run_time=9, rate_func=lambda a: a ** 2)
        self.wait(1.5)
        hand.clear_updaters(); lab_t.clear_updaters(); lab_m.clear_updaters()
        self.play(*[FadeOut(m) for m in [face, ticks, hand, lab_t, lab_m]])
        cap_off(cap)

        # ============================================================ 5. Axes, c2p, ParametricFunction
        cap = caption(5, "Axes, c2p & ParametricFunction", "plot your own curve: here y^2 = x^3 + 7", [
            "axes  = Axes(x_range=[-3, 7, 1], y_range=[-12, 7, 2])",
            "curve = ParametricFunction(lambda t: axes.c2p(np.cbrt(t*t - 7), t), t_range=[-11, 6])",
            "dot   = Dot(axes.c2p(x, y))     # c2p: curve coordinates -> screen",
        ])
        cap_on(cap)
        axes = Axes(x_range=[-3, 7, 1], y_range=[-12, 7, 2], x_length=10 * UX, y_length=19 * UY,
                    axis_config={"include_tip": True, "stroke_width": 2, "tick_size": 0.05})
        axes.shift(ORIG - axes.c2p(0, 0))
        scr = axes.c2p
        pt = lambda tt: scr(xs_of(tt), tt)
        curve = ParametricFunction(lambda tt: pt(tt), t_range=[-11, 6, 0.02], color=YELLOW, stroke_width=4)
        self.play(Create(axes), run_time=1.5)
        self.play(Create(curve), run_time=3.5)

        tp, tq = ValueTracker(0.5), ValueTracker(TQ)
        P_dot = always_redraw(lambda: Dot(pt(tp.get_value()), radius=0.09 * kk(), color=RED))
        Q_dot = always_redraw(lambda: Dot(pt(tq.get_value()), radius=0.09 * kk(), color=BLUE))
        P_lab = always_redraw(lambda: MathTex("P", color=RED, font_size=32).scale(kk())
                              .next_to(pt(tp.get_value()), UL, buff=0.08 * kk()))
        Q_lab = always_redraw(lambda: MathTex("Q", color=BLUE, font_size=32).scale(kk())
                              .next_to(pt(tq.get_value()), DL, buff=0.08 * kk()))
        self.add(P_dot, P_lab, Q_dot, Q_lab)
        self.wait(2.5)
        cap_off(cap)

        # ============================================================ 6. live geometry
        cap = caption(6, "Live geometry with updaters", "R is never animated: it is recomputed from P and Q every frame", [
            "line = always_redraw(lambda: Line(P.get_center(), Q.get_center()))",
            "R    = always_redraw(lambda: Dot(third_point(P, Q)))",
            "self.play(tp.animate.set_value(2.4), run_time=6)     # only P is animated",
        ])
        cap_on(cap)

        def R_scr():
            r = third_point(tp.get_value(), tq.get_value())
            return scr(*r) if r else None

        def build_line():
            p0, q0, r0 = pt(tp.get_value()), pt(tq.get_value()), R_scr()
            pts = [p0, q0] + ([r0] if r0 is not None else [])
            d = (q0 - p0) / np.linalg.norm(q0 - p0)
            s = [np.dot(x - p0, d) for x in pts]
            return Line(p0 + d * (min(s) - 2 * kk()), p0 + d * (max(s) + 2 * kk()),
                        color=GREEN, stroke_width=3 * kk())
        PQ_line = always_redraw(build_line)
        R_dot = always_redraw(lambda: Dot(R_scr(), radius=0.1 * kk(), color=ORANGE)
                              if R_scr() is not None else Dot(radius=0))
        R_lab = always_redraw(lambda: MathTex("R", color=ORANGE, font_size=32).scale(kk())
                              .next_to(R_scr(), DR, buff=0.08 * kk()) if R_scr() is not None else Dot(radius=0))
        self.add(PQ_line)
        self.wait(1.5)
        self.add(R_dot, R_lab)
        self.wait(1.5)
        self.play(tp.animate.set_value(2.4), run_time=6)
        self.play(tp.animate.set_value(1.2), run_time=3)
        cap_off(cap)

        # ============================================================ 7. UpdateFromAlphaFunc
        cap = caption(7, "UpdateFromAlphaFunc: one master clock", "a single alpha (0 -> 1) choreographs P and Q through keyframes", [
            "KF_P = [(0, 1.2), (0.35, 2.2), (0.7, 0.7), (1, 1.2)]    # (alpha, value)",
            "def drive(_, a): tp.set_value(interp(KF_P, a)); tq.set_value(interp(KF_Q, a))",
            "self.play(UpdateFromAlphaFunc(Mobject(), drive), run_time=10)",
        ])
        cap_on(cap)

        def interp(kf, a):
            for (a0, v0), (a1, v1) in zip(kf, kf[1:]):
                if a <= a1:
                    u = (a - a0) / (a1 - a0)
                    u = u * u * (3 - 2 * u)
                    return v0 + (v1 - v0) * u
            return kf[-1][1]
        KF_P = [(0, 1.2), (0.35, 2.2), (0.7, 0.7), (1, 1.2)]
        KF_Q = [(0, -3.5), (0.3, -6.5), (0.65, -4.2), (1, -3.5)]

        def drive(_, a):
            tp.set_value(interp(KF_P, a))
            tq.set_value(interp(KF_Q, a))
        self.play(UpdateFromAlphaFunc(Mobject(), drive), run_time=10, rate_func=linear)
        self.wait(1)
        cap_off(cap)

        # ============================================================ 7. Camera
        # Fixed on-screen items must follow the camera, so they are pinned to the frame.
        cap = caption(8, "Camera zoom (MovingCameraScene)", "the camera frame is an object you can animate", [
            "class Hello(MovingCameraScene): ...",
            "self.play(self.camera.frame.animate.set(width=40).move_to(...))",
            "frame.add_updater(fit)     # camera follows P, Q and R automatically",
        ])
        pin(cap)
        cap_on(cap)
        curve_ext = ParametricFunction(lambda tt: pt(tt), t_range=[-60, -11, 0.05], color=YELLOW, stroke_width=4)
        x_ext = Line(scr(7, 0), scr(18, 0), color=WHITE, stroke_width=2)
        y_ext = Line(scr(0, -12), scr(0, -60), color=WHITE, stroke_width=2)
        for m, w in [(curve, 4), (curve_ext, 4), (axes.x_axis, 2), (axes.y_axis, 2), (x_ext, 2), (y_ext, 2)]:
            m.add_updater(lambda mm, w=w: mm.set_stroke(width=w * kk()))
        self.add(curve_ext, x_ext, y_ext)
        curve_ext.set_stroke(opacity=0); x_ext.set_stroke(opacity=0); y_ext.set_stroke(opacity=0)

        # manual zoom out and back in
        self.play(frame.animate.set(width=34).move_to(scr(7, -22)), run_time=3)
        self.play(*[m.animate.set_stroke(opacity=1) for m in (curve_ext, x_ext, y_ext)], run_time=1)
        self.wait(1.5)
        self.play(frame.animate.set(width=W0).move_to(ORIGIN), run_time=3)
        self.wait(0.5)

        # automatic zoom: the camera follows P, Q and R while R flies away
        def fit(f):
            pts = [pt(tp.get_value()), pt(tq.get_value())]
            r = R_scr()
            if r is not None:
                pts.append(r)
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            h0 = max(ys) - min(ys)
            x0, x1 = min(min(xs) - 1.2, -W0 / 2), max(max(xs) + 1.2, W0 / 2)
            y0, y1 = min(min(ys) - 1.2 - 0.3 * h0, -4.0), max(max(ys) + 1.2, 4.0)
            W = max(x1 - x0, (y1 - y0) * 16 / 9)
            f.set(width=W)
            f.move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0])
        self.add(frame)
        frame.add_updater(fit)
        self.play(tp.animate.set_value(2.64), run_time=7, rate_func=lambda a: a ** 1.5)
        self.wait(1.5)
        self.play(tp.animate.set_value(1.0), run_time=5)
        frame.remove_updater(fit)
        self.play(frame.animate.set(width=W0).move_to(ORIGIN), run_time=1)
        cap_off(cap)

        for m in [P_dot, Q_dot, P_lab, Q_lab, PQ_line, R_dot, R_lab]:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in [axes, curve, curve_ext, x_ext, y_ext, P_dot, Q_dot, P_lab, Q_lab,
                                          PQ_line, R_dot, R_lab]])

        # ============================================================ 8. LaggedStart / Succession / Indicate
        cap = caption(9, "LaggedStart, Succession & highlights", "reveal many objects in rhythm, then point at the answer", [
            "LaggedStartMap(FadeIn, row_y, lag_ratio=0.08)",
            "Succession(*[FadeIn(v) for v in row_5y])",
            "Indicate(one);  Flash(one)",
        ])
        cap_on(cap)
        n, w = 19, 0.58
        xs0 = -w * (n - 1) / 2
        row_y = VGroup(*[Text(str(y), font_size=26).move_to([xs0 + w * y, 0.9, 0]) for y in range(n)])
        row_v = VGroup(*[Text(str(5 * y % 19), font_size=26).move_to([xs0 + w * y, 0.0, 0]) for y in range(n)])
        lab_y = Text("y", font_size=24, color=GRAY_B).move_to([-6.2, 0.9, 0])
        lab_v = MathTex(r"5y \bmod 19", font_size=30, color=GRAY_B).move_to([-6.2, 0.0, 0])
        self.play(FadeIn(lab_y), FadeIn(lab_v))
        self.play(LaggedStartMap(FadeIn, row_y, shift=DOWN * 0.2, lag_ratio=0.08), run_time=2.5)
        self.play(Succession(*[FadeIn(v, run_time=0.15) for v in row_v]))
        self.wait(0.5)
        one = row_v[4]
        box = SurroundingRectangle(VGroup(row_y[4], one), color=GREEN, buff=0.12)
        self.play(Indicate(one, color=GREEN, scale_factor=1.8), run_time=1.2)
        self.play(Create(box), Flash(one, color=GREEN, flash_radius=0.5), run_time=1.2)
        self.wait(2)
        self.play(*[FadeOut(m) for m in [row_y, row_v, lab_y, lab_v, box]])
        cap_off(cap)

        # ============================================================ recap
        title = Text("The toolbox", font_size=44).to_edge(UP, buff=0.5)
        items = [
            ("Text / MathTex / Write", "words and formulas"),
            ("ReplacementTransform", "morph one object into another"),
            ("rate_func", "control the tempo"),
            ("ValueTracker + always_redraw", "continuous, live updating"),
            ("Axes, c2p, ParametricFunction", "your own curves"),
            ("UpdateFromAlphaFunc", "one master clock for a choreography"),
            ("MovingCameraScene", "zoom and follow"),
            ("LaggedStart, Succession, Indicate", "rhythm and highlights"),
        ]
        lines = VGroup(*[
            VGroup(Text(f"{i + 1}.", font_size=24, color=YELLOW),
                   Text(a, font=MONO, font_size=22, color=WHITE),
                   Text(b, font_size=22, color=GRAY_B)).arrange(RIGHT, buff=0.25)
            for i, (a, b) in enumerate(items)
        ]).arrange(DOWN, buff=0.32, aligned_edge=LEFT).next_to(title, DOWN, buff=0.5)
        lines.set_x(0)
        self.play(Write(title))
        self.play(LaggedStartMap(FadeIn, lines, shift=RIGHT * 0.3, lag_ratio=0.3), run_time=5)
        self.wait(2)
        cmd = Text("manim -ql hello_manim.py HelloManim", font=MONO, font_size=24, color=GREEN)
        cmd.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(cmd, shift=UP * 0.2))
        self.wait(2.5)
        self.play(FadeOut(lines), FadeOut(title), FadeOut(cmd))
        bye = Text("Hello, World!", font_size=84)
        self.play(Write(bye))
        self.wait(1.5)
        self.play(FadeOut(bye))
