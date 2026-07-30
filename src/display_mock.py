"""Reference solid of the Touch Display 2 10" for interference checking.

Built purely from spec.py; used by verify.py to prove the printed parts never
intersect the display, and by render.py to draw assembly views. Slightly
conservative: the chassis is modelled at the full glass footprint (the real
chassis is inset), the connector hump at its assumed extents, and the Pi
standoffs at the worst-case 17.1 depth.
"""

from build123d import *

import spec


def build_display(worst_case: bool = True) -> Part:
    depth = spec.UNIT_DEPTH_WORST if worst_case else spec.UNIT_DEPTH
    body = extrude(
        RectangleRounded(spec.UNIT_W, spec.UNIT_H, spec.UNIT_CORNER_R),
        amount=spec.EDGE_T,
    )
    # connector hump: assumed extents; modelled at its stated worst-case
    # bound (as deep as the Pi standoffs) so interference checks stay
    # conservative
    hump_h = spec.HUMP_Y_MAX - spec.HUMP_Y_MIN
    body += Pos(0, (spec.HUMP_Y_MAX + spec.HUMP_Y_MIN) / 2, spec.EDGE_T) * extrude(
        Rectangle(2 * spec.HUMP_HALF_W, hump_h), amount=depth - spec.EDGE_T
    )
    # four bobbin posts (rectangular keep-out, tips at POST_TIP_Z)
    for sx in (-1, 1):
        for sy in (-1, 1):
            body += Pos(
                sx * spec.POST_SPACING_X / 2,
                sy * spec.POST_SPACING_Y / 2,
                spec.EDGE_T,
            ) * extrude(
                Rectangle(spec.POST_BOBBIN_W + 0.7, spec.POST_BOBBIN_H + 0.4),
                amount=spec.POST_PROTRUSION,
            )
    # four Pi standoffs (deepest features)
    cy_top = spec.UNIT_H / 2 - spec.PI_ROW_TOP_FROM_TOP     # +24.503
    cy_bot = spec.UNIT_H / 2 - spec.PI_ROW_BOT_FROM_TOP     # -33.497
    for sx in (-1, 1):
        for cy in (cy_top, cy_bot):
            body += Pos(sx * spec.PI_HOLES_X / 2, cy, spec.EDGE_T) * extrude(
                Circle(spec.PI_STANDOFF_BOSS_D / 2), amount=depth - spec.EDGE_T
            )
    return body


if __name__ == "__main__":
    part = build_display()
    bb = part.bounding_box()
    s = bb.size
    print(f"display mock bbox: {s.X:.2f} x {s.Y:.2f} x {s.Z:.2f}")
    export_stl(part, "../stl/_display_reference.stl", tolerance=0.05, angular_tolerance=0.3)
    print("exported ../stl/_display_reference.stl (reference only, do not print)")
