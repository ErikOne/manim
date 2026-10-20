"""Shared helpers for the elliptic curve y^2 = x^3 + a*x + b used across scenes."""
import numpy as np

A = -1.0
B = 1.0


def rhs(x):
    return x**3 + A * x + B


def y_on_curve(x, branch=1):
    """Return y so that (x, y) lies on the curve, branch = +1 (upper) or -1 (lower)."""
    v = rhs(x)
    return branch * np.sqrt(max(v, 0.0))


def curve_points(x_min=-3.0, x_max=3.5, n=2000):
    """Return (xs, ys_top, ys_bot) sampling only where rhs(x) >= 0."""
    xs_all = np.linspace(x_min, x_max, n)
    xs, ys_top, ys_bot = [], [], []
    for x in xs_all:
        v = rhs(x)
        if v >= 0:
            xs.append(x)
            ys_top.append(np.sqrt(v))
            ys_bot.append(-np.sqrt(v))
    return xs, ys_top, ys_bot


def third_intersection(x1, y1, x2, y2):
    """Given two distinct points on the curve, find the third intersection point
    of the secant line with the curve (before reflection)."""
    if abs(x1 - x2) < 1e-9:
        m = (3 * x1**2 + A) / (2 * y1)
    else:
        m = (y2 - y1) / (x2 - x1)
    x3 = m**2 - x1 - x2
    y3 = m * (x3 - x1) + y1
    return x3, y3, m


def add_points(x1, y1, x2, y2):
    """Elliptic curve point addition P + Q."""
    x3, y3, m = third_intersection(x1, y1, x2, y2)
    return x3, -y3, m
