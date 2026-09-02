# Stage 0 - Physical brief: bakery back room, 04:10, first rack out

**Function (one sentence).** A room where heat is the product, and everything is
arranged around getting steel trays into and out of it.

**Envelope.** ROOM: 4.20w x 7.20d x 3.20h  (commercial back-of-house ceiling)
- SPAN width: racks=0.70 aisle=2.70 bench=0.80  = 4.20 OK
- SPAN depth: ovens=1.40 work=3.20 near-zone=2.60 = 7.20 OK
- circulation 2.70m: a 0.70m speed rack must turn in it. OK

**Dominant class by volume.** The rack ovens - NOT the human.
| item | real w x d x h (m) | vs the baker (1.75m) |
|---|---|---|
| roll-in rack oven | 1.20 x 1.40 x 2.20 | 1.26x his height |
| oven door aperture | 1.00 x 1.80 | he walks a rack through it |
| speed rack (18 tray) | 0.70 x 0.46 x 1.75 | exactly his height |
| full sheet pan | 0.66 x 0.46 | - |
| steel work bench | 2.40 x 0.80 x 0.90 | hip height |
| baker, standing | 0.55 x 1.75 | the yardstick |
| flour sack | 0.50 x 0.30 x 0.70 | knee height |
| batard loaf | 0.30 x 0.12 x 0.10 | - |

**The human.** One baker, standing at the open oven, three-quarter back to
camera, sliding a peel in. He is *smaller than the thing he serves* - the oven
is a quarter again his height and four times his volume.

**Scene-specific constraints** - the physics the generic laws cannot contain:
1. A rack oven is a tonne of steel and firebrick. It is floor-fixed against a
   wall, never free-standing, never on castors, and it is always the back wall.
2. **The mouth is at floor level and the light source is therefore LOW** - the
   door aperture starts at the floor and rises to 1.8m. So this room is lit from
   below and in front: shadows travel *up* the far surfaces, faces are uplit,
   the ceiling takes the bounce, and the brightest floor is the strip directly
   in front of the door. Every other scene in this corpus is lit from above.
3. Trays travel oven -> rack -> bench, so the aisle stays clear; racks cluster
   on the cooling side, never against the oven.
4. Speed racks are on castors and are never square to anything.
5. Flour settles on horizontals: every up-facing surface is a value lighter
   than the vertical beside it.
6. Opening the door dumps steam. It rises, is lit from below by the mouth, and
   decays within about a metre.

**Palette** - derived, not chosen (`palette.py`): key = 2100K radiant deck,
ambient = 6200K LED strip at the far end, chromatic adaptation D=0.25 to the
key. That single arithmetic gives warm brass in the light and slate blue in
shadow without either being asserted anywhere.

**What the frame cuts.** A loaded speed rack cropped by the left edge and the
bottom; the bench runs out of frame bottom-right; the second oven is half out
of frame right.

**Camera.** 1.65m, standing, someone who has just walked in. k=288, datum 820,
so R = 288*1.65 = 475 and the horizon is y=345 (F1). VP (600,345), left of
centre. Reference plane d0=2.6m, so floor foreshortening f = 1.65/2.6 = 0.635.
