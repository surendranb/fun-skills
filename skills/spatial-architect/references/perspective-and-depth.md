# Perspective, Depth & Painterly Rendering

The knowledge that closes the "reality gap": camera, depth layering, density,
and light rendering. Load for any scene using the `painterly-perspective` preset
(the default for realistic scenes), and for depth/density rules in any preset.

## 1. One-point perspective - still deterministic arithmetic

The flat elevation is a diagram viewpoint; realistic scenes need a camera. One-
point perspective keeps every position computable:

1. **Horizon**: pick the camera EYE HEIGHT in metres, then derive `y_h` from it.
   `y_h = y_ref - k*H_cam` (F1). Never pick `y_h` by eye - a horizon that "looks
   about right" on a 1440x900 canvas lands the camera at 1.2m, a seated eye level
   nobody chose. Standing 1.6m at k=288 puts the horizon 461px above the datum.
2. **Vanishing point**: one VP on the horizon, `(x_vp, y_h)`. Off-center beats
   centered (centered = symmetric = staged).
3. **Reference plane**: choose the foreground standing line `y_ref` (e.g. 810)
   where scale s=1.0 and `k` px = 1m (declare `SCALE` there, `DATUM y=y_ref`).
4. **Scale rule** (declare it in a PERSPECTIVE comment):
   `s(y_foot) = (y_foot - y_h) / (y_ref - y_h)`
   An object standing at y_foot is drawn at `h_px = real_m * k * s(y_foot)`.
   This governs **position and extent both**. Deriving only the `y` values and
   then sizing the object by eye produces a scene that is internally consistent
   and absolutely wrong - see F7, and declare `SIZES` so the eval can check it.
5. **Converging lines**: floor planks/tiles run from the bottom edge toward the
   VP; wall-floor junctions, counters and rails running "into" the scene follow
   lines through the VP. Objects facing the camera (tables, chairs, people) are
   drawn frontal and scaled by s - no skewing needed.
6. **Eval compatibility**: keep `DATUM` = the foreground reference plane and put
   at least one foreground object's feet exactly on it; declare the horizon, VP
   and scale rule in comments so the coordinate map stays auditable.

## 2. Depth layering - the anti-frieze law

A scene reads flat when objects sit side by side on one ground line (a frieze).
Build no fewer than FOUR depth layers, and make every layer partially occlude
the one behind it:

```
L1 foreground  (s~1.0-1.5, may crop out of frame, may blur slightly)
L2 subject     (s~0.8-1.0, the star lives here or in L3)
L3 midground   (s~0.4-0.7)
L4 background  (walls/windows/exterior, atmospheric)
```

Overlap is the strongest depth cue in flat rendering: a chair tucked so it
overlaps the table skirt, a lamp hanging in front of a window frame, a counter
cutting off the bottom of the view. If nothing overlaps, re-compose.

## 3. Density and occupancy - reality is cluttered

Real interiors hold hundreds of visible objects (count the bottles in any real
bistro photo). Sparse scenes read as renders, not places.
- painterly-realistic preset: >=80 drawn forms; walls and counters carry props
  (bottles, tags, frames, stacked bowls, hooks); "empty" areas are deliberate
  rest zones (~15-25% of canvas), placed to let the star breathe - not leftovers.
- flat-vector preset keeps the lighter >=30 floor.
- Repeats via defs/use with per-instance variation (scale .9-1.1, rotate -6..6,
  alternate 2 palette tones). Perfect rows read as clip-art; 60/40 ordered/loose.

## 4. Atmospheric decay

Each layer back loses ~10-20% contrast and saturation. Implement as a veil:
overlay the layer with the scene ink (dusk/night) or the light tint (day) at
0.05-0.15 opacity. Exteriors seen through openings get the strongest veil plus
simplified shapes (a roofline is a silhouette, not a building drawing).

## 5. Painterly light kit (no hard-edged light)

Define once:
```xml
<filter id="soft" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="5"/></filter>
<filter id="softer" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="12"/></filter>
<radialGradient id="bloom"><stop offset="0%" stop-color="{glow}" stop-opacity=".85"/>
<stop offset="45%" stop-color="{glow}" stop-opacity=".28"/><stop offset="100%" stop-color="{glow}" stop-opacity="0"/></radialGradient>
```
- **Bloom**: every emitting practical (lamp, lantern, neon, screen) gets a bright
  core + a bloom ellipse (radial gradient, often also blurred). Light must LAND:
  a pool on the nearest surface, a lit patch on the wall behind it.
- **Sun/moon pools**: polygons from the opening toward the light direction,
  filled with the glow tint at 0.1-0.25, `filter="url(#softer)"` - never hard edges.
- **Shadows**: blurred ellipses/paths in the scene's shadow tint (never black,
  never grey): mauve-violet for warm scenes, deep blue for night. Contact shadow
  (tight, darker) under every standing object + soft ambient pool.
- **Hems and undersides**: cloth hems, table undersides, jar bottoms get a
  darker band - bright-bottomed objects float and glow like lampshades.

## 6. No-outline construction (painterly presets)

Form comes from value and color, not ink lines:
- Every object = base tone + shadow-side tone + lit-edge tone (2-3 values from
  the palette; shade with ink overlays at .1-.25, light with glow overlays).
- Strokes are allowed only as MATERIAL - a chair spindle, a cable, a window
  mullion - colored as the material, never as a dark contour around a fill.
- **Silhouette-first**: before drawing any object, name the 2-3 features that
  make it THAT object (portafilter protrudes; Eiffel legs splay with open
  arches; a bentwood chair is hoops and turned legs; a chochin is a squat
  ellipsoid with rib lines). Build those features first, decorate second.
- Depth-of-field, sparingly: the L1 foreground crop may take stdDeviation 1-1.5.

## 7. Camera / preset choice (Stage 3 decision)

| Preset | Camera | Outlines | Light | Density floor | Use for |
|---|---|---|---|---|---|
| `flat-vector` | elevation | ink 2-2.5px | hard shapes ok | 30 | icons, posters, stylized UI art |
| `painterly-perspective` | one-point | none (material strokes only) | blur kit (§5) | 80 | realistic scenes - THE DEFAULT for "make it look real" |

Declare the preset in a `STYLE:` comment. The laws (scale, contact, one light
story, palette discipline, value planes) hold in both presets.

## 8. Light physics - emitters, footprints, shadows

Sections 1-7 are craft. This section is arithmetic: the consequences of a light
are *derived*, never eyeballed. Derive the footprint BEFORE drawing it, the same
way you derive a y-coordinate from a real height. `eval_scene.py` enforces the
parts that are pure geometry.

### 8.1 The laws

- **L1 - one emitter, one set of consequences.** Every emitter produces exactly
  one footprint per surface it reaches and one shadow per occluder. If a pool or
  a shadow exists, some declared emitter must own it.
- **L2 - a distant source has ONE world position.** The sun and the moon are at
  infinity: every aperture in the scene looks at the *same* sky. A second window
  does not get its own sun. Extend the edges of every shaft backwards - they must
  converge on that single disc. (How many suns a scene *should* have is a
  composition decision, not physics; this law only says they cannot multiply.)
- **L3 - the footprint is the emitter's shape, projected.** Not a decorative
  blob: the emitter's outline swept along the light direction onto the receiving
  surface, then foreshortened by the camera. A strip light cannot make a circle.
- **L4 - a shadow is the occluder's silhouette, projected from the emitter.**
  Same projection as L3, inverted: light-coloured region minus occluder.
- **L5 - edge softness is a ratio, not a style.** Penumbra grows with source size
  and with the gap between occluder and surface (F5). Contact edges are crisp;
  edges far from contact are soft. One blur value for everything reads as fog.
- **L6 - falloff.** Local sources fall off as 1/d^2 - halve the distance,
  quadruple the illuminance. Distant sources (sun, moon) do not fall off at all
  across a room, which is why sunlight lands with even brightness front to back
  and a lamp does not.
- **L7 - shadow colour is subtraction, not darkening.** A shadow is the surface
  still lit by ambient: surface albedo x ambient colour. Never black, never the
  surface tone with the saturation pulled out.
- **L8 - the count is a choice; the consistency is not.** You may run several
  emitters, but each one owes the scene its own complete, agreeing set of
  footprints and shadows. Two emitters and one shadow direction is a physics bug.

**L9 - own the value range.** A frame reads as luminous when it has true darks
to sit on, a broad middle, and a decisive area of near-white. Missing any of the
three reads as gloom or as wash, and *mean brightness is not the measure*: a
scene can average mid-grey and still be gloomy because nothing in it is actually
bright. Measured on the render:

| band | floor | what it is |
|---|---|---|
| above 85% luminance | >= 0.8% of frame | specular / the light itself / a lit white plane |
| above 60% luminance | >= 6% | lit territory |
| below 20% luminance | >= 1.5% | the dark anchor |

  A 2100K bakery interior scored **0.0%** above 85% and looked exactly like that
  number. A daylight classroom scored 33%. The fix is never a global brightness
  lift - it is giving the key something bright to land on.

**L10 - pick the light archetype deliberately; "sealed box, one warm source" is
the default failure.** Interior scenes converge on a hearth: a dim enclosure lit
by a single small warm emitter, because low key hides weak material rendering -
everything falls into shadow and nothing has to be modelled. Choose explicitly
from the range, and notice that most of it is not dim:

| archetype | key | character |
|---|---|---|
| flooded daylight | large window/opening, 5600K | high key, big bright planes, soft |
| sun shapes | direct sun through an aperture | hard-edged light figures on floor/wall, deep darks |
| contre-jour | bright opening behind the subject | silhouettes against near-white, glare bloom |
| overcast box | huge soft source | low contrast, material does all the work |
| bright artificial | shop/gallery/theatre | even, saturated, specular |
| mixed temperature | daylight + interior lamp | two whites in one frame, the classic |
| single warm source | lamp, fire, screen | the hearth - one option, not the default |
| starved | moonlight, safelight | deliberate; must still satisfy L9 somewhere |

  The skill exists for *interiors, often with a view outside*. A room with no
  relationship to the outside is the hardest kind to make stunning and the
  easiest to make gloomy - if you build one, that has to be a decision.

### 8.2 The formulas

Notation: `k` px per metre at the reference plane, `y_h` horizon row, `y_ref`
reference-plane row, `R = y_ref - y_h`, `s(y) = (y - y_h)/R`.

**F1 - camera height is not free.** The horizon sits exactly one camera-height
above the reference plane, in scaled pixels:

    R = k * H_cam          =>   H_cam = R / k

  Worked: k=288, y_h=470, y_ref=810 -> R=340 -> H_cam = 1.18 m. That is a seated
  eye level. If you wanted a standing camera (1.6 m) you must place the horizon
  at R = 288*1.6 = 461 px above the reference plane, not wherever it looked nice.

**F2 - floor foreshortening.** With the camera H_cam above the floor and the
reference plane d0 metres away:

    f = H_cam / d0         (screen height per screen width, for floor shapes)

  A circle of radius r metres lying on the floor at the reference plane draws as
  an ellipse:  rx = r*k,  ry = r*k*f.
  Worked: H_cam=1.18, d0=3.0 -> f=0.39. A 0.5 m pool -> rx=144, ry=56.
  **Consequence: on a floor, every pool is a wide flat ellipse.** A perfectly
  round pool in screen space is only correct on a wall or a tabletop seen
  face-on. This is why "point source -> circle" is wrong as a screen-space rule.

**F3 - footprint of an emitter on the floor.** Emitter with half-length `a`
(along its axis) and half-width `b`, hanging `h` metres above the surface, light
travelling straight down:

    footprint half-extents (metres):  a' = a + p,   b' = b + p     (p from F5)
    screen:  rx = a'*k*s,   ry = b'*k*s*f          (axis horizontal on screen)

  The emitter's own length adds to the width the camera already stretches, so a
  strip light's pool is *more* elongated than a bulb's, never less.
  Worked (greenhouse LED bar): a=0.6 m, b=0.04 m, h=1.2 m, p~0.3 ->
  a'=0.9, b'=0.34 -> at s=1, f=0.39: rx=259, ry=38. Aspect ~6.8:1.
  A pool drawn 90x86 is not a dimmer version of this - it is a different fixture.

  If the tube runs *away* from the camera (axis pointing at the vanishing point),
  its length is foreshortened instead of added; the pool narrows and its far end
  shrinks. Draw it as a tapered quad, not an ellipse.

**F4 - offset when the light is not straight down.** Light travelling at
elevation `e` from horizontal, azimuth `phi`:

    horizontal offset of the footprint centre = h / tan(e), along phi
    shadow length of an object of height h_o  = h_o / tan(e), along phi

  Every shadow in the scene shares `e` and `phi`, so shadow lengths differ only
  by object height. Two objects of equal height with unequal shadows is a bug.

**F5 - penumbra (edge softness).** For a source of size `S`, an occluder `g`
metres from the receiving surface, and source-to-occluder distance `D`:

    p = S * g / D

  Worked: a 0.6 m strip 1.2 m above a bench, object sitting ON the bench (g~0) ->
  p~0 -> crisp contact edge. The same strip, object 0.4 m above the bench ->
  p = 0.6*0.4/0.8 = 0.3 m = 86 px at k=288. So: crisp where things touch, soft
  where they do not. Use at least two blur values per scene, not one.

**F6 - relative brightness.** For local sources, illuminance ~ I / d^2. When two
lamps of equal power hang at 1.2 m and 2.4 m above a counter, the far one lands a
pool a quarter as bright - not "slightly dimmer". For sun and moon, d^2 is
constant across the room: sunlit patches at the front and back of a floor are the
same brightness, and only the camera's atmospheric veil separates them.

**F7 - extents. The metric law governs SIZE, not just position.**
Every drawn dimension of an object is fixed by the same arithmetic as its
position. There is no free parameter:

    drawn_px = real_m * k * s          (both axes, for a frontal object)

  A shape recipe drawn in its own local box of `L` px is therefore placed with

    transform = translate(x, y) scale(real_m * k * s / L)

  and the multiplier is *derived*, never tuned until it looks right.

  **Why this needs its own law.** F1-F6 make a scene internally consistent: the
  floor, the shadows and the y-values all agree. They say nothing about absolute
  size, so an entire class of objects can be drawn at half scale and every other
  check still passes. That is what happened in the laundromat: every `y` was
  derived correctly, and the washers came out 0.35 x 0.49 m - mini-fridges - so a
  seated human out-scaled a commercial washer by 2x. The scene was arithmetically
  perfect and unmistakably fake.

  **Aspect is part of it.** A recipe's local box must match the object's real
  aspect ratio before it is scaled, or one axis is wrong even when the other is
  right. Real front-load washer 0.85 x 1.10 m -> aspect 0.773 -> local box
  110 x 142 (0.775). Check the recipe, not just the transform.

  **Depth, not screen row.** `s` is a property of an object's DEPTH. A unit
  stacked 1.1 m on top of another sits at the *same depth* as the one below it
  and takes the *same* `s`, even though its anchor is 300px higher on screen.
  Mark it `data-floor="<y of the ground its support chain reaches>"` so the
  derivation - and the eval - use depth rather than the anchor row.

  Declare the result so it is checkable:
  `<!-- SIZES: washer=0.85x1.10 | bench=1.60x0.89 | cart=0.75x0.85 -->`
  The eval measures each element's rendered bounding box back through
  `real_m = px / (k*s)` and errors outside 30%.

**F8 - the envelope closes.** The room is a fixed number of metres and the
floor is fully spent: every metre across any axis is either an object footprint
or circulation.

    sum(footprints + circulation) = room dimension        (per axis)

  Worked (laundromat): two banks of 0.85m-deep machines facing each other across
  a 2.40m aisle needs 0.85 + 2.40 + 0.85 = 4.10m of room width. Declare it:

    <!-- ROOM: 4.20w x 6.00d x 2.70h -->
    <!-- SPAN width: washers=0.85 aisle=2.40 washers=0.85 -->

  **Why this is the cheapest check in the skill.** It runs on two comments,
  before a single coordinate exists, and it catches the one class of error no
  pixel measurement can reach: a plan that is not physically possible in the room
  it claims to be in. Perspective arithmetic will happily render an impossible
  floor plan perfectly. Circulation has hard minima - 0.75m for one person to
  pass, 1.10m for two-way - and an aisle below those is a plan error, not a tight
  composition.

  The corollary is that Stage 0 is not paperwork. Until the envelope is stated,
  "the machines should be huge" and "the machines are 0.85m wide" are the same
  sentence with no way to tell which one the scene obeys.

### 8.3 Declare the rig

Put the emitters in a machine-readable comment next to SCALE and PERSPECTIVE, and
give every pool element an id:

    <!-- LIGHTS: sun=sun@1300,430
               | bar1=tube@620,300;axis=0;pool=pool-bar1
               | lamp=point@150,150;pool=pool-lamp
               | win=window@980,300;pool=pool-win -->

kinds: `sun` / `moon` (distant, no local footprint), `point` (bulb, pendant),
`tube` (strip, batten, LED bar), `area` (softbox, glowing panel), `window`
(aperture). `axis` is the emitter's long axis in screen degrees, 0 = horizontal.
`pool` is the id of the element that draws where its light lands.

`eval_scene.py` then enforces, from the source and without rendering:
a tube's pool must be elongated along its axis (F3); a window's pool must be a
quadrilateral, not an ellipse (a rectangle projects to a skewed rectangle); a
compact source's floor pool must be horizontally flattened (F2); and every
declared pool id must exist.

What the eval CANNOT judge, and the visual review must: whether the number of
sources is right, whether a shaft actually points back at its sun, whether the
light *reads* as that time of day, and whether the rim light on an object looks
like light or like a scratch.
