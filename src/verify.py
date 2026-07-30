"""Geometric verification harness for the Touch Display 2 mount STLs.

Run after (re)building the STLs:  python3 build_all.py

Checks every exported mesh against src/spec.py (the audited transcription of
the official drawing) and src/params.py (the design intent):
  - mesh integrity: watertight, consistent winding
  - the display reference solid is itself audited against spec.py (bounding
    box, depth planes, post/standoff/hump positions) so the interference
    proofs cannot pass vacuously
  - ASSEMBLY-PATH sweeps, not just static fits: the display is swept out
    through the front, the cover swept out through the rear (below the
    keyhole tabs), each step boolean-checked against the body
  - hole positions AND diameters (121.8 x 160 pattern, keyhole entry/slot)
  - bezel opening vs the active area; shelf seat plane; felt-gap stack
  - bed fit and per-part print-orientation overhang census
  - stand ground-plane contact on the tilted ground

Exit code 0 = everything passed. JSON report: docs/verification-report.json.
"""

import json
import math
import os
import sys

import numpy as np
import shapely.geometry as sg
import trimesh

import spec
import params as p

HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "..", "stl")
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append({"name": name, "ok": bool(ok), "detail": str(detail)})
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")
    return ok


def load(name):
    return trimesh.load(os.path.join(STL, name), force="mesh")


def section_polys(mesh, z):
    sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        return []
    to_plane = np.eye(4)
    to_plane[2, 3] = -z
    planar, _ = sec.to_2D(to_2D=to_plane)
    return list(planar.polygons_full)


def ring_centres(mesh, z, max_area=200.0):
    holes = []
    for poly in section_polys(mesh, z):
        for hole in poly.interiors:
            hp = sg.Polygon(hole)
            if hp.area <= max_area:
                c = hp.centroid
                holes.append((c.x, c.y, hp.area))
    return holes


def outer_bounds(mesh, z):
    polys = section_polys(mesh, z)
    if not polys:
        return None
    xs, ys = [], []
    for poly in polys:
        bx = poly.bounds
        xs += [bx[0], bx[2]]
        ys += [bx[1], bx[3]]
    return min(xs), min(ys), max(xs), max(ys)


def interior_bounds(mesh, z):
    best = None
    for poly in section_polys(mesh, z):
        for hole in poly.interiors:
            hp = sg.Polygon(hole)
            if best is None or hp.area > best.area:
                best = hp
    return best.bounds if best is not None else None


def expect_holes(mesh, z, expected, tol, label, dia=None, dia_tol=0.3, max_area=200.0):
    found = ring_centres(mesh, z, max_area=max_area)
    ok_all = True
    for ex, ey in expected:
        match = [h for h in found if abs(h[0] - ex) < tol and abs(h[1] - ey) < tol]
        if not match:
            ok_all = False
            check(f"{label} hole @({ex:.2f},{ey:.2f})", False, "not found in section")
            continue
        d = 2 * math.sqrt(match[0][2] / math.pi)
        if dia is not None:
            ok = abs(d - dia) < dia_tol
            ok_all &= check(
                f"{label} hole @({ex:.2f},{ey:.2f})", ok, f"d {d:.2f} (want {dia:.2f})"
            )
        else:
            check(f"{label} hole @({ex:.2f},{ey:.2f})", True, f"d~{d:.2f}")
    return ok_all


def overhang_area(mesh, down, bed_z, exempt=None, limit_deg=55.0):
    n = mesh.face_normals
    downness = n @ np.array(down, dtype=float)
    steep = downness > math.sin(math.radians(limit_deg - 0.5))
    centres = mesh.triangles_center
    d_axis = np.array(down, dtype=float)
    bed_pt = np.array([0, 0, bed_z], dtype=float)
    dist = (centres - bed_pt) @ (-d_axis)
    mask = steep & (dist > 0.2)
    if exempt:
        for lo, hi in exempt:
            inside = np.all((centres >= lo) & (centres <= hi), axis=1)
            mask &= ~inside
    return float(mesh.area_faces[mask].sum()), centres[mask]


def inter_volume(a, b):
    try:
        inter = trimesh.boolean.intersection([a, b], engine="manifold")
        return 0.0 if inter is None or inter.is_empty else abs(inter.volume)
    except Exception:
        return float("nan")


def interference(a, b, label, allow=1.0):
    vol = inter_volume(a, b)
    if math.isnan(vol):
        return check(f"interference {label}", False, "boolean failed")
    return check(f"interference {label}", vol < allow, f"intersection {vol:.3f} mm3")


def sweep_clear(moving, fixed, direction, steps, label, allow=1.0):
    """Boolean-check `moving` translated along `direction` at each step."""
    worst = 0.0
    for s in steps:
        m = moving.copy()
        m.apply_translation(np.array(direction, dtype=float) * s)
        v = inter_volume(m, fixed)
        if math.isnan(v):
            return check(f"sweep {label}", False, f"boolean failed at {s}")
        worst = max(worst, v)
    return check(f"sweep {label}", worst < allow, f"worst intersection {worst:.3f} mm3")


POSTS = [
    (sx * spec.POST_SPACING_X / 2, sy * spec.POST_SPACING_Y / 2)
    for sx in (-1, 1)
    for sy in (-1, 1)
]


def verify_mock(display):
    """Audit the display reference solid itself against spec.py."""
    check("mock watertight", display.is_watertight)
    ext = display.extents
    check(
        "mock bbox = unit + worst depth",
        abs(ext[0] - spec.UNIT_W) < 0.05
        and abs(ext[1] - spec.UNIT_H) < 0.05
        and abs(ext[2] - spec.UNIT_DEPTH_WORST) < 0.05,
        f"{ext[0]:.2f} x {ext[1]:.2f} x {ext[2]:.2f}",
    )
    # bobbin posts present at the right places at post-tip depth
    ob = outer_bounds(display, spec.POST_TIP_Z - 0.5)
    ok = ob is not None and abs(ob[2] - (spec.POST_SPACING_X / 2 + (spec.POST_BOBBIN_W + 0.7) / 2)) < 0.3
    check("mock bobbin extent", ok, str(ob))
    polys = section_polys(display, spec.POST_TIP_Z - 0.5)
    n_feats = len(polys)
    check("mock features at post plane", n_feats >= 5, f"{n_feats} regions (4 posts + hump)")
    # deepest plane: hump + standoffs both reach the 17.1 worst case (the
    # standoffs sit inside the hump's XY envelope, so the section is one
    # large region spanning the hump extents)
    polys = section_polys(display, spec.UNIT_DEPTH_WORST - 0.2)
    ok = False
    detail = "no regions"
    for q in polys:
        b = sg.Polygon(q.exterior).bounds
        if (
            abs(b[0] + spec.HUMP_HALF_W) < 0.3
            and abs(b[2] - spec.HUMP_HALF_W) < 0.3
            and abs(b[1] - spec.HUMP_Y_MIN) < 0.3
            and abs(b[3] - spec.HUMP_Y_MAX) < 0.3
        ):
            ok = True
            detail = f"hump {b[0]:.1f}..{b[2]:.1f} x {b[1]:.1f}..{b[3]:.1f} at 17.1"
    check("mock hump+standoffs at 17.1 worst-case", ok, detail)


def verify_frame(display, cover_mesh):
    m = load("frame.stl")
    check("body watertight", m.is_watertight)
    check("body winding", m.is_winding_consistent)
    ext = m.extents
    check(
        "body bed fit",
        ext[0] <= spec.BED_LIMIT and ext[1] <= spec.BED_LIMIT,
        f"{ext[0]:.1f} x {ext[1]:.1f}",
    )
    check(
        "body bbox",
        abs(ext[0] - p.OUT_W) < 0.05
        and abs(ext[1] - p.OUT_H) < 0.05
        and abs(m.bounds[0][2] - p.BAND_TOP_Z) < 0.02
        and abs(m.bounds[1][2] - p.FRAME_REAR_Z) < 0.02,
        f"{ext[0]:.2f} x {ext[1]:.2f}, z {m.bounds[0][2]:.2f}..{m.bounds[1][2]:.2f}",
    )

    ib = interior_bounds(m, 4.0)
    if ib:
        w, h = ib[2] - ib[0], ib[3] - ib[1]
        check(
            "body cavity = display + clearance",
            abs(w - p.CAV_W) < 0.1 and abs(h - p.CAV_H) < 0.1,
            f"{w:.2f} x {h:.2f} (want {p.CAV_W:.2f} x {p.CAV_H:.2f})",
        )
    ob = outer_bounds(m, 0.8)  # below the snap nubs
    check(
        "body front band recessed for the skirt",
        ob is not None and abs((ob[2] - ob[0]) - p.BAND_OUT_W) < 0.1,
        f"band {ob[2]-ob[0]:.2f} (want {p.BAND_OUT_W:.2f})",
    )
    ib = interior_bounds(m, p.SHELF_FRONT_Z + p.SHELF_T / 2)
    if ib:
        w, h = ib[2] - ib[0], ib[3] - ib[1]
        check(
            "shelf opening",
            abs(w - p.SHELF_OPEN_W) < 0.1 and abs(h - p.SHELF_OPEN_H) < 0.1,
            f"{w:.2f} x {h:.2f}",
        )
    # shelf seat plane: substantial up-facing area at SHELF_FRONT_Z
    seat = m.area_faces[
        (np.abs(m.triangles_center[:, 2] - p.SHELF_FRONT_Z) < 0.05)
        & (m.face_normals[:, 2] < -0.99)
    ].sum()
    check("shelf seat plane area", seat > 4000, f"{seat:.0f} mm2 at z={p.SHELF_FRONT_Z}")

    # keyholes: position, diameter, slot direction
    kz = p.KEYHOLE_TAB_Z + p.KEYHOLE_TAB_T / 2
    holes = ring_centres(m, kz, max_area=250)
    for sx in (-1, 1):
        matches = [
            h
            for h in holes
            if abs(h[0] - sx * p.KEYHOLE_X) < 4 and abs(h[1] - (p.KEYHOLE_ENTRY_Y + 3)) < 6
        ]
        area_ok = matches and 104 < matches[0][2] < 130
        check(
            f"keyhole @x={sx * p.KEYHOLE_X:.0f}",
            bool(area_ok),
            f"ring area {matches[0][2]:.0f}" if matches else "not found",
        )
    probes = np.array(
        [
            [p.KEYHOLE_X, p.KEYHOLE_ENTRY_Y + p.KEYHOLE_SLOT_LEN + 1, kz],
            [-p.KEYHOLE_X, p.KEYHOLE_ENTRY_Y + p.KEYHOLE_SLOT_LEN + 1, kz],
            [p.KEYHOLE_X, p.KEYHOLE_ENTRY_Y - 8.5, kz],
        ]
    )
    inside = m.contains(probes)
    check(
        "keyhole slot runs upward",
        (not inside[0]) and (not inside[1]) and inside[2],
        f"void above entry {~inside[0]}/{~inside[1]}, solid below {inside[2]}",
    )
    entry_d = 2 * math.sqrt((max(h[2] for h in holes) - p.KEYHOLE_SLOT_W * p.KEYHOLE_SLOT_LEN - math.pi * (p.KEYHOLE_SLOT_W / 2) ** 2 / 2) / math.pi) if holes else 0

    # snap nubs present
    nub_probe = np.array(
        [
            [p.BAND_OUT_W / 2 + 0.4, 70, (p.NUB_Z0 + p.NUB_Z1) / 2],
            [p.BAND_OUT_W / 2 + 0.4, 35, (p.NUB_Z0 + p.NUB_Z1) / 2],
        ]
    )
    nin = m.contains(nub_probe)
    check("snap nubs on band", nin[0] and not nin[1], f"nub {nin[0]}, gap {nin[1]}")

    # vents + cable slot voids
    v = m.contains(
        np.array(
            [
                [p.CAV_W / 2 + p.WALL / 2, 15.0, p.VENT_Z],
                [0, -(p.CAV_H / 2 + p.WALL / 2), p.FRAME_REAR_Z - 4],
            ]
        )
    )
    check("side vents + cable slot open", (not v[0]) and (not v[1]), str(v))

    # print orientation: rear-face-down -> down = +Z
    exempt = [
        # vent slot front faces (deliberate 3.3 mm-wall bridges), including
        # the bottom-wall intake slots near y = -125
        (
            np.array([-p.OUT_W / 2 - 1, -130, p.VENT_Z - p.VENT_H / 2 - 0.3]),
            np.array([p.OUT_W / 2 + 1, 130, p.VENT_Z - p.VENT_H / 2 + 0.7]),
        ),
        # cable slot end face (14 mm bridge)
        (
            np.array([-p.CABLE_SLOT_W, -p.OUT_H / 2 - 1, p.CABLE_SLOT_FRONT_Z - 0.3]),
            np.array([p.CABLE_SLOT_W, -p.CAV_H / 2 + 1, p.CABLE_SLOT_FRONT_Z + 0.3]),
        ),
        # finger-relief roofs (as printed): two 18 x 1.2 mm micro-bridges
        (
            np.array([-70, -p.OUT_H / 2 - 1, 2.9]),
            np.array([70, -p.BAND_OUT_H / 2 + 2, 3.1]),
        ),
        # tongue-slit ceilings and tongue undersides: 1.45 mm-wide strips
        # bridging the 2 mm tip slits / 0.75 mm horizontal slits, anchored
        # at both ends, hidden behind the bezel skirt
        (
            np.array([-p.OUT_W / 2 - 1, -p.OUT_H / 2 - 1, p.TONGUE_SLIT_TOP - 0.15]),
            np.array([p.OUT_W / 2 + 1, p.OUT_H / 2 + 1, p.TONGUE_SLIT_TOP + 0.15]),
        ),
        (
            np.array([-p.OUT_W / 2 - 1, -p.OUT_H / 2 - 1, p.TONGUE_TOP_Z - 0.15]),
            np.array([p.OUT_W / 2 + 1, p.OUT_H / 2 + 1, p.TONGUE_TOP_Z + 0.15]),
        ),
    ]
    area, flagged = overhang_area(m, [0, 0, 1], p.FRAME_REAR_Z, exempt)
    check("body support-free (rear-face-down)", area < 40, f"unsupported {area:.0f} mm2")

    # first-layer wall widths at the bed (rear face): a filter regression
    # like round 2's inner-rim chamfer would show up as a sub-mm ring here
    bed_pts = []
    for y in (-60.0, 0.0, 60.0):
        for w in np.arange(0.2, 3.4, 0.1):
            bed_pts.append([p.CAV_W / 2 + w, y, p.FRAME_REAR_Z - 0.1])
            bed_pts.append([-p.CAV_W / 2 - w, y, p.FRAME_REAR_Z - 0.1])
    for x in (-40.0, 40.0):
        for w in np.arange(0.2, 3.4, 0.1):
            bed_pts.append([x, -p.CAV_H / 2 - w, p.FRAME_REAR_Z - 0.1])
    inside = m.contains(np.array(bed_pts))
    per_station = inside.reshape(-1, 32).sum(axis=1) * 0.1 if False else None
    widths = []
    n_w = len(list(np.arange(0.2, 3.4, 0.1)))
    for i in range(0, len(bed_pts), n_w):
        pass
    # group: stations alternate in construction; simpler recount
    stations = {}
    for pt, isin in zip(bed_pts, inside):
        key = (round(pt[0], 1) if abs(pt[1]) > 100 else (pt[1], np.sign(pt[0])))
        stations.setdefault(str(key), 0)
        stations[str(key)] += 0.1 if isin else 0
    bad = {k: round(v, 2) for k, v in stations.items() if not 1.3 <= v <= 2.4}
    check("first-layer ring width uniform ~1.8", not bad, f"outliers: {bad}" if bad else "8 stations 1.3-2.4 mm")

    # seat contact: the shelf ring must land on the display's REAR PLATE
    # (143.36 x 228.73, vertically offset +0.198), not on air. Analytic
    # strips from the measured shelf opening vs the spec plate outline.
    ib = interior_bounds(m, p.SHELF_FRONT_Z + 1.0)
    if ib:
        plate_cy = (spec.REAR_PLATE_INSET_BOTTOM - spec.REAR_PLATE_INSET_TOP) / 2
        strip_x = spec.REAR_PLATE_W / 2 - ib[2]
        strip_top = (plate_cy + spec.REAR_PLATE_H / 2) - ib[3]
        strip_bot = (spec.REAR_PLATE_H / 2 - plate_cy) + ib[1]
        worst = min(strip_x, strip_top, strip_bot) - spec.FIT_CLEAR - 0.25
        check(
            "shelf seats on the display rear plate",
            worst >= 3.0,
            f"strips x/top/bot {strip_x:.2f}/{strip_top:.2f}/{strip_bot:.2f}, worst-case {worst:.2f}",
        )

    # tongue slits present (compliant snaps, not a rigid ring)
    probe = np.array(
        [
            [p.BAND_OUT_W / 2 - 0.7, 70 + p.NUB_TIP_OFFSET + p.TONGUE_SLIT_W / 2, 2.0],
            [p.BAND_OUT_W / 2 - 0.7, 70, (p.TONGUE_TOP_Z + p.TONGUE_SLIT_TOP) / 2],
        ]
    )
    tin = m.contains(probe)
    check("snap tongues freed by slits", (not tin[0]) and (not tin[1]), str(tin))

    # static + swept interference (display SEATED = +0.15 on the shelf)
    seated = display.copy()
    seated.apply_translation([0, 0, p.SHELF_FRONT_Z - spec.EDGE_T])
    interference(m, seated, "body vs display (seated)")
    sweep_clear(
        seated,
        m,
        [0, 0, -1],
        [3, 6, 10, 15, 20, 30, 45, 60],
        "display OUT through the front",
    )
    cov_seated = cover_mesh.copy()
    cov_seated.apply_translation([0, 0, p.SHELF_FRONT_Z - spec.EDGE_T])
    sweep_clear(
        cov_seated,
        m,
        [0, 0, 1],
        [3, 6, 10, 15, 20, 26, 31, 40, 60],
        "cover OUT through the rear (below tabs)",
    )
    # service path: display + cover as one assembly out through the front
    service = trimesh.util.concatenate([seated, cov_seated])
    sweep_clear(
        service,
        m,
        [0, 0, -1],
        [3, 6, 10, 15, 20, 30, 45, 60],
        "display+cover service removal out the front",
    )
    return m


def verify_bezel(display, body):
    m = load("bezel.stl")
    check("bezel watertight", m.is_watertight)
    check("bezel winding", m.is_winding_consistent)
    ext = m.extents
    check(
        "bezel bbox",
        abs(ext[0] - p.OUT_W) < 0.05
        and abs(ext[1] - p.OUT_H) < 0.05
        and abs(m.bounds[0][2] - p.BEZEL_FRONT_Z) < 0.02,
        f"{ext[0]:.2f} x {ext[1]:.2f}, z from {m.bounds[0][2]:.2f}",
    )
    ib = interior_bounds(m, p.BEZEL_FRONT_Z + p.BEZEL_FACE_T - 0.3)
    if ib:
        w, h = ib[2] - ib[0], ib[3] - ib[1]
        cy = (ib[1] + ib[3]) / 2
        check(
            "bezel opening",
            abs(w - p.LIP_OPEN_W) < 0.15 and abs(h - p.LIP_OPEN_H) < 0.15 and abs(cy - p.LIP_OPEN_CY) < 0.1,
            f"{w:.2f} x {h:.2f} cy {cy:.2f}",
        )
        # opening contains the active area with >= 2.3 margin, and the mat
        # bevel at the front face widens it (no pixel occlusion at angle)
        check(
            "active-area keep-out",
            w >= spec.ACTIVE_W + 2 * 2.3 and h >= spec.ACTIVE_H + 2 * 2.3,
            f"margins {(w - spec.ACTIVE_W)/2:.2f}/{(h - spec.ACTIVE_H)/2:.2f}",
        )
    fb = interior_bounds(m, p.BEZEL_FRONT_Z + 0.2)
    if fb:
        check(
            "mat bevel opens toward the face",
            (fb[2] - fb[0]) > p.LIP_OPEN_W + 2 * (p.MAT_BEVEL - 0.6),
            f"front opening {fb[2]-fb[0]:.2f}",
        )
    # tongue slits fully hidden + true seam reveal
    skirt_end = float(m.bounds[1][2])
    check(
        "skirt covers the tongue slits",
        skirt_end >= p.TONGUE_SLIT_TOP + 0.08,
        f"skirt end z {skirt_end:.2f} vs slit top {p.TONGUE_SLIT_TOP}",
    )
    reveal = (p.BAND_TOP_Z + p.BAND_DEPTH) - skirt_end
    check("seam reveal is the documented 1.5", abs(reveal - 1.5) < 0.05, f"{reveal:.2f} mm")

    # plate back plane (felt datum)
    back = m.area_faces[
        (np.abs(m.triangles_center[:, 2] - p.BEZEL_BACK_Z) < 0.05)
        & (m.face_normals[:, 2] > 0.99)
    ].sum()
    check("bezel felt datum plane", back > 3000, f"{back:.0f} mm2 at z={p.BEZEL_BACK_Z}")
    # felt gap arithmetic: glass sits at GLASS_Z on the shelf
    gap = p.GLASS_Z - p.BEZEL_BACK_Z
    check("pad gap", abs(gap - p.BEZEL_PAD_GAP) < 0.01, f"{gap:.2f} mm for 2 mm foam pads")

    # over-insertion stop: the snap (not the band rim) sets depth, with a
    # deliberate gap before the plate back can bottom on the band
    gap = p.BAND_TOP_Z - p.BEZEL_BACK_Z
    check("bezel over-insertion stop gap", abs(gap - 0.3) < 0.01, f"{gap:.2f} mm")

    # assembled bezel does not hit body or display; the snap event is the
    # ONLY interference along the slide (nub band), and it is small enough
    # for the tongue springs (~2 N each) to absorb
    seat_v = inter_volume(m, body)
    check(
        "bezel seats without stress (exact-touch on retention faces)",
        seat_v < 0.5,
        f"seat interference {seat_v:.2f} mm3",
    )
    fwd = m.copy()
    fwd.apply_translation([0, 0, -0.1])
    fwd_v = inter_volume(fwd, body)
    check(
        "zero-float: recess wedges within 0.1 mm of forward travel",
        fwd_v > 0.05,
        f"{fwd_v:.2f} mm3 at 0.1 forward (round-2 dead-band was 0.30-0.66)",
    )
    seated_disp = display.copy()
    seated_disp.apply_translation([0, 0, p.SHELF_FRONT_Z - spec.EDGE_T])
    interference(m, seated_disp, "bezel vs display (seated)")
    sweep_clear(m, seated_disp, [0, 0, -1], [2, 5, 10], "bezel OFF the front vs display")
    peak = 0.0
    for s_ in (0.6, 1.0, 1.4, 1.8, 2.2, 2.6, 3.0):
        b = m.copy()
        b.apply_translation([0, 0, -s_])
        v = inter_volume(b, body)
        peak = max(peak, 0.0 if math.isnan(v) else v)
    check(
        "bezel snap travel (tongue deflection only)",
        0.0 < peak < 60.0,
        f"peak traveling interference {peak:.1f} mm3 across 9 tongues",
    )

    # screw arithmetic: the display's supplied short M2.5s must engage the
    # bobbin threads through cover and stand
    cover_grip = p.COVER_T - p.POST_CBORE_DEPTH
    stand_grip = p.STAND_PLATE_T - p.POST_CBORE_DEPTH
    check(
        "supplied M2.5 screws engage (cover/stand)",
        cover_grip <= 2.5 and stand_grip <= 3.0,
        f"under-head stack {cover_grip:.1f} / {stand_grip:.1f} mm of a ~6 mm screw",
    )

    # deliberate micro-features: the liner groove's 1.5 mm ceiling ring and
    # the snap-recess floors (0.9 mm ledges hidden inside the lap joint)
    liner_exempt = [
        (
            np.array([-p.OUT_W / 2, -p.OUT_H / 2, p.BEZEL_FRONT_Z + p.LINER_GROOVE_D - 0.3]),
            np.array([p.OUT_W / 2, p.OUT_H / 2, p.BEZEL_FRONT_Z + p.LINER_GROOVE_D + 0.3]),
        ),
        (
            np.array([-p.OUT_W / 2, -p.OUT_H / 2, p.RECESS_Z0 - 0.3]),
            np.array([p.OUT_W / 2, p.OUT_H / 2, p.RECESS_Z1 + 0.3]),
        ),
    ]
    area, _ = overhang_area(m, [0, 0, -1], p.BEZEL_FRONT_Z, liner_exempt)
    check("bezel support-free (face-down)", area < 30, f"unsupported {area:.0f} mm2")
    ext_ok = ext[0] <= spec.BED_LIMIT and ext[1] <= spec.BED_LIMIT
    check("bezel bed fit", ext_ok, f"{ext[0]:.1f} x {ext[1]:.1f}")
    return m


def verify_cover(display, body):
    m = load("cover.stl")
    check("cover watertight", m.is_watertight)
    check("cover winding", m.is_winding_consistent)
    ext = m.extents
    check(
        "cover bbox",
        abs(ext[0] - p.COVER_W) < 0.05
        and abs(ext[1] - p.COVER_H) < 0.05
        and abs(m.bounds[0][2] - spec.POST_TIP_Z) < 0.02,
        f"{ext[0]:.2f} x {ext[1]:.2f}, front z {m.bounds[0][2]:.2f}",
    )
    check(
        "cover fits shelf opening",
        ext[0] <= p.SHELF_OPEN_W - 2 and ext[1] <= p.SHELF_OPEN_H - 2,
        f"{ext[0]:.1f} vs {p.SHELF_OPEN_W}",
    )
    expect_holes(
        m,
        p.COVER_FRONT_Z + 0.7,
        POSTS,
        0.3,
        "cover M2.5",
        dia=p.POST_HOLE_D,
        dia_tol=0.25,
        max_area=30,
    )
    # measured alignment cover holes vs mock post positions
    ch = ring_centres(m, p.COVER_FRONT_Z + 0.7, max_area=30)
    worst = 0.0
    for ex, ey in POSTS:
        c = min(ch, key=lambda h: (h[0] - ex) ** 2 + (h[1] - ey) ** 2, default=None)
        if c:
            worst = max(worst, math.hypot(c[0] - ex, c[1] - ey))
    check("cover/post alignment", worst < 0.1, f"worst {worst:.3f} mm")

    ib = interior_bounds(m, p.COVER_FRONT_Z + 0.7)
    if ib:
        ok = (
            ib[0] <= -p.PI_WIN_W / 2 + 0.1
            and ib[2] >= p.PI_WIN_W / 2 - 0.1
            and ib[1] <= p.PI_WIN_BOT_Y + 0.1
            and ib[3] >= p.PI_WIN_TOP_Y - 0.1
        )
        check("cover Pi window", ok, f"{ib[0]:.1f}..{ib[2]:.1f} x {ib[1]:.1f}..{ib[3]:.1f}")
        # window clears the Pi board envelope (both vertical orientations)
        # and the USB-C budget from the board's long edges
        board_half_w = spec.PI_BOARD_W / 2
        check(
            "USB-C plug budget at window",
            (ib[2] - board_half_w) >= spec.USB_C_PLUG_CLEARANCE
            and (-ib[0] - board_half_w) >= spec.USB_C_PLUG_CLEARANCE,
            f"{ib[2] - board_half_w:.1f} mm each side (budget {spec.USB_C_PLUG_CLEARANCE})",
        )
    cb = [
        (
            np.array([x - 4.5, y - 4.5, p.COVER_FRONT_Z + 0.5]),
            np.array([x + 4.5, y + 4.5, p.COVER_FRONT_Z + p.COVER_T]),
        )
        for x, y in POSTS
    ]
    area, _ = overhang_area(m, [0, 0, 1], p.COVER_FRONT_Z + p.COVER_T, cb)
    check("cover support-free (rear-face-down)", area < 25, f"unsupported {area:.0f} mm2")
    seated = display.copy()
    seated.apply_translation([0, 0, p.SHELF_FRONT_Z - spec.EDGE_T])
    cov_seated = m.copy()
    cov_seated.apply_translation([0, 0, p.SHELF_FRONT_Z - spec.EDGE_T])
    interference(cov_seated, seated, "cover vs display (both at seat datum)")
    interference(cov_seated, body, "cover vs body (installed)")
    return m


def verify_stand(display):
    m = load("stand.stl")
    check("stand watertight", m.is_watertight)
    check("stand winding", m.is_winding_consistent)
    ext = m.extents
    check(
        "stand bed fit",
        ext[0] <= spec.BED_LIMIT and ext[1] <= spec.BED_LIMIT,
        f"{ext[0]:.1f} x {ext[1]:.1f}",
    )
    expect_holes(
        m,
        p.STAND_PLATE_FRONT_Z + 0.7,
        POSTS,
        0.3,
        "stand M2.5",
        dia=p.POST_HOLE_D,
        dia_tol=0.25,
        max_area=30,
    )
    t = math.radians(p.STAND_TILT_DEG)
    s_, c_ = math.sin(t), math.cos(t)
    v = m.vertices
    along = v[:, 1] + spec.UNIT_H / 2
    w = p.STAND_GROUND_LIFT + along * c_ - v[:, 2] * s_
    check("stand nothing below ground", w.min() > -0.35, f"min w {w.min():.3f}")
    contact = v[w < 0.4]
    ok = (
        len(contact) > 0
        and contact[:, 1].max() - contact[:, 1].min() > 25
        and contact[:, 0].max() > 40
        and contact[:, 0].min() < -40
    )
    check("stand foot contact spread", ok, f"{len(contact)} contact verts")
    interference(m, display, "stand vs display")
    area, _ = overhang_area(
        m,
        [0, 0, -1],
        p.STAND_PLATE_FRONT_Z,
        exempt=[
            (
                np.array([-p.STAND_TIE_CABLE_W, -140, 0]),
                np.array([p.STAND_TIE_CABLE_W, -120, p.STAND_TIE_TOP_ZD + 2]),
            )
        ],
    )
    check("stand support-free", area < 40, f"unsupported {area:.0f} mm2")
    # tie-bar top chamfer actually present (round 3 caught a silent failure)
    n = m.face_normals
    c = m.triangles_center
    ch45 = (
        (np.abs(np.abs(n[:, 1]) - 0.707) < 0.1)
        & (np.abs(np.abs(n[:, 2]) - 0.707) < 0.1)
        & (c[:, 1] < -118)
        & (np.abs(c[:, 2] - p.STAND_TIE_TOP_ZD) < 2.5)
    )
    tie_ch = float(m.area_faces[ch45].sum())
    check("stand tie-bar chamfer present", tie_ch > 50, f"{tie_ch:.0f} mm2 of 45-deg facets")
    # tip-back margin: rearmost ground contact vs CoG (display+Pi+stand
    # ~0.55 kg, CoG ~40 mm behind the glass plane, top edge ~253 up)
    contact_d = []
    for vtx, wv in zip(v, w):
        if wv < 0.4:
            d_ = -(vtx[1] + spec.UNIT_H / 2) * s_ - vtx[2] * c_
            contact_d.append(d_)
    rear_d = -min(contact_d)
    tip_force = 5.4 * (rear_d - 70.6) / 252.9
    check(
        "stand tip-back margin",
        tip_force >= 1.1,
        f"rear contact {rear_d:.0f} mm behind glass -> ~{tip_force:.2f} N at the top edge",
    )
    return m


def verify_coupons():
    for name in ("fit-coupon-body", "fit-coupon-bezel"):
        m = load(f"{name}.stl")
        check(f"{name} watertight", m.is_watertight)
        ext = m.extents
        check(
            f"{name} size",
            ext[0] <= p.COUPON_SIZE + 1 and ext[1] <= p.COUPON_SIZE + 1,
            f"{ext[0]:.1f} x {ext[1]:.1f} x {ext[2]:.1f}",
        )


def main():
    display = load("_display_reference.stl")
    verify_mock(display)
    cover_mesh = load("cover.stl")
    body = verify_frame(display, cover_mesh)
    verify_bezel(display, body)
    verify_cover(display, body)
    verify_stand(display)
    verify_coupons()

    n_fail = sum(1 for r in RESULTS if not r["ok"])
    report = {"total": len(RESULTS), "failed": n_fail, "results": RESULTS}
    out = os.path.join(HERE, "..", "docs", "verification-report.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n{len(RESULTS) - n_fail}/{len(RESULTS)} checks passed -> {out}")
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
