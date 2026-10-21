"""Scene 5: Adding points on the Bitcoin curve y^2 = x^3 + 7, and the group structure.
P + Q (secant, no horizontal line), P + P (tangent), P + O (point at infinity), then the five group properties."""
from manim import *
import numpy as np

UX, UY = 0.9, 0.36                   # screen units per curve unit
ORIG = np.array([2.2, 0.0, 0.0])
PX = -6.7                            # left edge of the text panel
PC = -3.6                            # centre of the text panel
TANGENT_EPS = 1e-4


def xs_of(t):
    """y^2 = x^3 + 7 is a graph x = cbrt(y^2 - 7), so t = y parametrises it smoothly."""
    return np.cbrt(t * t - 7)


def third_point(tp, tq):
    xp, xq = xs_of(tp), xs_of(tq)
    if abs(tq - tp) < TANGENT_EPS:
        m = 3 * xp * xp / (2 * tp)
        x3 = m * m - 2 * xp
        return x3, tp + m * (x3 - xp)
    if abs(xq - xp) < 1e-6:
        return None
    m = (tq - tp) / (xq - xp)
    x3 = m * m - xp - xq
    return x3, tp + m * (x3 - xp)


class PointAdditionGroup(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-2, 5, 1], y_range=[-10, 10, 2],
            x_length=7 * UX, y_length=20 * UY,
            axis_config={"include_tip": True, "stroke_width": 2, "tick_size": 0.06},
        )
        axes.shift(ORIG - axes.c2p(0, 0))
        scr = axes.c2p
        curve = ParametricFunction(lambda t: scr(xs_of(t), t), t_range=[-9.5, 9.5, 0.02],
                                   color=YELLOW, stroke_width=4)
        numbers = VGroup(
            *[axes.x_axis.get_number_mobject(v, font_size=20) for v in range(-2, 6) if v],
            *[axes.y_axis.get_number_mobject(v, font_size=20) for v in range(-8, 9, 2) if v],
        )
        box = [(scr(-2, 0)[0], scr(5, 0)[0]), (scr(0, -10)[1], scr(0, 10)[1])]

        def clip_line(p, d, **kw):
            """Line through p with direction d, clipped to the axes box."""
            p, d = np.array(p, dtype=float), np.array(d, dtype=float)
            d = d / np.linalg.norm(d)
            t0, t1 = -1e9, 1e9
            for i, (lo, hi) in enumerate(box):
                if abs(d[i]) < 1e-12:
                    continue
                ta, tb = (lo - p[i]) / d[i], (hi - p[i]) / d[i]
                t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
            return Line(p + d * t0, p + d * t1, **kw)

        # P and Q: not on a horizontal line, not special in any way
        tp = ValueTracker(2.2)     # P = (-1.29, 2.20)
        tq = ValueTracker(-6.0)    # Q = ( 3.07, -6.00)
        p_vis, q_vis, r_vis, s_vis, l_vis = (ValueTracker(0.0) for _ in range(5))
        names = {"S": "P+Q"}

        tangent = lambda: abs(tq.get_value() - tp.get_value()) < TANGENT_EPS
        P_xy = lambda: (xs_of(tp.get_value()), tp.get_value())
        Q_xy = lambda: (xs_of(tq.get_value()), tq.get_value())
        R_xy = lambda: third_point(tp.get_value(), tq.get_value())

        def S_xy():
            r = R_xy()
            return None if r is None else (r[0], -r[1])

        def dot_of(fn, color, vis):
            def build():
                p = fn()
                return Dot(scr(*p) if p else ORIGIN, color=color, radius=0.09).set_opacity(vis.get_value() if p else 0)
            return always_redraw(build)

        def label_of(txt, color, fn, vis, direction):
            def build():
                p = fn()
                t = txt() if callable(txt) else txt
                m = MathTex(t, color=color, font_size=34)
                if p is None:
                    return m.set_opacity(0)
                return m.next_to(scr(*p), direction, buff=0.1).set_opacity(vis.get_value())
            return always_redraw(build)

        def secant():
            p = scr(*P_xy())
            if tangent():
                y = tp.get_value()
                d = np.array([UX, 3 * xs_of(y) ** 2 / (2 * y) * UY, 0])
            else:
                d = np.array(scr(*Q_xy())) - np.array(p)
            return clip_line(p, d, color=GREEN, stroke_width=4).set_opacity(l_vis.get_value())

        def reflect():
            r, s = R_xy(), S_xy()
            if r is None:
                return DashedLine(ORIGIN, RIGHT, color=GRAY).set_opacity(0)
            return DashedLine(scr(*r), scr(*s), color=GRAY).set_opacity(s_vis.get_value())

        def coord(name, color, fn, y, vis):
            def build():
                v = fn()
                n = name() if callable(name) else name
                if n == "Q" and tangent():
                    s = "Q = P"
                else:
                    s = f"{n} = ({v[0]:.2f},\\ {v[1]:.2f})"
                return MathTex(s, color=color, font_size=32).move_to([PX, y, 0], aligned_edge=LEFT).set_opacity(vis.get_value())
            return always_redraw(build)

        def say(text, wait=2.0):
            nonlocal step
            new = Text(text, font_size=24, line_spacing=0.8)
            if new.width > 6.0:
                new.scale_to_fit_width(6.0)
            new.move_to([PC, -3.1, 0])
            self.play(FadeOut(step) if step else Wait(0), FadeIn(new))
            step = new
            self.wait(wait)

        step = None

        # --- Title ---
        title = Text("Adding Points on\nan Elliptic Curve", font_size=44)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.scale(0.6).move_to([PC, 3.3, 0]))

        eq = MathTex("y^2 = x^3 + 7", font_size=44, color=ORANGE).move_to([PC, 2.2, 0])
        sub = Text("a = 0, b = 7: the Bitcoin curve", font_size=22).move_to([PC, 1.6, 0])
        self.play(Create(axes), FadeIn(numbers), FadeIn(eq), FadeIn(sub), run_time=2)
        self.play(Create(curve), run_time=3)

        # --- Live objects ---
        dotP, dotQ = dot_of(P_xy, RED, p_vis), dot_of(Q_xy, RED, q_vis)
        dotR, dotS = dot_of(R_xy, ORANGE, r_vis), dot_of(S_xy, BLUE, s_vis)
        labP = label_of("P", RED, P_xy, p_vis, UL)
        labQ = label_of(lambda: "" if tangent() else "Q", RED, Q_xy, q_vis, RIGHT)
        labR = label_of("R", ORANGE, R_xy, r_vis, LEFT)
        labS = label_of(lambda: names["S"], BLUE, S_xy, s_vis, RIGHT)
        coords = [
            coord("P", RED, P_xy, 0.7, p_vis),
            coord("Q", RED, Q_xy, 0.0, q_vis),
            coord("R", ORANGE, R_xy, -0.7, r_vis),
            coord(lambda: names["S"], BLUE, S_xy, -1.4, s_vis),
        ]
        line, refl = always_redraw(secant), always_redraw(reflect)
        self.add(line, refl, dotP, dotQ, dotR, dotS, labP, labQ, labR, labS, *coords)

        # --- P + Q ---
        say("Take two points P and Q on the curve,\nanywhere you like.", 0.5)
        self.play(p_vis.animate.set_value(1), q_vis.animate.set_value(1), run_time=1.5)
        self.wait(2)
        say("The line through P and Q meets the\ncurve in exactly one more point: R.", 0.5)
        self.play(l_vis.animate.set_value(1), run_time=1.5)
        self.play(r_vis.animate.set_value(1), run_time=1)
        self.play(Flash(scr(*R_xy()), color=ORANGE, flash_radius=0.4, line_length=0.2))
        self.wait(2)
        say("Definition: P + Q is the mirror image\nof R in the x-axis.", 0.5)
        self.play(s_vis.animate.set_value(1), run_time=2)
        rule = MathTex(r"P + Q = -R", font_size=44, color=BLUE).move_to([PC, -1.95, 0])
        self.play(FadeIn(rule))
        self.play(Indicate(dotS, scale_factor=2.2, color=BLUE))
        self.wait(3)

        # --- P + P: let Q slide onto P ---
        say("Now add P to itself: P + P.\nLet Q slide towards P \u2026", 0.5)
        self.play(FadeOut(rule), q_vis.animate.set_value(0), r_vis.animate.set_value(0),
                  s_vis.animate.set_value(0), l_vis.animate.set_value(0), run_time=1)
        tq.set_value(6.5)
        self.play(q_vis.animate.set_value(1), l_vis.animate.set_value(1),
                  r_vis.animate.set_value(1), s_vis.animate.set_value(1), run_time=1.2)
        self.wait(1)
        self.play(tq.animate.set_value(tp.get_value()), run_time=7, rate_func=smooth)
        names["S"] = "2P"
        say("\u2026 and the line becomes the tangent at P.\nIt meets the curve in a third point R.", 2)
        self.play(Flash(scr(*R_xy()), color=ORANGE, flash_radius=0.4, line_length=0.2))
        rule2 = MathTex(r"P + P = 2P = -R", font_size=44, color=BLUE).move_to([PC, -1.95, 0])
        self.play(FadeIn(rule2))
        self.play(Indicate(dotS, scale_factor=2.2, color=BLUE))
        self.wait(3)

        # --- P + (-P) = O ---
        say("Now add P and its mirror image \u2212P.", 0.5)
        self.play(FadeOut(rule2), q_vis.animate.set_value(0), r_vis.animate.set_value(0),
                  s_vis.animate.set_value(0), l_vis.animate.set_value(0), run_time=1)
        xP, yP = P_xy()
        negP = Dot(scr(xP, -yP), color=ORANGE, radius=0.09)
        negLab = MathTex("-P", color=ORANGE, font_size=34).next_to(negP, LEFT, buff=0.1)
        self.play(FadeIn(negP), FadeIn(negLab))
        self.play(Flash(scr(xP, -yP), color=ORANGE, flash_radius=0.4, line_length=0.2))
        vline = clip_line(scr(xP, yP), [0, 1, 0], color=GREEN, stroke_width=4)
        self.play(Create(vline), run_time=1.5)
        self.wait(1)
        say("The line through P and \u2212P is vertical:\nit has no third point on the curve.", 2.5)
        say("So we add one extra point, O, the point at\ninfinity: the third point of every vertical line.", 0.5)
        arrow = Arrow(scr(xP, 8.0), scr(xP, 9.6), buff=0, color=ORANGE, stroke_width=6,
                      max_tip_length_to_length_ratio=0.35)
        oLab = MathTex(r"O", color=ORANGE, font_size=40).next_to(arrow, RIGHT, buff=0.1)
        self.play(FadeIn(arrow), FadeIn(oLab))
        self.play(Flash(scr(xP, 9.0), color=ORANGE, flash_radius=0.4, line_length=0.2))
        self.wait(2)
        say("The mirror image of O is O itself.", 0.5)
        rule3 = MathTex(r"P + (-P) = O", font_size=44, color=BLUE).move_to([PC, -1.95, 0])
        self.play(FadeIn(rule3))
        self.play(Indicate(oLab, scale_factor=1.6, color=BLUE))
        self.wait(3.5)

        # --- P + O = P ---
        say("Now add O to P: P + O.\nThe line through P and O is the same vertical line.", 0.5)
        self.play(FadeOut(rule3))
        self.play(Indicate(vline, color=GREEN, scale_factor=1.0), run_time=1.5)
        self.wait(1.5)
        say("Its third point is \u2212P, and the mirror\nimage of \u2212P is P again.", 0.5)
        mirror = DashedLine(scr(xP, -yP), scr(xP, yP), color=GRAY)
        ring = Circle(radius=0.22, color=BLUE, stroke_width=5).move_to(scr(xP, yP))
        self.play(Create(mirror))
        self.play(Create(ring))
        rule4 = MathTex(r"P + O = -(-P) = P", font_size=44, color=BLUE).move_to([PC, -1.95, 0])
        self.play(FadeIn(rule4))
        self.wait(4)

        # --- Group structure ---
        for m in self.mobjects:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects])
        step = None
        head = Text("The curve forms an abelian group", font_size=40).move_to([0, 3.4, 0])
        defn = MathTex(r"E=\{(x,y):\ y^2=x^3+ax+b\}\cup\{O\},\qquad 4a^3+27b^2\neq 0", font_size=34).move_to([0, 2.55, 0])
        self.play(Write(head))
        self.play(FadeIn(defn))
        self.wait(2)
        rows = [
            ("1. Closure", r"P + Q \in E", "the line through P and Q always gives a third point (or O)"),
            ("2. Associativity", r"(P + Q) + R = P + (Q + R)", "true, but not obvious: proving it takes some algebra"),
            ("3. Identity", r"P + O = O + P = P", "we just saw this: O does nothing"),
            ("4. Inverse", r"P + (-P) = O, \quad -(x,y) = (x,-y)", "the vertical line through P and \u2212P has O as third point"),
            ("5. Commutativity", r"P + Q = Q + P", "the line through P and Q does not care about the order"),
        ]
        y = 1.5
        for name, formula, note in rows:
            n = Text(name, font_size=28, color=YELLOW).move_to([-6.8, y, 0], aligned_edge=LEFT)
            f = MathTex(formula, font_size=36).move_to([-2.7, y, 0], aligned_edge=LEFT)
            t = Text(note, font_size=20, color=GRAY).move_to([-2.7, y - 0.45, 0], aligned_edge=LEFT)
            self.play(FadeIn(n), Write(f), run_time=1.5)
            self.play(FadeIn(t))
            self.wait(2.5)
            y -= 0.95
        final = Text("(E, +) is an abelian group", font_size=34, color=BLUE).move_to([0, -3.5, 0])
        self.play(Write(final))
        self.wait(5)
