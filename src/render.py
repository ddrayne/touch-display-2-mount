"""Render review images of the STLs (matplotlib, no GPU needed).

Outputs multi-view PNGs per part plus assembly views into ../renders/.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
import params as p
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "..", "stl")
OUT = os.path.join(HERE, "..", "renders")
os.makedirs(OUT, exist_ok=True)

LIGHT = np.array([0.45, 0.35, 0.82])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def draw(ax, mesh, base_rgb, alpha=1.0):
    tris = mesh.triangles
    normals = mesh.face_normals
    shade = 0.45 + 0.55 * np.clip(normals @ LIGHT, 0, 1)
    order = np.argsort(tris[:, :, 2].mean(axis=1))
    cols = np.clip(np.outer(shade, base_rgb), 0, 1)[order]
    pc = Poly3DCollection(tris[order], facecolors=cols, edgecolor="none", alpha=alpha)
    ax.add_collection3d(pc)


def scene(meshes, path, elev=22, azim=-55, title=""):
    fig = plt.figure(figsize=(9, 9), dpi=130)
    ax = fig.add_subplot(projection="3d")
    allpts = np.vstack([m.vertices for m, _, _ in meshes])
    lo, hi = allpts.min(axis=0), allpts.max(axis=0)
    c = (lo + hi) / 2
    r = (hi - lo).max() / 2 * 1.05
    for m, rgb, alpha in meshes:
        draw(ax, m, np.array(rgb), alpha)
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def load(name):
    return trimesh.load(os.path.join(STL, name), force="mesh")


def main():
    frame = load("frame.stl")
    bezel = load("bezel.stl")
    cover = load("cover.stl")
    stand = load("stand.stl")
    coupon = load("fit-coupon-body.stl")
    coupon_b = load("fit-coupon-bezel.stl")
    display = load("_display_reference.stl")

    plastic = (0.30, 0.31, 0.34)     # charcoal PLA/PETG (lifted for legibility)
    plastic2 = (0.38, 0.40, 0.44)
    glass = (0.35, 0.55, 0.75)

    # individual parts
    bf = bezel.copy()
    bf.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0]))
    scene([(bf, plastic, 1.0)], f"{OUT}/bezel-front.png", elev=18, azim=-60,
          title="Bezel - front face (arris, liner groove, mat bevel)")
    scene([(bezel, plastic, 1.0)], f"{OUT}/bezel-back.png", elev=30, azim=-120,
          title="Bezel - back (skirt + snap recesses)")
    ff = frame.copy()
    ff.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0]))
    scene([(ff, plastic, 1.0)], f"{OUT}/body-front.png", elev=18, azim=-60,
          title="Body - front (band, nubs, shelf)")
    scene([(frame, plastic, 1.0)], f"{OUT}/body-back.png", elev=25, azim=-120,
          title="Body - back (keyhole tabs, cable slot, vents)")
    scene([(cover, plastic2, 1.0)], f"{OUT}/cover-back.png", elev=30, azim=-60,
          title="Cover - rear face (vents, window, zip anchors)")
    scene([(stand, plastic, 1.0)], f"{OUT}/stand-iso.png", elev=20, azim=-50,
          title="Desk stand")
    scene([(coupon, plastic2, 1.0), ], f"{OUT}/fit-coupon-body.png", elev=35, azim=-45,
          title="Body corner fit coupon")
    scene([(coupon_b, plastic2, 1.0)], f"{OUT}/fit-coupon-bezel.png", elev=35, azim=-45,
          title="Bezel corner fit coupon")

    # assemblies, rotated into world orientation (screen up = image up)
    def upright(mesh, tilt_deg=0.0):
        m = mesh.copy()
        m.apply_transform(
            trimesh.transformations.rotation_matrix(
                np.radians(90 + tilt_deg), [1, 0, 0]
            )
        )
        return m

    scene(
        [
            (upright(frame), plastic, 1.0),
            (upright(display), glass, 0.95),
            (upright(cover), plastic2, 1.0),
        ],
        f"{OUT}/assembly-wall-back.png", elev=18, azim=-125,
        title="Wall assembly - display + cover in body (from behind)",
    )
    scene(
        [
            (upright(bezel), plastic, 1.0),
            (upright(frame), plastic2, 1.0),
            (upright(display), glass, 0.95),
        ],
        f"{OUT}/assembly-wall-front.png", elev=8, azim=70,
        title="Wall assembly - front (bezel on)",
    )
    st_w = upright(stand, p.STAND_TILT_DEG)
    dp_w = upright(display, p.STAND_TILT_DEG)
    scene(
        [(st_w, plastic, 1.0), (dp_w, glass, 0.95)],
        f"{OUT}/assembly-stand.png", elev=14, azim=115,
        title="Stand assembly - display on desk stand",
    )
    scene(
        [(st_w, plastic, 1.0), (dp_w, glass, 0.95)],
        f"{OUT}/assembly-stand-side.png", elev=2, azim=0,
        title="Stand assembly - side (15 deg tilt)",
    )


if __name__ == "__main__":
    main()
