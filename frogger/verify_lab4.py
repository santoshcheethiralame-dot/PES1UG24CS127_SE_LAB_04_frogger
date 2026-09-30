"""
Headless verification of Lab-4 tasks 1-4.

Drives GameEngine directly (no window) and asserts every behaviour the
README's "Expected Behavior" section demands. Run: python verify_lab4.py
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from game.game_engine import (
    GameEngine, MAX_LIVES, ATTEMPT_TIME, STATE_RUNNING, STATE_HIT,
    STATE_GAME_OVER, STATE_WON,
)
from game.collisions import check_collision
from game.frog import Frog
from game.vehicle import Vehicle
from game.renderer import CELL_SIZE, GOAL_ROW, START_ROW

pygame.init()
pygame.display.set_mode((1, 1))

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


def run(engine, seconds):
    """Advance the engine for a fixed number of simulated seconds."""
    for _ in range(int(seconds / DT)):
        engine.update(DT)


# ---------------------------------------------------------------- Task 1
print("\n--- Task 1: collision detection uses real overlap ---")
frog = Frog(col=6, row=3, start_col=6, start_row=7, cols=12, start_row_limit=7)
frog_rect = frog.get_rect(CELL_SIZE)

# Vehicle whose LEFT edge is in a different column but whose body covers the frog.
truck = Vehicle(x=frog_rect.left - 60, row=3, width=70, height=42, speed=2.0)
check("wide vehicle covering frog is detected",
      check_collision(frog, [truck]) is True)

car = Vehicle(x=frog_rect.left - 20, row=3, width=40, height=42, speed=2.0)
check("car overlapping frog is detected",
      check_collision(frog, [car]) is True)

past = Vehicle(x=frog_rect.right + 10, row=3, width=40, height=42, speed=2.0)
check("vehicle fully past the frog is NOT a hit",
      check_collision(frog, [past]) is False)

same_col_other_row = Vehicle(x=frog_rect.x, row=5, width=40, height=42, speed=2.0)
check("sharing a column but not a row is NOT a hit",
      check_collision(frog, [same_col_other_row]) is False)

# ---------------------------------------------------------------- Task 2
print("\n--- Task 2: lives, respawn, visible hit, game over ---")
eng = GameEngine()
check("starts with 3 lives", eng.lives == MAX_LIVES, f"got {eng.lives}")
check("starts in RUNNING state", eng.state == STATE_RUNNING)

# Force a hit: park a truck right on top of the frog.
eng.frog.invuln_timer = 0.0
killer = Vehicle(x=eng.frog.col * CELL_SIZE + 4, row=eng.frog.row, width=70,
                 height=42, speed=0.0)
eng.vehicles = [killer]
eng.update(DT)
check("collision costs a life", eng.lives == MAX_LIVES - 1, f"got {eng.lives}")
check("collision enters HIT state (hit is visible)", eng.state == STATE_HIT)
check("hit flash timer is running", eng.frog.is_hit)

eng.handle_keydown(pygame.K_UP)
check("frog cannot hop during hit pause", eng.frog.row == START_ROW)

# The frame that detects the hit legitimately spends one dt of clock, so
# measure the pause against the value as it stands once the hit is known.
time_at_hit = eng.time_left
run(eng, 0.3)
check("timer is frozen during the hit pause", eng.time_left == time_at_hit,
      f"{eng.time_left} vs {time_at_hit}")

run(eng, 0.5)
check("respawns to the starting position",
      (eng.frog.col, eng.frog.row) == (eng.frog.start_col, eng.frog.start_row))
check("returns to RUNNING after the hit pause", eng.state == STATE_RUNNING)
check("respawn grants invulnerability", eng.frog.is_invulnerable)

# Two lives left. Burn them; the second one must end the run.
for expected_lives in (1, 0):
    eng.frog.invuln_timer = 0.0
    eng.vehicles = [Vehicle(x=eng.frog.col * CELL_SIZE + 4, row=eng.frog.row,
                            width=70, height=42, speed=0.0)]
    eng.update(DT)
    run(eng, 0.8)
    check(f"life count drops to {expected_lives}", eng.lives == expected_lives,
          f"got {eng.lives}")
    if expected_lives == 0:
        check("all lives spent -> GAME_OVER", eng.state == STATE_GAME_OVER,
              f"state={eng.state}")
    else:
        check("still playing with a life left", eng.state == STATE_RUNNING,
              f"state={eng.state}")

eng.handle_keydown(pygame.K_r)
check("R restarts from Game Over", eng.state == STATE_RUNNING and eng.lives == MAX_LIVES)

# ---------------------------------------------------------------- Task 3
print("\n--- Task 3: goal, score, win message ---")
eng = GameEngine()
eng.frog.row = GOAL_ROW
eng.update(DT)
check("reaching the goal scores", eng.score == 1, f"got {eng.score}")
check("reaching the goal wins", eng.state == STATE_WON, f"state={eng.state}")
check("win message is set", eng.message == "You Won!")

eng2 = GameEngine()
eng2.frog.row = GOAL_ROW
eng2.time_left = 0.2
for _ in range(int(0.2 / DT) + 2):
    eng2.update(DT)
check("reaching the goal wins even with almost no time left",
      eng2.state == STATE_WON, f"state={eng2.state}")

# ---------------------------------------------------------------- Task 4
print("\n--- Task 4: 30-second per-attempt timer ---")
eng = GameEngine()
check("timer starts at 30s", abs(eng.time_left - 30.0) < 0.01, f"got {eng.time_left}")
run(eng, 5.0)
check("timer counts down", eng.time_left < 26.0, f"got {eng.time_left}")

eng = GameEngine()
eng.vehicles = []          # isolate the timer from collisions
run(eng, 30.5)             # just past the limit: exactly one timeout
check("timeout costs a life (not a free reset)", eng.lives == MAX_LIVES - 1,
      f"lives={eng.lives}")
check("timeout shows a visible moment", eng.state == STATE_HIT, f"state={eng.state}")
check("timeout message is distinct", eng.message == "TIME UP!", f"got {eng.message!r}")

# Step to the exact frame the next attempt begins, then check the clock.
while eng.state == STATE_HIT:
    eng.update(DT)
check("new attempt begins", eng.state == STATE_RUNNING, f"state={eng.state}")
check("new attempt gets a full fresh 30s", abs(eng.time_left - 30.0) < 1e-9,
      f"got {eng.time_left}")
check("player continues after a timeout", eng.state == STATE_RUNNING,
      f"state={eng.state}")

# Idling without reaching the goal must keep costing lives - that is what
# makes a timeout a genuine failure rather than a free reset.
run(eng, 30.5)
while eng.state == STATE_HIT:
    eng.update(DT)
check("a second idle timeout costs another life", eng.lives == MAX_LIVES - 2,
      f"lives={eng.lives}")
check("second attempt also gets a fresh 30s", abs(eng.time_left - 30.0) < 1e-9,
      f"got {eng.time_left}")

# Third timeout ends the run.
run(eng, 30.5)
while eng.state == STATE_HIT:
    eng.update(DT)
check("three timeouts -> GAME_OVER", eng.state == STATE_GAME_OVER,
      f"state={eng.state} lives={eng.lives}")

eng.handle_keydown(pygame.K_r)
check("R resets the timer", abs(eng.time_left - 30.0) < 0.01, f"got {eng.time_left}")

# ---------------------------------------------------------------- movement
print("\n--- Expected behavior: movement rules ---")
eng = GameEngine()
for _ in range(10):
    eng.handle_keydown(pygame.K_DOWN)
check("frog cannot move below its starting row", eng.frog.row == START_ROW)
eng.handle_keydown(pygame.K_UP)
check("frog hops up one cell", eng.frog.row == START_ROW - 1)
eng.handle_keydown(pygame.K_LEFT)
check("frog hops left one cell",
      eng.frog.col == eng.frog.start_col - 1)

eng = GameEngine()
for _ in range(20):
    eng.handle_keydown(pygame.K_LEFT)
check("frog cannot move off the left edge", eng.frog.col == 0)
for _ in range(30):
    eng.handle_keydown(pygame.K_RIGHT)
check("frog cannot move off the right edge", eng.frog.col == 11)

# ---------------------------------------------------------------- summary
print(f"\n{'=' * 46}")
print(f"{passed} passed, {len(failed)} failed")
if failed:
    for name in failed:
        print(f"  FAILED: {name}")
    raise SystemExit(1)
print("All Lab-4 behaviours verified.")
