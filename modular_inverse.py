"""Modular arithmetic from scratch: clock (hours mod 24, minutes mod 60), addition,
multiplication, inverses (5^-1 mod 19), zero divisors (mod 12) and why p must be prime."""
from manim import *
import numpy as np

HOUR_C, MIN_C = BLUE, GREEN


class ModularInverse(Scene):
    # ---------- helpers ----------
    def stack(self, mobs, x, y0, gap=0.75, wait=1.0, rt=0.8):
        """Place mobs in a column centred on x, reveal them one by one."""
        grp = VGroup()
        for i, m in enumerate(mobs):
            m.move_to([x, y0 - i * gap, 0])
            grp.add(m)
            self.play(FadeIn(m, shift=UP * 0.2), run_time=rt)
            self.wait(wait)
        return grp

    def clear(self, *mobs, rt=0.6):
        self.play(*[FadeOut(m) for m in mobs], run_time=rt)

    def table(self, n, a, x0, w, y_top, show_values=True, fs=26):
        """Two-row table: y = 0..n-1 and a*y mod n. Returns (ys, vals, frame cells)."""
        ys, vals = VGroup(), VGroup()
        for y in range(n):
            x = x0 + w * (y + 0.5)
            ys.add(Text(str(y), font_size=fs).move_to([x, y_top, 0]))
            vals.add(Text(str(a * y % n), font_size=fs).move_to([x, y_top - 0.9, 0]))
        return ys, vals

    def construct(self):
        # =====================================================  1. THE CLOCK
        title = Text("Modular arithmetic", font_size=44)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP, buff=0.3).scale(0.7))

        C = np.array([-3.4, -0.4, 0.0])
        RAD = 2.4
        face = Circle(radius=RAD, color=WHITE, stroke_width=3).move_to(C)
        ticks = VGroup()
        for k in range(60):
            ang = 2 * PI * k / 60
            d = np.array([np.sin(ang), np.cos(ang), 0])
            ln = 0.22 if k % 5 == 0 else 0.1
            ticks.add(Line(C + d * (RAD - ln), C + d * RAD, stroke_width=3 if k % 5 == 0 else 1.5))
        nums = VGroup()
        for k in range(1, 13):
            ang = 2 * PI * k / 12
            nums.add(Text(str(k), font_size=26).move_to(C + 1.9 * np.array([np.sin(ang), np.cos(ang), 0])))
        t = ValueTracker(1200)  # minutes since 00:00 (starts at 20:00)

        def hand(length, frac, color, width):
            def mk():
                ang = 2 * PI * frac(t.get_value())
                return Line(C, C + length * np.array([np.sin(ang), np.cos(ang), 0]),
                            color=color, stroke_width=width)
            return always_redraw(mk)

        hour_hand = hand(1.35, lambda v: (v % 720) / 720, HOUR_C, 7)
        min_hand = hand(2.0, lambda v: (v % 60) / 60, MIN_C, 4)
        pivot = Dot(C, radius=0.07)

        def digital():
            v = int(t.get_value())
            h, m = (v // 60) % 24, v % 60
            return Text(f"{h:02d}:{m:02d}", font_size=88,
                        t2c={"[0:2]": HOUR_C, "[3:5]": MIN_C}).move_to([3.4, 1.7, 0])

        dig = always_redraw(digital)
        lab_h = Text("hours (0 – 23)", font_size=22, color=HOUR_C).move_to([2.2, 0.8, 0])
        lab_m = Text("minutes (0 – 59)", font_size=22, color=MIN_C).move_to([4.7, 0.8, 0])

        self.play(Create(face), FadeIn(ticks), FadeIn(nums), run_time=1.5)
        self.play(FadeIn(hour_hand), FadeIn(min_hand), FadeIn(pivot), FadeIn(dig),
                  FadeIn(lab_h), FadeIn(lab_m))

        c1 = Text("It is 20:00. What time is it 6 hours later?", font_size=26).move_to([3.4, -0.5, 0])
        self.play(FadeIn(c1))
        self.wait(1)
        self.play(t.animate.set_value(1560), run_time=4)  # 02:00
        c2 = MathTex(r"20 + 6 = 26 \equiv 2 \pmod{24}", color=HOUR_C).move_to([3.4, -1.3, 0])
        self.play(FadeIn(c2))
        self.wait(2)
        c3 = MathTex(r"45 + 30 = 75 \equiv 15 \pmod{60}", color=MIN_C).move_to([3.4, -2.6, 0])
        c3t = Text("Same for minutes:", font_size=24).move_to([3.4, -2.0, 0])
        self.play(FadeIn(c3t), FadeIn(c3))
        self.wait(2.5)
        c4 = Text("Add as usual, then keep the remainder after dividing by n.", font_size=26)
        c4.move_to([0, -3.5, 0])
        self.play(Write(c4))
        self.wait(2.5)

        dig.clear_updaters(); hour_hand.clear_updaters(); min_hand.clear_updaters()
        self.play(*[FadeOut(m) for m in [face, ticks, nums, hour_hand, min_hand, pivot, dig,
                                          lab_h, lab_m, c1, c2, c3, c3t, c4, title]])

        # =====================================================  2. MULTIPLICATION
        t2 = Text("Multiplication mod 19", font_size=40).to_edge(UP, buff=0.4)
        self.play(Write(t2))
        m1 = MathTex(r"4 \cdot 6 = 24 = 1\cdot 19 + 5 \;\Rightarrow\; 4\cdot 6 \equiv 5 \pmod{19}", font_size=40)
        m2 = MathTex(r"7 \cdot 8 = 56 = 2\cdot 19 + 18 \;\Rightarrow\; 7\cdot 8 \equiv 18 \pmod{19}", font_size=40)
        m3 = Text("Multiply as usual, then keep the remainder after dividing by 19.", font_size=28)
        g = self.stack([m1, m2, m3], 0, 1.0, gap=1.3, wait=1.8, rt=1.0)
        self.wait(1)
        self.clear(g, t2)

        # =====================================================  3. INVERSES IN Q
        t3 = Text("Inverses: first in the rational numbers", font_size=40).to_edge(UP, buff=0.4)
        self.play(Write(t3))
        q1 = MathTex(r"5 \cdot \tfrac{1}{5} = 1", font_size=64)
        q2 = Text("1/5 is the inverse of 5: the number you multiply 5 by to get 1.", font_size=28)
        q3 = Text("(1 is the neutral element of multiplication: x · 1 = x)", font_size=24, color=GRAY_B)
        g1 = self.stack([q1, q2, q3], 0, 1.8, gap=1.1, wait=1.5, rt=1.0)
        self.wait(1)
        self.clear(g1)
        ex = VGroup(
            MathTex(r"2 \cdot \tfrac{1}{2} = 1", font_size=48),
            MathTex(r"\tfrac{3}{4} \cdot \tfrac{4}{3} = 1", font_size=48),
            MathTex(r"0 \cdot ? = 1 \quad \text{(never!)}", font_size=48, color=RED),
        ).arrange(DOWN, buff=0.6).move_to([0, 0.5, 0])
        for m in ex:
            self.play(FadeIn(m, shift=UP * 0.2))
            self.wait(1.2)
        self.wait(0.8)
        self.clear(ex)
        n1 = Text("Notation: the inverse of x is written", font_size=30).move_to([0, 1.6, 0])
        n2 = MathTex(r"\tfrac{1}{5} = 5^{-1}", font_size=64).move_to([0, 0.3, 0])
        n3 = MathTex(r"x \cdot x^{-1} = 1", font_size=64, color=YELLOW).move_to([0, -1.3, 0])
        self.play(FadeIn(n1)); self.wait(0.8)
        self.play(Write(n2)); self.wait(1.5)
        self.play(Write(n3)); self.wait(2.5)
        self.clear(n1, n2, n3, t3)

        # =====================================================  4. 5^-1 MOD 19
        t4 = MathTex(r"\text{What is } 5^{-1} \pmod{19}\,?", font_size=48).to_edge(UP, buff=0.4)
        self.play(Write(t4))
        d1 = Text("There are no fractions in {0, 1, …, 18}.", font_size=28).move_to([0, 2.2, 0])
        d2 = MathTex(r"\text{So we look for } y \in \{0,\dots,18\} \text{ with } 5 \cdot y \equiv 1 \pmod{19}",
                     font_size=36).move_to([0, 1.3, 0])
        self.play(FadeIn(d1)); self.wait(1.5)
        self.play(Write(d2)); self.wait(2)

        x0, w, ytop = -4.9, 0.6, -0.2
        ys, vals = self.table(19, 5, x0, w, ytop)
        lab_y = Text("y", font_size=26).move_to([-6.1, ytop, 0])
        lab_v = MathTex(r"5y \bmod 19", font_size=30).move_to([-5.9, ytop - 0.9, 0])
        self.play(FadeIn(ys), FadeIn(lab_y), FadeIn(lab_v))

        def col_box(i, color=YELLOW):
            return Rectangle(width=w, height=1.5, color=color, stroke_width=3).move_to(
                [x0 + w * (i + 0.5), ytop - 0.45, 0])
        box = col_box(0)
        calc = MathTex(r"5 \cdot 0 = 0 \equiv 0", font_size=40).move_to([0, -2.6, 0])
        self.play(Create(box), FadeIn(vals[0]), FadeIn(calc))
        self.wait(0.6)
        for y in range(1, 5):
            new_calc = MathTex(rf"5 \cdot {y} = {5*y} \equiv {5*y % 19}", font_size=40).move_to([0, -2.6, 0])
            self.play(box.animate.move_to([x0 + w * (y + 0.5), ytop - 0.45, 0]),
                      FadeIn(vals[y]), Transform(calc, new_calc), run_time=0.7)
            self.wait(0.6)
        new_calc = MathTex(r"5 \cdot 4 = 20 = 1\cdot 19 + 1 \equiv 1", font_size=40, color=GREEN).move_to([0, -2.6, 0])
        self.play(Transform(calc, new_calc), box.animate.set_color(GREEN),
                  vals[4].animate.set_color(GREEN), ys[4].animate.set_color(GREEN))
        self.wait(2)
        self.play(LaggedStart(*[FadeIn(vals[y]) for y in range(5, 19)], lag_ratio=0.12), run_time=2.5)
        self.wait(1)
        e1 = Text("Every value 0 … 18 appears exactly once: there is exactly one inverse.",
                  font_size=26).move_to([0, -3.4, 0])
        self.play(FadeOut(calc), FadeIn(e1))
        self.wait(3)
        self.clear(e1, d1, d2, rt=0.6)
        res = MathTex(r"5^{-1} \equiv 4 \pmod{19}", font_size=64, color=GREEN).move_to([0, 2.0, 0])
        why = MathTex(r"\text{because } 5 \cdot 4 = 20 \equiv 1 \pmod{19}", font_size=40).move_to([0, 1.0, 0])
        self.play(Write(res)); self.wait(1)
        self.play(FadeIn(why))
        self.wait(3)
        self.clear(res, why, ys, vals, lab_y, lab_v, box, t4)

        # =====================================================  5. MOD 12: NOT ALWAYS POSSIBLE
        t5 = MathTex(r"\text{Now try } 3^{-1} \pmod{12}", font_size=48).to_edge(UP, buff=0.4)
        self.play(Write(t5))
        d3 = MathTex(r"\text{We look for } y \text{ with } 3 \cdot y \equiv 1 \pmod{12}", font_size=36).move_to([0, 2.2, 0])
        self.play(Write(d3))
        x0, w = -4.2, 0.85
        ys, vals = self.table(12, 3, x0, w, 0.9)
        lab_y = Text("y", font_size=26).move_to([-5.5, 0.9, 0])
        lab_v = MathTex(r"3y \bmod 12", font_size=30).move_to([-5.4, 0.0, 0])
        self.play(FadeIn(ys), FadeIn(lab_y), FadeIn(lab_v))
        self.play(LaggedStart(*[FadeIn(v) for v in vals], lag_ratio=0.15), run_time=2.5)
        self.wait(1)
        e2 = Text("The value 1 never appears: 3 has no inverse mod 12!", font_size=30, color=RED).move_to([0, -1.2, 0])
        self.play(FadeIn(e2)); self.wait(2.5)
        zeros = [vals[i] for i in range(12) if 3 * i % 12 == 0]
        self.play(*[z.animate.set_color(ORANGE) for z in zeros])
        e3 = MathTex(r"3 \cdot 4 = 12 \equiv 0 \pmod{12}", font_size=44, color=ORANGE).move_to([0, -2.2, 0])
        e4 = Text("although 3 ≠ 0 and 4 ≠ 0: these are zero divisors.", font_size=28).move_to([0, -3.0, 0])
        self.play(Write(e3)); self.wait(1.5)
        self.play(FadeIn(e4)); self.wait(3)
        self.clear(d3, ys, vals, lab_y, lab_v, e2, e3, e4, t5)

        t6 = MathTex(r"\text{Which numbers are invertible mod } 12\,?", font_size=44).to_edge(UP, buff=0.4)
        self.play(Write(t6))
        inv12 = {a: next((y for y in range(12) if a * y % 12 == 1), None) for a in range(12)}
        x0, w = -5.1, 0.85
        cells = VGroup()
        for a in range(12):
            ok = inv12[a] is not None
            cells.add(Text(str(a), font_size=34, color=GREEN if ok else RED).move_to([x0 + w * (a + 0.5), 1.5, 0]))
        self.play(FadeIn(cells), run_time=1.2)
        self.wait(1)
        zd = VGroup(
            MathTex(r"2 \cdot 6 \equiv 0", font_size=36),
            MathTex(r"3 \cdot 4 \equiv 0", font_size=36),
            MathTex(r"4 \cdot 9 \equiv 0", font_size=36),
            MathTex(r"8 \cdot 3 \equiv 0", font_size=36),
        ).arrange(RIGHT, buff=0.8).move_to([0, 0.3, 0])
        zdt = Text("red: zero divisors (or 0 itself) – no inverse", font_size=26, color=RED).move_to([0, -0.6, 0])
        self.play(FadeIn(zd), FadeIn(zdt))
        self.wait(2.5)
        ginv = VGroup(*[MathTex(rf"{a}^{{-1}} = {inv12[a]}", font_size=36, color=GREEN) for a in range(12) if inv12[a] is not None])
        ginv.arrange(RIGHT, buff=0.7).move_to([0, -1.7, 0])
        gt = Text("green: invertible (no common factor with 12)", font_size=26, color=GREEN).move_to([0, -2.6, 0])
        self.play(FadeIn(ginv), FadeIn(gt))
        self.wait(3.5)
        self.clear(cells, zd, zdt, ginv, gt, t6)

        # =====================================================  6. PRIME MODULUS
        t7 = MathTex(r"\text{Modulus } p \text{ prime, e.g. } p = 19", font_size=48).to_edge(UP, buff=0.4)
        self.play(Write(t7))
        grid = VGroup()
        for a in range(1, 19):
            inv = pow(a, -1, 19)
            col = YELLOW if a in (5, 4) else WHITE
            grid.add(MathTex(rf"{a}^{{-1}} = {inv}", font_size=34, color=col))
        grid.arrange_in_grid(rows=3, cols=6, buff=(0.5, 0.45)).move_to([0, 0.9, 0])
        self.play(LaggedStart(*[FadeIn(m) for m in grid], lag_ratio=0.12), run_time=3)
        self.wait(1.5)
        p1 = Text("Every non-zero number has an inverse – there are no zero divisors.", font_size=28).move_to([0, -1.7, 0])
        self.play(FadeIn(p1)); self.wait(2.5)
        p2 = MathTex(r"\{0,1,\dots,p-1\} \text{ with } + \text{ and } \cdot \;=\; \text{finite field } \mathbb{F}_p",
                     font_size=40, color=YELLOW).move_to([0, -2.6, 0])
        self.play(Write(p2)); self.wait(2.5)
        p3 = MathTex(r"\text{Division:}\quad a / b = a \cdot b^{-1}", font_size=40).move_to([0, -3.4, 0])
        self.play(FadeIn(p3)); self.wait(3)
        self.clear(grid, p1, p2, p3, t7)
