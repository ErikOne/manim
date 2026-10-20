"""Scene 1: Modular arithmetic explained with a clock/circle.

Opens with a point spinning around a 12-tick clock face while a live counter
shows the "real" value next to its wrapped remainder, counting from 0 to 100
at a steady pace. The clock then transforms into a 31-tick face right in
front of the viewer (a nice showcase of Manim's transform feature) -- the
remainder display morphs from "100 mod 12" to "100 mod 31" -- and counting
continues from 100 up to 1000, now mod 31 and noticeably slower than before
so the wraparound stays easy to follow. We then explain that this wraparound
lets us define sums: first a full worked cycle (1000 mod 12) that visits
every remainder exactly once, then the clock transforms back to 31 ticks to
show the same idea generalizes to any modulus.
"""
from manim import *
import numpy as np


class ModularArithmetic(Scene):
    def construct(self):
        title = Text("Modular Arithmetic", font_size=44)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        intro = Text(
            "We only care about the remainder after dividing by n.",
            font_size=26,
        )
        self.play(FadeIn(intro))
        self.wait(1.5)
        self.play(FadeOut(intro))

        # Shift the whole clock face up a bit so the bottom-of-screen text
        # stack (equation + transition line) never collides with it.
        center = UP * 0.3

        def build_clock(n, radius, font_size):
            """Build a circle with n evenly spaced tick marks and labels."""
            circ = Circle(radius=radius, color=BLUE).move_to(center)
            ticks_grp = VGroup()
            labels_grp = VGroup()
            pos_list = []
            for k in range(n):
                angle = PI / 2 - k * (2 * PI / n)  # start at top, go clockwise
                offset = radius * np.array([np.cos(angle), np.sin(angle), 0])
                pos = center + offset
                pos_list.append(pos)
                ticks_grp.add(Dot(pos, color=WHITE, radius=0.045))
                labels_grp.add(Text(str(k), font_size=font_size).move_to(center + offset * 1.18))
            return circ, ticks_grp, labels_grp, pos_list

        # Current clock state (mutable so updaters always read the live values).
        state = {"n": 12, "radius": 2.0}
        circle, ticks, labels, positions = build_clock(state["n"], state["radius"], 28)
        self.play(Create(circle))
        self.play(LaggedStartMap(FadeIn, labels, lag_ratio=0.04),
                   LaggedStartMap(FadeIn, ticks, lag_ratio=0.04), run_time=1.2)
        self.wait(0.2)

        # --- A point spins around the clock face while a live counter shows
        # the "real" value next to its wrapped remainder. Every time the real
        # value passes a multiple of n, the remainder simply resets to 0. ---
        counter = ValueTracker(0)

        def angle_for(v):
            return PI / 2 - (v % state["n"]) * (2 * PI / state["n"])

        def pos_for(v):
            a = angle_for(v)
            return center + state["radius"] * np.array([np.cos(a), np.sin(a), 0])

        radius_line = Line(center, positions[0], color=YELLOW)
        moving_dot = Dot(positions[0], color=YELLOW, radius=0.12)
        radius_line.add_updater(lambda ln: ln.put_start_and_end_on(center, pos_for(counter.get_value())))
        moving_dot.add_updater(lambda d: d.move_to(pos_for(counter.get_value())))

        def eq_text():
            real_val = int(counter.get_value())
            mod_val = real_val % state["n"]
            return Text(
                f"{real_val}   \u2261   {mod_val}   (mod {state['n']})", font_size=34
            ).to_edge(DOWN)

        eq_display = always_redraw(eq_text)

        self.play(FadeIn(radius_line), FadeIn(moving_dot))
        self.add(eq_display)
        self.wait(0.3)

        # Count 0 -> 100 at a steady pace, mod 12.
        self.play(counter.animate.set_value(100), run_time=10, rate_func=linear)

        # --- Transform the clock face live from 12 ticks to 31 ticks, and
        # morph "100 mod 12" into "100 mod 31" right in front of the viewer. ---
        moving_dot.clear_updaters()
        radius_line.clear_updaters()
        eq_display.clear_updaters()

        val_at_100 = int(counter.get_value())
        eq_before = Text(
            f"{val_at_100}   \u2261   {val_at_100 % state['n']}   (mod {state['n']})",
            font_size=34,
        ).to_edge(DOWN)
        self.remove(eq_display)
        self.add(eq_before)

        state["n"], state["radius"] = 31, 2.0
        new_circle, new_ticks, new_labels, new_positions = build_clock(state["n"], state["radius"], 15)
        positions = new_positions
        eq_after = Text(
            f"{val_at_100}   \u2261   {val_at_100 % state['n']}   (mod {state['n']})",
            font_size=34,
        ).to_edge(DOWN)

        self.play(
            ReplacementTransform(circle, new_circle),
            FadeOut(labels), FadeOut(ticks),
            FadeIn(new_labels), FadeIn(new_ticks),
            ReplacementTransform(eq_before, eq_after),
            moving_dot.animate.move_to(pos_for(val_at_100)),
            radius_line.animate.put_start_and_end_on(center, pos_for(val_at_100)),
            run_time=4,
        )
        circle, labels, ticks = new_circle, new_labels, new_ticks
        self.wait(1)

        # Resume the live counter/dot/equation updaters, now under mod 31,
        # and continue counting 100 -> 1000 -- noticeably slower this time
        # so the wraparound stays easy to follow.
        eq_display = always_redraw(eq_text)
        self.remove(eq_after)
        self.add(eq_display)
        moving_dot.add_updater(lambda d: d.move_to(pos_for(counter.get_value())))
        radius_line.add_updater(lambda ln: ln.put_start_and_end_on(center, pos_for(counter.get_value())))

        self.play(counter.animate.set_value(1000), run_time=7, rate_func=linear)

        # Freeze on the final value.
        moving_dot.clear_updaters()
        radius_line.clear_updaters()
        eq_display.clear_updaters()
        self.wait(1.2)

        final_val = int(counter.get_value())  # 1000

        # --- Transition: this wraparound lets us define sums. ---
        transition = Text(
            "This wraparound also lets us define sums, using only remainders:",
            font_size=26,
        ).next_to(eq_display, UP, buff=0.4)
        self.play(FadeIn(transition))
        self.wait(1.5)
        self.play(FadeOut(transition))

        # --- Transform the clock back down to 12 ticks, and morph
        # "1000 mod 31" into "1000 mod 12" for our first worked sum. ---
        eq_31 = Text(
            f"{final_val}   \u2261   {final_val % state['n']}   (mod {state['n']})",
            font_size=34,
        ).to_edge(DOWN)
        self.remove(eq_display)
        self.add(eq_31)

        state["n"], state["radius"] = 12, 2.0
        circle12, ticks12, labels12, positions12 = build_clock(state["n"], state["radius"], 28)
        base_mod12 = final_val % state["n"]
        eq_12 = Text(
            f"{final_val} mod {state['n']}   \u2261   {base_mod12}   (mod {state['n']})",
            font_size=34,
        ).to_edge(DOWN)

        self.play(
            ReplacementTransform(circle, circle12),
            FadeOut(labels), FadeOut(ticks),
            FadeIn(labels12), FadeIn(ticks12),
            ReplacementTransform(eq_31, eq_12),
            moving_dot.animate.move_to(positions12[base_mod12]),
            radius_line.animate.put_start_and_end_on(center, positions12[base_mod12]),
            run_time=1.8,
        )
        circle, labels, ticks, positions = circle12, labels12, ticks12, positions12
        self.wait(0.3)

        # --- Sums demo (mod 12): starting from 1000 mod 12, add
        # 1, 2, 3, ... 11, then 0 -- cycling through every remainder once. ---
        addends_12 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0]

        sums_eq = eq_12
        for k in addends_12:
            result = (final_val + k) % state["n"]
            new_eq = Text(
                f"{final_val} mod {state['n']} + {k}   \u2261   {result}   (mod {state['n']})",
                font_size=32,
            ).to_edge(DOWN)
            target = positions[result]
            self.play(
                ReplacementTransform(sums_eq, new_eq),
                moving_dot.animate.move_to(target),
                radius_line.animate.put_start_and_end_on(center, target),
                run_time=0.55,
            )
            sums_eq = new_eq
            self.wait(0.12)

        self.wait(0.6)

        # --- The same idea generalizes to any modulus -- show it again
        # with 31, transforming the clock face back up live. ---
        note31 = Text(
            "The same idea works for any modulus \u2014 for example, mod 31:",
            font_size=26,
        ).next_to(sums_eq, UP, buff=0.4)
        self.play(FadeIn(note31))
        self.wait(1.3)

        state["n"], state["radius"] = 31, 2.0
        circle31, ticks31, labels31, positions31 = build_clock(state["n"], state["radius"], 15)
        base_mod31 = final_val % state["n"]
        eq_31b = Text(
            f"{final_val} mod {state['n']}   \u2261   {base_mod31}   (mod {state['n']})",
            font_size=32,
        ).to_edge(DOWN)

        self.play(
            ReplacementTransform(circle, circle31),
            FadeOut(labels), FadeOut(ticks),
            FadeIn(labels31), FadeIn(ticks31),
            ReplacementTransform(sums_eq, eq_31b),
            moving_dot.animate.move_to(positions31[base_mod31]),
            radius_line.animate.put_start_and_end_on(center, positions31[base_mod31]),
            FadeOut(note31),
            run_time=1.8,
        )
        circle, labels, ticks, positions = circle31, labels31, ticks31, positions31
        self.wait(0.3)

        # Representative (not exhaustive, since 31 residues is a lot) set of
        # sums, still clearly showing the same wraparound behaviour.
        addends_31 = [1, 5, 10, 15, 20, 25, 30, 0]

        sums_eq = eq_31b
        for k in addends_31:
            result = (final_val + k) % state["n"]
            new_eq = Text(
                f"{final_val} mod {state['n']} + {k}   \u2261   {result}   (mod {state['n']})",
                font_size=32,
            ).to_edge(DOWN)
            target = positions[result]
            self.play(
                ReplacementTransform(sums_eq, new_eq),
                moving_dot.animate.move_to(target),
                radius_line.animate.put_start_and_end_on(center, target),
                run_time=0.55,
            )
            sums_eq = new_eq
            self.wait(0.12)

        self.wait(0.5)
        self.play(FadeOut(sums_eq))

        # General rule.
        general = MathTex("a", "+", "b", r"\equiv", "r", r"\pmod{n}", font_size=44)
        general.to_edge(DOWN).shift(UP * 0.6)
        note = Text(
            "r is simply what remains after going around the circle.",
            font_size=24,
        ).next_to(general, DOWN, buff=0.3)
        self.play(Write(general))
        self.play(FadeIn(note))
        self.wait(2.5)
