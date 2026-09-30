"""
Maps exactly WHERE the original collision test fires vs where the shapes
genuinely overlap, for every lane. Run from the before-original-code folder.

This is what makes the "before" bug filmable on demand instead of
something you have to hunt for.
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

# Import the ORIGINAL game package from before-original-code, wherever this
# script is invoked from.
HERE = os.path.dirname(os.path.abspath(__file__))
BEFORE = os.path.join(HERE, "..", "before-original-code", "frogger")
sys.path.insert(0, os.path.abspath(BEFORE))

import pygame

from game.frog import Frog
from game.vehicle import Vehicle
from game.collisions import check_collision
from game.renderer import CELL_SIZE, WIDTH

assert "before-original-code" in sys.modules["game"].__file__, \
    f"wrong game package loaded: {sys.modules['game'].__file__}"

pygame.init()
pygame.display.set_mode((1, 1))

LANE_SPEEDS = [1.5, -2, 2, -2.5, 1.5, -2]      # rows 1..6
FROG_COL = 6
frog = Frog(col=FROG_COL, row=3, start_col=FROG_COL, start_row=7, cols=12,
            start_row_limit=7)
frog_rect = frog.get_rect(CELL_SIZE)
print(f"frog occupies x {frog_rect.left}..{frog_rect.right}  (col {FROG_COL})\n")

for i, speed in enumerate(LANE_SPEEDS):
    row = i + 1
    vw = 40 if i % 2 == 0 else 70
    direction = "right" if speed > 0 else "LEFT"

    # The frog must sit IN this lane, since the test also compares rows.
    frog.row = row
    frog_rect = frog.get_rect(CELL_SIZE)

    v = Vehicle(x=0, row=row, width=vw, height=42, speed=speed)

    overlap_x, hit_x = [], []
    x = -vw
    while x <= WIDTH + vw:
        v.x = x
        if v.get_rect(CELL_SIZE).colliderect(frog_rect):
            overlap_x.append(int(x))
        if check_collision(frog, [v]):
            hit_x.append(int(x))
        x += 1

    def span(xs):
        return f"{min(xs)}..{max(xs)}" if xs else "never"

    missed = len(set(overlap_x) - set(hit_x))
    ghost = len(set(hit_x) - set(overlap_x))

    print(f"row {row}  speed {speed:>4} ({direction:>5})  width {vw:>3}px")
    print(f"    shapes truly overlap at x = {span(overlap_x)}")
    print(f"    test FIRES (reset)    at x = {span(hit_x)}")
    if missed:
        print(f"    >> MISSED {missed}px - vehicle is ON the frog, no reset happens")
    if ghost:
        print(f"    >> GHOST {ghost}px - vehicle already clear, frog still jumps to grass")
    if not missed and not ghost:
        print("    (no bug visible in this lane)")
    print()
