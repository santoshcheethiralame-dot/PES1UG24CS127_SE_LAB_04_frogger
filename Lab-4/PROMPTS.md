# Lab 4 — VibeCoding: Frogger

Working notes for the write-up. Everything below is the actual record of the
work, in the order it happened.

## Setup

The URL in the assignment handout (`SETAPESU2hhh6/01_frogger`) returns 404. The
repo actually lives under the org account:

```
git clone https://github.com/SETAPESU26/01_frogger.git
```

## Task 1 — Fix vehicle collision detection

**Prompt:** *"In `game/collisions.py` the collision test compares
`int(v.x // CELL_SIZE)` against `frog.col`. Vehicles are 40–70px wide but a
whole vehicle collapses into one grid column, so any overlap where the
vehicle's left edge sits in a neighbouring column is missed. Rewrite it to
test the frog's and vehicle's real rectangles. Don't add lives yet."*

**Diagnosis.** The frog moves in whole cells; vehicles move continuously in
pixel space. Rounding a vehicle's *left edge* to a column and comparing it to
the frog's column only registers a hit in the narrow band where those two
numbers happen to be equal. A 70px truck can sit almost entirely on top of
the frog and still report no collision.

`Verification/proof_of_bug.py` measures this against the original code — two
vehicles that genuinely overlap the frog, both reported as **no hit**:

```
MISSED  car 40px, left edge 20px left of frog
        vehicle rect <rect(280, 154, 40, 42)>  overlap=True  check_collision()=False
MISSED  truck 70px, left edge 60px left of frog (covers frog)
        vehicle rect <rect(240, 154, 70, 42)>  overlap=True  check_collision()=False
2/2 vehicles that REALLY overlap the frog were NOT detected as hits.
```

**Fix.** Both `Frog.get_rect()` and `Vehicle.get_rect()` already existed, so
the fix is a real AABB test — `pygame.Rect.colliderect()`. Removed the
duplicated hardcoded `CELL_SIZE = 50` in `collisions.py` and imported the
single source of truth from `renderer`. Added `colliding_vehicle()` for the
hit effect. Same harness afterwards: `0/2` missed, and the two negative
controls (vehicle fully past the frog) still correctly return `False`.

## Task 2 — Lives and respawn

**Prompt:** *"Add a 3-life system: lose a life on collision, respawn at the
start, keep playing while lives remain, show remaining lives, end the run at
zero. The hit itself must be visible — right now the frog just teleports
back to the start with no explanation."*

**Attempt 1 (insufficient).** Decrementing lives and calling `frog.reset()`
in the same frame reproduces exactly the "unexplained teleport" the README
complains about. Nothing on screen explains it.

**Attempt 2 (accepted).** Added a `HIT` state to the engine — a short
0.6-second pause where the frog is drawn inflated and red with a `HIT!`
label — before the respawn. Lives are shown as a numeric `Lives: N` readout.

Two details that were not in the brief but that the "visible moment"
requirement forces:

- **The hit pause is entered even on the last life**, otherwise the run ends
  instantly and the player never sees the hit that killed them.
- **1.2s of invulnerability after respawn.** The starting lane is only
  guaranteed safe at world-build time. Ten seconds later a vehicle can be
  sitting exactly on the spawn cell, so respawning without a grace window
  means an instant second death. The frog blinks semi-transparently while
  this is active so the grace is visible rather than hidden.

## Task 3 — Goal and score

**Prompt:** *"Reaching the goal should register the crossing, increase the
score, and end the game with a 'You Won!' message. Show the score during
play."*

The starter already had `if self.frog.row == GOAL_ROW: self.frog.reset()` —
it silently reset the frog instead of winning. Replaced with a `WON` state
that scores, then shows the `You Won!` banner.

**Decision worth flagging:** because the game ends on the first crossing, the
score can only ever reach 1. That is the literal reading of the spec ("end the
game with a clear 'You Won!' message"), so I did not add time bonuses or
multi-round scoring — that would contradict "that's a win regardless of how
much time is left."

## Task 4 — 30-second timer

**Prompt:** *"Add a 30-second countdown per attempt, show it, start it when an
attempt starts. Running out of time must be a genuine failure, not a silent
free reset — work out how it interacts with the lives system."*

**Design.** A timeout **costs a life** and starts a fresh 30-second attempt.
Three timeouts ends the run. A timeout shows a `TIME UP!` message, distinct
from `HIT!`, so the player can tell why they lost the life.

**The bug this task actually introduced, and the fix.** The first version had
`_lose_life()` respawn the frog without touching `time_left`. After a timeout
the clock was still `0.0`, so on the very next frame the respawned frog
timed out *again* — all three lives gone within a few frames of the first
expiry. The headless test caught it:

```
FAIL  new attempt gets a fresh 30s  got 0.0
FAIL  player continues after a timeout  state=HIT
```

`_lose_life()` now takes `reset_timer`. A **timeout** resets the clock to a
full 30 seconds; a **collision** deliberately does not, because getting hit
should not hand back clock the player already spent. The countdown is also
frozen during the hit pause, so dying never costs you extra time.

## Verification

Three headless suites, no window required, no keys needed. Run from inside
`Code/` (they import the `game` package):

| Script | What it covers | Result |
|---|---|---|
| `proof_of_bug.py` | Task 1, before vs after | 2/2 missed → 0/2 |
| `verify_lab4.py` | All 4 tasks + movement rules | **40 passed, 0 failed** |
| `verify_pixels.py` | HUD, hit flash, banners, colours | **17 passed, 0 failed** |

`verify_pixels.py` exists because the drawing code can't be reviewed by
reading it — it asserts on real framebuffer pixels, e.g. that the hit flash
draws red *outside* the frog's normal bounds (proving the "visible moment")
and that the same pixels are background in the healthy state.

Every line of the README's "Expected Behavior" list has a matching assertion.

## Known deliberate deviation

Invulnerability means a collision is not registered for 1.2s after a respawn
even if shapes overlap. This is a standard Frogger mechanic and is a
deliberate, visible (blinking) grace window, not a detection error — the
detection itself is exact overlap per Task 1.

## Still to do by hand

- Record the two 10-second videos (`Videos/` folder). The *before* video must
  come from the original code — `git stash` the changes, or check out `HEAD`,
  record, then restore.
- Export the chat history and drop it in this folder.
- Push to your own account. The upstream org repo must not get a PR.
