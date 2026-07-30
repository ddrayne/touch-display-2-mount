# touch-display-2-mount

3D-printed mounts for the **Raspberry Pi Touch Display 2 – 10″ Portrait**
(with a Raspberry Pi 5 on its back): a three-part **gallery shadow-box wall
frame** (body + snap-on bezel + rear cover) that makes the display read as
framed art — ideal for dashboards, photo frames, and home-automation panels
— and a one-piece **desk stand**, plus two quick corner **fit coupons**.

Every dimension derives from the official product brief
(`docs/touch-display-2-10in-product-brief.pdf`, RP-010276-MM-1-10, July
2026), transcribed into `src/spec.py` — **with one measured correction: a
production unit is ~167 mm wide, not the drawing's 161.76** (the brief
itself warns its dimensions are approximate; height and active area check
out). If your unit differs, set `spec.UNIT_W` from calipers and rebuild.
The transcription was independently audited against the
drawing, and re-measured from the exported STLs by `src/verify.py` on every
build — including **assembly-path sweeps** that prove the display, bezel,
and cover can physically be installed and removed.

## Parts

**Slicing? Import the files in `print/`** — they are pre-rotated so the
correct face lands on the plate as imported (the `stl/` copies are in the
CAD's canonical coordinates for the verification harness and would import
three parts upside-down).

| File | What | Print orientation |
|---|---|---|
| `stl/frame.stl` | Wall-frame body, 174.2 × 254.53 × 45.8 mm | **Rear-face-down** (as exported) |
| `stl/bezel.stl` | Snap-on front bezel (the visible frame face) | Face-down (as exported) |
| `stl/cover.stl` | Posts-only vented rear cover | Rear-face-down |
| `stl/stand.stl` | Desk stand, 15° easel lean | Plate-face-down (as exported) |
| `stl/fit-coupon-body.stl` + `stl/fit-coupon-bezel.stl` | Corner fit gauges — **print these first** | As exported |
| `stl/_display_reference.stl` | Display solid for CAD reference — **do not print** | — |

3MF copies of each part sit alongside the STLs.

## How it works

The wall mount is **front-loading**. The body is an open-fronted shadow box
with an internal shelf ring; the display — with the Pi 5 already screwed to
its rear standoffs and protruding backward — drops in from the front and
its chassis rim rests on the shelf (the depth datum). The **bezel** then
slides over the body's recessed front band and clicks onto nine snap nubs
riding compliant tongues; foam pads on its back press the glass onto the
shelf. The lap seam between bezel skirt and body reads as a deliberate
1.5 mm shadow reveal around the frame.

The Pi + Active Cooler live in the deep, hidden cavity behind the shelf,
washed by seven hidden vent slots per side. The small **cover** enters
through the rear opening (passing under the keyhole tabs), lands on the
display's four M2.5 bobbin posts (121.8 × 160 mm pattern), and takes four
of the display's own supplied screws — it tidies the back, carries zip-tie
anchors, and lets the USB-C lead run to the bottom cable slot.

The rear edge carries a 6 mm shadow-wedge chamfer, so the hung frame
appears to float off the wall — and the side vents exhaust into that
hidden wedge while bottom-wall slots draw intake air, giving the Pi a
proper convection path. The frame hangs on **two wall screws 110 mm
apart** via keyhole tabs printed solidly into the rear face (print `docs/drilling-template.pdf` at 100 %
scale for the wall marks). The **desk stand** screws straight onto the same
four posts and leans the display 15° on curved easel cheeks, bottom edge
floating 14 mm above the desk, cable dropping through a notch in the tie
bar.

## Bill of materials

| Qty | Item | Used for |
|---|---|---|
| 4 | M2.5 screws — **the display's own supplied screws fit** | cover → display posts (or stand → posts) |
| 2 | 4 mm / #8 pan-head wall screws + plugs | hanging the frame |
| 8 | soft EVA foam pads, 2 mm thick, ~15 × 8 mm self-adhesive | bezel back, around the opening (compressed to ~1 mm) |
| 2–4 | small zip ties | cable dressing on the cover |
| 4 | stick-on rubber feet (optional) | stand feet |

No other fasteners: the bezel presses on — nine snap nubs ride compliant
tongues hidden in the body's front band, so it clicks home with fingertip
force and pulls off with a firm, even tug (start at the two finger reliefs
under the bottom edge). **Only ever remove the bezel with the frame on a
bench, face up — never on the wall** (with the bezel off, nothing retains
the display).

## Print settings (Bambu X1 / P1 / A1, 0.4 mm nozzle)

| | frame (body) | bezel (+ coupons) | cover | stand |
|---|---|---|---|---|
| Material | **PETG** | PETG (match body) | PETG | PLA or PETG |
| Layer / first | 0.20 / 0.20 | 0.20 / 0.20 | 0.20 / 0.20 | 0.20 / 0.25 |
| Walls | 4 | 4 | 3 | 4 |
| Infill | 15 % gyroid | 20 % | 25 % grid | 15 % gyroid |
| Supports | **OFF** | **OFF** | **OFF** | **OFF** |
| Brim / skirt / draft shield | **all OFF — mandatory** (254.5 mm part; paint-on brim ears in ±X only if wanted) | all OFF (same footprint) | off | off |
| Plate | textured PEI | **textured PEI** (this face is the visible front) | any | any |
| Special | disable X1 flow-calibration lines / check the A1 prime line in preview; place at bed centre manually; keep the seam OFF the snap nubs (paint it onto a corner) | elephant-foot comp ≤ 0.15; seam on a corner, off the recesses | 4 bottom layers (counterbore bridges); M2.5 heads sit ~0.4 mm proud of the shallow counterbores (hidden, harmless) | full fan above z ≈ 90 (thin prongs) |

- Everything is designed support-free **in the stated orientation**; the
  only down-facing features are deliberate short bridges (vent roofs, cable
  slot end, counterbore floors, liner-groove ceiling) verified by the
  overhang census in `verify.py`.
- Holes are pre-compensated +0.25 mm (community mounts for this display
  printed M2.5 holes undersized). Keyholes are Ø10 entry / 5 mm slot with
  lead-in chamfers.
- A matte filament hides layer sheen; the bezel's face picks up the plate
  texture, so a textured plate gives it a uniform powder-coat look.
- **Bambu Handy note:** Handy can't toggle brim/skirt on a raw STL — slice
  in Bambu Studio (or a MakerWorld draft) with the settings above, then
  send to the printer; Handy is fine for monitoring.

**Print the two fit coupons first** (~1.5 h) — and treat them as
measurement artifacts, not feel-tests: print them with the *identical*
material, profile, and plate you'll use for the real parts, caliper their
62 mm edges, and set the filament's shrinkage compensation from the
measured percentage before slicing the body and bezel (a coupon that feels
"snug but OK" can still bind over the full 254 mm). Then check the display
corner's slip fit, shelf seat, bezel lap and snap click. Too tight →
raise `spec.FIT_CLEAR` (display) or `params.LAP_CLEAR` (bezel); loose →
lower them; rebuild and re-print the coupons.

**Body and bezel must be printed in the same material, same profile, same
plate** — a PLA-on-PETG pairing can eat the entire 0.25 mm lap clearance
through differential shrinkage.

## Assembly (wall frame)

1. Stick the eight foam pads to the bezel's back face around the opening
   (over the bezel's solid border, outside the visible 2.5 mm reveal).
2. Screw the Pi 5 to the display's standoffs (supplied screws), connect the
   GPIO power lead and DSI ribbon.
3. Body face-up on the bench: lower the display in, glass up — chin (wider
   bezel) toward the cable slot — until the rim rests on the shelf.
4. Fit the cover through the rear opening onto the four posts; drive four
   supplied M2.5 screws. Zip-tie the USB-C lead to the anchors, out the
   bottom slot.
5. Press the bezel on until all nine nubs click.
6. Wall: print `docs/drilling-template.pdf` at 100 %, level it, drill/plug,
   leave the two screw heads ~4 mm proud, hang and slide down.

For the stand: same steps 2, then screw the stand plate onto the posts
(supplied screws) and route the cable through the tie-bar notch.

## Care notes

- The stand tolerates normal touch use; very firm jabs at the top edge can
  rock any 15° easel — use the wall mount for enthusiastic households.
- A right-angle USB-C plug keeps the cable exit tidy on both mounts
  (straight plugs also fit — 13 mm of window clearance each side).

## Rebuilding / customising

```bash
pip install build123d trimesh shapely networkx rtree scipy matplotlib
cd src
python3 build_all.py     # builds STL+3MF, verifies (75 checks), renders
```

`src/spec.py` is the display (don't touch unless the drawing changes);
`src/params.py` is the design — reveal, wall, depth, tilt, clearances, snap
engagement — edit freely and rebuild; verification catches anything
unprintable, un-assemblable, or spec-breaking.

## Verification

- `src/verify.py`: 75 mesh-measured checks — integrity, the 121.8 × 160
  pattern position *and* diameters, bezel opening vs active area, shelf and
  felt datums, keyhole geometry incl. slot direction, bed fit, per-part
  overhang census, boolean interference against a worst-case display solid
  (which is itself audited against the spec), and translation sweeps along
  every assembly path. Report: `docs/verification-report.json`.
- Three independent multi-agent review rounds audited the drawing
  transcription, the STLs, printability, and the design; round 1's findings
  (including an assembly-impossibility proof against the v1 architecture)
  drove the current front-loading design.
