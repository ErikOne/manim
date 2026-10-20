"""Scene 6: The discrete logarithm problem.
Layout: the curve/graph lives on the left half of the screen, all explanatory
text lives in a panel on the right half (same split used in finite_field.py).
Uses p = 97 from the very start so the search space already looks big, does a
step-by-step forward walk G -> 2G -> ... -> kG (easy), then tries several
different wrong exponents and shows they land all over the curve instead of
on Q -- illustrating why recovering k from G and Q alone is hard."""
from manim import *


def inv_mod(x, p):
    return pow(x, p - 2, p)


def ec_add(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        m = (3 * x1 * x1 + a) * inv_mod(2 * y1, p) % p
    else:
        m = (y2 - y1) * inv_mod((x2 - x1) % p, p) % p
    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    return (x3, y3)


def scalar_mul(k, P, p, a):
    result = None
    for _ in range(k):
        result = ec_add(result, P, p, a)
    return result


# Left column: the graph  |  Right column (x >~ 1.0): the text panel.
AXES_CENTER = LEFT * 3.5 + DOWN * 0.5
PANEL_X = 1.3
PANEL_TOP_Y = 2.5


class DiscreteLog(Scene):
    def construct(self):
        title = Text("The Discrete Logarithm Problem", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        p, a, b = 97, -1, 1
        eq = MathTex(f"y^2 \\equiv x^3 - x + 1 \\pmod{{{p}}}", font_size=32)
        eq.move_to(LEFT * 3.3 + UP * 2.6)
        self.play(Write(eq))

        axes = Axes(
            x_range=[0, p, 10], y_range=[0, p, 10],
            x_length=4.8, y_length=4.8,
            axis_config={"include_tip": False, "include_numbers": False},
        ).move_to(AXES_CENTER)
        self.play(Create(axes))

        points = []
        for x in range(p):
            rhs = (x**3 + a * x + b) % p
            for y in range(p):
                if (y * y) % p == rhs:
                    points.append((x, y))
        curve_dots = VGroup(*[Dot(axes.c2p(x, y), radius=0.045, color=GRAY) for x, y in points])
        self.play(FadeIn(curve_dots), run_time=1)

        intro = Text(
            f"{len(points)} points on this curve\n(mod {p}) already \u2014 far too many\n"
            "to search by hand. Real curves\nused in cryptography are vastly\nbigger still.",
            font_size=20, line_spacing=1.2,
        )
        intro.move_to([PANEL_X, PANEL_TOP_Y, 0], aligned_edge=UL)
        self.play(FadeIn(intro))
        self.wait(1.5)
        self.play(FadeOut(intro))

        # --- Forward direction: G, 2G, 3G, ... is easy to compute ---
        header = Text("Forward: computing k \u00b7 G is easy", font_size=24)
        header.move_to([PANEL_X, PANEL_TOP_Y, 0], aligned_edge=UL)
        formula = MathTex(r"k \cdot G = \underbrace{G + G + \cdots + G}_{k\ \text{times}}", font_size=28)
        formula.next_to(header, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(FadeIn(header), Write(formula))

        G = (0, 1)
        dotG = Dot(axes.c2p(*G), color=RED, radius=0.11)
        labG = MathTex("G", color=RED, font_size=32).next_to(dotG, UP, buff=0.1)
        self.play(FadeIn(dotG), Write(labG))

        k_label = Text("k = 1", font_size=24)
        k_label.next_to(formula, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(FadeIn(k_label))

        cur = G
        moving_dot = Dot(axes.c2p(*G), color=YELLOW, radius=0.1)
        trail = VGroup()
        self.play(FadeIn(moving_dot))

        target_k = 29
        for k in range(2, target_k + 1):
            cur = ec_add(cur, G, p, a)
            new_dot_pos = axes.c2p(*cur)
            new_label = Text(f"k = {k}", font_size=24).move_to(k_label, aligned_edge=LEFT)
            left_trail = Dot(moving_dot.get_center(), color=BLUE, radius=0.045, fill_opacity=0.6)
            trail.add(left_trail)
            # Slower, fully visible jumps for the first few steps; speed up after.
            rt = 0.45 if k <= 6 else 0.18
            self.play(
                FadeIn(left_trail),
                moving_dot.animate.move_to(new_dot_pos),
                Transform(k_label, new_label),
                run_time=rt,
            )
        self.wait(0.3)

        Qdot = Dot(axes.c2p(*cur), color=BLUE, radius=0.12)
        labQ = MathTex(f"Q = {target_k} \\cdot G", color=BLUE, font_size=32).next_to(Qdot, DOWN, buff=0.15)
        self.play(FadeIn(Qdot), Write(labQ), FadeOut(moving_dot))
        self.wait(0.5)

        self.play(
            FadeOut(header), FadeOut(formula), FadeOut(k_label), FadeOut(trail),
        )

        # --- Backward direction: given only G and Q, k is hard to recover ---
        back_header = Text("Backward: finding k from G and Q", font_size=24, line_spacing=1.2)
        back_header.move_to([PANEL_X, PANEL_TOP_Y, 0], aligned_edge=UL)
        back_sub = Text(
            "is extremely hard.\nLet's try a few guesses for k:",
            font_size=20, line_spacing=1.2,
        ).next_to(back_header, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeIn(back_header), FadeIn(back_sub))
        self.wait(0.5)

        guess_log = VGroup()
        guesses = [8, 43, 58, 71, 89]
        for g in guesses:
            guess_point = scalar_mul(g, G, p, a)
            guess_dot = Dot(axes.c2p(*guess_point), color=ORANGE, radius=0.1)
            guess_lab = Text(f"k = {g}?", font_size=20, color=ORANGE).next_to(guess_dot, UP, buff=0.08)
            self.play(FadeIn(guess_dot), FadeIn(guess_lab), run_time=0.5)
            self.wait(0.3)
            cross = Text("\u2717 not Q", font_size=18, color=ORANGE)
            cross.next_to(guess_log[-1] if len(guess_log) else back_sub, DOWN, buff=0.22, aligned_edge=LEFT)
            self.play(FadeIn(cross), run_time=0.3)
            guess_log.add(cross)
            # Fade the failed guess to a faint gray mark so the curve keeps
            # accumulating visible "misses" instead of cluttering with labels.
            faded_dot = Dot(axes.c2p(*guess_point), color=GRAY, radius=0.055, fill_opacity=0.6)
            self.play(FadeOut(guess_lab), ReplacementTransform(guess_dot, faded_dot), run_time=0.3)

        self.wait(0.3)
        reveal = Text(
            f"The only exponent that works\nis k = {target_k}.",
            font_size=20, line_spacing=1.2, color=BLUE_A,
        )
        reveal.next_to(back_sub, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeOut(guess_log), FadeIn(reveal))
        self.wait(1)

        # --- On average, how many guesses would brute force need? ---
        n_here = p - 1  # number of possible nonzero exponents here
        avg_block = VGroup(
            MathTex(
                r"\text{average tries} = \frac{1+2+\cdots+n}{n} = \frac{n(n+1)}{2n} = \frac{n+1}{2}",
                font_size=21,
            ),
            Text(
                f"With n = {n_here} possible keys here,\n"
                f"average \u2248 {(n_here + 1) / 2:g} guesses needed.",
                font_size=20, line_spacing=1.2,
            ),
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        avg_block.next_to(back_sub, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeOut(reveal), FadeIn(avg_block))
        self.wait(2)

        # --- Scale the same formula up to a real 256-bit key ---
        big_block = VGroup(
            Text("Real elliptic curves use far\nlarger keys, e.g. 256 bits:", font_size=20, color=GRAY_B, line_spacing=1.2),
            MathTex(r"n = 2^{256} \quad\Rightarrow\quad \frac{n+1}{2} \approx 2^{255}", font_size=21),
            MathTex(r"\approx 5.8 \times 10^{76} \text{ guesses on average}", font_size=21, color=BLUE_A),
            Text(
                "\u2014 more than the number of atoms\nin the observable universe.",
                font_size=20, line_spacing=1.2, color=BLUE_A,
            ),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        big_block.next_to(back_sub, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeOut(avg_block), FadeIn(big_block))
        self.wait(2.5)

        self.play(FadeOut(back_header), FadeOut(back_sub), FadeOut(big_block))

        # --- Zoom out: what does a much bigger (but still modest) prime
        # actually look like? This showcases Manim's transform/zoom-out
        # capability while giving a visceral sense of scale. ---
        zoom_header = Text(
            "Let's zoom out to a bigger\n(but still modest) prime to get\na feel for that scale:",
            font_size=20, color=GRAY_B, line_spacing=1.2,
        )
        zoom_header.move_to([PANEL_X, PANEL_TOP_Y, 0], aligned_edge=UL)
        self.play(FadeIn(zoom_header))

        p_big = 999983  # the largest prime below 100,000
        axes_big = Axes(
            x_range=[0, p_big, p_big // 5],
            y_range=[0, p_big, p_big // 5],
            x_length=4.8, y_length=4.8,
            axis_config={"include_tip": False, "include_numbers": False},
        ).move_to(axes)
        eq_big = MathTex(
            f"y^2 \\equiv x^3 - x + 1 \\pmod{{{p_big}}}", font_size=28
        ).move_to(eq)

        # Exact point count via the Legendre symbol -- avoids an O(p^2) scan.
        count_big = 0
        for x in range(p_big):
            rhs = (x**3 + a * x + b) % p_big
            if rhs == 0:
                count_big += 1
            elif pow(rhs, (p_big - 1) // 2, p_big) == 1:
                count_big += 2

        # A sparse sample of the actual points -- plotting all ~100k points
        # would be far too many mobjects to animate. Since p_big % 4 == 3,
        # square roots mod p_big are simply rhs ** ((p_big + 1) / 4).
        sample_dots = VGroup()
        step = max(1, p_big // 1500)
        for x in range(0, p_big, step):
            rhs = (x**3 + a * x + b) % p_big
            if rhs == 0:
                sample_dots.add(Dot(axes_big.c2p(x, 0), radius=0.02, color=GRAY))
            elif pow(rhs, (p_big - 1) // 2, p_big) == 1:
                y = pow(rhs, (p_big + 1) // 4, p_big)
                sample_dots.add(Dot(axes_big.c2p(x, y), radius=0.02, color=GRAY))
                sample_dots.add(Dot(axes_big.c2p(x, p_big - y), radius=0.02, color=GRAY))

        self.play(
            ReplacementTransform(axes, axes_big),
            ReplacementTransform(eq, eq_big),
            FadeOut(curve_dots), FadeOut(dotG), FadeOut(labG), FadeOut(Qdot), FadeOut(labQ),
            FadeIn(sample_dots),
            run_time=3,
        )

        count_label = Text(
            f"{count_big:,} points on this curve\n(mod {p_big}) \u2014 and this prime\nis still tiny next to a real\n256-bit curve.",
            font_size=20, line_spacing=1.2,
        )
        count_label.next_to(zoom_header, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(FadeIn(count_label))
        self.wait(2.5)

        self.play(FadeOut(zoom_header), FadeOut(count_label))

        question = Text(
            "Forward (k \u2192 kG) is easy.\nGiven only G and Q, finding k\nis what makes this a hard\n"
            "problem to reverse \u2014 the\ndiscrete logarithm problem.",
            font_size=22, line_spacing=1.25,
        )
        question.move_to([PANEL_X, PANEL_TOP_Y, 0], aligned_edge=UL)
        self.play(FadeIn(question))
        self.wait(3)
