# Art Direction Reference

Geometry makes a scene correct. This file makes it beautiful. Apply Stage 5 fully.

## 1. Value structure (the single biggest quality lever)

Every scene has three tonal planes. Decide them BEFORE drawing:

| Plane | Role | Day scene | Night scene |
|---|---|---|---|
| Background (walls, window sky) | sets atmosphere | lightest tones | deep but not black |
| Midground (furniture, counter) | carries subject | mid tones | mid tones, lit faces |
| Foreground accents (chair back, plant) | frames, adds depth | darkest accents + brightest highlights | near-silhouette |

Test: squint at your planned scene. If all planes read the same tone, it will look
flat no matter how correct the geometry is. Fix the plan, not the pixels.

## 2. Palettes - DERIVE one per scene; never default to a stored anchor

5-14 colors including exactly one ink. A palette is not picked from a list - it is
derived, or every scene converges on the same warm cream/brown cliche. Derivation:

1. **Light temperature** from the brief's time and weather: dawn rose-gold, noon
   near-white, golden-hour amber, dusk violet-orange, night cool blue + warm
   practicals, overcast desaturated grey-green. This tints EVERYTHING.
2. **Material truth** of the place: list the real materials from the typology or
   place research (zinc = grey, tatami = straw, marble = white/grey veined,
   terracotta = orange). Their honest colors, shifted by step 1, are the mid tones.
3. **One identity accent** taken from the place itself, not from taste: the awning
   red of a bistro, the pink facade of La Maison Rose, the amber LEDs of a homelab.
   <=15% of canvas area.
4. **The check**: if the finished palette would also fit a completely different
   place and hour, it is generic - re-derive. A Kyoto teahouse at dawn and a Paris
   bistro at dusk must NOT share a palette.

Worked examples (historical anchors - examples of the procedure's OUTPUT, not a
menu to choose from):

**Cafe Morning** (warm light)
- ink `#001858` navy
- cream `#FEF6E4`, sand `#F2E3C9`, walnut `#8A5A3B`, espresso `#4A2F23`
- terracotta `#E07850`, brass `#C89B3C`, sage `#7FA08C`

**Homelab Dusk** (warm-cool contrast)
- ink `#1B1B2F`
- paper `#F5F1E8`, slate `#5C6B73`, steel-blue `#8BD3DD`
- amber LED `#FFB454`, pine `#C9A87C`, graphite `#3D3D52`

**Bookshop Rain** (warm interior / cold wet window)
- ink `#26324A`, shadow slate `#2E3D5C`
- paper `#F6EFE0`, sand `#EADFC8`, sand-deep `#D8CBAD`
- oak `#C9A87C`, walnut `#8A5A3B`, espresso `#5C4030`, brass `#C89B3C`, rust `#B65C3F`
- lamp warm `#FFD9A0`; exterior: sky `#C7D2DC`, slate `#93A5B4`, slate-deep `#5C6E7E`

Rules:
- Ink does double duty as outline and text; never pure black `#000000`.
- Warm scenes: cool accent for balance (teal/sage). Cool scenes: warm accent.
- Accent colors get <=15% of canvas area. If everything is accented, nothing is.

## 3. Shadows - colored, never black

Real shadows are the scene color minus direct light plus ambient skylight:
they shift toward blue/indigo and drop opacity, they do not go black.

Recipe: take the floor/wall color under the object, mix ~30% toward indigo
(`#2B2B5C` family), render at opacity 0.14-0.22.

```xml
<ellipse cx="850" cy="722" rx="120" ry="10" fill="#2B2B5C" opacity="0.16"/>
```

Contact shadows (directly under an object edge) are tighter and slightly darker;
cast shadows (offset along L) are longer and lighter. Both share the same direction.

## 4. Gradients and two-tone construction

Any surface larger than ~100px gets >=3-stop gradients with subtle hue shifts, never two flat stops.

```xml
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%"  stop-color="#FEF6E4"/>
  <stop offset="55%" stop-color="#F7EBD4"/>
  <stop offset="100%" stop-color="#EDDCBF"/>
</linearGradient>
```

Hue-shift rule: move stop hues 3-8 degrees warmer toward the light side, cooler away.
Vertical surfaces darken toward the floor (bounce light is weaker than sky light).

**Two-tone rule (the anti-flat law):** no discrete object larger than ~80px ships as
one flat fill + outline. Every object carries:
1. base tone
2. shadow-side overlay - ink at .12-.18 opacity, on the side away from the key light
3. lit-edge accent - 1.5-2px line in a lighter tone along the key-light side

```xml
<rect x="0" y="0" width="120" height="60" fill="#8A5A3B"/>
<rect x="0" y="0" width="26" height="60" fill="#001858" opacity=".14"/>  <!-- shade -->
<line x1="119" y1="1" x2="119" y2="59" stroke="#FFD9A0" stroke-width="2" opacity=".6"/>
```

This single habit is most of the gap between "generated" and "authored".

## 5. Lighting hierarchy

1. **Key**: one directional source (sun through window, or strongest practical).
   Declared in Force Fields; every highlight and shadow agrees with it.
2. **Glow**: max ONE radial warm glow per scene (pendant, lamp, screen). Falloff to
   zero by 60% radius. Two competing glows = amateur.
3. **Rim/accent**: thin bright edge on 1-2 focal objects facing the key light.
   A 1.5px lighter stroke on the lit side reads as craft.

Sun shafts: polygon from window aperture along L, fill = warm white at 0.10-0.18
opacity, soft edges via blur filter if needed. Add 3-6 dust motes (1.5-2.5px circles,
same tint, 0.3-0.5 opacity) inside the shaft.

## 6. Texture - kill the digital flatness

Define once in defs, reference once on top of everything:

```xml
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.8"
  numOctaves="2" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>
...
<rect width="1440" height="900" filter="url(#grain)" opacity="0.05"
  style="mix-blend-mode:multiply" pointer-events="none"/>
```

Opacity 0.04-0.06. Above 0.08 looks dirty. On light themes use multiply blend;
this single layer is what separates "AI-flat" from "printed".

## 7. Composition

- Focal zone (espresso machine, monitor setup, rack) sits on a third line, not center.
- Negative space >= 40% of canvas. Crowded = cheap.
- One foreground framing element entering from an edge (chair back, plant leaf,
  shelf corner) adds depth in every pro scene. Exactly one.
- Repeated items (cups, books, servers): vary size/rotation slightly; stack with the
  60/40 rule (60% ordered, 40% loose). Perfect grids read as clip-art.

## 8. Depth cues (flat-style legal)

- Atmospheric fade: things seen through windows lose saturation and contrast (~20%).
- Overlap beats outline: let shapes occlude instead of outlining everything.
- Floor: plank/tile lines converge very slightly toward datum edges; keep it subtle.
