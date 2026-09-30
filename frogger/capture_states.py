"""
Visual smoke test: renders each game state to a PNG so the drawing code
(hud, hit flash, banners, invulnerability blink) is actually exercised.
Run: python capture_states.py
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.game_engine import (
    GameEngine, STATE_HIT, STATE_RUNNING, HIT_PAUSE,
)
from game.vehicle import Vehicle
from game.renderer import CELL_SIZE, WINDOW_SIZE

pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
font = pygame.font.SysFont("consolas", 20)
big_font = pygame.font.SysFont("consolas", 26, bold=True)
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state_shots")
os.makedirs(out_dir, exist_ok=True)

DT = 1 / 60.0


def shot(name, engine):
    engine.draw(screen, big_font)
    path = os.path.join(out_dir, name)
    pygame.image.save(screen, path)
    print(f"saved {path}")


# 1. Normal play, mid-road, with the HUD.
eng = GameEngine()
for _ in range(30):
    eng.update(DT)
eng.frog.move(0, -1)
eng.frog.move(0, -1)
eng.frog.move(0, -1)
shot("1_running.png", eng)

# 2. The hit moment - inflated red frog + HIT! text.
eng2 = GameEngine()
eng2.frog.invuln_timer = 0.0
eng2.vehicles = [Vehicle(x=eng2.frog.col * CELL_SIZE + 4, row=eng2.frog.row,
                         width=70, height=42, speed=0.0)]
eng2.update(DT)
print(f"state={eng2.state} lives={eng2.lives} message={eng2.message!r}")
shot("2_hit.png", eng2)

# 3. Post-respawn invulnerability blink.
eng3 = GameEngine()
eng3.frog.invuln_timer = 0.5
shot("3_invulnerable_blink.png", eng3)

# 4. Game Over banner.
eng4 = GameEngine()
eng4.state = STATE_HIT
eng4.lives = 0
eng4.message = "Game Over"
eng4.frog.hit_timer = 0.0
eng4.update(DT)
print(f"state={eng4.state}")
shot("4_game_over.png", eng4)

# 5. You Won! banner with score.
eng5 = GameEngine()
eng5.frog.row = 0
eng5.update(DT)
print(f"state={eng5.state} score={eng5.score}")
shot("5_you_won.png", eng5)

# 6. Low-time warning colour.
eng6 = GameEngine()
eng6.time_left = 3.4
shot("6_low_time.png", eng6)

# 7. Long-run soak: 60 simulated seconds, make sure nothing raises.
eng7 = GameEngine()
frames = 0
for _ in range(int(60 / DT)):
    eng7.update(DT)
    frames += 1
print(f"soak ok: {frames} frames, final state={eng7.state}, lives={eng7.lives}")
shot("7_after_60s_idle.png", eng7)

print("\nAll states rendered without error.")
