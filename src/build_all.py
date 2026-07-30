"""Build every part, export STL + 3MF, then run verification and renders.

    python3 build_all.py          # build + verify + render
    python3 build_all.py --fast   # build only
"""

import os
import subprocess
import sys

from build123d import Mesher, export_stl

import params  # noqa: F401  (fail fast on parameter errors)
from bezel import build_bezel
from cover import build_cover
from coupon import build_bezel_coupon, build_body_coupon
from display_mock import build_display
from frame import build_frame
from stand import build_stand

HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "..", "stl")


def export(part, name):
    os.makedirs(STL, exist_ok=True)
    stl_path = os.path.join(STL, f"{name}.stl")
    export_stl(part, stl_path, tolerance=0.05, angular_tolerance=0.3)
    m = Mesher()
    m.add_shape(part)
    m.write(os.path.join(STL, f"{name}.3mf"))
    print(f"exported {name}.stl / {name}.3mf")


def main():
    export(build_frame(), "frame")
    export(build_bezel(), "bezel")
    export(build_cover(), "cover")
    export(build_stand(), "stand")
    export(build_body_coupon(), "fit-coupon-body")
    export(build_bezel_coupon(), "fit-coupon-bezel")
    export(build_display(), "_display_reference")
    if "--fast" not in sys.argv:
        subprocess.run([sys.executable, os.path.join(HERE, "verify.py")], check=True)
        subprocess.run([sys.executable, os.path.join(HERE, "render.py")], check=True)


if __name__ == "__main__":
    main()
