"""Camera chin pod: mounts a Raspberry Pi Camera Module 3 under the frame.

One printed piece + four M2 screws. Two J-hooks enter the frame's inner
pair of bottom intake vent slots (tilt the pod, slide the hooks up, rotate
flat): the hook horns land over the wall's inner face and gravity locks
them - no frame changes, no flexing snaps, tool-free removal. The camera
board mounts ribbon-UP (image flipped in software) so the mini ribbon runs
straight up a concealed channel in the pod's tail and through the frame's
existing cable slot to the Pi's free MIPI port.

The camera bay opens toward the rear (hidden under the frame), so the
board drops in from behind onto four M2 self-tap bosses - no lid needed,
and the bay stays ventilated.

Modelled in the frame's assembly coordinates (x across, y up, z rearward;
frame bottom outer wall face at y = -127.26). Printed sole-face-down (the
print/ export rotates it).
"""

import math

from build123d import *

import spec
import params as p

SOLE_Y = -(p.OUT_H / 2 + 0.2)          # pod top face, just below the frame
BOX_FRONT_Z = -2.0                     # slightly behind the bezel face
BOX_DEPTH = 18.0
BOX_H = 31.0
TAIL_H = 7.0
TAIL_END_Z = p.FRAME_REAR_Z - 0.5
CH_W = 20.0                            # ribbon channel width
CH_D = 4.0

BAY_W = spec.CAM_BOARD_W + 1.0
BAY_H = spec.CAM_BOARD_H + 1.4
BOARD_FACE_Z = BOX_FRONT_Z + p.POD_FACE_T + spec.CAM_FRONT_T + 0.6
# board sits ribbon-up: the lens is CAM_LENS_CY below the board's TOP edge,
# and the top edge sits 0.7 below the bay ceiling
LENS_CY = (SOLE_Y - 2.4 - 0.7) - spec.CAM_LENS_CY
PILOT_D = p.CAM_SCREW_PILOT + spec.HOLE_COMP


def build_pod() -> Part:
    # front camera box + slim tail ---------------------------------------
    box = Pos(0, SOLE_Y - BOX_H / 2, BOX_FRONT_Z + BOX_DEPTH / 2) * Box(
        p.POD_W, BOX_H, BOX_DEPTH
    )
    tail = Pos(0, SOLE_Y - TAIL_H / 2, (BOX_FRONT_Z + TAIL_END_Z) / 2) * Box(
        p.POD_W, TAIL_H, TAIL_END_Z - BOX_FRONT_Z
    )
    pod = box + tail

    # camera bay, open to the rear ---------------------------------------
    bay_cz = (BOX_FRONT_Z + p.POD_FACE_T + BOX_DEPTH + 2) / 2
    pod -= Pos(0, SOLE_Y - 2.4 - BAY_H / 2, bay_cz) * Box(
        BAY_W, BAY_H, BOX_DEPTH - p.POD_FACE_T + 2
    )

    # M2 bosses + pilots for the camera's 21 x 12.5 pattern --------------
    boss_len = BOARD_FACE_Z - (BOX_FRONT_Z + p.POD_FACE_T)
    for sx in (-1, 1):
        for sy in (-1, 1):
            hx = sx * spec.CAM_HOLES_X / 2
            hy = LENS_CY + sy * spec.CAM_HOLES_Y / 2
            pod += Pos(hx, hy, BOX_FRONT_Z + p.POD_FACE_T + boss_len / 2) * Cylinder(
                2.6, boss_len
            )
            pod -= Pos(hx, hy, BOARD_FACE_Z - 2.25) * Cylinder(PILOT_D / 2, 4.5)

    # lens aperture: cone + teardrop apex through the face ---------------
    half = math.radians(spec.CAM_FOV_DEG / 2 + p.POD_CONE_MARGIN)
    lens_z = BOARD_FACE_Z - spec.CAM_FRONT_T
    r_face = math.tan(half) * (lens_z - (BOX_FRONT_Z - 0.5)) + 2.0
    pod -= loft(
        [
            Pos(0, LENS_CY, lens_z) * Circle(2.0),
            Pos(0, LENS_CY, BOX_FRONT_Z - 0.5) * Circle(r_face),
        ]
    )
    pod -= loft(
        [
            Pos(0, LENS_CY + 1.2, lens_z) * Rectangle(2.4, 2.4),
            Pos(0, LENS_CY + r_face * 0.5, BOX_FRONT_Z - 0.5) * Rectangle(r_face * 0.9, r_face * 0.8),
        ]
    )

    # ribbon channel in the tail's top face ------------------------------
    ch_z0 = BOX_FRONT_Z + p.POD_FACE_T + 2
    pod -= Pos(0, SOLE_Y - CH_D / 2 + 0.01, (ch_z0 + TAIL_END_Z + 1) / 2) * Box(
        CH_W, CH_D, TAIL_END_Z + 1 - ch_z0
    )

    # J-hooks into the frame's bottom vent slots -------------------------
    # Tilt-in J-hooks: nose the pod down, slide the blades up the slots,
    # rotate flat - the forward horns land over the wall's inner face and
    # the pod's forward centre of gravity presses them down (self-locking;
    # lift the nose to remove). Blades sit front-biased in the 5 mm slots.
    # Rear-biased in the slots: the shelf's internal chamfer toe reaches
    # z = 40 on the measured-width build, so the horns engage the wall's
    # inner face BEHIND it (z >= 40.3).
    wall_inner_y = -(p.CAV_H / 2)          # the face the horns grip
    blade_t = 2.4
    horn_len = 1.6
    tip_y = wall_inner_y + 2.0
    blade_cz = p.VENT_Z + (p.VENT_H - blade_t) / 2 - 0.2   # rear-biased
    for x in p.PRONG_XS:
        pod += Pos(x, (SOLE_Y + tip_y) / 2, blade_cz) * Box(
            p.PRONG_W, tip_y - SOLE_Y, blade_t
        )
        # horn forward of the blade, resting just above the wall inner face
        pod += Pos(x, wall_inner_y + 0.85, blade_cz - blade_t / 2 - horn_len / 2) * Box(
            p.PRONG_W, 1.2, horn_len
        )

    # cosmetics ----------------------------------------------------------
    front_edges = [
        e
        for e in pod.edges()
        if abs(e.center().Z - BOX_FRONT_Z) < 1e-6
        and math.hypot(e.center().X, e.center().Y - LENS_CY) > r_face + 1.0
    ]
    try:
        pod = chamfer(front_edges, p.POD_CHAMFER)
    except Exception:
        pass
    bottom_edges = [
        e for e in pod.edges() if abs(e.center().Y - (SOLE_Y - BOX_H)) < 1e-6
    ]
    try:
        pod = chamfer(bottom_edges, 1.2)
    except Exception:
        pass
    return pod


if __name__ == "__main__":
    part = build_pod()
    bb = part.bounding_box()
    s = bb.size
    print(f"pod bbox: {s.X:.2f} x {s.Y:.2f} x {s.Z:.2f}  vol {part.volume/1000:.1f} cm3")
    export_stl(part, "../stl/camera-pod.stl", tolerance=0.05, angular_tolerance=0.3)
    print("exported ../stl/camera-pod.stl")
