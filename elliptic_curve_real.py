"""Scene 2: The standard elliptic curve over the real numbers, with a and b animated live
to show how the shape of the curve changes (showcasing Manim's updater/transform strengths).
Ends with the cryptographic curve a=0, b=7 (secp256k1) and a camera zoom-out."""
from manim import *
import numpy as np

# Unit scale of the main axes: x in [-3, 4] over 6.2 units, y in [-8, 8] over 6.2 units.
X_LEN, Y_LEN = 6.2, 6.2
UNIT_X, UNIT_Y = X_LEN / 7, Y_LEN / 16
AXES_CENTER = np.array([2.8, -0.3, 0])
PANEL_X = -4.1  # centre of the text panel on the left


def curve_mobject(axes, a, b, x_min=-3.0, x_max=4.0, n=600, color=YELLOW, stroke_width=4):
    """Build a VGroup containing all real branches of y^2 = x^3 + a*x + b."""
    f = lambda x: x**3 + a * x + b
    xs_all = np.linspace(x_min, x_max, n)

    def root(lo, hi):
        # bisection between a negative and a non-negative point, so branches reach the x-axis
        for _ in range(40):
            mid = (lo + hi) / 2
            if (f(mid) >= 0) == (f(hi) >= 0):
                hi = mid
            else:
                lo = mid
        return hi if f(hi) >= 0 else lo

    branches = []
    cur = []
    prev = None
    for x in xs_all:
        v = f(x)
        if v >= 0:
            if not cur and prev is not None:
                r = root(prev, x)
                cur.append(r)
            cur.append(x)
        else:
            if cur:
                cur.append(root(cur[-1], x))
                if len(cur) > 1:
                    branches.append(cur)
            cur = []
        prev = x
    if len(cur) > 1:
        branches.append(cur)

    group = VGroup()
    for xs in branches:
        ys = [np.sqrt(max(f(x), 0)) for x in xs]
        top_pts = [axes.c2p(x, y) for x, y in zip(xs, ys)]
        bot_pts = [axes.c2p(x, -y) for x, y in zip(xs, ys)]
        group.add(VMobject(color=color, stroke_width=stroke_width).set_points_smoothly(top_pts))
        group.add(VMobject(color=color, stroke_width=stroke_width).set_points_smoothly(bot_pts))
    return group


class EllipticCurveReal(MovingCameraScene):
    def construct(self):
        title = Text("Elliptic Curves over the Real Numbers", font_size=40).to_edge(UP)
        self.play(Write(title))

        # The formula starts big in the centre of the screen.
        eq = MathTex("y^2", "=", "x^3", "+", "ax", "+", "b", font_size=64)
        self.play(Write(eq))
        self.wait(5)

        axes = Axes(
            x_range=[-3, 4, 1],
            y_range=[-8, 8, 2],
            x_length=X_LEN,
            y_length=Y_LEN,
            axis_config={"include_tip": True},
        ).move_to(AXES_CENTER)

        a_tracker = ValueTracker(-1.0)
        b_tracker = ValueTracker(1.0)
        xmax_tracker = ValueTracker(4.0)
        hl_tracker = ValueTracker(0.0)  # 0 = normal colour, 1 = highlighted (a=0, b=7)

        curve = always_redraw(
            lambda: curve_mobject(
                axes,
                a_tracker.get_value(),
                b_tracker.get_value(),
                x_max=xmax_tracker.get_value(),
                # keep the line thickness visible while the camera zooms out
                stroke_width=4 * self.camera.frame.width / config.frame_width,
                color=interpolate_color(YELLOW, ORANGE, hl_tracker.get_value()),
            )
        )

        value_label = always_redraw(
            lambda: MathTex(
                f"a = {a_tracker.get_value():.2f}",
                font_size=44,
            ).move_to([-6.4, 1.9, 0], aligned_edge=LEFT)
        )
        value_label_b = always_redraw(
            lambda: MathTex(
                f"b = {b_tracker.get_value():.2f}",
                font_size=44,
            ).move_to([-6.4, 1.1, 0], aligned_edge=LEFT)
        )

        # The formula moves to the bottom-left corner while the curve starts being drawn.
        self.play(
            eq.animate.scale(0.6).to_corner(DL, buff=0.5),
            Create(axes),
            run_time=2,
        )
        self.play(Create(curve), FadeIn(value_label), FadeIn(value_label_b))
        self.wait(1)

        # A tour through several (a, b) pairs, each giving a visibly different shape.
        # (-3, 0) has three real roots -> the curve splits into an oval plus a branch.
        # (0, 0) is the singular "cuspidal" cubic y^2 = x^3.
        waypoints = [(-3.0, 2.0), (0.0, 1.0), (-3.0, 0.0), (0.0, 0.0), (-1.0, 1.0)]
        for new_a, new_b in waypoints:
            self.play(
                a_tracker.animate.set_value(new_a),
                b_tracker.animate.set_value(new_b),
                run_time=3,
                rate_func=smooth,
            )
            self.wait(2.0)

        # Symmetry: the curve is mirrored in the x-axis, (x, y) on the curve => (x, -y) too.
        # The tour ends on (a, b) = (-1, 1), so the curve is still y^2 = x^3 - x + 1 here.
        px = ValueTracker(0.5)
        py = lambda: np.sqrt(px.get_value() ** 3 - px.get_value() + 1)
        mirror_axis = DashedLine(axes.c2p(-3, 0), axes.c2p(4, 0), color=BLUE, stroke_width=5)
        mirror_label = Text("mirror axis", font_size=20, color=BLUE).next_to(
            axes.c2p(4, 0), UP, buff=0.15).shift(LEFT * 0.6)
        dot_p = always_redraw(lambda: Dot(axes.c2p(px.get_value(), py()), color=RED, radius=0.09))
        dot_m = always_redraw(lambda: Dot(axes.c2p(px.get_value(), -py()), color=GREEN, radius=0.09))
        link = always_redraw(lambda: DashedLine(
            axes.c2p(px.get_value(), py()), axes.c2p(px.get_value(), -py()),
            color=GREY_B, stroke_width=2))
        lab_p = always_redraw(lambda: MathTex("P", color=RED, font_size=30).next_to(dot_p, UR, buff=0.05))
        lab_m = always_redraw(lambda: MathTex("-P", color=GREEN, font_size=30).next_to(dot_m, DR, buff=0.05))
        sym_title = Text("The curve is symmetric\nabout the x-axis", font_size=26).move_to([PANEL_X, 0.1, 0])
        coord_p = always_redraw(lambda: MathTex(
            f"P = ({px.get_value():.2f},\\ {py():.2f})", color=RED, font_size=34
        ).move_to([-6.4, -0.9, 0], aligned_edge=LEFT))
        coord_m = always_redraw(lambda: MathTex(
            f"-P = ({px.get_value():.2f},\\ {-py():.2f})", color=GREEN, font_size=34
        ).move_to([-6.4, -1.6, 0], aligned_edge=LEFT))
        sym_rule = MathTex(r"(x, y) \Rightarrow (x, -y)", font_size=34).move_to([PANEL_X, -2.4, 0])

        self.play(FadeIn(sym_title), Create(mirror_axis), FadeIn(mirror_label))
        self.play(FadeIn(dot_p), FadeIn(dot_m), Create(link), FadeIn(lab_p), FadeIn(lab_m),
                  FadeIn(coord_p), FadeIn(coord_m))
        self.play(FadeIn(sym_rule))
        self.play(px.animate.set_value(4.0), run_time=3, rate_func=smooth)
        self.play(px.animate.set_value(-1.2), run_time=4, rate_func=smooth)
        self.wait(1)
        self.play(*[FadeOut(m) for m in (
            sym_title, mirror_axis, mirror_label, dot_p, dot_m, link, lab_p, lab_m,
            coord_p, coord_m, sym_rule)])


        # Special case: the curve used in cryptography (Bitcoin): a = 0, b = 7.
        ecc_note = VGroup(
            Text("Special case:", font_size=28),
            Text("a = 0,  b = 7", font_size=36, color=ORANGE),
            Text("secp256k1, the curve used\nby Bitcoin", font_size=24),
        ).arrange(DOWN, buff=0.25).move_to([PANEL_X, -0.6, 0])
        self.play(
            a_tracker.animate.set_value(0.0),
            b_tracker.animate.set_value(7.0),
            hl_tracker.animate.set_value(1.0),
            run_time=3,
        )
        self.play(FadeIn(ecc_note))
        self.wait(2)

        # Zoom out with the camera so the whole curve is visible.
        self.play(FadeOut(title), FadeOut(eq), FadeOut(value_label),
                  FadeOut(value_label_b), FadeOut(ecc_note), run_time=0.8)

        x_max, y_max = 9.0, 30.0
        zoom_w = 44.0
        K = zoom_w / config.frame_width
        big_axes = Axes(
            x_range=[-3, x_max, 1],
            y_range=[-y_max, y_max, 5],
            x_length=(x_max + 3) * UNIT_X,
            y_length=2 * y_max * UNIT_Y,
            axis_config={"include_tip": True, "stroke_width": 2 * K, "tick_size": 0.1 * K},
        )
        big_axes.shift(axes.c2p(0, 0) - big_axes.c2p(0, 0))
        big_axes.get_x_axis().add_numbers(x_values=range(-2, 10, 2), font_size=36 * K)
        big_axes.get_y_axis().add_numbers(
            x_values=[-30, -20, -10, 10, 20, 30], font_size=36 * K)

        center = np.array([axes.c2p(-3, 0)[0] + 5.3, axes.c2p(0, 0)[1], 0])
        self.play(
            self.camera.frame.animate.set(width=zoom_w).move_to(center),
            FadeOut(axes),
            FadeIn(big_axes),
            xmax_tracker.animate.set_value(x_max),
            run_time=8,
            rate_func=smooth,
        )

        # Labels placed in the zoomed frame, scaled so they look like normal text.
        left = center[0] - zoom_w / 2
        label = VGroup(
            Text("secp256k1", font_size=24, color=ORANGE),
            MathTex("y^2 = x^3 + 7", font_size=48),
            Text("a = 0, b = 7", font_size=28),
            Text("the elliptic curve\nused by Bitcoin", font_size=24),
            Text("symmetric about the x-axis", font_size=22, color=BLUE),
        ).arrange(DOWN, buff=0.3)
        label.scale(K * 0.8).move_to([left + 8, center[1], 0])
        self.play(FadeIn(label))
        self.wait(6)
