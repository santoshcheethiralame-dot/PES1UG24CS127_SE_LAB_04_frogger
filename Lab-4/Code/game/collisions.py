"""
collisions: frog-vs-vehicle collision detection.

Detection is based on the frog's and the vehicle's real drawn rectangles
(overlap / AABB test), not on grid columns. Vehicles move continuously in
pixel space, so a grid-column test silently misses any overlap where the
vehicle's left edge sits in a different column than the frog.
"""

from game.renderer import CELL_SIZE


def check_collision(frog, vehicles):
    """
    Returns True if the frog's rectangle actually overlaps any vehicle's
    rectangle. Merely sharing a lane is not enough - the shapes must
    truly intersect on screen.
    """
    frog_rect = frog.get_rect(CELL_SIZE)
    for v in vehicles:
        if v.get_rect(CELL_SIZE).colliderect(frog_rect):
            return True
    return False


def colliding_vehicle(frog, vehicles):
    """Returns the first vehicle actually overlapping the frog, else None."""
    frog_rect = frog.get_rect(CELL_SIZE)
    for v in vehicles:
        if v.get_rect(CELL_SIZE).colliderect(frog_rect):
            return v
    return None
