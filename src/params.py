"""Design parameters for the Touch Display 2 10-inch mount parts.

Coordinate system (all parts except the stand's ground features): display
centre at XY origin, X right, Y up (portrait), Z=0 at the nominal FRONT
surface of the lens glass, +Z pointing BEHIND the display. The display body
occupies z ~0.15..8.75 at its rim when seated (see SHELF_FRONT_Z) and its
deepest features (Pi standoffs) reach z 16.2..17.25.

ARCHITECTURE (v2, after the round-1 insertion audit): the wall mount is
FRONT-LOADING. The body is an open-fronted shadow box with an internal
shelf ring; the display (with Pi attached) drops in from the front and its
chassis rim rests on the shelf. A slim bezel then snaps over the body's
recessed front band — the lap seam doubles as the frame's shadow reveal —
holding the glass against felt. The rear stays permanently featured
(keyhole tabs, vents, cable slot) because nothing is ever inserted from
the rear except the small posts-only cover, which passes below the tabs.

Everything here is a design choice layered on top of src/spec.py (the
transcribed drawing). Change values here, re-run build_all.py, and the
verification suite still has to pass.
"""

import spec

# ------------------------------------------------------------ shared shell
WALL = 3.3                          # body wall thickness (full section)
CAV_W = spec.UNIT_W + 2 * spec.FIT_CLEAR          # 162.36
CAV_H = spec.UNIT_H + 2 * spec.FIT_CLEAR          # 247.926
CAV_R = spec.UNIT_CORNER_R + spec.FIT_CLEAR       # 5.3
OUT_W = CAV_W + 2 * WALL                          # 168.96
OUT_H = CAV_H + 2 * WALL                          # 254.526
OUT_R = CAV_R + WALL                              # 8.6

# ------------------------------------------------------------------ shelf
# The display's chassis rim (rear face at spec.EDGE_T = 8.6 nominal) rests
# on this ring; the shelf sets the display's depth datum.
SHELF_FRONT_Z = spec.EDGE_T + 0.15  # 8.75 (0.15 nominal float, felt absorbs)
SHELF_T = 6.0                       # shelf ring thickness (z)
SHELF_OPEN_W = 135.0                # clears bobbins (±65.9); ~4.2 mm seat
                                    # strip on the display's rear plate
SHELF_OPEN_H = 220.0                # clears bobbins (±89); ~4.4 mm seat strip
SHELF_OPEN_R = 8.0
GLASS_Z = SHELF_FRONT_Z - spec.EDGE_T             # 0.15 nominal glass plane

# ------------------------------------------------------------------ bezel
# Face plate + outer skirt lapping over the body's recessed front band.
BEZEL_FACE_T = 3.0
BEZEL_PAD_GAP = 1.0                 # plate back to glass: 2 mm soft EVA foam
                                    # pads compressed ~50%, tolerant of the
                                    # drawing's +/-0.5 depth uncertainty
BEZEL_FRONT_Z = GLASS_Z - BEZEL_PAD_GAP - BEZEL_FACE_T    # -3.85
BEZEL_BACK_Z = BEZEL_FRONT_Z + BEZEL_FACE_T               # -0.4
SKIRT_T = 1.6
SKIRT_DEPTH = 6.3                   # skirt beyond the plate back: covers the
                                    # tongue slits (top 5.35) with margin and
                                    # makes the seam reveal a true 1.5 mm
LAP_CLEAR = 0.25                    # per side, skirt over body band
LIP_MARGIN = 2.5                    # bezel opening beyond the active area
LIP_OPEN_W = spec.ACTIVE_W + 2 * LIP_MARGIN       # 140.36
LIP_OPEN_H = spec.ACTIVE_H + 2 * LIP_MARGIN       # 221.576
LIP_OPEN_R = 3.0
LIP_OPEN_CY = spec.ACTIVE_CY_OFFSET               # active area sits high
FRONT_CHAMFER = 2.25                # bezel outer face arris
MAT_BEVEL = 2.0                     # 45 deg bevel on the opening (mat cue)
LINER_GROOVE_W = 1.5                # face shadow-gap "liner" ring
LINER_GROOVE_D = 0.6
LINER_GROOVE_INSET = 3.75           # from the outer edge to groove outer wall

# body front band that the skirt laps over
BAND_TOP_Z = BEZEL_BACK_Z + 0.3                    # -0.55: 0.3 stop gap so the
                                                   # snap, not the rim, sets depth
BAND_DEPTH = SKIRT_DEPTH + 1.2                     # 7.5: with the 0.3 stop gap
                                                   # this yields a TRUE 1.5 mm
                                                   # seam reveal (band end 6.95,
                                                   # skirt end 5.45)
BAND_OUT_W = OUT_W - 2 * (SKIRT_T + LAP_CLEAR)     # 165.26
BAND_OUT_H = OUT_H - 2 * (SKIRT_T + LAP_CLEAR)     # 250.826
BAND_OUT_R = OUT_R - (SKIRT_T + LAP_CLEAR)         # 6.75
BAND_CHAMFER_RUN = 2.25                            # band -> full outline, 45ish

# snap interface: each nub rides a compliant cantilever tongue cut into the
# (hidden) body band, so the rigid skirt never has to stretch. Tongue: ~18
# long x 5.15 tall x 1.45 thick, root on one side, ~2 N deflection force.
# The nub's rear face is steep (60 deg) and the skirt recess's rear wall
# lands on it with zero float, so the snap - not the foam - sets the bezel's
# axial position.
NUB_PROUD = 0.8
NUB_LEN = 8.0
NUB_Z0, NUB_Z1 = 1.5, 4.0          # nub z extent on the tongue
NUB_LEAD_RUN = 1.3                 # front 45-deg lead-in for pressing on
NUB_HOLD_RUN = 1.0                 # rear ~54-deg retention face (printable
                                   # without support, firm against pull-off)
NUB_SIDE_YS = [-70.0, 0.0, 70.0]   # three per side wall
NUB_TOP_XS = [0.0]
NUB_BOT_XS = [-30.0, 30.0]         # symmetric, clear of the cable slot
TONGUE_LEN = 18.0                  # free length from root to tip
TONGUE_SLIT_W = 2.0
TONGUE_TOP_Z = 4.6                 # horizontal slit 4.6..5.35, hidden under
TONGUE_SLIT_TOP = 5.35             # the skirt (which covers to z 5.45 with
                                   # SKIRT_DEPTH 6.3: -0.85 + 6.3 = 5.45)
NUB_TIP_OFFSET = 5.0               # nub centre sits this far from the tip
RECESS_Z0 = NUB_Z0 + 0.55          # front wall clears the lead-in
# The rear wall must land ON the 54-deg retention face where that face
# crosses the skirt-inner radius (crest ends at NUB_Z1 - NUB_HOLD_RUN, the
# face then retreats ~1.4 mm radially per mm of rise; it crosses the
# 0.55-proud skirt-inner surface ~0.39 later). 3.40 puts the wall a hair
# up the ramp: the tongues sit ~0.15 pre-deflected at seat, so the bezel
# has ZERO free forward float (round-3 audit: the +0.05 version left
# 0.66 mm of dead-band and defeated the foam preload).
RECESS_Z1 = 3.40
RECESS_EXTRA = 0.6                 # recess length beyond the nub, each side
RECESS_DEPTH = 0.9
# finger reliefs under the bottom skirt edge for removal grip
RELIEF_XS = [-55.0, 55.0]
RELIEF_W = 18.0
RELIEF_D = 1.2

# ----------------------------------------------------------- body depth
# Swallows the display (17.25 worst incl. shelf float), the cover, and a
# Pi 5 with the official Active Cooler.
FRAME_REAR_Z = spec.UNIT_DEPTH_WORST + 0.15 + spec.PI_ASSY_DEPTH + 2.0  # 45.25
REAR_CHAMFER_FLANK = 6.0            # rear shadow-wedge: 6 up the flank...
REAR_CHAMFER_REAR = 1.5             # ...by 1.5 across the rear face, so the
                                    # frame floats off the wall and the vents
                                    # exhaust into the hidden wedge

# ------------------------------------------------------ wall-hang keyholes
# Two tabs in the top rear corners, printed solid on the bed. The frame
# hangs on two screws 110 mm apart; slots run upward so the frame drops on.
KEYHOLE_TAB_T = 4.0
KEYHOLE_TAB_Z = FRAME_REAR_Z - KEYHOLE_TAB_T      # 41.25
KEYHOLE_X = 55.0
KEYHOLE_ENTRY_Y = 103.0
KEYHOLE_ENTRY_D = 10.0             # No.8 / 4 mm screw head passes, printed
KEYHOLE_SLOT_W = 5.0
KEYHOLE_SLOT_LEN = 10.0
KEYHOLE_TAB_W = 52.0               # tab extent from cavity corner, X
KEYHOLE_TAB_H = 30.0               # tab extent, Y

# ------------------------------------------------------------- cable slot
CABLE_SLOT_W = 14.0
CABLE_SLOT_FRONT_Z = 32.0          # slot reaches this far forward from rear

# ------------------------------------------------------------- wall vents
VENT_L = 20.0
VENT_H = 5.0
VENT_Z = 42.0                      # slots open into the rear shadow-wedge
VENT_PITCH = 30.0
VENT_COUNT_SIDE = 6                # rows at y +/-15/45/75: the old 7th row
                                   # at +/-90 was one-third blocked by the
                                   # keyhole tabs
VENT_COUNT_TOP = 0                 # top vents deleted: dust chutes
VENT_BOT_XS = [-52.0, -30.0, 30.0, 52.0]   # bottom-wall intake slots

# ------------------------------------------------------------------ cover
# Posts-only vented panel: enters from the rear (passing below the keyhole
# tabs), lands flat on the four bobbin-post tips, four M2.5 screws. Prints
# rear-face-down.
COVER_T = 3.0
COVER_FRONT_Z = spec.POST_TIP_Z                    # 11.6, on the post tips
COVER_W = 131.0                    # inside the shelf opening, 2/side clear
COVER_H = 183.0
COVER_R = 5.0
POST_HOLE_D = spec.M2_5_CLEAR_D + spec.HOLE_COMP   # 3.15
POST_CBORE_D = 5.6                                 # M2.5 pan head + comp
POST_CBORE_DEPTH = 1.6
# Pi window: the Pi 5 + cooler pass through; the display's connector hump
# (worst case as deep as the standoffs) and the USB-C plug (12 mm budget
# from the board edge at x ±28) stay in free air.
PI_WIN_W = 82.0
PI_WIN_TOP_Y = 50.0
PI_WIN_BOT_Y = -65.0
PI_WIN_R = 4.0
COVER_VENT_W = 4.0
COVER_VENT_L = 20.0
ZIP_SLOT_PAIRS = [-78.0, -86.0]    # y centres; slots at x = +/-8
ZIP_SLOT_X = 8.0
ZIP_SLOT_W = 2.8
ZIP_SLOT_L = 5.0

# ------------------------------------------------------------------ stand
# Modelled in display coordinates (plate face-down = print orientation); the
# ground plane is tilted STAND_TILT_DEG relative to the plate.
STAND_TILT_DEG = 15.0
STAND_PLATE_W = 150.0
STAND_PLATE_H = 180.0              # spans display y -90 .. +90
STAND_PLATE_T = 4.0
STAND_PLATE_R = 8.0
STAND_CHEEK_T = 8.0
STAND_CHEEK_OUT_X = 75.0           # cheek outer face flush with plate edge
STAND_REAR_REACH = 140.0           # rear foot, behind the glass plane; the
                                   # foot fillet + ground trim pull the real
                                   # contact ~11 mm forward, and tip-back
                                   # margin at the top edge needs the reach
STAND_GROUND_LIFT = 14.0           # display bottom edge floats this high
STAND_CHEEK_TOP_Y = 55.0           # cheek meets plate up to this display y
STAND_PLATE_FRONT_Z = spec.POST_TIP_Z            # 11.6, flat on the posts
STAND_CHEEK_EMBED_ZD = 13.5        # cheek weld line sunk into the plate
STAND_ARC_SAGITTA = 26.0           # concave "easel" curve on the hypotenuse
STAND_FOOT_FILLET = 4.0            # rear foot corner radius (a big fillet
                                   # pulls the ground-contact tangent forward
                                   # and costs tip-back margin)
STAND_EDGE_CHAMFER = 2.0           # cheek side-edge chamfers
STAND_TIE_TOP_ZD = 20.0            # cross-tie bar behind the display bottom
STAND_TIE_CABLE_W = 16.0           # cable notch in the tie bar
STAND_RIB_W = 4.0                  # plate stiffening ribs beside the window
STAND_RIB_H = 6.0
STAND_RIB_X = 47.0                 # outboard of the 82 mm window
STAND_WIN_TOP_Y = 50.0
STAND_WIN_BOT_Y = -65.0

# ---------------------------------------------------------------- coupon
COUPON_SIZE = 62.0                 # corner test-fit gauge extent


# ------------------------------------------------------------- camera pod
# Chin-mounted pod for a Camera Module 3 (viewer-facing presence camera).
# Two snap prongs grip the frame's inner pair of bottom intake vent slots
# (at x = +/-30, 20 x 5 through the 3.3 wall) - no frame changes needed.
# The pod face tilts POD_TILT_DEG upward; the mini ribbon exits the pod's
# top and runs through the frame's existing cable slot to the Pi.
POD_TILT_DEG = 10.0
POD_W = 76.0                       # spans both prongs with clean margins
POD_H = 32.0                       # face height (covers board + ribbon bend)
POD_FACE_T = 2.4
POD_WALL = 2.4
POD_DEPTH = 15.0                   # face to back, before the tilt wedge
POD_R = 5.3                        # matches the frame's cavity corner radius
POD_CHAMFER = 2.25                 # same arris as the bezel
POD_APERTURE_D = 10.0              # lens window in the face
POD_CONE_MARGIN = 8.0              # aperture cone half-angle beyond FoV/2
PRONG_XS = [-30.0, 30.0]           # the frame's inner bottom vent slots
PRONG_W = 15.0                     # inside the slot's straight section
                                   # (20 long with R2.4 corner rounding)
PRONG_T = 3.6                      # slot is 5 tall
PRONG_REACH = 9.0                  # through the 3.3 wall + nose inside
PRONG_NOSE = 1.0                   # snap engagement past the wall
CAM_SCREW_PILOT = 1.75             # M2 self-tap pilot (+comp applied in CAD)
POD_LID_T = 2.0
POD_LID_CLEAR = 0.2
