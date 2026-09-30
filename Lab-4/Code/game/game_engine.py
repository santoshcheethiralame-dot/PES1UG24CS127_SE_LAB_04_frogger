"""
GameEngine: owns the frog and all vehicles, and runs one frame's worth
of game logic.

States:
    RUNNING    - normal play, timer counting down
    HIT        - brief visible pause after being hit / timing out
    GAME_OVER  - all lives spent
    WON        - frog reached the goal

Collision detection is real rectangle overlap (see game/collisions.py).
"""

import random

import pygame

from game.frog import Frog
from game.vehicle import Vehicle
from game.collisions import check_collision
from game.renderer import (
    GRID_COLS, GRID_ROWS, GOAL_ROW, ROAD_ROWS, START_ROW, CELL_SIZE, WIDTH, HEIGHT,
)

LANE_SPEEDS = [1.5, -2, 2, -2.5, 1.5, -2]   # one entry per road row, alternating direction

MAX_LIVES = 3
ATTEMPT_TIME = 30.0     # Task 4: seconds allowed per attempt
HIT_PAUSE = 0.6          # Task 2: how long the hit moment stays on screen
INVULN_TIME = 1.2        # grace period after respawning

STATE_RUNNING = "RUNNING"
STATE_HIT = "HIT"
STATE_GAME_OVER = "GAME_OVER"
STATE_WON = "WON"


class GameEngine:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        """Full restart: new entities, 3 lives, zero score, fresh timer."""
        self.lives = MAX_LIVES
        self.score = 0
        self.time_left = ATTEMPT_TIME
        self.state = STATE_RUNNING
        self.message = ""
        self._build_entities()
        self.frog.invuln_timer = INVULN_TIME

    def _build_entities(self):
        start_col = GRID_COLS // 2
        self.frog = Frog(
            col=start_col, row=START_ROW,
            start_col=start_col, start_row=START_ROW,
            cols=GRID_COLS, start_row_limit=START_ROW,
        )
        frog_x_range = (start_col * CELL_SIZE, start_col * CELL_SIZE + CELL_SIZE)

        self.vehicles = []
        for i, row in enumerate(ROAD_ROWS):
            speed = LANE_SPEEDS[i % len(LANE_SPEEDS)]
            vehicle_width = 40 if i % 2 == 0 else 70   # mix of cars and wider trucks
            spacing = 300
            count = 2

            # Try a few random phases and keep the first one that doesn't
            # already overlap the frog's starting column - guarantees a
            # safe first lane instead of leaving it to chance.
            for _attempt in range(20):
                phase = random.randint(0, spacing - 1)
                positions = []
                safe = True
                for n in range(count):
                    offset = phase + n * spacing
                    x = offset if speed > 0 else WIDTH - offset - vehicle_width
                    positions.append(x)
                    if not (x + vehicle_width <= frog_x_range[0] or x >= frog_x_range[1]):
                        safe = False
                if safe:
                    break

            for x in positions:
                self.vehicles.append(Vehicle(x=x, row=row, width=vehicle_width,
                                              height=CELL_SIZE - 8, speed=speed))

    def handle_keydown(self, key):
        # R restarts from any state, including Game Over / You Won.
        if key == pygame.K_r:
            self.reset_game()
            return

        # No hopping while dead, finished, or mid hit-animation.
        if self.state != STATE_RUNNING:
            return

        if key == pygame.K_UP:
            self.frog.move(0, -1)
        elif key == pygame.K_DOWN:
            self.frog.move(0, 1)
        elif key == pygame.K_LEFT:
            self.frog.move(-1, 0)
        elif key == pygame.K_RIGHT:
            self.frog.move(1, 0)

    def update(self, dt=1 / 60.0):
        for v in self.vehicles:
            v.update(road_width_px=WIDTH)

        self.frog.update_timers(dt)

        if self.state == STATE_HIT:
            # Hit pause is over - respawn, or end the run if no lives left.
            if not self.frog.is_hit:
                if self.lives > 0:
                    self.frog.reset()
                    self.frog.invuln_timer = INVULN_TIME
                    self.state = STATE_RUNNING
                else:
                    self.state = STATE_GAME_OVER
            return

        if self.state != STATE_RUNNING:
            return

        # Task 4: the clock only runs during live play, so the hit pause
        # never steals time from the player.
        self.time_left -= dt
        if self.time_left <= 0:
            self.time_left = 0.0
            self._lose_life("TIME UP!", reset_timer=True)
            return

        # Task 1: true rectangle overlap, not shared grid column.
        if not self.frog.is_invulnerable and check_collision(self.frog, self.vehicles):
            self._lose_life("HIT!")
            return

        # Task 3: reaching the goal ends the run as a win, whatever the clock says.
        if self.frog.row == GOAL_ROW:
            self.score += 1
            self.state = STATE_WON
            self.message = "You Won!"

    def _lose_life(self, message, reset_timer=False):
        """Task 2/4: spend a life and show the hit moment before respawning.

        reset_timer is True for a timeout, which must start a brand new
        30-second attempt. It is False for a collision: getting hit costs a
        life but must not hand back clock the player already spent.
        """
        self.lives -= 1
        self.message = message
        self.frog.hit_timer = HIT_PAUSE
        self.frog.invuln_timer = 0.0
        if reset_timer:
            self.time_left = ATTEMPT_TIME
        # Always enter the hit pause, even on the last life, so the player
        # actually sees the final hit before the Game Over banner appears.
        self.state = STATE_HIT

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.frog, self.vehicles)
        renderer.draw_text(surface, font, "Arrow keys to move. R to restart.",
                           (10, HEIGHT - 24))
        renderer.draw_hud(surface, font, self)

        if self.state == STATE_HIT:
            renderer.draw_text_centered(surface, font, self.message, HEIGHT // 2 - 10,
                                        renderer.COLOR_HIT)
        elif self.state == STATE_GAME_OVER:
            renderer.draw_banner(surface, font, "Game Over")
            renderer.draw_text_centered(surface, font, f"Final score: {self.score}",
                                        HEIGHT // 2 + 24)
            renderer.draw_text_centered(surface, font, "Press R to play again",
                                        HEIGHT // 2 + 46, renderer.COLOR_WARN)
        elif self.state == STATE_WON:
            renderer.draw_banner(surface, font, "You Won!")
            renderer.draw_text_centered(surface, font, f"Score: {self.score}",
                                        HEIGHT // 2 + 24)
            renderer.draw_text_centered(surface, font, "Press R to play again",
                                        HEIGHT // 2 + 46, renderer.COLOR_WARN)
