"""Verified mechanical specification: Raspberry Pi Touch Display 2 - 10" Portrait.

Every value here is transcribed from the official product brief
(docs/touch-display-2-10in-product-brief.pdf, RP-010276-MM-1-10, July 2026),
page 4 "Physical specification" mechanical drawing, unless marked DERIVED or
ASSUMED. Axes: portrait, as seen from the FRONT. Origin used by the CAD
models: display centre, X right, Y up, Z=0 at the front of the lens glass
with +Z pointing BEHIND the display.

Independently audited against the drawing by a second reader (see
docs/verification-report.md): the side-view depth callouts are attributed as
follows. 1.1 = lens glass; 7.5 = chassis behind the lens (rear face at 8.6);
3 = bobbin-post protrusion beyond the chassis (tips at 11.6); 8.5 =
Pi-standoff protrusion beyond the chassis. The drawing is internally
inconsistent about the deepest plane (8.6 + 8.5 = 17.1 vs the overall 16.05
callout; the drawn geometry supports 16.05), so mounts treat standoff-tip
depth as 16.05 nominal / 17.1 worst case.

Drawing note reproduced from the PDF: "All dimensions are approximate and for
reference purposes only ... subject to part and manufacturing tolerances."
Fit-critical interfaces therefore get printed clearances plus a test-fit
coupon part.
"""

# ---------------------------------------------------------------- unit body
# MEASURED CORRECTION (2026-07-26): a production unit measures ~167 x 247 mm.
# The drawing's 161.76 width is wrong for real hardware (its own note says
# dimensions are approximate and not for production data); the height and
# active area check out. Width is therefore set from the measured unit; the
# side bezels derive to ~15.8 instead of the drawn 13.2.
UNIT_W = 167.0             # MEASURED (drawing said 161.76)
UNIT_H = 247.326           # p4 front view, overall height
UNIT_CORNER_R = 5.0        # p4 front view "R=5" leader to the unit corner
LENS_T = 1.1               # p4 side view "1.1 lens" - cover glass thickness
BODY_T = 7.5               # p4 side view - chassis behind lens
EDGE_T = LENS_T + BODY_T   # DERIVED = 8.6: chassis rear face depth.
                           # CAUTION: the chassis outline is inset from the
                           # glass perimeter (~3 mm at the top edge, ~9 mm at
                           # the bottom, uncalloutted); at the extreme rim
                           # only the 1.1 mm glass is present.
POST_PROTRUSION = 3.0      # p4 side view "3": bobbin posts beyond chassis
POST_TIP_Z = EDGE_T + POST_PROTRUSION        # DERIVED = 11.6 datum plane
PI_STANDOFF_PROTRUSION = 8.5   # p4 side view "8.5": Pi standoffs beyond
                               # chassis (implies 17.1 deepest, see below)
UNIT_DEPTH = 16.05         # p4 side view: glass front -> Pi standoff tips,
                           # the unit's deepest feature (nominal)
UNIT_DEPTH_WORST = EDGE_T + PI_STANDOFF_PROTRUSION   # DERIVED = 17.1

# ------------------------------------------------------------- front bezels
ACTIVE_W = 135.36          # p4 front view, active area width
ACTIVE_H = 216.576         # p4 front view, active area height
BEZEL_TOP = 13.0           # p4 front: top edge -> active area
BEZEL_SIDE = (UNIT_W - ACTIVE_W) / 2   # DERIVED = 15.82 on the measured
                           # unit (drawing showed 13.2); active area assumed
                           # centred, as drawn
BEZEL_BOTTOM = UNIT_H - BEZEL_TOP - ACTIVE_H   # DERIVED = 17.75 (chin)
# Active-area centre offset from unit centre (positive = active sits higher):
ACTIVE_CY_OFFSET = (BEZEL_BOTTOM - BEZEL_TOP) / 2.0   # DERIVED = +2.375 up
LENS_OPEN_W = 136.36       # p4 front, dashed module opening (12.7 from right)
LENS_OPEN_H = 217.576      # p4 front, dashed module opening (12.5 from top)

# ----------------------------------------------- rear enclosure mount posts
# Four M2.5-threaded bobbin posts; their tips define the POST_TIP_Z = 11.6
# plane (NOT the 16.05 plane - that belongs to the Pi standoffs).
POST_SPACING_X = 121.8     # p4 rear view, centre-to-centre horizontal
POST_SPACING_Y = 160.0     # p4 rear view, centre-to-centre vertical
# Right post centre is 10.78 from the rear-plate edge which is 9.2 from the
# unit edge -> 19.98 from unit edge; 121.8 + 2*19.98 = 161.76 = UNIT_W, so the
# pattern is exactly centred horizontally.
# Top row: 9.1 (plate inset) + 34.56 = 43.660 below the top edge; the bottom
# row derives to 43.666 above the bottom edge -> centred to within 0.01.
POST_PATTERN_CENTERED = True   # DERIVED, verified both axes
POST_EDGE_OFFSET_X = (UNIT_W - POST_SPACING_X) / 2   # DERIVED = 22.6 on the
                               # measured unit; the 121.8 spacing itself is
                               # trusted (it cross-checked exactly against
                               # the rear-plate offsets in the drawing)
POST_EDGE_OFFSET_Y = 43.663    # DERIVED: unit edge -> post centre (mean of
                               # 43.660 top / 43.666 bottom)
POST_THREAD = "M2.5"           # product brief: eight M2.5 screws included
POST_BOBBIN_W = 9.3            # ASSUMED from drawing scale: spool width
POST_BOBBIN_H = 17.6           # ASSUMED from drawing scale: spool height
                               # (keep-out is ~10 x 18 rectangular, not round)

# --------------------------------------------------------- rear cover plate
REAR_PLATE_W = 143.36      # p4 rear view
REAR_PLATE_H = 228.73      # p4 rear view
REAR_PLATE_INSET_SIDE = 9.2       # p4 rear view (both sides, centred)
REAR_PLATE_INSET_TOP = 9.1        # p4 rear view
REAR_PLATE_INSET_BOTTOM = UNIT_H - REAR_PLATE_INSET_TOP - REAR_PLATE_H
                                  # DERIVED = 9.496: NOT vertically centred
REAR_PLATE_NOTCH = 2.5            # p4 rear view, bottom-right corner step

# ------------------------------------------------- Raspberry Pi mount bosses
# Standard Raspberry Pi 58 x 49 hole pattern on tall standoffs; the standoff
# tips are the unit's deepest feature (UNIT_DEPTH / UNIT_DEPTH_WORST above).
PI_HOLES_X = 49.0          # p4 rear view (horizontal, portrait frame)
PI_HOLES_Y = 58.0          # p4 rear view (vertical)
PI_STANDOFF_BOSS_D = 10.0  # p4 rear view "R=5" leaders point at the standoff
                           # boss outer circle (it is not a corner radius)
# Locations, measured from the drawing (from behind): top standoff row is
# 90.06 below the rear-plate top line -> 9.1 + 90.06 = 99.16 below unit top;
# right column 47.16 from rear-plate right line -> 9.2 + 47.16 = 56.36 from
# the unit edge. Columns straddle the centreline symmetrically to within
# 0.02 (56.36 right vs 56.40 left).
PI_ROW_TOP_FROM_TOP = 99.16      # DERIVED: unit top edge -> upper hole row
PI_ROW_BOT_FROM_TOP = 157.16     # DERIVED
PI_PATTERN_CX_OFFSET = 0.0       # DERIVED: centred horizontally (0.02 slop)

# ------------------------------------------------------------ Pi 5 envelope
# Raspberry Pi 5: 85 x 56 board, holes 3.5 from edges (58 x 49 pattern), the
# USB/Ethernet end overhangs its hole row by 23.5. Orientation on the display
# (from the p2 photo): board long axis vertical. The mounts keep a clearance
# envelope generous enough for either vertical orientation, plus the official
# Active Cooler and cable dressing.
PI_BOARD_L = 85.0
PI_BOARD_W = 56.0
PI_HOLE_EDGE = 3.5
PI_PORT_OVERHANG = 23.5          # board beyond hole row at the USB/Eth end
PI_ASSY_DEPTH = 26.0             # ASSUMED: board 1.4 + Active Cooler ~22 +
                                 # margin, measured behind the standoff tips

# ------------------------------------------------------------------ cabling
# Display is powered from the Pi GPIO (supplied cable) and driven over a
# 22-way mini-mini DSI ribbon (supplied). Both display-side connectors live
# on the raised central connector hump (approx |x| < 35, -63 < y < +47,
# measured from the drawing; no taller than the Pi standoffs). The Pi 5 needs
# its own USB-C 27 W lead routed out of the mount.
HUMP_HALF_W = 35.0               # ASSUMED from drawing scale
HUMP_Y_MIN = -63.0               # ASSUMED from drawing scale
HUMP_Y_MAX = 47.0                # ASSUMED from drawing scale
USB_C_PLUG_CLEARANCE = 12.0      # ASSUMED: straight plug body + bend start

# --------------------------------------------------------------- fasteners
M2_5_CLEAR_D = 2.9         # close clearance hole for M2.5
M2_5_HEAD_D = 4.7          # pan/flat head max
M3_SELFTAP_PILOT_D = 2.6   # self-tap pilot in printed boss
M3_CLEAR_D = 3.4
M3_HEAD_D = 6.0

# ------------------------------------------------- FDM printing compensation
HOLE_COMP = 0.25           # add to vertical-axis hole diameters
FIT_CLEAR = 0.30           # per-side clearance, display body in frame pocket
PART_CLEAR = 0.25          # per-side clearance, printed part in printed pocket
ELEPHANT_CHAMFER = 0.5     # chamfer on bed-contact edges
MIN_WALL = 2.4
BED_LIMIT = 255.0          # Bambu X1/P1/A1 print 256 mm; print the frame with
                           # no brim/skirt (or a draft-shield-free profile)
