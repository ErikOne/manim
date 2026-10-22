"""Addendum: reusing the ECDSA nonce k reveals the private key d.
Same toy curve as ecdh_ecdsa.py (y^2 = x^3 + 2x + 2 over F_17, G = (5, 1), n = 19).
Alice signs two different messages with the SAME k. Same k gives the same R = k*G,
so both signatures share x_R, and three lines of algebra expose k and then d.
All numbers are computed in Python and asserted."""
from manim import *

from ecdh_ecdsa import (EcdhEcdsa, CurvePlot, ec_mul, ec_add, pt_tex, G, N,
                        C_A, C_E, C_S, C_G)


class EcdsaNonceReuse(EcdhEcdsa):
    def construct(self):
        self.cap = None
        self.hold_scale = 1.0

        d, k, h1, h2 = 5, 8, 6, 3
        Q = ec_mul(d)
        R = ec_mul(k)
        r = R[0]
        assert r < N and r != 0
        kinv = pow(k, -1, N)
        s1 = kinv * (h1 + r * d) % N
        s2 = kinv * (h2 + r * d) % N
        assert s1 != s2

        # what the attacker does, using only public data
        k_rec = (h1 - h2) * pow(s1 - s2, -1, N) % N
        d_rec = (s1 * k_rec - h1) * pow(r, -1, N) % N
        assert k_rec == k and d_rec == d and ec_mul(d_rec) == Q
        inv_ds = pow(s1 - s2, -1, N)
        inv_r = pow(r, -1, N)

        LX = -6.9
        slot_y = lambda i: 2.3 - 0.85 * i

        def header(text, color):
            return Text(text, font_size=34, color=color).move_to([LX, 3.3, 0], aligned_edge=LEFT)

        def line(tex, i, color=WHITE, size=36):
            m = self.tex(tex, color, size, maxw=7.9)
            m.move_to([LX, slot_y(i), 0], aligned_edge=LEFT)
            return m

        # --- title -------------------------------------------------------------------
        title = Text("Addendum: never reuse k", font_size=42, color=C_E)
        sub = Text("Two signatures with the same k reveal the private key",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1.2)
        self.play(FadeIn(sub))
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(sub))

        plot = CurvePlot([4.1, -0.1, 0], 4.8)
        self.play(FadeIn(plot), FadeIn(plot.klabels))
        mg = self.mark(plot, G, C_G, "G", UL)
        self.play(FadeIn(mg))

        # --- 1. same k -> same R ---------------------------------------------------------
        head = header("1  Same k, same R", C_A)
        a0 = line(rf"\text{{Alice signs }} m_1,\ m_2 \text{{ with the same }} k = {k}", 0, WHITE, 32)
        a1 = line(rf"h_1 = {h1},\qquad h_2 = {h2}", 1, GREY_B)
        a2 = line(rf"R = k\cdot G = {pt_tex(R)}\ \text{{for both messages}}", 2.1, C_S)
        a3 = line(rf"\Rightarrow\ x_R = r = {r}\ \text{{in both signatures}}", 3.1, C_S)
        self.play(FadeIn(head))
        self.play(FadeIn(a0))
        self.say("Suppose Alice signs two different messages, but is careless and uses the same k both times.", 5)
        self.play(FadeIn(a1))
        arrR = self.arrow(plot, G, R, C_S)
        mR = self.mark(plot, R, C_S, "R", UL)
        self.play(FadeIn(a2), Create(arrR), FadeIn(mR))
        self.say("R = k·G only depends on k. Same k means the same point R, so the same x-coordinate r in both signatures.", 7)
        self.play(FadeIn(a3))
        self.wait(1)

        # --- 2. what everybody sees ------------------------------------------------------
        self.play(*[FadeOut(o) for o in (a0, a1, a2, a3, arrR)], run_time=0.5)
        head.become(header("2  What an attacker sees", C_E))
        b1 = line(rf"(r,\,s_1) = ({r},\,{s1}),\quad h_1 = {h1}", 0.2, WHITE, 36)
        b2 = line(rf"(r,\,s_2) = ({r},\,{s2}),\quad h_2 = {h2}", 1.2, WHITE, 36)
        b3 = line(r"\text{unknown: } k \text{ and } d", 2.4, C_E, 36)
        self.play(FadeIn(b1), FadeIn(b2))
        self.say("Signatures and messages are public. The same r in both signatures is the giveaway.", 5)
        self.play(FadeIn(b3))
        self.say("Unknown to the attacker: k and the private key d. Two equations, two unknowns.", 5)
        self.play(*[FadeOut(o) for o in (b1, b2, b3)], run_time=0.5)

        # --- 3. the algebra -----------------------------------------------------------------
        head.become(header("3  The algebra: all mod n", C_E))
        c1 = line(r"s_1 = k^{-1}\,(h_1 + r\,d)", 0)
        c2 = line(r"s_2 = k^{-1}\,(h_2 + r\,d)", 1)
        c3 = line(r"s_1 - s_2 = k^{-1}\,(h_1 - h_2)", 2.1, YELLOW)
        c4 = line(r"k = \dfrac{h_1 - h_2}{s_1 - s_2}", 3.4, YELLOW)
        c5 = line(r"d = \dfrac{s_1\,k - h_1}{r}", 4.9, GREEN, 40)
        self.play(FadeIn(c1), FadeIn(c2))
        self.say("Both signatures follow the same recipe: s = k⁻¹(h + r·d).", 4)
        self.play(FadeIn(c3))
        self.say("Subtract them. The term r·d is identical in both, so it cancels and the private key disappears from the equation.", 7)
        self.play(FadeIn(c4))
        self.say("Solve for k: only public numbers appear: two hashes and two signature values. k is now known.", 6)
        self.play(*[FadeOut(o) for o in (c1, c2, c3)], c4.animate.move_to([LX, slot_y(0), 0], aligned_edge=LEFT), run_time=0.8)
        e1 = line(r"s_1 = k^{-1}\,(h_1 + r\,d)\ \Rightarrow\ d = r^{-1}\,(s_1\,k - h_1)", 1.3, WHITE, 34)
        self.play(FadeIn(e1))
        self.say("Now that k is known, go back to one signature and solve for d.", 5)
        self.play(FadeOut(e1), run_time=0.4)
        c5.move_to([LX, slot_y(1.6), 0], aligned_edge=LEFT)
        self.play(FadeIn(c5))
        self.say("Everything on the right-hand side is known. The private key d falls out.", 5)

        # --- 4. with numbers --------------------------------------------------------------------
        self.play(FadeOut(c4), FadeOut(c5), run_time=0.5)
        head.become(header("4  With our numbers (mod 19)", GREEN))
        n1 = line(rf"k = \dfrac{{{h1} - {h2}}}{{{s1} - {s2}}} = {(h1 - h2) % N}\cdot {(s1 - s2) % N}^{{-1}}"
                  rf" = {(h1 - h2) % N}\cdot {inv_ds} = {k_rec}", 0.2, YELLOW, 34)
        n2 = line(rf"d = \dfrac{{{s1}\cdot {k_rec} - {h1}}}{{{r}}} = {(s1 * k_rec - h1) % N}\cdot {r}^{{-1}}"
                  rf" = {(s1 * k_rec - h1) % N}\cdot {inv_r} = {d_rec}", 1.5, GREEN, 34)
        n3 = line(rf"\text{{check: }}\ d\cdot G = {d_rec}\cdot G = {pt_tex(ec_mul(d_rec))} = Q\ \checkmark", 2.9, WHITE, 34)
        self.play(FadeIn(n1))
        self.say(f"Fill in the numbers (note {s1} − {s2} = −2 ≡ {(s1 - s2) % N} mod {N}): k = {k_rec}, exactly the secret nonce Alice used.", 6)
        self.play(FadeIn(n2))
        self.say(f"And d = {d_rec}: Alice's private key, computed from public data in a few lines.", 5)
        mQ = self.mark(plot, Q, C_A, "Q", UR)
        self.play(FadeIn(n3), FadeIn(mQ), Flash(plot.pos(Q), color=C_A, flash_radius=0.5))
        self.say("As a check: d·G equals Alice's public key Q. The attacker can now sign anything as Alice.", 6, C_E)
        self.clear_caption()

        # --- recap ------------------------------------------------------------------------------
        self.play(*[FadeOut(m_) for m_ in self.mobjects])
        recap = VGroup(
            Text("Same k  ⇒  same R  ⇒  same r", font_size=34),
            MathTex(r"s_1 - s_2 = k^{-1}(h_1 - h_2)\ \Rightarrow\ k = \dfrac{h_1 - h_2}{s_1 - s_2}", font_size=38),
            MathTex(r"d = \dfrac{s_1\,k - h_1}{r}", font_size=40, color=GREEN),
            Text("k must be fresh and unpredictable for every signature", font_size=30, color=C_E),
            Text("Fix: RFC 6979, k = HMAC(d, h): deterministic, different per message",
                 font_size=26, color=GREEN),
        ).arrange(DOWN, buff=0.5)
        for rr in recap:
            self.play(FadeIn(rr), run_time=0.7)
            self.wait(1.5)
        self.wait(2)
        self.play(FadeOut(recap))
