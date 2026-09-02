---
name: spatial-svg-architect
description: >-
  Build realistic, art-directed SVG scenes (interiors, often with a view outside)
  as self-contained, web-ready HTML. Hardcoded spatial math (metric scale, datum,
  one-point perspective) + per-scene derived art direction + a deterministic eval
  the agent runs in a fix loop, then a written quality scorecard against a
  calibrated rubric. Use when asked to create or edit an illustrated scene, hero
  illustration, or vector environment for a website or product.
---

# Spatial SVG Architect

**The goal:** a web-ready SVG scene a viewer believes is a real place. Priority:

1. **It reads as a specific place** (researched signifiers, authored detail)
2. **It looks real** (camera, depth, density, light - the quality rubric)
3. **It is physically true** (scale, contact, gravity - the eval)

## Architecture: laws, choices, construction

**LAWS are hardcoded** - the same for every scene, machine-checkable where
possible: one declared metric scale and datum, every coordinate derived from
real dimensions; gravity and contact (support chains to the floor); one key
light with globally consistent shadow direction/length and colored (never
black) shadows; at most one glow story; atmospheric decay with distance; three
separable value planes; a bounded declared palette with exactly one ink;
back-to-front emission matching physical assembly; the eval + look loop.

**CHOICES are derived per scene, by procedure - never picked from a stored
menu**: the palette (derive: light temperature x material truth x one identity
accent - `art-direction.md` §2); the props (derive: place research, below); the
camera and style preset (`perspective-and-depth.md` §7); density and rest areas.

**EXAMPLES are non-normative**: typologies, shape recipes, palette anchors and
shipped builds show the procedures' output. They are evidence, not menus.

## Pipeline (work stages in order; no `<svg>` before Stage 5)

```
0 PHYSICAL BRIEF         -> the room as a function; envelope in m; constraints
1 BRIEF + RESEARCH + PLAN -> place, signifiers, and the room's topology
2 ART DIRECTION          -> derived palette + value plan + composition + light
3 WORLD RULES            -> canvas/datum/scale + CAMERA/STYLE preset + sun/wind
4 COORDINATE MAP         -> every y AND every extent derived (F7); SIZES declared
5 EMISSION               -> 8-phase DOM order, defs reuse, preset craft rules
6 EVAL + SCORECARD LOOP  -> eval_scene.py exit 0 (floor), then rubric scorecard
```

### Stage 0 - Physical brief (before anything visual)

A model asked for "a laundromat" will produce a props list and distribute it
along whatever surfaces exist. It will not, unprompted, work out that a
laundromat is a narrow aisle between two walls of large machines. Write this
down first, in prose and in metres:

1. **The room as a function**, one sentence. Not "a laundromat" - *"a place
   where people wait while machines do work for them."* The function tells you
   what dominates and where the human looks.
2. **The envelope**, declared: `<!-- ROOM: 4.20w x 6.00d x 2.70h -->`.
   Domestic ceilings 2.4-2.7m, commercial 3.0-4.5m, industrial to ~12m.
3. **How the floor is spent**, declared and summing to the envelope (F8):
   `<!-- SPAN width: washers=0.85 aisle=2.40 washers=0.85 -->`
   If the numbers do not close, the plan is impossible in the room it claims -
   and you know that before placing a single coordinate. A person needs 0.75m
   to pass and 1.10m for two-way traffic; an aisle below that is a plan error,
   not a tight composition.
4. **The dominant class and its real dimensions.** Answer honestly: what
   occupies the most volume here? It is almost never the human. Commercial
   front-loader 0.85 x 1.10m; restaurant table 0.75m high; classroom desk
   0.70m. Get these from research, not from feel.
5. **The human as yardstick.** Where they are, what they are doing, what they
   are looking at, how tall. State every other object as a ratio to them - "the
   washer stack is twice her seated height" survives translation into pixels in
   a way that "0.85m" does not.
6. **Scene-specific constraints - the physics the generic laws do not contain.**
   The laws in this skill cover gravity, contact and light. They cannot know
   that washing machines need plumbing and so stand against walls, never free;
   that their doors swing into the aisle; that classroom desks face one way
   because attention has a direction; that a bar's back counter is deep because
   bottles live there. Derive three to five of these from the room's function
   and write them down. They are the difference between a room and a showroom.
7. **What the frame cuts.** A view that contains every object entirely is a
   catalogue photograph. Name what the edges crop.

### Stage 1 - Brief + place research
One paragraph: which place, what time and season, what mood word, what single
object/view is the star. Then research the place BEFORE any drawing - this is
what makes it read as somewhere real:
- List >=6 signature elements with real dimensions (what is actually in a ramen
  counter, a Viennese Kaffeehaus, a Kerala tea stall) - from a matching entry in
  `references/typologies.md` if one exists, else derive fresh and hold it to the
  same standard (dimension table, materials, failure modes).
- A real, named place or landmark gets its actual silhouette and 2-3 material
  facts (what color the thing really is). New typologies get MORE Stage 6
  critique rounds, not fewer.

**Then write a PLAN, not a props list.** A list of objects gets distributed
along whatever surfaces exist and produces a showroom. Real interiors have a
topology - the thing the room is FOR, arranged the way the work actually flows.
State it in a comment before any coordinate:
```html
<!-- PLAN: two banks of stacked washers facing each other across a 2.4m aisle;
     bench on the left bank, occupant facing the machines she is watching;
     near stacks cropped by the frame; window on the back wall closing the aisle -->
```
Answer four questions: what dominates by VOLUME (usually not the human); what
faces what; where the human is and what they are looking at; what the frame
cuts. A laundromat is two walls of large machines with a narrow aisle - if the
plan does not say that, no amount of correct arithmetic will produce it.

### Stage 2 - Art direction lock
Read `references/art-direction.md`. Write down before drawing: the DERIVED
palette (5-14 hexes, one ink, in a PALETTE comment - §2 derivation, not an
anchor pick); the three value planes; composition (star off-center, deliberate
rest areas, one foreground framing element); the light story (one key + max one
glow story, shadow tint named).

**Name the light archetype** from the table in `perspective-and-depth.md` L10,
and say why. Interiors converge hard on one of the eight - a dim box lit by a
single small warm source - because low key hides weak material rendering. Six of
the eight archetypes are not dim. **Own the value range** (L9): the frame needs
true darks, a broad middle, AND a decisive near-white area; the eval measures
all three off the render. Deriving the palette from a warm illuminant is not a
licence to put nothing bright in the picture.

### Stage 3 - World rules + camera
Canvas `1440x900`. Declare machine-readable comments:
```html
<!-- SCALE: 288px = 1m (at the reference plane) -->
<!-- DATUM y=810 -->
<!-- ROOM: 4.20w x 6.00d x 2.70h -->
<!-- SPAN width: washers=0.85 aisle=2.40 washers=0.85 -->
<!-- STYLE: painterly-perspective -->
<!-- PERSPECTIVE: horizon y=810-k*H_cam, VP (900,y_h), s(y)=(y-y_h)/(810-y_h) -->
<!-- LIGHTS: sun=sun@1300,430 | bar=tube@620,300;axis=0;pool=pool-bar -->
<!-- SIZES: washer=0.85x1.10 | bench=1.60x0.89 | cart=0.75x0.85 -->
<!-- PALETTE: ... -->
```
**The horizon is not a free choice.** `R = y_ref - y_h = k * H_cam`
(`perspective-and-depth.md` F1), so pick the camera's eye height first and derive
the horizon: standing 1.6m at k=288 puts the horizon 461px above the reference
plane. Every scene built before this rule existed came out at 1.18-1.49m - a
seated camera nobody chose.

**Declare the light rig too.** Every non-distant emitter names the element that
draws where its light lands, and the footprint is *derived* from the emitter's
shape (`perspective-and-depth.md` §8): a strip light cannot cast a circular pool,
a rectangular window projects to a quadrilateral, and on a floor seen in
perspective every pool is flattened by `f = H_cam / d0`. The eval checks this
from the source, before rendering.
Choose the preset (`perspective-and-depth.md` §7): `painterly-perspective` is
the default for realistic scenes; `flat-vector` for stylized poster work. Sun
elevation from hour and latitude; shadow length = height / tan(elevation); all
shadows share one direction. Wind drives curtains, steam, rain shear.

### Stage 4 - Coordinate map
Markdown table in a comment: Entity | real size | s(y_foot) | drawn px | y |
contact check. Never guess a coordinate. Standing objects rest ON their support
(eval checks bottoms against the datum +/-4px for the foreground plane).

**Derive extents too, not just positions** (`perspective-and-depth.md` F7).
`drawn_px = real_m * k * s` on both axes, so a shape recipe with a local box of
`L` px is placed at `scale = real_m*k*s / L` - a derived number, never one tuned
until it looks right. Deriving only the y-values leaves a scene that is
internally consistent and absolutely wrong: the laundromat passed every check
with washers drawn at 0.35 x 0.49m, so a seated human out-scaled a commercial
machine 2x. Declare `SIZES` for every class the room is *about* and the eval
measures the rendered boxes back to metres (30% tolerance). An object stacked on
another shares its DEPTH, so it takes the same `s` - mark it
`data-floor="<ground y of its support chain>"` or the check reads the anchor row
and both of you will be wrong.

### Stage 5 - Emission
DOM order = build order = z-order, grouped as `<g id="phase-N-name">`:
```
1 Shell   2 Portals   3 Fixtures   4 Volumetrics
5 Furniture   6 Millwork   7 Occlusion   8 Foreground
```
Wall-anchored things (wainscot, paneling) belong to the SHELL so furniture
paints over them - a z-order bug here swallows whole objects.
Craft rules by preset (`perspective-and-depth.md` §§2-6): >=4 depth layers with
overlap; density floor (80 painterly / 30 flat) - but **the count is not the
point**: twelve identical clones of one machine satisfy every density rule and
read as a tiling. Repeats must differ in STATE (door open/ajar, running/idle),
AGE (wear, a replaced panel) and CONTENT (loaded, empty, occupied); the eval
warns when a symbol used 4+ times has fewer than `1 + n/4` variants;
>=3-stop gradients on large surfaces; one grain overlay at 0.04-0.06;
atmospheric veil per layer; blur-kit light in painterly (bloom that lands,
blurred tinted shadows, dark hems); silhouette-first object construction
(`shape-library.md` recipes fit flat-vector; adapt shading for painterly).
SVG budget < 20KB - it ships as a web asset.

### Stage 6 - Eval + scorecard loop (mandatory, non-skippable)

`python3 scripts/eval_scene.py <file>.html --render` until exit 0. **A PASS is
a structural floor, not a verdict** - it knows nothing about what real places
look like. Then render and LOOK:
```bash
# headless chrome reserves ~87px of the window for UI, so --window-size=1440,900
# paints only an 813px-tall viewport and the bottom of the shot is page
# background - which silently fakes a dark foreground band and corrupts the
# eval's void-cell check. Render taller, then crop to the true frame:
chrome --headless=new --disable-gpu --hide-scrollbars --window-size=1440,987 \
  --screenshot=/tmp/raw.png "file://$(pwd)/<file>.html"
python3 -c "from PIL import Image; \
  Image.open('/tmp/raw.png').convert('RGB').crop((0,0,1440,900)).save('/tmp/scene.png')"
```
If a scene shows a flat band across the very bottom, verify the renderer before
"fixing" the scene - matching the page background to hide it bakes a fake
shadow into the artwork.
View the PNG full-size plus >=2 crops at 2x (the star; the weakest region).
Score a WRITTEN scorecard against `references/quality-rubric.md`, comparing
side-by-side with the 2 nearest goldens in `references/quality/` and the owner
reference anchors. Fix every axis below 4 and re-render. Done = eval exit 0 AND
two consecutive renders with no axis below 4 AND (for new work) owner sign-off.
Minimum 3 look-rounds for any new typology or preset. Warnings: resolve or
state in writing why they stand (a sunset legitimately spans extra hue
families; the threshold is a proxy, the law is palette discipline).

## Testing the skill itself

| What | Command | Proves |
|---|---|---|
| every check fires | `python3 scripts/test_rules.py` | one violating fixture per rule; a check with no failing fixture is a comment, not a check |
| derivation rules bite | `python3 scripts/corpus_report.py builds/` | outputs SPREAD across scenes - clustering means the rule is dead even though every scene passes |
| it looks right | `references/quality-rubric.md` | the part no metric reaches |

See `TESTING.md`. Add a mutation to `test_rules.py` in the same commit as any new
eval check.

## References
| File | Load when |
|---|---|
| `references/art-direction.md` | always (Stage 2) |
| `references/perspective-and-depth.md` | always for painterly-perspective; depth/density rules for all |
| `references/quality-rubric.md` | always (Stage 6) |
| `references/typologies.md` | Stage 1 (worked examples of place research) |
| `references/shape-library.md` | Stage 5, flat-vector recipes + silhouette rules |
| `references/architectural-math.md` | non-standard canvases or objects |
| `references/forces-and-physics.md` | cables, rain, fans, steam |
| `references/telemetry-bindings.md` | live solar/weather/gaze scenes only |
| `TESTING.md` | changing the eval, or before a release |

## Examples (non-normative)
Only scenes built under the current laws ship in `builds/`. Everything earlier
lives in the sibling archive folder, because examples that contradict the rules
teach the wrong thing.
- `builds/13-laundromat-2am.html` - F7 extents; stacked units and `data-floor`
- `builds/14-bakery-oven-mouth-0410.html` + `14-bakery-stage0.md` - a low key
  light source, and a worked Stage 0 brief. Also the L9 counter-example: it
  scores 0.0% near-white and looks it.
- `builds/15-taverna-arch-1640.html` + `15-taverna-stage0.md` - L10 contre-jour,
  palette from illuminant x per-channel reflectance, F8 envelope
- `references/quality/calibration-round1-sheet.png` - the anti-goldens: seven
  early builds, flat cameras and one warm palette, before F1/F7/L9/L10 existed
- `shots/hearth-vs-view.png` - the same skill at 0.0% and 20% near-white
