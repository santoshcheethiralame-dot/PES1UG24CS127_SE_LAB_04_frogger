"""
Proof-of-bug harness (Task 1 evidence, run against the UNMODIFIED code).

Frog sits at column 6, row 3. We place vehicles that VISUALLY overlap the
frog's 42x42 rect and ask check_collision(). A correct overlap test must
return True for all of these.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.frog import Frog
from game.vehicle import Vehicle
from game.collisions import check_collision
from game.renderer import CELL_SIZE

pygame.init()
pygame.display.set_mode((1, 1))

frog = Frog(col=6, row=3, start_col=6, start_row=7, cols=12, start_row_limit=7)
frog_rect = frog.get_rect(CELL_SIZE)
print(f"frog col=6 row=3 -> rect {frog_rect}\n")

# 40px car, its LEFT edge one cell to the LEFT of the frog, so its body
# already covers the frog's rect. Overlap is obvious, but the buggy test
# reads vehicle_col = (col6_left - 50)//50 == 5 != 6.
cases = [
    ("car 40px, left edge 50px left of frog (deep overlap)", 300 - 50, 40),
    ("car 40px, left edge 20px left of frog (deep overlap)", 300 - 20, 40),
    ("truck 70px, left edge 60px left of frog (covers frog)", 300 - 60, 70),
    ("truck 70px, left edge 90px left of frog (covers frog)", 300 - 90, 70),
]

missed = 0
overlapping_total = 0
for label, vx, vw in cases:
    v = Vehicle(x=vx, row=3, width=vw, height=CELL_SIZE - 8, speed=2.0)
    v_rect = v.get_rect(CELL_SIZE)
    truly_overlapping = v_rect.colliderect(frog_rect)
    detected = check_collision(frog, [v])

    if truly_overlapping:
        overlapping_total += 1
        ok = "OK   " if detected else "MISSED"
        if not detected:
            missed += 1
    else:
        # Negative control: vehicle has moved fully past the frog, so
        # False is the correct answer. Not counted either way.
        ok = "pass "

    print(f"{ok}  {label}")
    print(f"        vehicle rect {v_rect}  overlap={truly_overlapping}  check_collision()={detected}")

print(f"\n{missed}/{overlapping_total} vehicles that REALLY overlap the frog were NOT detected as hits.")
print("This is the Task 1 bug: collision compares grid columns, not real rectangles.")
print("The longer the vehicle, the more of the frog it can cover without ever")
print("registering, because only the vehicle's LEFT edge column is ever tested.")
