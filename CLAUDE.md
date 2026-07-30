# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Parametric CAD (build123d) for 3D-printed mounts for the Raspberry Pi Touch Display 2 (10″ portrait) with a Pi 5 on its back: a front-loading shadow-box wall frame (body + snap-on bezel + rear cover), a desk stand, and two corner fit coupons. The STL/3MF files, renders, and verification report in the repo are build artifacts of `src/`.

## Commands

```bash
pip install build123d trimesh shapely networkx rtree scipy matplotlib

cd src
python build_all.py          # build all parts -> ../stl/, then verify + render
python build_all.py --fast   # build/export only, skip verify + render
python verify.py             # re-run verification against existing ../stl/ files
python render.py             # re-render ../renders/ PNGs from existing STLs
```

There are no tests other than `verify.py` — it is the test suite: 75 mesh-measured checks (watertightness, hole positions/diameters, datum planes, bed fit, per-part overhang census, boolean interference against a worst-case display solid, and translation sweeps along every assembly path). Exit code 0 = pass; report written to `docs/verification-report.json`. Any geometry change must end with a passing `build_all.py` run.

## Architecture

Data flows one way: `spec.py` → `params.py` → part builders → `build_all.py` → `verify.py`/`render.py`.

- `src/spec.py` — the display itself: dimensions transcribed from the official product brief, each value annotated with its drawing source (or DERIVED/ASSUMED), plus one measured correction (`UNIT_W = 167.0`, the drawing's 161.76 is wrong for real hardware). Do not edit unless the drawing changes or a unit is re-measured.
- `src/params.py` — the design: wall thicknesses, clearances, bezel reveal, snap engagement, stand tilt, etc., all derived from `spec` values. This is the file to edit for customization; `verify.py` must still pass afterwards.
- Part builders (`frame.py`, `bezel.py`, `cover.py`, `stand.py`, `coupon.py`, `display_mock.py`) — each exposes a `build_*()` returning a build123d solid. `display_mock.py` builds the worst-case display reference solid used by the interference/assembly checks (exported as `_display_reference` — not printable).
- Shared coordinate system (all parts except the stand's ground features): display centre at XY origin, X right, Y up (portrait), Z=0 at the front of the lens glass, +Z pointing behind the display. Verification measures the exported meshes in these coordinates.

## Gotchas

- `stl/` is exported in canonical CAD coordinates for the verification harness; `print/` holds pre-rotated copies for slicing. **No script generates `print/`** — after a rebuild, the affected `print/` STLs must be re-derived (rotated so the correct face lands on the plate, per the README's orientation table) or they go stale.
- Verification measures STL files on disk, not in-memory solids — always export (via `build_all.py`) before `verify.py`.
- The frame body is 254.5 mm on a 255 mm bed limit (`spec.BED_LIMIT`); README print settings (no brim/skirt/draft shield) exist to protect that margin.
- The README references `docs/touch-display-2-10in-product-brief.pdf`, which is not committed; `spec.py`'s docstrings are the authoritative transcription of it.
