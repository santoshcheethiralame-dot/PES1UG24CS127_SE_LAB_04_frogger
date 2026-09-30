"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import pygame

CELL_SIZE = 50
GRID_COLS = 12
GRID_ROWS = 8

WIDTH = CELL_SIZE * GRID_COLS
HEIGHT = CELL_SIZE * GRID_ROWS
WINDOW_SIZE = (WIDTH, HEIGHT)

GOAL_ROW = 0
ROAD_ROWS = list(range(1, GRID_ROWS - 1))   # rows 1..6
START_ROW = GRID_ROWS - 1                     # row 7

COLOR_BG = (20, 20, 25)
COLOR_GOAL = (40, 130, 60)
COLOR_ROAD = (45, 45, 50)
COLOR_START = (40, 90, 60)
COLOR_LANE_LINE = (90, 90, 90)
COLOR_FROG = (80, 220, 100)
COLOR_FROG_BLINK = (80, 220, 100, 90)
COLOR_FROG_HIT = (255, 90, 90)
COLOR_VEHICLE = (220, 80, 70)
COLOR_TEXT = (255, 255, 255)
COLOR_HIT = (255, 120, 120)
COLOR_WARN = (255, 200, 80)


def draw_scene(surface, frog, vehicles):
    surface.fill(COLOR_BG)

    for row in range(GRID_ROWS):
        rect = pygame.Rect(0, row * CELL_SIZE, WIDTH, CELL_SIZE)
        if row == GOAL_ROW:
            pygame.draw.rect(surface, COLOR_GOAL, rect)
        elif row == START_ROW:
            pygame.draw.rect(surface, COLOR_START, rect)
        else:
            pygame.draw.rect(surface, COLOR_ROAD, rect)
            pygame.draw.line(surface, COLOR_LANE_LINE, (0, row * CELL_SIZE), (WIDTH, row * CELL_SIZE), 1)

    for v in vehicles:
        pygame.draw.rect(surface, COLOR_VEHICLE, v.get_rect(CELL_SIZE), border_radius=6)

    _draw_frog(surface, frog)


def _draw_frog(surface, frog):
    """Draw the frog, showing hits and the post-respawn invulnerability blink."""
    rect = frog.get_rect(CELL_SIZE)

    if frog.is_hit:
        # Slightly inflated + red: the hit is obvious, not a silent teleport.
        rect = rect.inflate(10, 10)
        pygame.draw.rect(surface, COLOR_FROG_HIT, rect, border_radius=8)
        return

    if frog.is_invulnerable:
        # Semi-transparent so the player can see they are briefly safe.
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, COLOR_FROG_BLINK, overlay.get_rect(), border_radius=8)
        surface.blit(overlay, rect.topleft)
        return

    pygame.draw.rect(surface, COLOR_FROG, rect, border_radius=8)


def draw_hud(surface, font, engine):
    """Task 2/3/4 readouts: remaining lives, score, and time left."""
    draw_text(surface, font, f"Lives: {engine.lives}", (10, 8))
    draw_text(surface, font, f"Score: {engine.score}", (10, 26))

    time_label = f"Time: {max(0, int(engine.time_left))}"
    time_color = COLOR_WARN if engine.time_left <= 5 else COLOR_TEXT
    draw_text(surface, font, time_label, (WIDTH - 82, 8), time_color)


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_text_centered(surface, font, text, y, color=COLOR_TEXT):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(surface.get_width() // 2, y))
    surface.blit(surf, rect)


def draw_banner(surface, font, text):
    surf = font.render(text, True, (255, 220, 80))
    rect = surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.blit(surf, rect)
