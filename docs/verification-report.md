# Verification history (Touch Display 2 10-inch mount)

The machine-readable current status lives in `verification-report.json`
(written by `src/verify.py` on every build). This file records the
independent review rounds and what they changed.

## Round 0 — spec transcription audit (before any CAD)

An independent reader re-measured the product-brief drawing (p4) at 20x
zoom and audited `src/spec.py`. **Blocker found and fixed:** the side-view
depth callouts were mis-attributed — the "3" callout belongs to the bobbin
posts (tips at 11.6 mm), the "8.5" to the Pi standoffs (deepest plane,
16.05 nominal / 17.1 worst case, the drawing being internally inconsistent
by 1.05 mm). Also captured: the rear-view "R=5" is the Pi-standoff boss
radius (Ø10), the rear plate is not vertically centred (9.1 top / 9.496
bottom insets), the bobbin keep-out is ~10 × 18 rectangular, and the
chassis is inset from the glass perimeter at the rim.

## Round 1 — three independent reviews of the v1 build

- **Design review:** keyhole entry too small for screw heads; cover
  counterbores broke out of the part edge; proposed the mat bevel, arris,
  liner groove, shadow reveal, easel-arc stand, and top-vent deletion.
- **Printability review:** confirmed the keyhole blocker (only hole with no
  print compensation); keyhole tabs were corner-anchored bridge islands;
  M3×8 bottomed out in the rib pilots; rib ramps measured 54.1°.
- **Spec/assembly audit:** every static dimension measured correct to
  ±0.005 mm, **but a swept-path boolean proved the display could not be
  inserted past the cover-seat ribs and keyhole tabs at all** — the v1
  frame was un-assemblable, and the 51-check harness had no check that
  could catch it. The display reference solid's connector hump was also
  0.95 mm shallower than its stated worst-case bound.

## v2 response (current architecture)

Front-loading: internal shelf ring seats the display (depth datum
8.75 mm), snap-on bezel with lap-seam reveal and felt preload closes the
face, cover shrinks to a posts-only vented panel using the display's own
screws, keyhole tabs print solid on the bed (orientation flipped to
rear-face-down), keyholes enlarged to Ø10/5 with lead-ins, shelf rear
carries a ≤45° printable chamfer, display mock rebuilt fully worst-case,
and `verify.py` grew: mock self-audit, hole diameter assertions, keyhole
slot-direction check, felt/datum stack checks, and boolean translation
sweeps along every assembly path (display in/out the front, bezel on/off,
cover in/out the rear). 64/64 checks pass.

## Round 2 — three fresh adversarial reviews of v2

Recorded in the repository history alongside any fixes they produced; the
build shipped only after a clean round.
