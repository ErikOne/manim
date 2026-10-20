"""Combined render: stitches all six scenes into a single continuous video,
holding an extra 5 seconds on the final frame of each scene before cutting to
the next one. Run with:

    manim -ql full_video.py FullVideo --media_dir media -o FullVideo

Order: elliptic curves over R -> two points give a third -> point addition ->
modular arithmetic -> finite field -> discrete logarithm problem.

ThirdIntersection is a MovingCameraScene (it zooms the camera out), so
FullVideo inherits from it too -- that gives the combined scene a MovingCamera
for its entire runtime, which is a strict superset of a plain Scene's camera
and works transparently for the other five scenes as well. FiniteFieldCurve's
get_moving_and_static_mobjects override (a render-cache workaround) is picked
up the same way through normal multiple-inheritance MRO.
"""
from manim import *

from elliptic_curve_real import EllipticCurveReal
from third_intersection import ThirdIntersection
from point_addition import PointAddition
from modular_arithmetic import ModularArithmetic
from finite_field import FiniteFieldCurve
from discrete_log import DiscreteLog


class FullVideo(ThirdIntersection, FiniteFieldCurve, EllipticCurveReal,
                PointAddition, ModularArithmetic, DiscreteLog):
    def construct(self):
        scenes_in_order = [
            EllipticCurveReal,
            ThirdIntersection,
            PointAddition,
            ModularArithmetic,
            FiniteFieldCurve,
            DiscreteLog,
        ]
        for i, scene_cls in enumerate(scenes_in_order):
            scene_cls.construct(self)
            if i < len(scenes_in_order) - 1:
                self.wait(5)
                self.clear()
