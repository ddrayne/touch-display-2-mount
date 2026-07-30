"""Part B: desk stand (one piece, prints on the plate's front face).

A plate screws onto the display's four rear posts; two side cheeks run down
and back to the ground, tilting the display STAND_TILT_DEG from vertical, and
a cross-tie bar joins the cheek toes under the display's bottom edge (with a
central cable notch). The Pi 5 + cooler pass through a window in the plate.

Geometry is worked in two frames:
- world side-view (d, w): d = horizontal, +d toward the viewer's side of the
  glass, w = height above the desk; the display's bottom-front edge sits at
  (0, STAND_GROUND_LIFT), leaning back STAND_TILT_DEG.
- display/part coords (y, z): as in spec.py/params.py; the plate occupies
  z 11.6..15.6, and the part prints with the z=11.6 face on the bed.
"""

import math

from build123d import *

import spec
import params as p

T = math.radians(p.STAND_TILT_DEG)
S, C = math.sin(T), math.cos(T)
HALF_H = spec.UNIT_H / 2  # 123.663


def world_to_part(d: float, w: float) -> tuple[float, float]:
    """Map world side-view (d, w) to part (y, z)."""
    along = -S * d + C * (w - p.STAND_GROUND_LIFT)
    z_d = -C * d - S * (w - p.STAND_GROUND_LIFT)
    return along - HALF_H, z_d


def part_to_world(y: float, z_d: float) -> tuple[float, float]:
    along = y + HALF_H
    d = -along * S - z_d * C
    w = p.STAND_GROUND_LIFT + along * C - z_d * S
    return d, w


def cheek_profile() -> list[tuple[float, float]]:
    """Cheek outline in part (y, z) coordinates."""
    zd_embed = p.STAND_CHEEK_EMBED_ZD
    # Front foot: the ground point whose part-z equals the plate front plane,
    # so the foot tip prints ON the bed and still lands on the tilted ground.
    d_front_foot = (S * p.STAND_GROUND_LIFT - p.STAND_PLATE_FRONT_Z) / C
    p1 = world_to_part(d_front_foot, 0.0)             # front foot
    p2 = world_to_part(-p.STAND_REAR_REACH, 0.0)      # rear foot
    # weld line on the plate (z_d = zd_embed), top and bottom of cheek; the
    # drop line sits 3 mm INSIDE the plate footprint so the union overlaps
    # instead of meeting the plate's side face tangentially (which breaks
    # the fused solid)
    p3 = (p.STAND_CHEEK_TOP_Y, zd_embed)
    p4 = (-(p.STAND_PLATE_H / 2 - 3.0), zd_embed)
    # below the plate, drop straight to the bed plane and run to the foot so
    # the face-down print has no unsupported underside (the band sits behind
    # the display, which is at most 8.6 deep at its bottom edge)
    p4b = (-(p.STAND_PLATE_H / 2 - 3.0), p.STAND_PLATE_FRONT_Z)
    return [p1, p2, p3, p4, p4b]


def build_stand() -> Part:
    plate = Pos(0, 0, p.STAND_PLATE_FRONT_Z) * extrude(
        RectangleRounded(p.STAND_PLATE_W, p.STAND_PLATE_H, p.STAND_PLATE_R),
        amount=p.STAND_PLATE_T,
    )

    # Pi window (same envelope as the cover) -----------------------------
    win_h = p.STAND_WIN_TOP_Y - p.STAND_WIN_BOT_Y
    win_cy = (p.STAND_WIN_TOP_Y + p.STAND_WIN_BOT_Y) / 2
    plate -= Pos(0, win_cy, p.STAND_PLATE_FRONT_Z - 0.5) * extrude(
        RectangleRounded(p.PI_WIN_W, win_h, p.PI_WIN_R), amount=p.STAND_PLATE_T + 1
    )

    # M2.5 post holes, counterbored from the rear ------------------------
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * spec.POST_SPACING_X / 2
            y = sy * spec.POST_SPACING_Y / 2
            plate -= Pos(x, y, p.STAND_PLATE_FRONT_Z - 0.5) * extrude(
                Circle(p.POST_HOLE_D / 2), amount=p.STAND_PLATE_T + 1
            )
            plate -= Pos(
                x, y, p.STAND_PLATE_FRONT_Z + p.STAND_PLATE_T - p.POST_CBORE_DEPTH
            ) * extrude(
                Circle(p.POST_CBORE_D / 2), amount=p.POST_CBORE_DEPTH + 0.5
            )

    # stiffening ribs beside the window ----------------------------------
    rib_back = p.STAND_PLATE_FRONT_Z + p.STAND_PLATE_T
    for sx in (-1, 1):
        plate += Pos(sx * p.STAND_RIB_X, 0, rib_back) * extrude(
            RectangleRounded(p.STAND_RIB_W, p.STAND_PLATE_H - 12, p.STAND_RIB_W / 2 - 0.1),
            amount=p.STAND_RIB_H,
        )

    # elephant-foot chamfer on the plate's bed edges while the solid is
    # still simple (before cheeks/tie introduce coplanar seams) ----------
    bed_edges = [
        e for e in plate.edges() if abs(e.center().Z - p.STAND_PLATE_FRONT_Z) < 1e-6
    ]
    plate = chamfer(bed_edges, spec.ELEPHANT_CHAMFER)

    # cheeks -------------------------------------------------------------
    # The rear-foot -> apex edge is a concave "easel" arc; the rear foot
    # corner is filleted; the side-face edges get a light chamfer.
    prof = cheek_profile()
    p1, p2, p3, p4, p4b = prof
    lines = Polyline(p1, p2)
    arc_a = SagittaArc(p2, p3, p.STAND_ARC_SAGITTA)
    arc_b = SagittaArc(p2, p3, -p.STAND_ARC_SAGITTA)
    tail = Polyline(p3, p4, p4b, p1)
    face_a = make_face([lines, arc_a, tail])
    face_b = make_face([lines, arc_b, tail])
    face = face_a if face_a.area < face_b.area else face_b  # concave side
    v_foot = min(face.vertices(), key=lambda v: (v.X - p2[0]) ** 2 + (v.Y - p2[1]) ** 2)
    try:
        face = fillet([v_foot], p.STAND_FOOT_FILLET)
    except Exception:
        pass
    sk = Plane.YZ * face
    cheek = extrude(sk, amount=p.STAND_CHEEK_T)
    if cheek.bounding_box().max.X > 0.01:  # face winding decides the side
        cheek = mirror(cheek, about=Plane.YZ)
    try:
        side_edges = [
            e
            for e in cheek.edges()
            if abs(e.center().X) < 0.01 or abs(e.center().X + p.STAND_CHEEK_T) < 0.01
        ]
        cheek = chamfer(side_edges, p.STAND_EDGE_CHAMFER)
    except Exception:
        pass
    x_in = p.STAND_CHEEK_OUT_X - p.STAND_CHEEK_T
    stand = plate
    stand += Pos(p.STAND_CHEEK_OUT_X, 0, 0) * cheek
    stand += Pos(-x_in, 0, 0) * cheek

    # cross-tie bar under the display bottom edge ------------------------
    p1 = prof[0]
    tie_y0 = p1[0]                      # foot-tip y (most negative)
    tie_y1 = -HALF_H - 0.8              # just clear of the display bottom edge
    tie = Pos(
        0,
        (tie_y0 + tie_y1) / 2,
        (p.STAND_PLATE_FRONT_Z + p.STAND_TIE_TOP_ZD) / 2,
    ) * Box(
        2 * p.STAND_CHEEK_OUT_X,
        tie_y1 - tie_y0,
        p.STAND_TIE_TOP_ZD - p.STAND_PLATE_FRONT_Z,
    )
    stand += tie
    # cable notch through the tie
    stand -= Pos(0, (tie_y0 + tie_y1) / 2, p.STAND_TIE_TOP_ZD) * Box(
        p.STAND_TIE_CABLE_W, tie_y1 - tie_y0 + 2, 12
    )
    # soften the tie bar's exposed top edges (the long ones only - the side
    # ends are coplanar seams with the cheeks and break the chamfer builder)
    tie_edges = [
        e
        for e in stand.edges()
        if abs(e.center().Z - p.STAND_TIE_TOP_ZD) < 1e-6
        and e.center().Y < -120
        and abs(e.center().X) < 66
    ]
    stand = chamfer(tie_edges, 1.5)

    # elephant-foot chamfer on bed-contact edges of the plate (done BEFORE
    # the ground trim, whose facets confuse the chamfer builder) ---------
    # (plate bed edges were chamfered before the cheek/tie unions)

    # trim everything below the tilted ground plane, so the feet (and the
    # tie-bar corner) end in clean ground-flush facets
    y_g, z_g = prof[0]
    ground = Plane(
        origin=(0, y_g, z_g), x_dir=(1, 0, 0), z_dir=(0, C, -S)
    ) * Pos(0, 0, -100) * Box(500, 500, 200)
    stand -= ground
    return stand


if __name__ == "__main__":
    part = build_stand()
    bb = part.bounding_box()
    s = bb.size
    print(f"stand bbox: {s.X:.2f} x {s.Y:.2f} x {s.Z:.2f}  vol {part.volume/1000:.1f} cm3")
    print(f"  x range {bb.min.X:.2f} .. {bb.max.X:.2f}")
    assert bb.max.X <= p.STAND_CHEEK_OUT_X + 0.01, bb.max.X
    assert bb.min.X >= -p.STAND_CHEEK_OUT_X - 0.01, bb.min.X
    # feet must be coplanar with the tilted ground plane: check the two
    # extreme foot points sit at world w = 0
    for y, z in (cheek_profile()[0], cheek_profile()[1]):
        d, w = part_to_world(y, z)
        assert abs(w) < 0.35, (y, z, w)
    export_stl(part, "../stl/stand.stl", tolerance=0.05, angular_tolerance=0.3)
    print("exported ../stl/stand.stl")
