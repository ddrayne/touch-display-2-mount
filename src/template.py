"""Generate the wall-drilling template PDF (print at 100% scale, A4).

Two keyhole screw positions 110 mm apart on a level line, with the frame
outline for reference and a scale-check ruler.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch

import params as p
import spec

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "docs", "drilling-template.pdf")

MM = 1 / 25.4  # inches per mm

# A4 in portrait
fig = plt.figure(figsize=(210 * MM, 297 * MM))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 210)
ax.set_ylim(0, 297)
ax.set_aspect("equal")
ax.axis("off")

cx = 105.0
cy = 239.0  # screw line height on the sheet

# screw crosses: centres KEYHOLE_X*2 apart; screws engage the slot tips,
# KEYHOLE_SLOT_LEN above the entry centre
span = 2 * p.KEYHOLE_X
for sx in (-1, 1):
    x = cx + sx * span / 2
    ax.plot([x - 6, x + 6], [cy, cy], "k-", lw=0.8)
    ax.plot([x, x], [cy - 6, cy + 6], "k-", lw=0.8)
    ax.add_patch(plt.Circle((x, cy), 2.4, fill=False, lw=0.8))
    ax.annotate("drill here\n(4 mm / #8 screw)", (x, cy - 9), ha="center",
                va="top", fontsize=8)

ax.plot([cx - span / 2 - 25, cx + span / 2 + 25], [cy, cy], "k--", lw=0.5)
ax.annotate("LEVEL LINE - use a spirit level", (cx, cy + 8), ha="center", fontsize=9)
ax.annotate(f"{span:.0f} mm", (cx, cy + 2), ha="center", fontsize=9)

# frame outline reference (top of frame relative to screws): screws sit at
# display y = KEYHOLE_ENTRY_Y + SLOT_LEN when hung; frame top edge is at
# display y = OUT_H/2 above centre => distance from screw line to frame top:
top_above = p.OUT_H / 2 - (p.KEYHOLE_ENTRY_Y + p.KEYHOLE_SLOT_LEN)
ax.add_patch(
    Rectangle(
        (cx - p.OUT_W / 2, cy + top_above - p.OUT_H),
        p.OUT_W,
        p.OUT_H,
        fill=False,
        lw=0.6,
        ls=":",
    )
)
ax.annotate(
    "frame outline when hung (dotted)",
    (cx, cy + top_above - p.OUT_H - 4),
    ha="center",
    fontsize=8,
)

# 100 mm scale check ruler
rx, ry = 30, 40
ax.plot([rx, rx + 100], [ry, ry], "k-", lw=1.2)
for i in range(0, 101, 10):
    ax.plot([rx + i, rx + i], [ry, ry + (4 if i % 50 == 0 else 2.5)], "k-", lw=0.8)
ax.annotate(
    "scale check: this bar must measure exactly 100 mm - print at 100% / actual size",
    (rx, ry - 6),
    fontsize=8,
)

ax.annotate(
    "Wall drilling template  -  Raspberry Pi Touch Display 2 10\" Portrait mount\n"
    "Leave screw heads ~4 mm proud of the wall, hang the frame, slide down to lock.",
    (cx, 270),
    ha="center",
    fontsize=10,
)

fig.savefig(OUT)
print("wrote", OUT)
