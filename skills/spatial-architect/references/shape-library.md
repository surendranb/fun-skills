# Shape Library - worked examples of silhouette-first construction

**This is a set of examples, not a menu of allowed objects.** The law is the
METHOD below; the recipes exist to show what the method produces. A scene needing
a kerosene stove, a lathe or a rolling ladder is not blocked - you derive it the
same way these were derived. Never let a missing recipe push you toward a generic
substitute.

## The method (applies to every object, in or out of this file)
1. Name the 2-3 features that make the object THAT object and nothing else - the
   portafilter must protrude past the machine body; a monstera leaf needs deep
   notches cut from the outer edge; the Eiffel Tower's legs splay with open arch
   underneath; a bentwood chair is hoops and turned legs. Get these first.
2. Get its real-world size, and scale from it via k (and s(y) in perspective).
3. Build the silhouette from primitives, then shade: base tone + shadow-side tone
   + lit edge. Decoration comes last and is optional.
4. Check the result at arm's length: does it read as its subject with the caption
   hidden? If not, the silhouette is wrong - fix that, not the detail.

These recipes are written for the `flat-vector` preset (ink outlines, 2-2.5px).
For `painterly-perspective`, keep the silhouettes and drop the outlines: form
comes from value, and strokes survive only where they are real material.

COPY the recipes below when they fit,
place with `transform="translate(x y) scale(s)"`, vary size/rotation <=10%, and
only then customize. All recipes live in a local box (stated per shape) with the
origin at the shape's anchor point (usually its floor/base contact).

Conventions:
- stroke: ink color, 2-2.5px, `stroke-linejoin="round"`
- shading: overlay the INK color at opacity .10-.18 on the shadow side (never new hexes)
- every recipe states its real-world size so metric math picks the scale for you

## Props

### Cup/mug (36x34, anchor = base, real: 9cm tall -> 26px)
```xml
<g id="mug">
  <path d="M4 0 h24 q2 0 2 3 v18 q0 8 -9 8 h-10 q-9 0 -9 -8 V3 q0 -3 2 -3 Z"/>
  <path d="M30 7 q10 1 9 8 q-1 7 -10 6" fill="none"/>
  <ellipse cx="17" cy="2" rx="12" ry="3" fill="{lighter}"/>
</g>
```

### Bean bag / coffee sack (30x26, anchor = base)
```xml
<g id="sack">
  <path d="M2 0 v-14 q0 -10 12 -10 h2 q12 0 12 10 V0 Z"/>
  <path d="M6 -16 h18" stroke-width="1.5"/>
  <circle cx="15" cy="-8" r="1.6" fill="{ink}" stroke="none"/>
</g>
```

### Storage jar (26x30, anchor = base)
```xml
<g id="jar">
  <rect x="2" y="-24" width="22" height="24" rx="4"/>
  <rect x="5" y="-30" width="16" height="7" rx="2"/>
</g>
```

### Potted plant - monstera (140x150, anchor = pot base; real: 50cm -> 144px)
Split-leaf construction: each leaf is a lobed blade with DEEP notches cut from the
outer edge (a solid oval with holes reads as a ball, not a leaf). 2-3 leaves at
different angles + one drooping.
```xml
<g id="monstera">
  <path d="M-22 0 h44 l-6 -28 h-32 Z"/>                            <!-- pot -->
  <rect x="-27" y="-35" width="54" height="9" rx="2"/>             <!-- rim -->
  <path d="M0 -35 Q-2 -60 0 -78" fill="none" stroke-width="3"/>    <!-- stem -->
  <!-- big leaf, deep splits: outer lobes connected near the midrib -->
  <path d="M0 -78 Q-26 -84 -38 -70 L-16 -60 Q-40 -58 -44 -42 L-18 -42
           Q-36 -32 -30 -18 L-10 -30 Q-12 -16 -2 -12 Q8 -16 8 -30 L26 -20
           Q34 -32 18 -42 L42 -44 Q40 -58 16 -60 L36 -72 Q24 -84 0 -78 Z"/>
  <!-- second leaf, rotated via separate path angled right -->
  <path d="M2 -50 Q22 -60 34 -52 L20 -44 Q38 -42 40 -30 L22 -32 Q32 -24 26 -14
           L10 -24 Q8 -14 0 -12 L0 -50 Z"/>
</g>
```

### Pendant lamp (56x40 below cord, anchor = cord top)
```xml
<g id="pendant">
  <line x1="0" y1="0" x2="0" y2="{drop}"/>
  <path d="M-26 {drop+34} L-8 {drop} q8 -4 16 0 L26 {drop+34} Z"/> <!-- cone -->
  <ellipse cx="0" cy="{drop+35}" rx="9" ry="4" fill="{bulb}"/>
</g>
```

### Bar stool (64x100, anchor = floor; real: seat 65cm -> 187px)
```xml
<g id="stool">
  <rect x="-32" y="-100" width="64" height="14" rx="7"/>
  <line x1="-22" y1="-86" x2="-28" y2="0"/>
  <line x1="22" y1="-86" x2="28" y2="0"/>
  <line x1="-26" y1="-30" x2="26" y2="-30" stroke-width="4"/>
  <line x1="-24" y1="-14" x2="24" y2="-14" stroke-width="4"/>
</g>
```

### Curtain - gathered panel (70 wide x H, anchor = rod attach)
```xml
<g id="curtain"> <!-- H = rod y to sill y; folds via inner strokes -->
  <path d="M0 0 H56 Q50 {H*.4} 40 {H*.75} Q34 {H*.95} 20 {H} Q6 {H*.9} 8 {H*.5}
           Q10 {H*.2} 0 0 Z"/>
  <path d="M14 {H*.1} Q10 {H*.5} 18 {H*.9} M30 {H*.05} Q26 {H*.45} 32 {H*.85}"
        fill="none" stroke-opacity=".25" stroke-width="1.5"/>
</g>
```

## Furniture / architecture

### Espresso machine (140x115, anchor = base on counter; real: 42cm -> 121px)
Silhouette rules: taller than wide reads "espresso", the portafilter handle MUST
protrude past the body edge, group head sits low-center, wand hugs the body side.
```xml
<g id="espresso">
  <rect x="10" y="-115" width="120" height="115" rx="7"/>            <!-- body -->
  <rect x="10" y="-115" width="120" height="14" rx="7" fill="{brass}"/> <!-- top -->
  <rect x="24" y="-101" width="92" height="10" fill="{light}" opacity=".25"/>
  <circle cx="36" cy="-84" r="8" fill="{light}"/>                    <!-- gauge -->
  <line x1="36" y1="-84" x2="40" y2="-89" stroke-width="2"/>
  <rect x="30" y="-38" width="90" height="16" rx="3"/>               <!-- group housing -->
  <rect x="60" y="-22" width="30" height="6" rx="2" fill="{brass}"/> <!-- drip tray -->
  <path d="M68 -22 v5 m12 -5 v5" stroke-width="3"/>                  <!-- spouts -->
  <rect x="118" y="-34" width="26" height="8" rx="4" fill="{brass}"/><!-- handle OUT -->
  <line x1="130" y1="-52" x2="118" y2="-34" stroke-width="4" stroke-linecap="round"/> <!-- wand -->
</g>
```

### Counter/bar (W x H=259px for 0.90m, anchor = floor)
```xml
<g id="counter">
  <rect x="0" y="-259" width="{W}" height="18" fill="{wood-mid}"/>   <!-- top -->
  <rect x="8" y="-241" width="{W-16}" height="241" fill="{wood}"/>   <!-- front -->
  <line x1="0" y1="-241" x2="{W}" y2="-241" stroke-width="2.5"/>
  <line x1="{W*.2}" y1="-241" x2="{W*.2}" y2="0" stroke-opacity=".3"/>
  <line x1="{W*.55}" y1="-241" x2="{W*.55}" y2="0" stroke-opacity=".3"/>
  <line x1="0" y1="-80" x2="{W}" y2="-80" stroke="{brass}" stroke-width="5"/> <!-- rail -->
</g>
```

### Window (W x H, anchor = sill-left; sill 0.97m, head 2.20m -> H=353px)
```xml
<g id="window">
  <rect x="-12" y="-{H-14}" width="{W+24}" height="{H}" rx="4" fill="{frame}"/>
  <rect x="0" y="-{H-26}" width="{W}" height="{H-40}" fill="url(#skyGrad)"/>
  <line x1="{W/2}" y1="-{H-26}" x2="{W/2}" y2="-26" stroke-width="3"/>  <!-- mullion -->
  <rect x="0" y="-{H-26}" width="{W}" height="{H-40}" fill="none" stroke-width="3"/>
  <rect x="-18" y="0" width="{W+36}" height="14" fill="{frame-dark}"/>  <!-- sill lip -->
</g>
```

### Chalkboard menu (W=260 H=230, anchor = top-left; 2.0m -> 1.2m)
```xml
<g id="menu">
  <rect width="260" height="230" rx="6" fill="{board}"/>
  <rect x="12" y="12" width="236" height="206" rx="3" fill="none" stroke="{brass}" stroke-width="2"/>
  <!-- chalk text = squiggle paths, 3px round caps, .85 opacity; prices in accent -->
</g>
```

### Wall shelf (L x 10, anchor = left end; brackets every ~120px)
```xml
<g id="shelf">
  <rect width="{L}" height="10"/>
  <path d="M20 10 v14 h10 M{L-30} 10 v14 h10" fill="none" stroke-width="3"/> <!-- brackets -->
</g>
```

### Desk (homelab; W x 216px = 0.75m, anchor = floor)
```xml
<g id="desk">
  <rect x="0" y="-216" width="{W}" height="16" rx="2" fill="{wood}"/>
  <rect x="14" y="-200" width="10" height="200" fill="{steel}"/>
  <rect x="{W-24}" y="-200" width="10" height="200" fill="{steel}"/>
  <line x1="19" y1="-60" x2="{W-19}" y2="-60" stroke="{steel}" stroke-width="6"/> <!-- crossbar -->
</g>
```

### Monitor 27in (96x60 screen + stand, anchor = base on desk; top edge ~1.35m seated)
```xml
<g id="monitor">
  <rect x="-48" y="-118" width="96" height="60" rx="4" fill="{ink}"/>
  <rect x="-43" y="-113" width="86" height="50" rx="2" fill="{screen}"/>
  <path d="M0 -58 v22" stroke="{steel}" stroke-width="6"/>
  <rect x="-26" y="-36" width="52" height="5" rx="2" fill="{steel}"/>
</g>
```

### Server rack 42U (110x576, anchor = floor; 2.0m tall)
```xml
<g id="rack">
  <rect x="0" y="-576" width="110" height="576" rx="4"/>
  <!-- unit seams every 14px: <line> stroke-opacity .25 -->
  <!-- 2-3 LED pairs per few units: r=2 circles {amber}/{green} -->
  <rect x="8" y="-560" width="94" height="544" fill="none" stroke-opacity=".4"/>
</g>
```

### Keyboard (110x18, anchor = base on desk)
```xml
<g id="keyboard">
  <rect x="0" y="-18" width="110" height="18" rx="3"/>
  <path d="M8 -13 h94 M8 -8 h94 M14 -3 h82" stroke-opacity=".3" stroke-width="1.5"/>
</g>
```

## Usage rules
1. Place via `<use href="#id" x y transform>` or `<g transform>`; scale from real-world
   size via k (288px/m) - never eyeball scale.
2. Vary repeats: rotation -4..4deg, scale .92-1.08, alternate fill between two palette
   tones. Identical clones read as clip-art.
3. **Two-tone rule: every shape larger than ~80px ships pre-shaded.** Base tone +
   shadow-side overlay (ink at .12-.18 opacity) + a lit-edge line (1.5-2px, lighter
   tone or glow tint) on the side facing the key light. Recipes above show the
   pattern: shade path + rim line are PART of the recipe, not optional dressing.
   A flat single-tone shape with an outline is the #1 tell of amateur vector work.
4. Ground large objects: a rug, mat, or tonal band under furniture clusters anchors
   them to the floor plane. Floating-on-planks reads unfinished.
5. Anything not in this library: derive it with the method at the top of this file
   and build it from primitives with the same conventions. Do NOT stall, and do NOT
   swap in a generic stand-in because no recipe exists. Adding a proven recipe back
   here afterwards is welcome but never a precondition for building the scene.
