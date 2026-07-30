"""Part A0: snap-on front bezel of the wall frame (prints face-down).

The visible picture-frame face: a 3 mm plate whose opening reveals the
active area with an even 2.5 mm margin, plus an outer skirt that laps over
the body's recessed front band and clicks onto its snap nubs. Felt strips
on the plate's back press the display glass onto the shelf datum.

Face details: 3 mm outer arris, 2 mm 45-degree mat bevel around the
opening, and a recessed liner groove ring - the visual grammar of a real
frame, all printed as crisp bed-side geometry.
"""

from build123d import *

import spec
import params as p


def build_bezel() -> Part:
    # face plate ---------------------------------------------------------
    plate = Pos(0, 0, p.BEZEL_FRONT_Z) * extrude(
        RectangleRounded(p.OUT_W, p.OUT_H, p.OUT_R), amount=p.BEZEL_FACE_T
    )
    plate -= Pos(0, p.LIP_OPEN_CY, p.BEZEL_FRONT_Z - 0.5) * extrude(
        RectangleRounded(p.LIP_OPEN_W, p.LIP_OPEN_H, p.LIP_OPEN_R),
        amount=p.BEZEL_FACE_T + 1,
    )

    # skirt ---------------------------------------------------------------
    skirt_outer = RectangleRounded(p.OUT_W, p.OUT_H, p.OUT_R)
    skirt_inner = RectangleRounded(
        p.OUT_W - 2 * p.SKIRT_T, p.OUT_H - 2 * p.SKIRT_T, p.OUT_R - p.SKIRT_T
    )
    plate += extrude(
        Pos(0, 0, p.BEZEL_BACK_Z) * (skirt_outer - skirt_inner),
        amount=p.SKIRT_DEPTH,
    )

    # snap recesses inside the skirt --------------------------------------
    in_w = p.OUT_W / 2 - p.SKIRT_T          # skirt inner half-width
    in_h = p.OUT_H / 2 - p.SKIRT_T
    rw = p.NUB_LEN + 2 * p.RECESS_EXTRA
    # the recess covers only where the nub stands proud of the lap
    # clearance, so a solid skirt lip remains behind it to snap over
    rz0 = p.RECESS_Z0
    rz1 = p.RECESS_Z1
    for y in p.NUB_SIDE_YS:
        for sx in (-1, 1):
            plate -= Pos(sx * (in_w + p.RECESS_DEPTH / 2 - 0.005), y, (rz0 + rz1) / 2) * Box(
                p.RECESS_DEPTH, rw, rz1 - rz0
            )
    for x in p.NUB_TOP_XS:
        plate -= Pos(x, in_h + p.RECESS_DEPTH / 2 - 0.005, (rz0 + rz1) / 2) * Box(
            rw, p.RECESS_DEPTH, rz1 - rz0
        )
    for x in p.NUB_BOT_XS:
        plate -= Pos(x, -(in_h + p.RECESS_DEPTH / 2 - 0.005), (rz0 + rz1) / 2) * Box(
            rw, p.RECESS_DEPTH, rz1 - rz0
        )

    # liner groove ring on the face --------------------------------------
    g_o = p.LINER_GROOVE_INSET
    g_i = p.LINER_GROOVE_INSET + p.LINER_GROOVE_W
    groove = RectangleRounded(
        p.OUT_W - 2 * g_o, p.OUT_H - 2 * g_o, max(p.OUT_R - g_o, 1.0)
    ) - RectangleRounded(
        p.OUT_W - 2 * g_i, p.OUT_H - 2 * g_i, max(p.OUT_R - g_i, 0.8)
    )
    plate -= extrude(Pos(0, 0, p.BEZEL_FRONT_Z - 0.5) * groove, amount=p.LINER_GROOVE_D + 0.5)

    # face chamfers: outer arris + mat bevel ------------------------------
    def on_front(e):
        return abs(e.center().Z - p.BEZEL_FRONT_Z) < 1e-6

    def is_outer(e):
        c = e.center()
        return abs(c.X) > p.LIP_OPEN_W / 2 + 2.5 or abs(c.Y) > p.LIP_OPEN_H / 2 + 4.5

    outer_edges = [e for e in plate.edges() if on_front(e) and is_outer(e)]
    # exclude the liner groove's own edges (they sit between opening and rim)
    outer_edges = [
        e
        for e in outer_edges
        if abs(e.center().X) > p.OUT_W / 2 - p.LINER_GROOVE_INSET + 0.2
        or abs(e.center().Y) > p.OUT_H / 2 - p.LINER_GROOVE_INSET + 0.2
    ]
    plate = chamfer(outer_edges, p.FRONT_CHAMFER)
    mat_edges = [
        e
        for e in plate.edges()
        if abs(e.center().Z - p.BEZEL_FRONT_Z) < 1e-6
        and abs(e.center().X) <= p.LIP_OPEN_W / 2 + 2.5
        and abs(e.center().Y) <= p.LIP_OPEN_H / 2 + 4.5
    ]
    plate = chamfer(mat_edges, p.MAT_BEVEL)
    return plate


if __name__ == "__main__":
    part = build_bezel()
    bb = part.bounding_box()
    s = bb.size
    print(f"bezel bbox: {s.X:.2f} x {s.Y:.2f} x {s.Z:.2f}  vol {part.volume/1000:.1f} cm3")
    assert abs(s.X - p.OUT_W) < 0.05 and abs(s.Y - p.OUT_H) < 0.05
    assert abs(bb.min.Z - p.BEZEL_FRONT_Z) < 0.01
    export_stl(part, "../stl/bezel.stl", tolerance=0.05, angular_tolerance=0.3)
    print("exported ../stl/bezel.stl")
