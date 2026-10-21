"""Scene 6: ECDH (key agreement) and ECDSA (digital signatures) on a toy curve.
Curve y^2 = x^3 + 2x + 2 over F_17, base point G = (5, 1) of prime order n = 19, so
every number on screen can be checked by hand. All values are computed in Python,
nothing is hard-coded, and the script asserts the maths (both ECDH sides agree,
a valid signature verifies, a tampered message fails)."""
from manim import *
import numpy as np

P_MOD, CA, CB, N = 17, 2, 2, 19
G = (5, 1)

C_G, C_A, C_B, C_S, C_E = ORANGE, BLUE, GREEN, YELLOW, RED


def ec_add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    if P[0] == Q[0] and (P[1] + Q[1]) % P_MOD == 0:
        return None
    if P == Q:
        m = (3 * P[0] ** 2 + CA) * pow(2 * P[1], -1, P_MOD) % P_MOD
    else:
        m = (Q[1] - P[1]) * pow(Q[0] - P[0], -1, P_MOD) % P_MOD
    x = (m * m - P[0] - Q[0]) % P_MOD
    return (x, (m * (P[0] - x) - P[1]) % P_MOD)


def ec_mul(k, P=G):
    R = None
    for _ in range(k % N):
        R = ec_add(R, P)
    return R


KG = {k: ec_mul(k) for k in range(1, N)}
ALL_POINTS = list(KG.values())
assert len(set(ALL_POINTS)) == 18 and ec_mul(N) is None
K_OF = {pt: k for k, pt in KG.items()}


def pt_tex(pt):
    return f"({pt[0]},{pt[1]})"


class CurvePlot(VGroup):
    """The 18 points of the curve over F_17 as dots on a grid."""

    def __init__(self, center, size):
        super().__init__()
        self.u = size / 17.5
        self.org = np.array(center, dtype=float) + np.array([-size / 2 + 0.75 * self.u, -size / 2 + 0.75 * self.u, 0])
        box = Rectangle(width=size, height=size, color=GREY_D, stroke_width=1.5).move_to(center)
        self.add(box)
        for v in (0, 4, 8, 12, 16):
            self.add(Line(self.pos((v, -0.75)), self.pos((v, 16.75)), color=GREY_E, stroke_width=1))
            self.add(Line(self.pos((-0.75, v)), self.pos((16.75, v)), color=GREY_E, stroke_width=1))
            self.add(Text(str(v), font_size=16, color=GREY_B).next_to(self.pos((v, -0.75)), DOWN, buff=0.06))
            self.add(Text(str(v), font_size=16, color=GREY_B).next_to(self.pos((-0.75, v)), LEFT, buff=0.06))
        self.dots = VGroup(*[Dot(self.pos(pt), radius=0.055, color=GREY_B) for pt in ALL_POINTS])
        self.add(self.dots)
        # the small number k next to every point means "this point is k*G"
        self.klabels = VGroup(*[
            Text(str(k), font_size=13, color=GREY_C).next_to(self.pos(pt), UR, buff=0.02)
            for k, pt in KG.items()
        ])

    def pos(self, pt):
        return self.org + np.array([pt[0] * self.u, pt[1] * self.u, 0])


class EcdhEcdsa(Scene):
    # ------------------------------------------------------------------ helpers
    def say(self, text, hold=None, color=WHITE):
        if len(text) > 95:
            words = text.split(" ")
            cut = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(text) / 2))
            text = " ".join(words[:cut]) + "\n" + " ".join(words[cut:])
        new = Text(text, font_size=26, color=color, line_spacing=0.9)
        if new.width > 12.8:
            new.scale_to_fit_width(12.8)
        new.move_to([0, -3.5, 0])
        if getattr(self, "cap", None) is not None:
            self.play(FadeOut(self.cap), FadeIn(new), run_time=0.4)
        else:
            self.play(FadeIn(new), run_time=0.4)
        self.cap = new
        self.wait(self.hold_scale * hold if hold is not None else 1.2 + 0.045 * len(text))

    def clear_caption(self):
        if getattr(self, "cap", None) is not None:
            self.play(FadeOut(self.cap), run_time=0.3)
            self.cap = None

    def mark(self, plot, pt, color, label, direction=UR, r=0.11):
        d = Dot(plot.pos(pt), radius=r, color=color).set_z_index(5)
        l = MathTex(label, color=color, font_size=30).set_stroke(BLACK, 5, background=True)
        l.next_to(d, direction, buff=0.06).set_z_index(6)
        return VGroup(d, l)

    def arrow(self, plot, a, b, color, angle=-TAU / 6):
        return CurvedArrow(plot.pos(a), plot.pos(b), angle=angle, color=color,
                           stroke_width=3, tip_length=0.15).set_z_index(4)

    def hop(self, plot, ks, color, t=0.45):
        """A marker hops through the points k1*G, k2*G, ... leaving arrows behind."""
        pts = [plot.pos(KG[k]) for k in ks]
        m = Dot(pts[0], radius=0.13, color=color).set_z_index(7)
        self.play(FadeIn(m, scale=1.6), run_time=0.3)
        arcs = []
        for a, b in zip(pts, pts[1:]):
            arc = CurvedArrow(a, b, angle=-TAU / 6, color=color, stroke_width=3, tip_length=0.15).set_z_index(4)
            arcs.append(arc)
            self.play(Create(arc), m.animate.move_to(b), run_time=t)
        return m, arcs

    def finish_hop(self, m, arcs, mk):
        self.play(FadeOut(VGroup(*arcs)), FadeIn(mk), run_time=0.6)
        self.remove(m)

    def tex(self, s, color=WHITE, size=30, maxw=None):
        m = MathTex(s, color=color, font_size=size)
        if maxw is not None and m.width > maxw:
            m.scale_to_fit_width(maxw)
        return m

    # ------------------------------------------------------------------ ECDH
    def ecdh(self):
        a_sec, b_sec = 3, 7
        A, B = KG[a_sec], KG[b_sec]
        S = ec_mul(a_sec * b_sec)
        assert ec_mul(a_sec, B) == ec_mul(b_sec, A) == S

        title = Text("Elliptic Curve Diffie–Hellman (ECDH)", font_size=44)
        sub = Text("Agreeing on a secret key over an open channel", font_size=28, color=GREY_B)
        sub.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(sub))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(sub))

        # --- the cast ---------------------------------------------------------
        AL, BL = -6.7, 3.2  # left edge of Alice's / Bob's panel
        alice = Text("Alice", font_size=38, color=C_A).move_to([AL + 1.9, 3.3, 0])
        bob = Text("Bob", font_size=38, color=C_B).move_to([BL + 1.9, 3.3, 0])
        eve = Text("Eve (eavesdropper)", font_size=24, color=C_E).move_to([0, 3.6, 0])
        channel = DashedLine([-3.3, 2.85, 0], [3.3, 2.85, 0], color=GREY_C, stroke_width=2)
        chan_lbl = Text("public channel", font_size=18, color=GREY_B).next_to(channel, UP, buff=0.05)
        self.play(FadeIn(alice), FadeIn(bob))
        self.play(Create(channel), FadeIn(chan_lbl), FadeIn(eve))
        self.say("Alice and Bob want a shared secret key, but Eve can read everything they send.", 3.5)

        slot_y = lambda i: 2.2 - 0.8 * i

        def line(tex, left, i, color):
            m = self.tex(tex, color, 32, maxw=3.9)
            m.move_to([left, slot_y(i), 0], aligned_edge=LEFT)
            return m

        # --- public parameters --------------------------------------------------
        plot = CurvePlot([0, -0.1, 0], 4.6)
        self.play(FadeIn(plot))
        self.say("Public parameters: the curve y² = x³ + 2x + 2 over the numbers mod 17 …", 3.5)
        mg = self.mark(plot, G, C_G, "G", UL)
        self.play(FadeIn(mg))
        self.say("… and a base point G = (5, 1). Everybody, including Eve, knows these.", 3.5)
        self.play(FadeIn(plot.klabels))
        self.say("Adding G to itself gives G, 2G, 3G, …: the small numbers show k for each point kG. "
                 "After 19G we are back at the start.", 6)

        # --- secrets and public keys -------------------------------------------
        a_line = line(rf"\text{{secret }} a = {a_sec}", AL, 0, C_A)
        b_line = line(rf"\text{{secret }} b = {b_sec}", BL, 0, C_B)
        self.play(FadeIn(a_line), FadeIn(b_line))
        self.say("Each picks a random secret number. It never leaves their side.", 3.5)

        self.say("Alice computes her public key A = 3·G: she adds G to itself three times.", 1.0)
        m, arcs = self.hop(plot, [1, 2, 3], C_A, 0.6)
        mA = self.mark(plot, A, C_A, "A", UL)
        self.finish_hop(m, arcs, mA)
        a_pub = line(rf"A = {a_sec}\cdot G = {pt_tex(A)}", AL, 1, C_A)
        self.play(FadeIn(a_pub))
        self.wait(1)

        self.say("Bob does the same with his secret: B = 7·G (real systems use fast double-and-add).", 1.0)
        m, arcs = self.hop(plot, [1, 2, 3, 4, 5, 6, 7], C_B, 0.35)
        mB = self.mark(plot, B, C_B, "B", UR)
        self.finish_hop(m, arcs, mB)
        b_pub = line(rf"B = {b_sec}\cdot G = {pt_tex(B)}", BL, 1, C_B)
        self.play(FadeIn(b_pub))
        self.wait(1)

        # --- exchange -----------------------------------------------------------
        self.say("They send A and B over the public channel. Only the public keys travel, never a or b.", 1.0)
        a_copy, b_copy = a_pub.copy(), b_pub.copy()
        path_a = VMobject().set_points_as_corners(
            [a_pub.get_center(), [AL + 1.8, 2.85, 0], [BL + 1.8, 2.85, 0], [BL + 1.8, slot_y(2), 0]])
        path_b = VMobject().set_points_as_corners(
            [b_pub.get_center(), [BL + 1.8, 2.45, 0], [AL + 1.8, 2.45, 0], [AL + 1.8, slot_y(2), 0]])
        self.play(MoveAlongPath(a_copy, path_a), run_time=2.2)
        self.play(MoveAlongPath(b_copy, path_b), run_time=2.2)
        eve_sees = MathTex(
            r"\text{Eve sees only: }G,\ A=" + pt_tex(A) + r",\ B=" + pt_tex(B), color=C_E, font_size=28
        ).move_to([0, 3.6, 0])
        self.play(Transform(eve, eve_sees))
        self.wait(2)
        a_got = line(rf"\text{{gets }} B = {pt_tex(B)}", AL, 2, C_B)
        b_got = line(rf"\text{{gets }} A = {pt_tex(A)}", BL, 2, C_A)
        self.play(ReplacementTransform(a_copy, a_got), ReplacementTransform(b_copy, b_got))

        # --- shared secret --------------------------------------------------------
        self.say("Alice multiplies Bob's public key by her secret: 3·B = B + B + B = 3·(7·G).", 1.0)
        a_ks = [7, (2 * 7) % N, (3 * 7) % N]
        m, arcs = self.hop(plot, a_ks, C_A, 0.7)
        mS = self.mark(plot, S, C_S, "S", RIGHT, r=0.13)
        self.finish_hop(m, arcs, mS)
        a_S = line(rf"S = {a_sec}\cdot B = {pt_tex(S)}", AL, 3, C_S)
        self.play(FadeIn(a_S))
        self.wait(1.5)

        self.say("Bob multiplies Alice's public key by his secret: 7·A = 7·(3·G).", 1.0)
        b_ks = [(3 * i) % N for i in range(1, 8)]
        b_ks[0] = 3
        m, arcs = self.hop(plot, b_ks, C_B, 0.3)
        self.play(FadeOut(VGroup(*arcs)), Flash(plot.pos(S), color=C_S, flash_radius=0.4), run_time=0.8)
        self.remove(m)
        b_S = line(rf"S = {b_sec}\cdot A = {pt_tex(S)}", BL, 3, C_S)
        self.play(FadeIn(b_S))
        self.say("The same point! 3·(7·G) = 21·G = 7·(3·G), and 21 mod 19 = 2, so S = 2G = (6, 3).", 6)
        key = self.tex(rf"\text{{shared key}} = x_S = {S[0]}", C_S, 30)
        key_b = key.copy()
        key.move_to([AL, slot_y(4), 0], aligned_edge=LEFT)
        key_b.move_to([BL, slot_y(4), 0], aligned_edge=LEFT)
        self.play(FadeIn(key), FadeIn(key_b))
        self.say("Both sides now hold the same key (in practice: a hash of the coordinates) "
                 "and can encrypt with it.", 5)

        # --- why Eve fails ----------------------------------------------------------
        self.say("Eve knows G, A and B. To get S she needs a or b, so she must solve A = a·G for a.", 5, C_E)
        m, arcs = self.hop(plot, [1, 2, 3], C_E, 0.5)
        self.say("On this toy curve she simply tries a = 1, 2, 3 … and finds a = 3 in no time.", 3.5, C_E)
        self.play(FadeOut(VGroup(*arcs)), FadeOut(m), run_time=0.5)

        big = VGroup(
            Text("secp256k1 (Bitcoin): about", font_size=28),
            MathTex(r"1.16\cdot 10^{77}", font_size=76, color=C_E),
            Text("possible secrets", font_size=28),
        ).arrange(DOWN, buff=0.25).move_to(plot.get_center())
        big_bg = BackgroundRectangle(big, color=BLACK, fill_opacity=0.85, buff=0.3)
        self.play(*[m_.animate.set_opacity(0.2) for m_ in (plot.dots, plot.klabels)],
                  *[FadeOut(m_) for m_ in (mg, mA, mB, mS)], FadeIn(big_bg), FadeIn(big))
        self.say("A real curve has about 10⁷⁷ points: trying them all would take longer than the age of the universe.", 6, C_E)
        self.say("Forward is easy (a → a·G), backward is practically impossible: the discrete logarithm problem.", 6)
        self.clear_caption()

        # --- recap --------------------------------------------------------------------
        self.play(*[FadeOut(m_) for m_ in self.mobjects])
        recap = VGroup(
            Text("ECDH in four steps", font_size=38, color=YELLOW),
            MathTex(r"1.\ \text{Public: curve and base point } G", font_size=34),
            MathTex(r"2.\ A = a\cdot G\ \text{(Alice)},\quad B = b\cdot G\ \text{(Bob)}\ \text{are exchanged}", font_size=34),
            MathTex(r"3.\ S = a\cdot B = b\cdot A = ab\cdot G\ \text{on both sides}", font_size=34),
            MathTex(r"4.\ \text{Eve sees } G, A, B\ \Rightarrow\ \text{she needs the discrete logarithm}", font_size=34),
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        recap[0].align_to(recap, LEFT)
        for r in recap:
            self.play(FadeIn(r), run_time=0.7)
            self.wait(1.8)
        self.wait(1)
        self.play(FadeOut(recap))
        self.cap = None

    # ------------------------------------------------------------------ ECDSA
    def ecdsa(self):
        d, k, h, h_bad = 5, 8, 6, 3
        Q = ec_mul(d)
        R = ec_mul(k)
        xR = R[0]
        assert xR < N  # so x_R mod n = x_R on this toy curve
        s = pow(k, -1, N) * (h + xR * d) % N
        assert xR != 0 and s != 0
        s_inv = pow(s, -1, N)
        c1, c2 = s_inv * h % N, s_inv * xR % N
        Pv = ec_add(ec_mul(c1), ec_mul(c2, Q))
        assert Pv == R and Pv[0] == xR
        c1b = s_inv * h_bad % N
        Pb = ec_add(ec_mul(c1b), ec_mul(c2, Q))
        assert Pb is not None and Pb[0] != xR

        title = Text("Elliptic Curve Digital Signature Algorithm (ECDSA)", font_size=38)
        sub = Text("Proving that a message really comes from Alice and was not altered",
                   font_size=26, color=GREY_B).next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(sub))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(sub))

        LX = -6.9
        plot = CurvePlot([4.1, -0.1, 0], 4.8)
        self.play(FadeIn(plot), FadeIn(plot.klabels))
        mg = self.mark(plot, G, C_G, "G", UL)
        self.play(FadeIn(mg))
        self.say("Same curve and same base point G as before. G has order n = 19, so signature numbers are computed mod 19.", 6)

        slot_y = lambda i: 2.3 - 0.85 * i

        def header(text, color):
            t = Text(text, font_size=34, color=color).move_to([LX, 3.3, 0], aligned_edge=LEFT)
            return t

        def line(tex, i, color=WHITE, size=36):
            m = self.tex(tex, color, size, maxw=7.9)
            m.move_to([LX, slot_y(i), 0], aligned_edge=LEFT)
            return m

        def swap(old, new_items):
            self.play(*[FadeOut(o) for o in old], run_time=0.5)
            self.play(*[FadeIn(n) for n in new_items], run_time=0.7)
            return new_items

        # --- 1. key pair --------------------------------------------------------------
        panel = [header("1  Key pair (Alice)", C_A)]
        self.play(FadeIn(panel[0]))
        l1 = line(rf"\text{{private key }} d = {d}\quad(\text{{secret}})", 0, C_A)
        self.play(FadeIn(l1))
        self.say("Alice chooses a private key d: a secret number that only she knows.", 3.5)
        arrQ = self.arrow(plot, G, Q, C_A)
        mQ = self.mark(plot, Q, C_A, "Q", UR)
        l2 = line(rf"\text{{public key }} Q = d\cdot G = {pt_tex(Q)}", 1, C_A)
        self.play(Create(arrQ), FadeIn(mQ), FadeIn(l2))
        self.say("Her public key is the point Q = d·G. Everyone may know Q; nobody can work out d from it.", 5)
        panel += [l1, l2]
        self.play(FadeOut(arrQ))

        # --- 2. message + hash ----------------------------------------------------------
        self.play(*[FadeOut(o) for o in panel[1:]], run_time=0.5)
        panel[0].become(header("2  The message", WHITE))
        msg = Text('m = "Pay Bob 5 EUR"', font_size=32).move_to([LX, slot_y(0), 0], aligned_edge=LEFT)
        hl = line(rf"h = H(m) \bmod n = {h}", 1, YELLOW)
        self.play(FadeIn(msg))
        self.say("Alice wants to sign this message.", 2.5)
        self.play(FadeIn(hl))
        self.say("A hash function turns the message into a number h. (Real ECDSA: SHA-256; here a toy value.) "
                 "Change one letter and h changes completely.", 7)
        self.play(FadeOut(msg), FadeOut(hl))

        # --- 3. sign -----------------------------------------------------------------------
        panel[0].become(header("3  Signing (Alice, uses d)", C_A))
        s1 = line(rf"\text{{pick a fresh random number }} k = {k}", 0, WHITE)
        s2 = line(rf"R = k\cdot G = {pt_tex(R)},\quad x_R = {xR}", 1, YELLOW)
        s3 = line(rf"s = k^{{-1}}\,(h + x_R\cdot d) \bmod n", 2, WHITE)
        s3b = line(rf"\;\;= {pow(k, -1, N)}\cdot({h} + {xR}\cdot {d}) \bmod {N} = {s}", 3, WHITE)
        s4 = line(rf"\text{{signature }} (x_R,\, s) = ({xR},\, {s})", 4.3, C_S, 36)
        box = SurroundingRectangle(s4, color=C_S, buff=0.15)
        self.play(FadeIn(s1))
        self.say("Step 1: a fresh random number k, used once and kept secret.", 3.5)
        arrR = self.arrow(plot, G, R, C_S)
        mR = self.mark(plot, R, C_S, "R", UL)
        self.play(FadeIn(s2), Create(arrR), FadeIn(mR))
        self.say("Step 2: R = k·G is a point on the curve. Its x-coordinate x_R becomes the first part of the signature. "
                 "(Real ECDSA reduces it mod n and calls it r.)", 7)
        self.play(FadeIn(s3))
        self.say("Step 3: s mixes the hash h, x_R and the private key d, hidden behind k⁻¹ (the inverse of k mod n).", 5)
        self.play(FadeIn(s3b))
        self.wait(2)
        self.play(FadeIn(s4), Create(box))
        self.say("Alice sends the message together with the signature (x_R, s). The private key d never leaves her.", 5)
        self.say("Never reuse k! With two signatures made with the same k, the private key can be computed "
                 "(this is how the PlayStation 3 was hacked).", 6, GREY_B)
        self.play(*[FadeOut(o) for o in (s1, s2, s3, s3b, s4, box, arrR)])

        # --- 4. verify: recover kG from public data -----------------------------------
        panel[0].become(header("4  Verifying (Bob): the idea", C_B))
        v0 = line(rf"\text{{Bob knows: }} m,\ (x_R,s)={pt_tex((xR, s))},\ Q,\ G", 0, GREY_B, 32)
        e1 = line(r"s = k^{-1}\,(h + x_R\,d)", 1.1)
        e2 = line(r"\Rightarrow\ k = s^{-1}\,(h + x_R\,d)", 2.1, YELLOW)
        e3 = self.tex(r"k\cdot G = s^{-1}h\cdot G + s^{-1}x_R\cdot (d\cdot G)", WHITE, 36, 7.9)
        e3.move_to([LX, slot_y(3.1), 0], aligned_edge=LEFT)
        e4 = self.tex(r"\phantom{k\cdot G} = s^{-1}h\cdot G + s^{-1}x_R\cdot Q", YELLOW, 38, 7.9)
        e4.move_to([LX, slot_y(4.0), 0], aligned_edge=LEFT)
        self.play(FadeIn(v0))
        self.say("Bob has the message, the signature and Alice's public key Q. He does NOT know d or k.", 5)
        self.play(FadeIn(e1))
        self.say("Alice built s from k, h, x_R and her private key d.", 4)
        self.play(FadeIn(e2))
        self.say("Solve that for k: k = s⁻¹(h + x_R·d). Bob cannot compute this directly, because he does not know d.", 6)
        self.play(FadeIn(e3))
        self.say("So multiply everything by G. Now the secret d only appears as the product d·G …", 5)
        self.play(FadeIn(e4))
        self.say("… and d·G is Alice's PUBLIC key Q! The right-hand side needs only public data: s, x_R, h, Q and G.", 6.5)
        self.say("Yet this point equals k·G, so the secret d is hidden inside it. "
                 "Only the owner of d could have produced an s that makes it work.", 7)

        # --- 5. verify: the check --------------------------------------------------------
        self.play(*[FadeOut(o) for o in (v0, e1, e2, e3, e4)])
        panel[0].become(header("5  Verifying (Bob): the check", C_B))
        k1 = line(rf"s^{{-1}} \bmod n = {s_inv}", 0)
        k2 = line(r"P = s^{-1}h\cdot G + s^{-1}x_R\cdot Q", 1)
        k3 = line(rf"\;\;= {s_inv}\cdot{h}\,G + {s_inv}\cdot{xR}\,Q = {c1}G + {c2}Q = {pt_tex(Pv)}", 2)
        k4 = line(rf"x_P = {Pv[0]} = x_R\ \Rightarrow\ \text{{signature valid}}", 3.4, GREEN, 36)
        tick = MathTex(r"\checkmark", color=GREEN, font_size=60).next_to(k4, RIGHT, buff=0.3)
        self.play(FadeIn(k1))
        self.say(f"Bob computes the inverse of s modulo n = {N}.", 3.5)
        self.play(FadeIn(k2))
        self.say("He computes the point P from public data only, and fills in the numbers.", 4.5)
        self.play(FadeIn(k3))
        ring = Circle(radius=0.25, color=C_S, stroke_width=5).move_to(plot.pos(Pv)).set_z_index(8)
        self.play(Create(ring), Flash(plot.pos(Pv), color=C_S, flash_radius=0.5))
        self.say("P lands exactly on R, the point Alice used when signing!", 4.5)
        self.play(FadeIn(k4), FadeIn(tick))
        self.say("x_P equals x_R: the signature is valid. Only the owner of d can make this happen, "
                 "and h ties the signature to this exact message.", 7)
        self.play(*[FadeOut(o) for o in (k1, k2, k3, k4, tick, ring)])

        # --- 6. tamper ---------------------------------------------------------------------
        panel[0].become(header("6  What if the message is changed?", C_E))
        t0 = Text('m′ = "Pay Bob 500 EUR"', font_size=32, color=C_E).move_to([LX, slot_y(0), 0], aligned_edge=LEFT)
        t1 = line(rf"h' = H(m') = {h_bad}\ \ (\text{{was }}{h})", 1)
        t3 = line(rf"P' = s^{{-1}}h'\cdot G + s^{{-1}}x_R\cdot Q = {c1b}G + {c2}Q = {pt_tex(Pb)}", 2.2)
        t4 = line(rf"x_{{P'}} = {Pb[0]} \neq x_R = {xR}\ \Rightarrow\ \text{{signature invalid}}", 3.6, C_E, 34)
        cross = MathTex(r"\times", color=C_E, font_size=70).next_to(t4, RIGHT, buff=0.3)
        self.play(FadeIn(t0))
        self.say("Now an attacker changes the amount but keeps the old signature (x_R, s).", 4.5)
        self.play(FadeIn(t1))
        self.say("The hash of the new message is a completely different number.", 3.5)
        mPb = self.mark(plot, Pb, C_E, "P'", UR)
        self.play(FadeIn(t3), FadeIn(mPb))
        self.say("Bob's computation now gives a different point P′, not R.", 5)
        self.play(FadeIn(t4), FadeIn(cross))
        self.say("x ≠ x_R: the signature is rejected. A forger would need d (or k) to make a matching s.", 6, C_E)
        self.clear_caption()

        # --- recap -------------------------------------------------------------------------
        self.play(*[FadeOut(m_) for m_ in self.mobjects])
        recap = VGroup(
            Text("ECDSA in short", font_size=38, color=YELLOW),
            MathTex(r"\text{Keys: private } d,\quad \text{public } Q = d\cdot G", font_size=34),
            MathTex(r"\text{Sign: } R = k\cdot G,\ s = k^{-1}(h + x_R\,d),\ \text{send } (x_R, s)", font_size=34),
            MathTex(r"\text{Verify: } P = s^{-1}h\cdot G + s^{-1}x_R\cdot Q = k\cdot G\ \Rightarrow\ x_P = x_R", font_size=34),
            Text("Authentic (only d can sign) and unaltered (h changes)", font_size=28, color=GREEN),
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        for rr in recap:
            self.play(FadeIn(rr), run_time=0.7)
            self.wait(1.5)
        self.wait(1)
        final = VGroup(
            Text("Both rest on the same one-way street:", font_size=32),
            MathTex(r"d \longmapsto d\cdot G\ \text{ is easy,}\qquad d\cdot G \longmapsto d\ \text{ is practically impossible}", font_size=36, color=YELLOW),
        ).arrange(DOWN, buff=0.4)
        self.play(FadeOut(recap))
        self.play(FadeIn(final))
        self.wait(2.5)
        self.play(FadeOut(final))

    def construct(self):
        self.cap = None
        self.hold_scale = 0.6  # ECDH is shorter on text, ECDSA gets more time
        self.ecdh()
        self.cap = None
        self.hold_scale = 1.0
        self.ecdsa()
