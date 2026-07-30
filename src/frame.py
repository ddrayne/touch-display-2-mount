"""Part A1: shadow-box body of the wall frame (one piece, prints
REAR-FACE-DOWN).

Front-loading: the display (with Pi attached) drops in from the front and
its chassis rim rests on the internal shelf ring; the bezel (bezel.py) then
snaps over the recessed front band. The rear keeps the keyhole hang tabs,
hidden side vents, and the bottom cable slot; the posts-only cover
(cover.py) enters from the rear, passing below the tabs.

Printed rear-face-down: the keyhole tabs lie solid on the bed (no bridges),
the band->full-outline loft faces upward, and the shelf ring carries a
45-degree chamfer on its rear side so its only support-free-critical face
(the seat itself) prints as a clean top surface.
"""

from build123d import *

import spec
import params as p


def _nub(wall: str, along: float) -> Part:
    """Snap nub on the band: 45-deg lead-in, steeper retention face."""
    half_w = p.BAND_OUT_W / 2
    half_h = p.BAND_OUT_H / 2
    embed = 0.6
    prof = [
        (-embed, p.NUB_Z0),
        (p.NUB_PROUD, p.NUB_Z0 + p.NUB_LEAD_RUN),
        (p.NUB_PROUD, p.NUB_Z1 - p.NUB_HOLD_RUN),
        (-embed, p.NUB_Z1),
    ]
    sk = Plane.XZ * Polygon(*prof, align=None)
    nub = extrude(sk, amount=p.NUB_LEN / 2, both=True)
    if wall == "left":
        return Pos(-half_w, along, 0) * Rot(0, 0, 180) * nub
    if wall == "right":
        return Pos(half_w, along, 0) * nub
    if wall == "top":
        return Pos(along, half_h, 0) * Rot(0, 0, 90) * nub
    return Pos(along, -half_h, 0) * Rot(0, 0, -90) * nub


def _tongue_slits(wall: str, along: float) -> list:
    """Two through-cuts that free a cantilever tongue under each nub.

    The tongue (root on one side, ~18 mm free length) lets the nub deflect
    inward at ~2 N instead of forcing the rigid skirt to stretch. Both slits
    hide behind the bezel skirt (which covers the band to z 5.45).
    """
    cuts = []
    tip = along + p.NUB_TIP_OFFSET
    root = tip - p.TONGUE_LEN
    # vertical slit at the tip end
    v_len = p.TONGUE_SLIT_TOP - (p.BAND_TOP_Z - 0.5)
    v = Box(6.0, p.TONGUE_SLIT_W, v_len)
    # horizontal slit separating the tongue's top edge
    h_len = tip + p.TONGUE_SLIT_W - root
    h = Box(6.0, h_len, p.TONGUE_SLIT_TOP - p.TONGUE_TOP_Z)
    half_w = p.BAND_OUT_W / 2 - 0.7
    half_h = p.BAND_OUT_H / 2 - 0.7
    for box, cy, cz in (
        (v, tip + p.TONGUE_SLIT_W / 2, p.BAND_TOP_Z - 0.5 + v_len / 2),
        (h, (root + tip + p.TONGUE_SLIT_W) / 2, (p.TONGUE_TOP_Z + p.TONGUE_SLIT_TOP) / 2),
    ):
        if wall == "left":
            cuts.append(Pos(-half_w, cy, cz) * box)
        elif wall == "right":
            cuts.append(Pos(half_w, cy, cz) * box)
        elif wall == "top":
            cuts.append(Pos(cy, half_h, cz) * Rot(0, 0, 90) * box)
        else:
            cuts.append(Pos(cy, -half_h, cz) * Rot(0, 0, 90) * box)
    return cuts


def _keyhole_cut(sx: float) -> Part:
    entry = Pos(sx * p.KEYHOLE_X, p.KEYHOLE_ENTRY_Y) * Circle(p.KEYHOLE_ENTRY_D / 2)
    slot = Pos(sx * p.KEYHOLE_X, p.KEYHOLE_ENTRY_Y + p.KEYHOLE_SLOT_LEN / 2) * Rectangle(
        p.KEYHOLE_SLOT_W, p.KEYHOLE_SLOT_LEN
    )
    tip = Pos(sx * p.KEYHOLE_X, p.KEYHOLE_ENTRY_Y + p.KEYHOLE_SLOT_LEN) * Circle(
        p.KEYHOLE_SLOT_W / 2
    )
    sk = entry + slot + tip
    return extrude(Pos(0, 0, p.KEYHOLE_TAB_Z - 0.5) * sk, amount=p.KEYHOLE_TAB_T + 1)


def build_frame() -> Part:
    band_end = p.BAND_TOP_Z + p.BAND_DEPTH                     # 6.95
    trans_end = band_end + p.BAND_CHAMFER_RUN                  # 8.35

    # shell: recessed band -> chamfer transition -> full section ---------
    band = Pos(0, 0, p.BAND_TOP_Z) * extrude(
        RectangleRounded(p.BAND_OUT_W, p.BAND_OUT_H, p.BAND_OUT_R),
        amount=p.BAND_DEPTH,
    )
    trans = loft(
        [
            Pos(0, 0, band_end) * RectangleRounded(p.BAND_OUT_W, p.BAND_OUT_H, p.BAND_OUT_R),
            Pos(0, 0, trans_end) * RectangleRounded(p.OUT_W, p.OUT_H, p.OUT_R),
        ]
    )
    body_main = Pos(0, 0, trans_end) * extrude(
        RectangleRounded(p.OUT_W, p.OUT_H, p.OUT_R),
        amount=p.FRAME_REAR_Z - trans_end,
    )
    frame = band + trans + body_main

    # through cavity (front-loading) -------------------------------------
    frame -= Pos(0, 0, p.BAND_TOP_Z - 1) * extrude(
        RectangleRounded(p.CAV_W, p.CAV_H, p.CAV_R),
        amount=p.FRAME_REAR_Z - p.BAND_TOP_Z + 2,
    )

    # shelf ring with a 45-degree rear chamfer (printable rear-face-down):
    # solid from the seat plane back to where the chamfer meets the wall,
    # minus the straight opening prism, minus a lofted void that flares
    # from the opening out to the cavity at 45 degrees.
    protrusion = max(
        (p.CAV_W - p.SHELF_OPEN_W) / 2, (p.CAV_H - p.SHELF_OPEN_H) / 2
    )                                                           # 11.97
    shelf_rear = p.SHELF_FRONT_Z + p.SHELF_T                    # 14.75
    # 1.55 x rise keeps even the corner facets of the loft (whose run is the
    # diagonal of both protrusions) comfortably under a 45-degree overhang
    chamfer_end = shelf_rear + 1.55 * protrusion                # ~36.4
    shelf_outer = RectangleRounded(p.CAV_W + 2, p.CAV_H + 2, p.CAV_R + 1)
    shelf_inner = RectangleRounded(p.SHELF_OPEN_W, p.SHELF_OPEN_H, p.SHELF_OPEN_R)
    shelf = Pos(0, 0, p.SHELF_FRONT_Z) * extrude(
        shelf_outer, amount=chamfer_end - p.SHELF_FRONT_Z
    )
    shelf -= Pos(0, 0, p.SHELF_FRONT_Z - 1) * extrude(
        shelf_inner, amount=p.SHELF_T + 1
    )
    shelf -= loft(
        [
            Pos(0, 0, shelf_rear) * shelf_inner,
            Pos(0, 0, chamfer_end)
            * RectangleRounded(p.CAV_W, p.CAV_H, p.CAV_R),
        ]
    )
    frame += shelf

    # snap nubs on compliant tongues -------------------------------------
    nubs = (
        [("left", y) for y in p.NUB_SIDE_YS]
        + [("right", y) for y in p.NUB_SIDE_YS]
        + [("top", x) for x in p.NUB_TOP_XS]
        + [("bottom", x) for x in p.NUB_BOT_XS]
    )
    for wall, along in nubs:
        frame += _nub(wall, along)
    for wall, along in nubs:
        for cut in _tongue_slits(wall, along):
            frame -= cut

    # finger reliefs for bezel removal: shallow scallops in the bottom
    # band running from under the skirt edge out through the reveal, so a
    # fingernail gets real purchase behind the skirt (round-3 audit: the
    # earlier fully-buried version was unreachable)
    band_end_z = p.BAND_TOP_Z + p.BAND_DEPTH
    for x in p.RELIEF_XS:
        frame -= Pos(
            x, -(p.BAND_OUT_H / 2 - p.RELIEF_D / 2 + 0.01), (3.0 + band_end_z + 0.4) / 2
        ) * Box(p.RELIEF_W, p.RELIEF_D, band_end_z + 0.4 - 3.0)

    # keyhole hang tabs + wedge ramps ------------------------------------
    cav_outline = RectangleRounded(p.CAV_W, p.CAV_H, p.CAV_R)
    for sx in (-1, 1):
        corner = Pos(
            sx * (p.CAV_W / 2 - p.KEYHOLE_TAB_W / 2),
            p.CAV_H / 2 - p.KEYHOLE_TAB_H / 2,
        ) * Rectangle(p.KEYHOLE_TAB_W, p.KEYHOLE_TAB_H)
        tab_sk = corner & cav_outline
        # printed rear-face-down the tabs lie solid on the bed; a 45-degree
        # front-side chamfer wedge eases their transition into the walls
        frame += extrude(Pos(0, 0, p.KEYHOLE_TAB_Z) * tab_sk, amount=p.KEYHOLE_TAB_T)
    for sx in (-1, 1):
        frame -= _keyhole_cut(sx)

    # rear shadow-wedge (BEFORE the slot/vent cuts pierce its faces) -----
    # Asymmetric chamfer, 6 mm up the flank x 1.5 mm across the rear face:
    # the hung frame floats on a dark reveal and the side vents exhaust
    # into it. The +0.5 selection tolerance keeps floating-point edge
    # centres from dragging the INNER cavity rim into the chamfer (a
    # round-2 print blocker: it left a 0.5 mm first layer on two walls).
    rear_outer = [
        e
        for e in frame.edges()
        if abs(e.center().Z - p.FRAME_REAR_Z) < 1e-6
        and (
            abs(e.center().X) > p.CAV_W / 2 + 0.5
            or abs(e.center().Y) > p.CAV_H / 2 + 0.5
        )
    ]
    frame = chamfer(rear_outer, p.REAR_CHAMFER_FLANK, p.REAR_CHAMFER_REAR)

    # bottom cable slot --------------------------------------------------
    slot_h = p.FRAME_REAR_Z - p.CABLE_SLOT_FRONT_Z
    frame -= Pos(
        0, -(p.CAV_H / 2 + p.WALL / 2), p.CABLE_SLOT_FRONT_Z + slot_h / 2 + 0.5
    ) * Box(p.CABLE_SLOT_W, p.WALL + 2, slot_h + 1)

    # hidden vents: sides exhaust into the rear shadow-wedge, bottom wall
    # slots feed intake air (openings face down - no dust path) ----------
    side_vent = extrude(
        Plane.YZ * RectangleRounded(p.VENT_L, p.VENT_H, 2.4),
        amount=p.WALL + 2,
    )
    n = p.VENT_COUNT_SIDE
    ys = [(i - (n - 1) / 2) * p.VENT_PITCH for i in range(n)]
    for y in ys:
        frame -= Pos(-(p.CAV_W / 2 + p.WALL + 1), y, p.VENT_Z) * side_vent
        frame -= Pos(p.CAV_W / 2 - 1, y, p.VENT_Z) * side_vent
    bot_vent = extrude(
        Plane.ZX * RectangleRounded(p.VENT_H, p.VENT_L, 2.4),
        amount=p.WALL + 2,
    )
    for x in p.VENT_BOT_XS:
        frame -= Pos(x, -(p.CAV_H / 2 + p.WALL + 1), p.VENT_Z) * bot_vent

    # remaining chamfers -------------------------------------------------
    # lead-in on the cavity mouth so the display lays down forgivingly
    mouth = [
        e
        for e in frame.edges()
        if abs(e.center().Z - p.BAND_TOP_Z) < 1e-6
        and abs(e.center().X) <= p.CAV_W / 2 + 0.5
        and abs(e.center().Y) <= p.CAV_H / 2 + 0.5
    ]
    if mouth:
        try:
            frame = chamfer(mouth, 1.5)
        except Exception:
            pass
    keyhole_rims = [
        e
        for e in frame.edges()
        if abs(e.center().Z - p.FRAME_REAR_Z) < 1e-6
        and abs(abs(e.center().X) - p.KEYHOLE_X) < 8
        and abs(e.center().Y - (p.KEYHOLE_ENTRY_Y + 4)) < 14
    ]
    if keyhole_rims:
        frame = chamfer(keyhole_rims, 0.5)
    return frame


if __name__ == "__main__":
    part = build_frame()
    bb = part.bounding_box()
    s = bb.size
    print(f"body bbox: {s.X:.2f} x {s.Y:.2f} x {s.Z:.2f}  vol {part.volume/1000:.1f} cm3")
    assert abs(s.X - p.OUT_W) < 0.05 and abs(s.Y - p.OUT_H) < 0.05, (s.X, s.Y)
    assert abs(bb.min.Z - p.BAND_TOP_Z) < 0.01 and abs(bb.max.Z - p.FRAME_REAR_Z) < 0.01
    export_stl(part, "../stl/frame.stl", tolerance=0.05, angular_tolerance=0.3)
    print("exported ../stl/frame.stl")
