# Videos to record here

Two 10-second screen recordings, as required by the lab.

> **Simplest approach (recommended).** The before/after contrast does *not*
> depend on catching the collision bug on camera. The original starter has
> no lives, no score, no timer, no hit feedback and no win state — the fix
> adds all five, and they are plainly visible. Film the game as delivered
> and the difference sells itself.
>
> `demo_bug.py` below is only for the write-up, to show the collision
> precision fix under slow motion.

---

## `before.mp4` — the starter as delivered

```powershell
cd C:\Users\carbo\projects\01_frogger\Lab-4\before-original-code\frogger
python main.py
```

Film ~10 s of:

1. Hop the frog up a few rows with the arrow keys.
2. Get hit by a vehicle.
3. **The frog instantly teleports back to the grass.** No flash, no label, no
   explanation, and nothing on screen tells you how many lives are left,
   what the score is, or how much time is running out.
4. The only text on screen is `Arrow keys to move. R to restart.` at the bottom.

That unexplained teleport is the exact complaint in the README: *"an instant,
unexplained teleport back to the start."*

## `after.mp4` — the same moment, fixed

```powershell
cd C:\Users\carbo\projects\01_frogger\frogger
python main.py
```

Film the same 10 s. Compare shot-for-shot:

| What the camera shows | Before | After |
|---|---|---|
| On getting hit | frog vanishes instantly | frog flashes **red and swollen** + `HIT!` for 0.6 s |
| Lives | *nothing* | `Lives: 3` → `Lives: 2` |
| Timer | *nothing* | `Time: 30` counting down, **amber** at 5 s |
| Score | *nothing* | `Score: 0` |
| Reaching the goal | silently resets the frog | `You Won!` banner |
| Out of lives | *never happens* — infinite retries | `Game Over` + final score |

Best single take: hold still in a lane and get hit, then press `R` to show a
full restart. Then hop to the top row for the win.

---

## Optional: showing the Task 1 collision fix on camera

The collision is genuinely wrong in the original — it fires on only 41% of the
frames where the shapes overlap, and can fire 4px *after* the vehicle has
cleared. But it looks fine in normal play, so it is hard to film in 10 s.

`Verification/demo_bug.py` runs the untouched original code in slow motion and
draws a **yellow outline around the frog whenever it is genuinely overlapped
but no collision fires** — the exact 65px window where the bug lives:

```powershell
cd C:\Users\carbo\projects\01_frogger\Lab-4\Verification
python demo_bug.py 2 0.2      # lane 2, 5x slow motion
```

- Lane `2`, `4`, or `6` are the left-moving 70px trucks (biggest miss window).
- `SPACE` pause, `R` restart, `ESC` quit.
- Record with `Win + Alt + R` while it runs.

Supporting evidence for the write-up:

- `Verification/bug-proof.png` — a truck completely covering the frog while the
  original test reports **no collision**.
- `Verification/bug-windows-output.txt` — every lane measured:

| Lane | Vehicle | Overlap | Reset fires | Missed | Ghost |
|---|---|---|---|---|---|
| 1, 3, 5 | 40px car | x 265–345 | x 300–349 | 35px | 4px |
| 2, 4, 6 | 70px truck | x 235–345 | x 300–349 | **65px** | 4px |
