"""Scene 3: Any line through two points on the curve meets it at a third point.
Uses the Bitcoin curve y^2 = x^3 + 7. P and Q move along the curve, the secant line and the
third intersection R follow live, and the camera zooms out automatically when R runs away.
The text panel on the left is pinned to the camera frame so it stays readable while zooming."""
from manim import *
import numpy as np

UNIT_X, UNIT_Y = 0.75, 0.37          # screen units per curve unit
ORIGIN_SCREEN = np.array([2.2, -0.3, 0])
PANEL_FRAC = 0.41                    # share of the frame width reserved for text
FRAME_W0 = config.frame_width
TANGENT_EPS = 1e-4


def xs_of(t):
    """The curve y^2 = x^3 + 7 is a graph x = cbrt(y^2 - 7), so t = y parametrises it smoothly."""
    return np.cbrt(t * t - 7)


def third_point(tp, tq):
    xp, xq = xs_of(tp), xs_of(tq)
    if abs(tq - tp) < TANGENT_EPS:
        # Q has reached P: the secant becomes the tangent, slope 3x^2 / (2y)
        if abs(tp) < 1e-9:
            return None
        m = 3 * xp * xp / (2 * tp)
        x3 = m * m - 2 * xp
        return x3, tp + m * (x3 - xp)
    if abs(xq - xp) < 1e-6:
        return None  # vertical line: no third point (point at infinity)
    m = (tq - tp) / (xq - xp)
    x3 = m * m - xp - xq
    return x3, tp + m * (x3 - xp)


class ThirdIntersection(MovingCameraScene):
    def construct(self):
        frame = self.camera.frame
        kk = lambda: frame.width / FRAME_W0

        axes = Axes(
            x_range=[-3, 13, 1],
            y_range=[-40, 40, 2],
            x_length=16 * UNIT_X,
            y_length=80 * UNIT_Y,
            axis_config={"include_tip": True, "stroke_width": 2, "tick_size": 0.06},
        )
        axes.shift(ORIGIN_SCREEN - axes.c2p(0, 0))
        curve = ParametricFunction(
            lambda t: axes.c2p(xs_of(t), t), t_range=[-45, 45, 0.05], color=YELLOW, stroke_width=4
        )
        numbers = VGroup(
            *[axes.x_axis.get_number_mobject(v, font_size=20) for v in range(-2, 7) if v],
            *[axes.y_axis.get_number_mobject(v, font_size=20) for v in range(-8, 9, 2) if v],
        )

        tp = ValueTracker(np.sqrt(3.625))   # P = (-1.5, +1.90)
        tq = ValueTracker(-np.sqrt(3.5 ** 3 + 7))                    # Q = (3.5, -7.06)
        r_vis = ValueTracker(1.0)

        scr = lambda x, y: axes.c2p(x, y)
        P_pt = lambda: scr(xs_of(tp.get_value()), tp.get_value())
        Q_pt = lambda: scr(xs_of(tq.get_value()), tq.get_value())

        def R_pt():
            r = third_point(tp.get_value(), tq.get_value())
            return scr(*r) if r else None

        # The camera follows P, Q and R (R only while visible); the left panel needs PANEL_FRAC.
        def fit(f):
            pts = [P_pt(), Q_pt()]
            if r_vis.get_value() > 0.01 and R_pt() is not None:
                pts.append(R_pt())
            xs = [p[0] for p in pts] + [0.0, 5.8]
            ys = [p[1] for p in pts] + [-3.4, 2.9]
            m = 1.5
            W = max(FRAME_W0, (max(ys) - min(ys) + 2 * m) * 16 / 9,
                    (max(xs) - min(xs) + 2 * m) / (1 - PANEL_FRAC))
            f.set(width=W)
            f.move_to([(max(xs) + min(xs)) / 2 - (0.5 - PANEL_FRAC) * W, (max(ys) + min(ys)) / 2, 0])

        fit(frame)
        self.add(frame)
        frame.add_updater(fit)

        def pin(m, offset):
            """Keep a static mobject at a fixed place and relative size inside the camera frame."""
            w0 = m.width
            m.add_updater(lambda mm: (
                mm.set(width=w0 * kk()),
                mm.move_to(frame.get_center() + kk() * np.array(offset)),
            ))
            m.update()
            return m

        def live(build, offset):
            return always_redraw(lambda: build().scale(kk()).move_to(
                frame.get_center() + kk() * np.array(offset), aligned_edge=LEFT))

        # --- Title in the centre, then up into the panel ---
        title = Text("Two Points Always\nGive a Third", font_size=44)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.scale(0.8).move_to(frame.get_center() + np.array([-4.2, 3.0, 0])))
        pin(title, [-4.2, 3.0, 0])
        # Reading P, Q, R in the panel makes the always-redraw items independent of the camera.

        # --- The Bitcoin curve ---
        eq = pin(MathTex("y^2 = x^3 + 7", font_size=44, color=ORANGE), [-4.2, 1.7, 0])
        sub = pin(Text("a = 0, b = 7: the Bitcoin curve", font_size=22), [-4.2, 1.05, 0])
        self.play(Create(axes), FadeIn(numbers), FadeIn(eq), FadeIn(sub), run_time=2)
        curve.add_updater(lambda c: c.set_stroke(width=4 * kk()))
        axes.x_axis.add_updater(lambda a: a.set_stroke(width=2 * kk()))
        axes.y_axis.add_updater(lambda a: a.set_stroke(width=2 * kk()))
        self.play(Create(curve), run_time=4)
        self.wait(1)

        step = None

        def say(text, wait=2.0):
            nonlocal step
            new = Text(text, font_size=24, line_spacing=0.8)
            if new.width > 5.2:
                new.scale_to_fit_width(5.2)
            pin(new, [-4.2, -2.5, 0])
            self.play(FadeOut(step) if step else Wait(0), FadeIn(new))
            step = new
            self.wait(wait)

        # --- Dots, labels, line ---
        dotP = always_redraw(lambda: Dot(P_pt(), color=RED, radius=0.09 * kk()))
        dotQ = always_redraw(lambda: Dot(Q_pt(), color=RED, radius=0.09 * kk()))

        def dotR_build():
            p = R_pt()
            d = Dot(p if p is not None else ORIGIN, color=ORANGE, radius=0.09 * kk())
            return d.set_opacity(r_vis.get_value() if p is not None else 0)

        dotR = always_redraw(dotR_build)

        def label(txt, color, pt_fn, direction, vis=None):
            def build():
                p = pt_fn()
                m = MathTex(txt, color=color, font_size=34).scale(kk())
                if p is None:
                    return m.set_opacity(0)
                m.next_to(p, direction, buff=0.08 * kk())
                return m.set_opacity(vis.get_value() if vis is not None else 1)
            return always_redraw(build)

        labP = label("P", RED, P_pt, UP)
        labQ = label("Q", RED, Q_pt, DL)
        labR = label("R", ORANGE, R_pt, DL, r_vis)

        # The line is clipped to the axes box so it never runs through the text panel.
        box = [(axes.c2p(-3, 0)[0], axes.c2p(13, 0)[0]), (axes.c2p(0, -40)[1], axes.c2p(0, 40)[1])]

        def secant():
            p = np.array(P_pt())
            if abs(tq.get_value() - tp.get_value()) < TANGENT_EPS:
                y = tp.get_value()
                m = 3 * xs_of(y) ** 2 / (2 * y)
                d = np.array([UNIT_X, m * UNIT_Y, 0])
            else:
                d = np.array(Q_pt()) - p
            d = d / np.linalg.norm(d)
            t0, t1 = -1e9, 1e9
            for i, (lo, hi) in enumerate(box):
                if abs(d[i]) < 1e-12:
                    continue
                ta, tb = (lo - p[i]) / d[i], (hi - p[i]) / d[i]
                t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
            return Line(p + d * t0, p + d * t1, color=GREEN, stroke_width=4 * kk())

        line = always_redraw(secant)

        coord_vis = ValueTracker(1.0)

        def coord_text(name, color, fn, y):
            def build():
                v = fn()
                if name == "Q" and abs(tq.get_value() - tp.get_value()) < TANGENT_EPS:
                    s = "Q = P"
                elif v is None:
                    s = f"{name} = \\infty"
                elif name == "R" and r_vis.get_value() < 0.5:
                    s = f"{name} = {{?}}"
                else:
                    s = f"{name} = ({v[0]:.2f},\\ {v[1]:.2f})"
                return MathTex(s, color=color, font_size=32).set_opacity(coord_vis.get_value())
            return live(build, [-6.6, y, 0])

        P_xy = lambda: (xs_of(tp.get_value()), tp.get_value())
        Q_xy = lambda: (xs_of(tq.get_value()), tq.get_value())
        coordP = coord_text("P", RED, P_xy, 0.2)
        coordQ = coord_text("Q", RED, Q_xy, -0.5)
        coordR = coord_text("R", ORANGE, lambda: third_point(tp.get_value(), tq.get_value()), -1.2)

        say("Pick two points on the curve:\nP and Q, anywhere.", 0.5)
        self.play(FadeIn(dotP), FadeIn(labP), FadeIn(coordP))
        self.play(FadeIn(dotQ), FadeIn(labQ), FadeIn(coordQ))
        

        say("Draw the straight line\nthrough P and Q.", 0.5)
        self.play(Create(line), run_time=2)
        

        say("This line always hits the curve\nin exactly one more point: R.", 0.5)
        self.play(FadeIn(dotR), FadeIn(labR), FadeIn(coordR))
        self.play(Flash(R_pt(), color=ORANGE, flash_radius=0.5, line_length=0.25))
        self.play(Indicate(dotR, scale_factor=2.5, color=ORANGE))
        

        say("P, Q and R are the three\nintersections of line and curve.", 3)

        # --- Move P ---
        
        self.play(tp.animate.set_value(-1.2), run_time=2, rate_func=smooth)
        self.play(tp.animate.set_value(np.sqrt(3.625)), run_time=2, rate_func=smooth)
        self.wait(0.5)

        # --- Move Q: R runs away, the camera zooms out ---
        
        self.play(tq.animate.set_value(-100.0), run_time=6, rate_func=smooth)
        self.play(tq.animate.set_value(-3.0), run_time=2, rate_func=smooth)
        self.wait(1)
        
        self.play(FadeOut(numbers), run_time=0.5)
        self.play(tq.animate.set_value(-2.646), run_time=1, rate_func=smooth)
        self.wait(1)

        self.play(tq.animate.set_value(-np.sqrt(3.5 ** 3 + 7)), run_time=2, rate_func=smooth)
        self.play(FadeIn(numbers), run_time=0.5)
        self.wait(1)

        # --- The vertical exception ---
        say("One exception: Q directly\nbelow P gives a vertical line.", 1)
        self.play(r_vis.animate.set_value(0.0), run_time=1)
        self.play(tq.animate.set_value(-np.sqrt(3.625)), run_time=6, rate_func=smooth)
        say("A vertical line meets the curve\nonly twice: no third point\n(the 'point at infinity').", 5)
        self.play(tq.animate.set_value(-np.sqrt(3.5 ** 3 + 7)), run_time=4, rate_func=smooth)
        self.play(r_vis.animate.set_value(1.0), run_time=1)
        

        # --- The tangent: Q slides onto P ---
        say("What if the two points\nare the same point?", 1)
        self.play(tp.animate.set_value(-4.0), run_time=6, rate_func=smooth)
        self.wait(1)
        say("Slide Q along the curve\ntowards P.", 1)
        self.play(tq.animate.set_value(-5.0), run_time=3, rate_func=smooth)
        self.play(tq.animate.set_value(-4.2), run_time=5, rate_func=rush_from)
        self.wait(1)
        say("The closer Q gets to P, the\nmore the line turns into\nthe tangent at P.", 1)
        self.play(tq.animate.set_value(-4.0), run_time=4, rate_func=smooth)
        self.wait(2)
        say("The tangent at P also meets\nthe curve in a third point R.", 0.5)
        self.play(Flash(R_pt(), color=ORANGE, flash_radius=0.5, line_length=0.25))
        self.play(Indicate(dotR, scale_factor=2.5, color=ORANGE))
        self.wait(3)
        say("So two points, or one point\nand its tangent: always a third.", 5)

        # --- The formulas, and the condition on a and b ---
        self.play(FadeOut(step), coord_vis.animate.set_value(0.0), run_time=1)
        step = None
        general = pin(MathTex("y^2 = x^3 + ax + b", font_size=44, color=ORANGE), [-4.2, 1.7, 0])
        self.play(FadeOut(eq), FadeOut(sub), FadeIn(general))

        def block(*items, y=-0.9, gap=0.3):
            g = VGroup(*items).arrange(DOWN, buff=gap)
            g.scale_to_fit_width(min(g.width, 5.3))
            if g.height > 4.0:
                g.scale_to_fit_height(4.0)
            return pin(g, [-4.2, y, 0])

        formulas = block(
            Text("How to compute R exactly:", font_size=24),
            MathTex(r"m = \frac{y_Q - y_P}{x_Q - x_P}", font_size=38),
            MathTex(r"\text{tangent } (Q = P):\ m = \frac{3x_P^2 + a}{2y_P}", font_size=30),
            MathTex(r"x_R = m^2 - x_P - x_Q", font_size=38),
            MathTex(r"y_R = y_P + m\,(x_R - x_P)", font_size=38),
        )
        self.play(FadeIn(formulas))
        self.wait(8)

        condition = block(
            Text("For this to work, a and b must satisfy:", font_size=24),
            MathTex(r"4a^3 + 27b^2 \neq 0", font_size=46, color=YELLOW),
            Text("Otherwise the curve has a cusp or crosses\nitself and the tangent breaks down.", font_size=20),
            MathTex(r"\text{Bitcoin: } 4\cdot 0^3 + 27\cdot 7^2 = 1323 \neq 0 \ \checkmark", font_size=30),
            y=-0.9,
        )
        self.play(FadeOut(formulas), FadeIn(condition))
        self.wait(6)

        # --- Curves that violate the condition ---
        gone = [dotP, dotQ, dotR, labP, labQ, labR, line]
        for m in gone:
            m.clear_updaters()
        self.play(FadeOut(*gone), FadeOut(curve), FadeOut(condition), run_time=1.5)

        # Parametrisations: y^2 = x^3 -> (t^2, t^3); y^2 = (x-1)^2 (x+2) -> (s^2 - 2, s^3 - 3s)
        cusp = ParametricFunction(lambda t: axes.c2p(t ** 2, t ** 3), t_range=[-2, 2, 0.02],
                                  color=RED_C, stroke_width=4)
        node = ParametricFunction(lambda t: axes.c2p(t ** 2 - 2, t ** 3 - 3 * t), t_range=[-2.5, 2.5, 0.02],
                                  color=RED_C, stroke_width=4)
        cusp_info = block(
            Text("Example 1: a = 0, b = 0", font_size=24),
            MathTex(r"y^2 = x^3", font_size=44, color=RED_C),
            MathTex(r"4\cdot 0^3 + 27\cdot 0^2 = 0", font_size=34),
            Text("A cusp: there is no tangent\nin the sharp point, so the\nthird point breaks down.", font_size=22),
        )
        self.play(Create(cusp), FadeIn(cusp_info), run_time=3)
        cusp_dot = Dot(axes.c2p(0, 0), color=WHITE, radius=0.09 * kk())
        self.play(FadeIn(cusp_dot), Indicate(cusp_dot, scale_factor=3))
        self.wait(7)

        node_info = block(
            Text("Example 2: a = \u22123, b = 2", font_size=24),
            MathTex(r"y^2 = x^3 - 3x + 2", font_size=44, color=RED_C),
            MathTex(r"4\cdot(-3)^3 + 27\cdot 2^2 = 0", font_size=34),
            Text("A self-crossing: two different\ntangents in the same point.", font_size=22),
        )
        self.play(FadeOut(cusp), FadeOut(cusp_dot), FadeOut(cusp_info), run_time=1)
        self.play(Create(node), FadeIn(node_info), run_time=3)
        node_dot = Dot(axes.c2p(1, 0), color=WHITE, radius=0.09 * kk())
        self.play(FadeIn(node_dot), Indicate(node_dot, scale_factor=3))
        self.wait(7)

