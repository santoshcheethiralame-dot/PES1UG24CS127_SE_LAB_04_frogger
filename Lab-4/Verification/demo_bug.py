"""
Slow-motion demo of the ORIGINAL collision bug, for the "before" video.

Runs the untouched starter code (imported from ../before-original-code) and
outlines the frog whenever the shapes genuinely overlap but the original
test reports no hit - so the missed window lights up on camera instead of
being a flicker you might miss.

Usage:  python demo_bug.py <lane_row> <slow_motion>
        e.g. python demo_bug.py 2 0.2     -> lane 2, 5x slower

Controls: SPACE pause, R restart, ESC quit.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BEFORE = os.path.abspath(os.path.join(HERE, "..", "before-original-code", "frogger"))
sys.path.insert(0, BEFORE)

import pygame  # noqa: E402

from game.game_engine import GameEngine  # noqa: E402
from game import renderer  # noqa: E402
from game import collisions as orig_collisions  # noqa: E402

assert "before-original-code" in sys.modules["game"].__file__, \
    f"refusing to run: wrong game package {sys.modules['game'].__file__}"

ROW = int(sys.argv[1]) if len(sys.argv) > 1 else 2
SLOW = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2
if SLOW <= 0:
    SLOW = 1.0

MISSED = (255, 255, 0)    # yellow  = on the frog, no collision fired (the bug)
FAKE = (255, 0, 255)      # magenta = collision fired, frog not actually touched

pygame.init()
screen = pygame.display.set_mode(renderer.WINDOW_SIZE)
pygame.display.set_caption("Frogger - ORIGINAL collision bug (slow motion)")
font = pygame.font.SysFont("consolas", 20)
small = pygame.font.SysFont("consolas", 16)
clock = pygame.time.Clock()

engine = GameEngine()
paused = False
accum = 0.0
FRAME = 1 / 60.0

while True:
    real_dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_r:
                engine.handle_keydown(pygame.K_r)

    # Slow motion: advance the original fixed-step update less often.
    if not paused:
        accum += real_dt * SLOW
        while accum >= FRAME:
            accum -= FRAME
            engine.update()        # original update(): no dt, original logic
            engine.frog.row = ROW  # park the frog in the demo lane

    engine.draw(screen, font)

    # Compare the original test against true rectangle overlap.
    frog_rect = engine.frog.get_rect(renderer.CELL_SIZE)
    true_overlap = any(
        v.get_rect(renderer.CELL_SIZE).colliderect(frog_rect)
        for v in engine.vehicles
    )
    hit = orig_collisions.check_collision(engine.frog, engine.vehicles)

    colour, label = None, ""
    if true_overlap and not hit:
        colour, label = MISSED, "MISSED - truck is ON the frog, no collision fired"
    elif hit and not true_overlap:
        colour, label = FAKE, "GHOST - vehicle already clear, frog still resets"

    if colour:
        pygame.draw.rect(screen, colour, frog_rect.inflate(16, 16), width=4)
        renderer.draw_text(screen, small, label, (6, 2), colour)

    footer = (f"ORIGINAL code | lane {ROW} | {1 / SLOW:.0f}x slow motion | "
              "SPACE pause, R restart, ESC quit")
    renderer.draw_text(screen, small, footer, (6, renderer.HEIGHT - 20), (190, 190, 190))

    pygame.display.flip()
