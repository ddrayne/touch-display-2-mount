"""Part A2: posts-only vented cover (prints rear-face-down).

A small panel that enters through the frame's rear opening (passing below
the keyhole tabs), lands flat on the display's four bobbin-post tips, and
takes the four supplied M2.5 screws. It tidies the back of the display,
carries the vent field and the zip-tie cable anchors; the Pi 5 + Active
Cooler pass through its window into the frame cavity. Structurally the
display hangs on the shelf/bezel - the cover carries only itself.
"""

from build123d import *

import spec
import params as p

POSTS = [
    (sx * spec.POST_SPACING_X / 2, sy * spec.POST_SPACING_Y / 2)
    for sx in (-1, 1)
    for sy in (-1, 1)
]


def _stadium(w: float, l: float) -> Sketch:
    return RectangleRounded(w, l, w / 2 - 0.01)


def build_cover() -> Part:
    plate = Pos(0, 0, p.COVER_FRONT_Z) * extrude(
        RectangleRounded(p.COVER_W, p.COVER_H, p.COVER_R), amount=p.COVER_T
    )

    # Pi window ---------------------------------------------------------
    win_h = p.PI_WIN_TOP_Y - p.PI_WIN_BOT_Y
    win_cy = (p.PI_WIN_TOP_Y + p.PI_WIN_BOT_Y) / 2
    plate -= Pos(0, win_cy, p.COVER_FRONT_Z - 0.5) * extrude(
        RectangleRounded(p.PI_WIN_W, win_h, p.PI_WIN_R), amount=p.COVER_T + 1
    )

    # M2.5 post holes, counterbored from the rear ------------------------
    for x, y in POSTS:
        plate -= Pos(x, y, p.COVER_FRONT_Z - 0.5) * extrude(
            Circle(p.POST_HOLE_D / 2), amount=p.COVER_T + 1
        )
        plate -= Pos(
            x, y, p.COVER_FRONT_Z + p.COVER_T - p.POST_CBORE_DEPTH
        ) * extrude(Circle(p.POST_CBORE_D / 2), amount=p.POST_CBORE_DEPTH + 0.5)

    # vent slats --------------------------------------------------------
    def clear_of_posts(x: float, y: float, half_len: float) -> bool:
        return all(
            abs(x - px) > p.POST_CBORE_D / 2 + p.COVER_VENT_W / 2 + 2.5
            or abs(y - py) > half_len + p.POST_CBORE_D / 2 + 2.5
            for px, py in POSTS
        )

    slat = extrude(
        Pos(0, 0, p.COVER_FRONT_Z - 0.5) * _stadium(p.COVER_VENT_W, p.COVER_VENT_L),
        amount=p.COVER_T + 1,
    )
    cols_x = [-58, -49, 49, 58]
    rows_y = [-78, -52, -26, 0, 26, 52, 78]
    for x in cols_x:
        for y in rows_y:
            if clear_of_posts(x, y, p.COVER_VENT_L / 2):
                plate -= Pos(x, y, 0) * slat
    # field above the Pi window (the zip-anchor zone below stays solid)
    for x in [-30, -20, -10, 0, 10, 20, 30]:
        plate -= Pos(x, 60, p.COVER_FRONT_Z - 0.5) * extrude(
            _stadium(p.COVER_VENT_W, 14), amount=p.COVER_T + 1
        )

    # zip-tie anchor slots ------------------------------------------------
    for y in p.ZIP_SLOT_PAIRS:
        for sx in (-1, 1):
            plate -= Pos(sx * p.ZIP_SLOT_X, y, p.COVER_FRONT_Z - 0.5) * extrude(
                RectangleRounded(p.ZIP_SLOT_W, p.ZIP_SLOT_L, 1.2),
                amount=p.COVER_T + 1,
            )

    # elephant-foot chamfer on the bed-side (rear) edges -----------------
    back_z = p.COVER_FRONT_Z + p.COVER_T
    back_edges = [e for e in plate.edges() if abs(e.center().Z - back_z) < 1e-6]
    plate = chamfer(back_edges, spec.ELEPHANT_CHAMFER)
    return plate


if __name__ == "__main__":
    part = build_cover()
    bb = part.bounding_box()
    s = bb.size
    print(f"cover bbox: {s.X:.2f} x {s.Y:.2f} x {s.Z:.2f}  vol {part.volume/1000:.1f} cm3")
    assert abs(bb.min.Z - spec.POST_TIP_Z) < 0.01
    export_stl(part, "../stl/cover.stl", tolerance=0.05, angular_tolerance=0.3)
    print("exported ../stl/cover.stl")
