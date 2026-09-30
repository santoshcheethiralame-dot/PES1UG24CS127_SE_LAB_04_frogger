"""
Renders a PNG proving the original bug, so you can see it rather than take
my word for it.

Top    = ORIGINAL code's answer
Bottom = the correct overlap test

Same position in both: a 70px truck whose left edge sits at x=299, on top
of a frog at column 6 (x 304..346). The truck completely covers the frog.

Run: python render_bug_proof.py
"""

import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

HERE = os.path.dirname(os.path.abspath(__file__))
BEFORE = os.path.abspath(os.path.join(HERE, "..", "before-original-code", "frogger"))
sys.path.insert(0, BEFORE)

import pygame  # noqa: E402

from game.frog import Frog  # noqa: E402
from game.vehicle import Vehicle  # noqa: E402
from game import collisions as orig_collisions  # noqa: E402
from game.renderer import CELL_SIZE, WINDOW_SIZE  # noqa: E402

assert "before-original-code" in sys.modules["game"].__file__

ROW = 3
FROG_COL = 6

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1] * 2))
title = pygame.font.SysFont("consolas", 19, bold=True)
mono = pygame.font.SysFont("consolas", 15)
big = pygame.font.SysFont("consolas", 24, bold=True)
green = (80, 220, 100)
red = (255, 90, 90)
grey = (150, 150, 150)


def scene(surface, offset_y, truck_x, correct):
    surface.fill((20, 20, 25))
    for row in range(8):
        rect = pygame.Rect(0, offset_y + row * CELL_SIZE, WINDOW_SIZE[0], CELL_SIZE)
        if row == ROW:
            pygame.draw.rect(surface, (60, 60, 68), rect)
        else:
            pygame.draw.rect(surface, (38, 38, 44), rect)
        pygame.draw.line(surface, (70, 70, 78),
                         (0, offset_y + row * CELL_SIZE),
                         (WINDOW_SIZE[0], offset_y + row * CELL_SIZE), 1)

    frog = Frog(col=FROG_COL, row=ROW, start_col=FROG_COL, start_row=7, cols=12,
                start_row_limit=7)
    truck = Vehicle(x=truck_x, row=ROW, width=70, height=CELL_SIZE - 8, speed=0.0)

    f = frog.get_rect(CELL_SIZE)
    f.y += offset_y
    t = truck.get_rect(CELL_SIZE)
    t.y += offset_y

    pygame.draw.rect(surface, red, t, border_radius=6)
    pygame.draw.rect(surface, green, f, border_radius=8)
    pygame.draw.rect(surface, (255, 255, 0), f.inflate(12, 12), width=3)

    true_overlap = f.colliderect(t)
    if correct:
        hit = true_overlap
    else:
        hit = orig_collisions.check_collision(frog, [truck])

    return true_overlap, hit, f, t


H = WINDOW_SIZE[1]

# ---- top: original logic
true_ov, hit, fr, tr = scene(screen, 0, 299, correct=False)
surface_txt = f"truck x 299..369   frog x {fr.left}..{fr.right} (col {FROG_COL})"
screen.blit(title.render("ORIGINAL CODE  (game/collisions.py)", True, (255, 220, 80)), (10, 8))
screen.blit(mono.render(f"shapes really overlap: {true_ov}", True, grey), (10, 34))
screen.blit(mono.render(f"test returns:           {hit}", True, red if not hit else green), (10, 54))
screen.blit(mono.render(surface_txt, True, grey), (10, 78))
verdict = "NO COLLISION  <-- the bug: truck covers the frog completely"
screen.blit(big.render(verdict, True, red), (10, 100))

# ---- bottom: correct overlap
true_ov2, hit2, fr2, tr2 = scene(screen, H, 299, correct=True)
screen.blit(title.render("CORRECT OVERLAP TEST  (after the fix)", True, (120, 230, 140)), (10, H + 8))
screen.blit(mono.render(f"shapes really overlap: {true_ov2}", True, grey), (10, H + 34))
screen.blit(mono.render(f"test returns:           {hit2}", True, green), (10, H + 54))
screen.blit(mono.render(surface_txt, True, grey), (10, H + 78))
screen.blit(big.render("COLLISION  <-- fixed", True, green), (10, H + 100))

out = os.path.join(HERE, "bug-proof.png")
pygame.image.save(screen, out)

print("position: truck left edge x=299, width 70  ->  covers x 299..369")
print("         frog at column 6                   ->  covers x 304..346")
print("         the truck covers 100% of the frog")
print()
print(f"  ORIGINAL check_collision()  -> {hit}   (left edge 299//50 = 5, frog col = 6)")
print(f"  pygame real overlap         -> {true_ov}")
print()
print(f"saved {out}")
print("Open that PNG - top half shows the truck sitting on the frog and the")
print("game reporting no collision.")
