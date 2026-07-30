"""Test-fit coupons: matching top-right corner sections of body and bezel.

Print both (~40 minutes total) before committing to the full frame print.
Together they prove: the display corner's slip fit and shelf seat, the
corner radius, the bezel's lap fit and snap-nub engagement, and the lip
reveal/felt gap. Too tight -> raise spec.FIT_CLEAR (display) or
params.LAP_CLEAR (bezel); rattling loose -> lower them; rebuild and
re-print the coupons, not the frame.
"""

from build123d import *

import params as p
from bezel import build_bezel
from frame import build_frame


def _corner_box(depth_lo: float, depth_hi: float) -> Part:
    size = p.COUPON_SIZE
    return Pos(
        p.OUT_W / 2 - size / 2,
        p.OUT_H / 2 - size / 2,
        (depth_lo + depth_hi) / 2,
    ) * Box(size, size, depth_hi - depth_lo)


def build_body_coupon() -> Part:
    # deep enough to include the shelf seat and a snap nub, shallow enough
    # to stay a quick print
    return build_frame() & _corner_box(p.BAND_TOP_Z - 1, 18.0)


def build_bezel_coupon() -> Part:
    return build_bezel() & _corner_box(p.BEZEL_FRONT_Z - 1, 7.0)


if __name__ == "__main__":
    for name, part in (
        ("fit-coupon-body", build_body_coupon()),
        ("fit-coupon-bezel", build_bezel_coupon()),
    ):
        bb = part.bounding_box()
        s = bb.size
        print(f"{name}: {s.X:.2f} x {s.Y:.2f} x {s.Z:.2f}  vol {part.volume/1000:.1f} cm3")
        export_stl(part, f"../stl/{name}.stl", tolerance=0.05, angular_tolerance=0.3)
        print(f"exported ../stl/{name}.stl")
