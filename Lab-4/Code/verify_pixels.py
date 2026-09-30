"""
Pixel-level verification of the drawing code. I cannot eyeball the PNGs,
so assert on actual framebuffer pixels: is the HUD inked, does the hit
flash actually inflate and recolour the frog, do the banners appear.
Run: python verify_pixels.py
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.game_engine import GameEngine, STATE_HIT
from game.vehicle import Vehicle
from game import renderer
from game.renderer import CELL_SIZE, WINDOW_SIZE, START_ROW

pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
font = pygame.font.SysFont("consolas", 20)
big_font = pygame.font.SysFont("consolas", 26, bold=True)

DT = 1 / 60.0
passed = 0
failed = []


def check(name, cond, detail=""):
    global passed
    if cond:
        passed += 1
        print(f"PASS  {name}")
    else:
        failed.append(name)
        print(f"FAIL  {name}  {detail}")


def region_has_ink(surface, rect, background):
    """True if the region contains at least one pixel that is not background."""
    for x in range(rect.left, rect.right):
        for y in range(rect.top, rect.bottom):
            if surface.get_at((x, y))[:3] != background:
                return True
    return False


def count_color(surface, color):
    n = 0
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            if surface.get_at((x, y))[:3] == color:
                n += 1
    return n


START_COL = 6
frog_rect = pygame.Rect(START_COL * CELL_SIZE + 4, START_ROW * CELL_SIZE + 4,
                        CELL_SIZE - 8, CELL_SIZE - 8)

# --------------------------------------------------------- HUD is drawn
print("\n--- HUD (lives / score / time) ---")
eng = GameEngine()
check("a fresh spawn starts invulnerable (blink grace)", eng.frog.is_invulnerable)
eng.frog.invuln_timer = 0.0   # let the grace lapse to see the solid frog
eng.draw(screen, font)
check("lives readout is inked",
      region_has_ink(screen, pygame.Rect(0, 0, 120, 20), renderer.COLOR_BG))
check("score readout is inked",
      region_has_ink(screen, pygame.Rect(0, 20, 120, 20), renderer.COLOR_BG))
check("time readout is inked",
      region_has_ink(screen, pygame.Rect(WINDOW_SIZE[0] - 100, 0, 100, 20),
                     renderer.COLOR_BG))
check("normal frog is solid green at its centre",
      screen.get_at(frog_rect.center)[:3] == renderer.COLOR_FROG,
      str(screen.get_at(frog_rect.center)))

# --------------------------------------------------------- hit moment
print("\n--- Hit moment is visible ---")
eng2 = GameEngine()
eng2.frog.invuln_timer = 0.0
eng2.vehicles = [Vehicle(x=eng2.frog.col * CELL_SIZE + 4, row=eng2.frog.row,
                         width=70, height=42, speed=0.0)]
eng2.update(DT)
check("engine is in HIT state", eng2.state == STATE_HIT, f"state={eng2.state}")
eng2.draw(screen, font)

check("hit frog is recoloured red",
      screen.get_at(frog_rect.center)[:3] == renderer.COLOR_FROG_HIT,
      str(screen.get_at(frog_rect.center)))

# A ring just outside the normal frog rect must be red only if the hit
# flash inflates the frog. This is the "you can SEE the hit" requirement.
ring = [(frog_rect.left - 3, frog_rect.centery),
        (frog_rect.right + 2, frog_rect.centery),
        (frog_rect.centerx, frog_rect.top - 3),
        (frog_rect.centerx, frog_rect.bottom + 2)]
inked = sum(1 for p in ring if screen.get_at(p)[:3] == renderer.COLOR_FROG_HIT)
check("hit flash expands past the normal frog bounds", inked >= 3,
      f"{inked}/4 ring pixels are hit-red")

check("HIT! message is on screen", count_color(screen, renderer.COLOR_HIT) > 0,
      "no COLOR_HIT pixels")

# And the same ring must NOT be red in the healthy state.
eng3 = GameEngine()
eng3.draw(screen, font)
ring_normal = sum(1 for p in ring if screen.get_at(p)[:3] == renderer.COLOR_FROG_HIT)
check("healthy frog does not draw the hit ring", ring_normal == 0,
      f"{ring_normal}/4 ring pixels are hit-red")

# --------------------------------------------------------- invulnerability
print("\n--- Respawn invulnerability blink ---")
eng4 = GameEngine()
eng4.frog.invuln_timer = 0.5
eng4.draw(screen, font)
centre = screen.get_at(frog_rect.center)
check("invulnerable frog is drawn semi-transparent, not solid green",
      centre[:3] != renderer.COLOR_FROG, str(centre))
check("invulnerable frog keeps some green", centre[1] > centre[0], str(centre))

# --------------------------------------------------------- banners
print("\n--- End-of-run banners ---")
BANNER = (255, 220, 80)

eng5 = GameEngine()
eng5.frog.row = 0
eng5.update(DT)
eng5.draw(screen, big_font)
check("You Won! banner is drawn", count_color(screen, BANNER) > 0,
      "no banner pixels")

eng6 = GameEngine()
eng6.lives = 0
eng6.state = STATE_HIT
eng6.frog.hit_timer = 0.0
eng6.update(DT)
check("engine reached GAME_OVER", eng6.state == "GAME_OVER", f"state={eng6.state}")
eng6.draw(screen, big_font)
check("Game Over banner is drawn", count_color(screen, BANNER) > 0,
      "no banner pixels")

# --------------------------------------------------------- low-time colour
print("\n--- Low-time warning colour ---")
eng7 = GameEngine()
eng7.time_left = 3.0
eng7.draw(screen, font)
low_ink = 0
for x in range(WINDOW_SIZE[0] - 100, WINDOW_SIZE[0]):
    for y in range(0, 20):
        if screen.get_at((x, y))[:3] == renderer.COLOR_WARN:
            low_ink += 1
check("time readout turns amber when low", low_ink > 0, f"{low_ink} amber pixels")

eng8 = GameEngine()
eng8.time_left = 28.0
eng8.draw(screen, font)
high_ink = 0
for x in range(WINDOW_SIZE[0] - 100, WINDOW_SIZE[0]):
    for y in range(0, 20):
        if screen.get_at((x, y))[:3] == renderer.COLOR_WARN:
            high_ink += 1
check("time readout is white when plenty of time remains", high_ink == 0,
      f"{high_ink} amber pixels")

print(f"\n{'=' * 46}")
print(f"{passed} passed, {len(failed)} failed")
if failed:
    for name in failed:
        print(f"  FAILED: {name}")
    raise SystemExit(1)
print("All drawing verified at the pixel level.")
