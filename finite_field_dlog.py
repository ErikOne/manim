"""Scene 5+6 (merged): Elliptic curve over a finite field F_p, and the discrete logarithm problem.
The first part is identical to finite_field.py; after 8G the walk continues to Q = 29G (easy
direction), then we try to recover k from G and Q (hard direction), and end with an easy-vs-hard summary.

Original text of the finite-field part:
Elliptic curve over a finite field F_p.
Layout: the curve/graph lives on the left half of the screen, all explanatory
text lives in a panel on the right half, so the two never overlap. Builds the
curve point by point (plug in x, solve y^2 (mod p), fly the resulting point
onto the axes), shows how the point count explodes as the modulus grows
(17 -> 31 -> 97 -> 997 -> 999983), and walks step-by-step through point
addition (secant/tangent, third point, reflect) building up to k*G -- slow
and detailed up to 4G, then faster up to 8G."""
from manim import *
from manim.utils.family import extract_mobject_family_members


def curve_points_mod(p, a, b):
    pts = []
    for x in range(p):
        rhs = (x**3 + a * x + b) % p
        for y in range(p):
            if (y * y) % p == rhs:
                pts.append((x, y))
    return pts


def tonelli_shanks(n, p):
    """Modular square root of n mod prime p (or None if none exists).
    Needed because not every big prime used below is 3 mod 4, where the
    simple n**((p+1)/4) shortcut would otherwise apply."""
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = pow(t2, 2, p)
            i += 1
        bb = pow(c, 2 ** (m - i - 1), p)
        m, c, t, r = i, pow(bb, 2, p), (t * bb * bb) % p, (r * bb) % p
    return r


def count_points_fast(p, a, b):
    """Exact point count via the Legendre symbol -- O(p) instead of O(p^2),
    the only way to count points on curves too big to enumerate directly."""
    cnt = 0
    for x in range(p):
        rhs = (x**3 + a * x + b) % p
        if rhs == 0:
            cnt += 1
        elif pow(rhs, (p - 1) // 2, p) == 1:
            cnt += 2
    return cnt


def inv_mod(x, p):
    return pow(x, p - 2, p)


def ec_step(P, Q, p, a):
    """Secant (P != Q) or tangent (P == Q) through P, Q.
    Returns slope m, the raw third intersection point, and the final sum."""
    x1, y1 = P
    x2, y2 = Q
    if P == Q:
        m = (3 * x1 * x1 + a) * inv_mod(2 * y1, p) % p
    else:
        m = (y2 - y1) * inv_mod((x2 - x1) % p, p) % p
    x3 = (m * m - x1 - x2) % p
    y3_raw = (m * (x3 - x1) + y1) % p
    y3_sum = (-y3_raw) % p
    return m, x3, y3_raw, y3_sum


# Left column: x <~ -0.8  |  Right column (text panel): x >~ 1.0
AXES_CENTER = LEFT * 3.5 + DOWN * 0.5
PANEL_X = 1.3
PANEL_TOP_Y = 2.5


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
    return (x3, (m * (x1 - x3) - y1) % p)


def scalar_mul(k, P, p, a):
    result = None
    for _ in range(k):
        result = ec_add(result, P, p, a)
    return result


def wrapped_line(axes, P, m, p, color=GREEN):
    """The 'line' through P with slope m (mod p) is the set of grid points with y = m(x-x1)+y1 (mod p):
    drawn on the grid it is a family of parallel segments (the line wraps around)."""
    ms = m if m <= p // 2 else m - p  # smallest-magnitude representative of the slope
    x1, y1 = P
    c = y1 - ms * x1
    top = p - 1
    segs = VGroup()
    for j in range(-(abs(ms) + 2), abs(ms) + 3):
        cj = c + j * p
        if ms == 0:
            if 0 <= cj <= top:
                segs.add(Line(axes.c2p(0, cj), axes.c2p(top, cj), color=color, stroke_width=1.2, stroke_opacity=0.5))
            continue
        xa, xb = sorted(((0 - cj) / ms, (top - cj) / ms))
        lo, hi = max(0, xa), min(top, xb)
        if hi - lo > 1e-9:
            segs.add(Line(axes.c2p(lo, ms * lo + cj), axes.c2p(hi, ms * hi + cj), color=color, stroke_width=1.2, stroke_opacity=0.5))
    return segs


class FiniteFieldDLog(Scene):
    def get_moving_and_static_mobjects(self, animations):
        # Workaround: the Cairo renderer's static-background cache can bake an
        # already-removed Text mobject into later frames in scenes with many
        # short-lived text swaps. Treating everything as "moving" disables
        # that (harmless at this scene's size) and guarantees every frame is
        # drawn fresh.
        all_mobjects = list(self.mobjects) + list(self.foreground_mobjects)
        all_families = extract_mobject_family_members(
            all_mobjects, use_z_index=self.renderer.camera.use_z_index
        )
        return all_families, []

    def construct(self):
        title = Text("Elliptic Curves over a Finite Field", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))

        p, a, b = 17, -1, 1
        # Left: the coordinate grid. Right: the curve equation written with a
        # modulo-equivalence sign (not "="), the field it's defined over, and
        # a running log of x -> y derivations.
        axes = Axes(
            x_range=[0, p, 1], y_range=[0, p, 1],
            x_length=4.8, y_length=4.8,
            axis_config={"include_tip": False, "include_numbers": False},
        ).move_to(AXES_CENTER)
        self.play(Create(axes))

        grid_dots = VGroup(*[
            Dot(axes.c2p(x, y), radius=0.025, color=GRAY, fill_opacity=0.4)
            for x in range(p) for y in range(p)
        ])
        self.play(FadeIn(grid_dots), run_time=1)

        eq = MathTex(f"y^2 \\equiv x^3 - x + 1 \\pmod{{{p}}}", font_size=30)
        eq.move_to([PANEL_X, PANEL_TOP_Y, 0], aligned_edge=UL)
        self.play(Write(eq))

        field_set = MathTex(
            r"\mathbb{Z}/%d\mathbb{Z} = \{0,1,2,\ldots,%d\}" % (p, p - 1), font_size=24,
        )
        field_set.next_to(eq, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeIn(field_set))
        self.wait(0.5)

        plug_header = Text("Plug in x, solve for y (mod 17):", font_size=20, color=GRAY_B)
        plug_header.next_to(field_set, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeIn(plug_header))

        curve_dots = VGroup()
        coord_labels = VGroup()

        def rhs_of(x):
            return (x ** 3 + a * x + b) % p

        # --- Slow, fully-explained derivations for x = 0, 1, 2, 3 ---
        # For each x we don't just state the answer: we visibly scan
        # y = 0, 1, 2, ... (mod p), turning the line green the moment it
        # satisfies y^2 (and sending that point flying to the axes right
        # then and there, instead of leaving it stranded next to the text).
        # x=2 deliberately has no solution: not every x gives a point.
        for x in range(0, 4):
            rhs = rhs_of(x)

            calc1 = Text(f"x = {x}:  x\u00b3 - x + 1 \u2261 {rhs} (mod {p})", font_size=19)
            calc1.next_to(plug_header, DOWN, buff=0.3, aligned_edge=LEFT)
            self.play(FadeIn(calc1))
            self.wait(0.4)

            scan_label = Text(f"Try y = 0, 1, 2, \u2026 in y\u00b2 (mod {p}):", font_size=18, color=GRAY_B)
            scan_label.next_to(calc1, DOWN, buff=0.3, aligned_edge=LEFT)
            self.play(FadeIn(scan_label))

            # Stable template row: the words ("y =", "y^2 =", etc.) are
            # created once and never recreated or moved -- only the number
            # slots (y, raw square, reduced value, check/cross mark) are
            # swapped in place at fixed positions as y counts up. This way
            # nothing reflows or "jumps"; only the highlighted digits change,
            # right next to the already-known target rhs on the same line.
            lbl_y_eq = Text("y =", font_size=18)
            lbl_sq_eq = Text(":  y\u00b2 =", font_size=18)
            lbl_equiv = Text("\u2261", font_size=18)
            lbl_target = Text(f"(mod {p})   [target: {rhs}]", font_size=18, color=GRAY_B)

            # Placeholders sized to the widest possible value, used only to
            # measure and reserve fixed slot positions -- never displayed.
            ph_y = Text(str(p - 1), font_size=18)
            ph_raw = Text(str((p - 1) ** 2), font_size=18)
            ph_mod = Text(str(p - 1), font_size=18)
            ph_mark = Text("\u2713", font_size=18)

            row = VGroup(lbl_y_eq, ph_y, lbl_sq_eq, ph_raw, lbl_equiv, ph_mod, lbl_target, ph_mark)
            row.arrange(RIGHT, buff=0.1)
            row.next_to(scan_label, DOWN, buff=0.3, aligned_edge=LEFT)

            y_slot_pos = ph_y.get_center()
            raw_slot_pos = ph_raw.get_center()
            mod_slot_pos = ph_mod.get_center()
            mark_slot_pos = ph_mark.get_center()

            self.play(FadeIn(lbl_y_eq), FadeIn(lbl_sq_eq), FadeIn(lbl_equiv), FadeIn(lbl_target))

            y_num = raw_num = mod_num = mark_sym = None
            found = []
            for y in range(p):
                raw = y * y
                y2 = raw % p
                match = y2 == rhs
                color = GREEN if match else WHITE
                mark = "\u2713" if match else "\u2717"

                # Phase 1: show y and its raw square (not yet reduced).
                new_y_num = Text(str(y), font_size=18).move_to(y_slot_pos)
                new_raw_num = Text(str(raw), font_size=18).move_to(raw_slot_pos)
                if y_num is None:
                    self.play(FadeIn(new_y_num), FadeIn(new_raw_num), run_time=0.22)
                    y_num, raw_num = new_y_num, new_raw_num
                else:
                    self.play(Transform(y_num, new_y_num), Transform(raw_num, new_raw_num), run_time=0.22)
                self.wait(0.25)

                # Phase 2: reduce mod p and mark whether it hits the target
                # rhs shown right there on the same line.
                new_mod_num = Text(str(y2), font_size=18, color=color).move_to(mod_slot_pos)
                new_mark_sym = Text(mark, font_size=18, color=color).move_to(mark_slot_pos)
                if mod_num is None:
                    self.play(FadeIn(new_mod_num), FadeIn(new_mark_sym), run_time=0.22)
                    mod_num, mark_sym = new_mod_num, new_mark_sym
                else:
                    self.play(Transform(mod_num, new_mod_num), Transform(mark_sym, new_mark_sym), run_time=0.22)
                self.wait(0.12)

                if match:
                    dot = Dot(mark_sym.get_right() + RIGHT * 0.3, color=YELLOW, radius=0.08)
                    label = Text(f"({x},{y})", font_size=11, color=YELLOW_A).next_to(dot, UP, buff=0.04)
                    self.play(FadeIn(dot), FadeIn(label), run_time=0.2)
                    self.play(
                        dot.animate(path_arc=-60 * DEGREES).move_to(axes.c2p(x, y)),
                        label.animate(path_arc=-60 * DEGREES).next_to(axes.c2p(x, y), UR, buff=0.03),
                        run_time=0.9,
                    )
                    found.append((dot, label))

            curve_dots.add(*[d for d, _ in found])
            coord_labels.add(*[l for _, l in found])

            row_mobjects = [lbl_target, lbl_y_eq, lbl_sq_eq, lbl_equiv, y_num, raw_num, mod_num, mark_sym]
            if not found:
                no_point = Text("no point for this x", font_size=18, color=GRAY)
                no_point.next_to(row, DOWN, buff=0.2, aligned_edge=LEFT)
                self.play(FadeIn(no_point))
                self.wait(0.6)
                self.play(FadeOut(calc1), FadeOut(scan_label), *[FadeOut(m) for m in row_mobjects], FadeOut(no_point))
            else:
                self.wait(0.3)
                self.play(FadeOut(calc1), FadeOut(scan_label), *[FadeOut(m) for m in row_mobjects])

        # --- Speed up: same y-scan process, much faster, for x = 4 ... 16 ---
        self.play(FadeOut(plug_header))
        fast_header = Text("Continuing faster through x = 4 ... 16, testing all y:", font_size=18, color=GRAY_B)
        fast_header.next_to(field_set, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeIn(fast_header))

        # Same stable-template idea as the slow loop: the words never move
        # or get recreated -- only the x, y, reduced-value and mark slots
        # are swapped in place, just much faster, so it reads as "the same
        # sentence ticking over" rather than a new line jumping in each time.
        lbl_x_eq = Text("x =", font_size=16)
        lbl_y_eq2 = Text(", y =", font_size=16)
        lbl_sq_eq2 = Text(":  y\u00b2 \u2261", font_size=16)
        lbl_mod2 = Text(f"(mod {p})", font_size=16)

        ph_x = Text(str(p - 1), font_size=16)
        ph_y2 = Text(str(p - 1), font_size=16)
        ph_mod2 = Text(str(p - 1), font_size=16)
        ph_mark2 = Text("\u2713", font_size=16)

        row2 = VGroup(lbl_x_eq, ph_x, lbl_y_eq2, ph_y2, lbl_sq_eq2, ph_mod2, lbl_mod2, ph_mark2)
        row2.arrange(RIGHT, buff=0.08)
        row2.next_to(fast_header, DOWN, buff=0.3, aligned_edge=LEFT)

        x_slot_pos = ph_x.get_center()
        y_slot_pos2 = ph_y2.get_center()
        mod_slot_pos2 = ph_mod2.get_center()
        mark_slot_pos2 = ph_mark2.get_center()

        self.play(FadeIn(lbl_x_eq), FadeIn(lbl_y_eq2), FadeIn(lbl_sq_eq2), FadeIn(lbl_mod2))

        x_num = y_num2 = mod_num2 = mark_sym2 = None
        for x in range(4, p):
            rhs = rhs_of(x)
            y_anims = []
            found = []
            for y in range(p):
                y2 = (y * y) % p
                match = y2 == rhs
                color = GREEN if match else WHITE
                mark = "\u2713" if match else "\u2717"

                new_x = Text(str(x), font_size=16).move_to(x_slot_pos)
                new_y2 = Text(str(y), font_size=16).move_to(y_slot_pos2)
                new_mod2 = Text(str(y2), font_size=16, color=color).move_to(mod_slot_pos2)
                new_mark2 = Text(mark, font_size=16, color=color).move_to(mark_slot_pos2)

                if x_num is None:
                    y_anims.append(AnimationGroup(
                        FadeIn(new_x), FadeIn(new_y2), FadeIn(new_mod2), FadeIn(new_mark2), run_time=0.05,
                    ))
                    x_num, y_num2, mod_num2, mark_sym2 = new_x, new_y2, new_mod2, new_mark2
                else:
                    y_anims.append(AnimationGroup(
                        Transform(x_num, new_x), Transform(y_num2, new_y2),
                        Transform(mod_num2, new_mod2), Transform(mark_sym2, new_mark2),
                        run_time=0.05,
                    ))

                if match:
                    dot = Dot(mark_sym2.get_right() + RIGHT * 0.25, color=YELLOW, radius=0.06)
                    label = Text(f"({x},{y})", font_size=11, color=YELLOW_A).next_to(dot, UP, buff=0.03)
                    y_anims.append(AnimationGroup(FadeIn(dot), FadeIn(label), run_time=0.08))
                    y_anims.append(AnimationGroup(
                        dot.animate(path_arc=-60 * DEGREES).move_to(axes.c2p(x, y)),
                        label.animate(path_arc=-60 * DEGREES).next_to(axes.c2p(x, y), UR, buff=0.03),
                        run_time=0.3,
                    ))
                    found.append((dot, label))

            self.play(Succession(*y_anims))
            curve_dots.add(*[d for d, _ in found])
            coord_labels.add(*[l for _, l in found])

        self.play(
            FadeOut(x_num), FadeOut(y_num2), FadeOut(mod_num2), FadeOut(mark_sym2),
            FadeOut(lbl_x_eq), FadeOut(lbl_y_eq2), FadeOut(lbl_sq_eq2), FadeOut(lbl_mod2),
            FadeOut(fast_header),
        )

        points = curve_points_mod(p, a, b)
        count_label = Text(f"{len(points)} points\non the curve\n(mod {p})", font_size=24, line_spacing=1.2)
        count_label.next_to(eq, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(FadeOut(field_set), FadeIn(count_label))
        self.wait(1.5)

        # --- Grow the modulus: 17 -> 31 -> 97 -> 997 -> 999983, watching the
        # curve (and the point count) explode as the field gets bigger. The
        # coordinate system itself morphs live for each jump -- full exact
        # enumeration while it's cheap, then an exact Legendre-symbol count
        # plus a sparse sampled scatter once p is too big to enumerate. ---
        self.play(FadeOut(coord_labels), FadeOut(count_label))

        # Keep an untouched copy of the equation mobject: ReplacementTransform
        # mutates its source mobject's points in place, and we still need the
        # *original* (unstepped) `eq`/`axes`/`curve_dots`/`grid_dots` as the
        # starting point for the very first growth-loop transform below.
        cur_axes, cur_grid, cur_curve, cur_eq = axes, grid_dots, curve_dots, eq
        cur_count_label = None

        growth_steps = [31, 97, 997, 999983]
        for step_i, p_step in enumerate(growth_steps):
            is_last = step_i == len(growth_steps) - 1
            show_grid = p_step <= 31  # beyond this, p^2 background dots is too many mobjects

            axes_step = Axes(
                x_range=[0, p_step, max(1, p_step // 5)],
                y_range=[0, p_step, max(1, p_step // 5)],
                x_length=4.8, y_length=4.8,
                axis_config={"include_tip": False, "include_numbers": False},
            ).move_to(AXES_CENTER)

            if p_step <= 997:
                # Still cheap to enumerate exactly (p^2 iterations, <1s).
                step_points = curve_points_mod(p_step, a, b)
                count = len(step_points)
                dot_radius = 0.06 if p_step <= 31 else (0.045 if p_step == 97 else 0.025)
                dot_color = YELLOW if p_step <= 97 else GRAY
                curve_step = VGroup(*[
                    Dot(axes_step.c2p(x, y), radius=dot_radius, color=dot_color) for x, y in step_points
                ])
            else:
                # Too big to enumerate (p^2 ~ 10^12): count exactly via the
                # Legendre symbol (O(p)), but only *sample* ~10,000 points to
                # actually draw -- enough to suggest the dense point cloud
                # without creating a million mobjects.
                count = count_points_fast(p_step, a, b)
                curve_step = VGroup()
                sample_step = 100  # sample every 100th x -- denser, still far from all p points
                for x in range(0, p_step, sample_step):
                    rhs = (x**3 + a * x + b) % p_step
                    if rhs == 0:
                        curve_step.add(Dot(axes_step.c2p(x, 0), radius=0.02, color=GRAY))
                    elif pow(rhs, (p_step - 1) // 2, p_step) == 1:
                        y = tonelli_shanks(rhs, p_step)
                        curve_step.add(Dot(axes_step.c2p(x, y), radius=0.02, color=GRAY))
                        curve_step.add(Dot(axes_step.c2p(x, p_step - y), radius=0.02, color=GRAY))

            eq_step = MathTex(f"y^2 \\equiv x^3 - x + 1 \\pmod{{{p_step}}}", font_size=30)
            eq_step.move_to(eq, aligned_edge=UL)

            anims = [
                ReplacementTransform(cur_axes, axes_step),
                ReplacementTransform(cur_curve, curve_step),
                ReplacementTransform(cur_eq, eq_step),
            ]
            if show_grid:
                grid_step = VGroup(*[
                    Dot(axes_step.c2p(x, y), radius=0.02, color=GRAY, fill_opacity=0.35)
                    for x in range(p_step) for y in range(p_step)
                ])
                anims.append(ReplacementTransform(cur_grid, grid_step))
                cur_grid = grid_step
            elif cur_grid is not None:
                anims.append(FadeOut(cur_grid))
                cur_grid = None
            if cur_count_label is not None:
                anims.append(FadeOut(cur_count_label))

            self.play(*anims, run_time=2.5)

            count_label_step = Text(
                f"{count:,} points\non the curve\n(mod {p_step})", font_size=24, line_spacing=1.2,
            )
            count_label_step.next_to(eq_step, DOWN, buff=0.4, aligned_edge=LEFT)
            self.play(FadeIn(count_label_step))

            cur_axes, cur_curve, cur_eq, cur_count_label = axes_step, curve_step, eq_step, count_label_step

            if p_step == 97:
                # Snapshot now (before later ReplacementTransforms mutate these
                # in place) so the addition walkthrough can land on the mod-97
                # curve instead of mod 17 -- same idea as the axes_17 snapshot.
                axes_97 = axes_step.copy()
                curve_dots_97 = curve_step.copy()
                eq_97 = eq_step.copy()

            if is_last:
                note = Text(
                    "More points means a\nbigger haystack to search \u2014\n"
                    "this growth is the basis\nof elliptic-curve cryptography.",
                    font_size=20, line_spacing=1.2,
                ).next_to(cur_count_label, DOWN, buff=0.4, aligned_edge=LEFT)
                self.play(FadeIn(note))
                self.wait(2.5)
                self.play(FadeOut(note))
            else:
                self.wait(1.2)

        # --- Back to a still-workable example, now at p = 97 (bigger field,
        # nicer-looking scatter of points than the very first p = 17 grid) ---
        self.play(
            FadeOut(cur_count_label),
            ReplacementTransform(cur_axes, axes_97),
            ReplacementTransform(cur_curve, curve_dots_97),
            ReplacementTransform(cur_eq, eq_97),
            run_time=2,
        )
        self.wait(0.5)
        # Use the restored (unmutated) p=97 axes for all remaining coordinate math.
        axes = axes_97
        p = 97
        # The equation has served its purpose -- clear the panel's top slot
        # for the addition walkthrough that follows.
        self.play(FadeOut(eq_97))

        # --- Step-by-step addition walkthrough: G, 2G, 3G, 4G (slow), 5G-8G (fast) ---
        header = Text("Computing multiples of G", font_size=24)
        header.move_to([PANEL_X, PANEL_TOP_Y, 0], aligned_edge=UL)
        self.play(FadeIn(header))

        G = (0, 1)
        cur = G
        trail_all = VGroup()
        dotG = Dot(axes.c2p(*G), color=RED, radius=0.1)
        labG = MathTex("G", color=RED, font_size=28).next_to(dotG, UP, buff=0.08)
        self.play(FadeIn(dotG), Write(labG))

        log_lines = VGroup(Text("G = (0,1)", font_size=20, color=RED_A))
        log_lines[0].next_to(header, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeIn(log_lines[0]))
        self.wait(0.4)

        # --- Slow, fully-explained steps for 2G, 3G, 4G ---
        for k in range(2, 5):
            m, x3, y3_raw, y3_sum = ec_step(cur, G, p, a)
            # Always anchor the transient detail line just below the last
            # permanent log entry, so it cascades downward as the log grows
            # instead of sitting at a fixed spot and overlapping new lines.
            detail_anchor = log_lines[-1].get_bottom() + DOWN * 0.45

            connector = wrapped_line(axes, cur, m, p)
            self.play(Create(connector))
            if k == 2:
                wrap_note = Text(
                    "Mod 97 a line wraps around the grid:\nit shows up as parallel pieces.",
                    font_size=17, color=GRAY_B, line_spacing=1.2,
                ).move_to([PANEL_X, -2.6, 0], aligned_edge=UL)
                self.play(FadeIn(wrap_note))

            raw_dot = Dot(axes.c2p(x3, y3_raw), color=ORANGE, radius=0.09)
            raw_lab = MathTex("R", color=ORANGE, font_size=26).next_to(raw_dot, UP, buff=0.06)
            info = Text(
                f"{cur}+{G} \u2192 R={(x3, y3_raw)}",
                font_size=19,
            ).move_to(detail_anchor, aligned_edge=LEFT)
            self.play(FadeIn(raw_dot), Write(raw_lab), FadeIn(info))
            self.wait(0.6)

            sum_dot = Dot(axes.c2p(x3, y3_sum), color=BLUE, radius=0.09)
            trail_all.add(sum_dot)
            sum_lab = MathTex(f"{k}G", color=BLUE, font_size=26).next_to(sum_dot, DOWN, buff=0.06)
            reflect_arrow = DashedLine(axes.c2p(x3, y3_raw), axes.c2p(x3, y3_sum), color=GRAY)
            info2 = Text(
                f"reflect \u2192 {k}G = {(x3, y3_sum)}",
                font_size=19,
            ).move_to(detail_anchor, aligned_edge=LEFT)
            self.play(Create(reflect_arrow))
            self.play(FadeIn(sum_dot), Write(sum_lab), ReplacementTransform(info, info2))
            self.wait(0.8)

            new_line = Text(f"{k}G = {(x3, y3_sum)}", font_size=20, color=RED_A)
            new_line.next_to(log_lines[-1], DOWN, buff=0.22, aligned_edge=LEFT)
            trail_dot = Dot(axes.c2p(x3, y3_sum), color=BLUE, radius=0.055)
            trail_all.add(trail_dot)
            self.play(
                FadeOut(connector), FadeOut(raw_dot), FadeOut(raw_lab),
                FadeOut(reflect_arrow), FadeOut(info2),
                FadeOut(sum_lab), FadeIn(trail_dot), FadeIn(new_line),
            )
            log_lines.add(new_line)
            cur = (x3, y3_sum)

        # --- Speed up: same process, much faster, continuing to 8G ---
        speed_header = Text("Speeding up \u2014 same process, now quicker:", font_size=18, color=GRAY_B)
        speed_header.next_to(log_lines[-1], DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeIn(speed_header), FadeOut(wrap_note))
        self.wait(0.3)

        # Track every label added in this phase so all of them (not just the
        # most recent one) get cleared away together at the end.
        speed_group = VGroup(speed_header)

        for k in range(5, 9):
            m, x3, y3_raw, y3_sum = ec_step(cur, G, p, a)

            connector = wrapped_line(axes, cur, m, p)
            raw_dot = Dot(axes.c2p(x3, y3_raw), color=ORANGE, radius=0.08)
            sum_dot = Dot(axes.c2p(x3, y3_sum), color=BLUE, radius=0.08)
            reflect_arrow = DashedLine(axes.c2p(x3, y3_raw), axes.c2p(x3, y3_sum), color=GRAY)
            fast_label = Text(f"{k}G = {(x3, y3_sum)}", font_size=19, color=RED_A)
            fast_label.next_to(speed_group[-1], DOWN, buff=0.22, aligned_edge=LEFT)

            self.play(
                Create(connector), FadeIn(raw_dot), Create(reflect_arrow),
                FadeIn(sum_dot), FadeIn(fast_label),
                run_time=0.5,
            )
            self.wait(0.2)
            trail_dot = Dot(axes.c2p(x3, y3_sum), color=BLUE, radius=0.05)
            trail_all.add(trail_dot)
            self.play(
                FadeOut(connector), FadeOut(raw_dot), FadeOut(reflect_arrow),
                FadeOut(sum_dot), FadeIn(trail_dot),
                run_time=0.3,
            )
            speed_group.add(fast_label)
            cur = (x3, y3_sum)

        # ================= Part 2: the discrete logarithm problem =================
        self.play(FadeOut(header), FadeOut(log_lines), FadeOut(speed_group))
        new_title = Text("The Discrete Logarithm Problem", font_size=36).to_edge(UP)
        self.play(ReplacementTransform(title, new_title))

        # --- Forward: keep adding G until 29G (easy) ---
        fwd = Text("Forward: computing k \u00b7 G is easy", font_size=24)
        fwd.move_to([PANEL_X, PANEL_TOP_Y, 0], aligned_edge=UL)
        formula = MathTex(r"k \cdot G = \underbrace{G + G + \cdots + G}_{k\ \text{times}}", font_size=28)
        formula.next_to(fwd, DOWN, buff=0.5, aligned_edge=LEFT)
        self.play(FadeIn(fwd), Write(formula))
        k_label = Text("k = 8", font_size=24).next_to(formula, DOWN, buff=0.5, aligned_edge=LEFT)
        moving_dot = Dot(axes.c2p(*cur), color=YELLOW, radius=0.1)
        self.play(FadeIn(k_label), FadeIn(moving_dot))

        target_k = 29
        for k in range(9, target_k + 1):
            cur = ec_add(cur, G, p, a)
            new_label = Text(f"k = {k}", font_size=24).move_to(k_label, aligned_edge=LEFT)
            left_trail = Dot(moving_dot.get_center(), color=BLUE, radius=0.045, fill_opacity=0.6)
            trail_all.add(left_trail)
            self.play(
                FadeIn(left_trail),
                moving_dot.animate.move_to(axes.c2p(*cur)),
                Transform(k_label, new_label),
                run_time=0.2,
            )
        self.wait(0.3)

        Qdot = Dot(axes.c2p(*cur), color=BLUE, radius=0.12)
        labQ = MathTex(f"Q = {target_k} \\cdot G", color=BLUE, font_size=32).next_to(Qdot, DOWN, buff=0.15)
        self.play(FadeIn(Qdot), Write(labQ), FadeOut(moving_dot))
        self.wait(0.8)
        self.play(FadeOut(fwd), FadeOut(formula), FadeOut(k_label), FadeOut(trail_all))

        # --- Backward: given only G and Q, k is hard to recover ---
        back_header = Text("Backward: finding k from G and Q", font_size=24, line_spacing=1.2)
        back_header.move_to([PANEL_X, PANEL_TOP_Y, 0], aligned_edge=UL)
        back_sub = Text(
            "is extremely hard.\nLet's try a few guesses for k:",
            font_size=20, line_spacing=1.2,
        ).next_to(back_header, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeIn(back_header), FadeIn(back_sub))
        self.wait(0.5)

        guess_log = VGroup()
        for g in [8, 43, 58, 71, 89]:
            guess_point = scalar_mul(g, G, p, a)
            guess_dot = Dot(axes.c2p(*guess_point), color=ORANGE, radius=0.1)
            guess_lab = Text(f"k = {g}?", font_size=20, color=ORANGE).next_to(guess_dot, UP, buff=0.08)
            self.play(FadeIn(guess_dot), FadeIn(guess_lab), run_time=0.5)
            self.wait(0.3)
            cross = Text("\u2717 not Q", font_size=18, color=ORANGE)
            cross.next_to(guess_log[-1] if len(guess_log) else back_sub, DOWN, buff=0.22, aligned_edge=LEFT)
            self.play(FadeIn(cross), run_time=0.3)
            guess_log.add(cross)
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

        # --- Brute force: how many guesses on average? ---
        n_here = p - 1
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

        big_block = VGroup(
            Text("Real elliptic curves use far\nlarger keys, e.g. 256 bits:", font_size=20, color=GRAY_B, line_spacing=1.2),
            MathTex(r"n = 2^{256} \quad\Rightarrow\quad \frac{n+1}{2} \approx 2^{255}", font_size=21),
            MathTex(r"\approx 5.8 \times 10^{76} \text{ guesses on average}", font_size=21, color=BLUE_A),
            Text("\u2014 hopeless for any computer.", font_size=20, color=BLUE_A),
        ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        big_block.next_to(back_sub, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(FadeOut(avg_block), FadeIn(big_block))
        self.wait(2.5)
        self.play(FadeOut(back_header), FadeOut(back_sub), FadeOut(big_block))

        # --- Summary: addition is easy in one direction, hard in the other ---
        easy = VGroup(
            Text("k  \u2192  k \u00b7 G", font_size=26, color=GREEN),
            Text("EASY: just add (the doubling trick\nneeds only \u2248 256 steps for a\n256-bit k)", font_size=19, line_spacing=1.2),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        hard = VGroup(
            Text("G, k \u00b7 G  \u2192  k", font_size=26, color=RED),
            Text("HARD: no efficient method known;\nguessing needs \u2248 2\u00b2\u2075\u2075 tries", font_size=19, line_spacing=1.2),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        easy.move_to([PANEL_X, PANEL_TOP_Y, 0], aligned_edge=UL)
        hard.next_to(easy, DOWN, buff=0.6, aligned_edge=LEFT)
        self.play(FadeIn(easy)); self.wait(2.5)
        self.play(FadeIn(hard)); self.wait(3)
        final = Text(
            "A one-way street: this is the\ndiscrete logarithm problem \u2014\nthe security of elliptic-curve\ncryptography rests on it.",
            font_size=21, line_spacing=1.2, color=YELLOW,
        ).next_to(hard, DOWN, buff=0.6, aligned_edge=LEFT)
        self.play(FadeIn(final))
        self.wait(4)

