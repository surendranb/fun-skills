# Typology Library (v1: indoor)

A typology is what makes a scene read as *that place* instead of "a room".
Use the signature checklist; use the precomputed y-coordinates (288px/m, datum 720).

---

## Specialty Coffee Shop

### Dimension table (precomputed)
| Element | Real height | y |
|---|---|---|
| Ceiling | 2.60-3.00m | above frame or y=0 |
| Pendant lamp shade bottom | ~2.05m over counter | y~130 |
| Menu chalkboard top / bottom | 2.00m / 1.20m | y=144 / y=374 |
| Back-bar shelf (cups, bags) | 1.50-1.80m | y=204-288 |
| Bar counter top (customer side) | 1.05-1.10m | y=408-424 |
| Service counter work surface | 0.90m | y=461 |
| Pastry case top | 1.20-1.30m | y=346-375 |
| Stool seat | 0.65-0.75m | y=504-533 |
| Floor datum | 0.00m | y=720 |

### Signature elements (need >=4)
- [ ] Espresso machine on service counter (the usual focal object)
- [ ] Menu board: handwritten-style chalk text, tilted items
- [ ] Pendant lamps hanging LOW over counter (~75cm clearance to surface)
- [ ] Pastry case with glass front + visible shelves
- [ ] Cup rows on back-bar shelf, bagged beans (60/40 stacking)
- [ ] Steam: wand steam during use, or cup steam plume shearing with W

### Materials & palette
Walnut + brass + terrazzo/concrete + cream plaster. Use `Cafe Morning` palette
(art-direction.md). Steam = light gray strokes, never white-on-white.

### Failure modes
Machine floating above counter (contact!), pendants at eye height (they hang low),
menu board with generic sans-serif text, everything centered.

---

## Homelab / Desk Biome

### Dimension table (precomputed)
| Element | Real height | y |
|---|---|---|
| Cable tray / track light | 2.25m | y=72 |
| 42U rack top | 2.00m | y=144 |
| Monitor top edge (27in on riser) | ~1.35m | y=331 |
| Eye line (seated) | ~1.20m | y=374 |
| Desk surface | 0.75m | y=504 |
| Keyboard deck | desk - 2cm | y=498 |
| Chair seat | 0.45m | y=590 |
| Floor datum | 0.00m | y=720 |

### Signature elements (need >=4)
- [ ] Monitor(s) with dark screen OR terminal glow; thin bezels
- [ ] Cable management: catenary sags to floor, velcro'd bundles (straight lines = fail)
- [ ] Rack or NAS shelf with blinking LEDs (amber/green, 2-3px)
- [ ] LED strip under shelf/desk casting upward glow on wall
- [ ] Mechanical keyboard, mouse, mug (steam optional)
- [ ] Plant or headphones for silhouette interest

### Materials & palette
Matte black steel + pine desktop + cable spaghetti. Use `Homelab Dusk` palette.
Screens emit; they do not reflect full-room brightness.

### Failure modes
Straight power cables, monitor floating off desk edge, LEDs lighting nothing,
rack proportions wrong (42U is TALL - nearly full wall), screen brighter than room.

---

## Independent Bookstore

### Dimension table (precomputed)
| Element | Real height | y |
|---|---|---|
| Tall stack shelving top | 2.15m | y=101 |
| Shelf bands | 1.75 / 1.30 / 0.85m | y=216 / 346 / 475 |
| Counter / display table top | 0.95m | y=446 |
| Reading armchair back top / seat | 0.95m / 0.42m | y=446 / y=599 |
| Side table | 0.55m | y=622 |
| Window head / sill | 2.20m / 0.97m | y=87 / y=440 (W=404, H=353) |
| Pendant / lamp shade bottom | ~1.95m | y=158 |
| Floor datum | 0.00m | y=720 |

### Signature elements (need >=6)
- [ ] Rolling ladder on the stack shelving (rails + rungs + base wheels)
- [ ] Book spines as vertical texture (60/40 ordered/loose; varied heights, tilts, colors)
- [ ] Reading armchair + side table + stack of books (the usual focal object)
- [ ] Warm reading lamp over the nook - the ONE glow
- [ ] Rain-streaked window, grey street beyond (diagonal streaks sheared by W, atmospheric fade)
- [ ] New arrivals display table
- [ ] Handwritten recommendation cards / chalk sign

### Materials & palette
Oak/walnut stacks + brass fittings + paper cream + one upholstered warm chair. Exterior
grey-blue and ~20% desaturated. Use `Bookshop Rain` palette (art-direction.md). Interior
must read WARM against the cold window; shadows tinted toward cool slate.

### Failure modes
Books as uniform color blocks (vary spine heights/tilts/colors), rain as straight vertical
lines (diagonal, sheared by wind), cold interior (paper/wood/brass warmth required),
lamp glow lighting nothing (pool + lit surfaces must agree), uniform shelf rows
(perfect grids read as clip-art).

---

## Retro Parisian Riverside Bistro

### Dimension table (precomputed)
| Element | Real height | y |
|---|---|---|
| Awning valance bottom | ~2.2m | y=90 |
| Chalkboard top / bottom | 1.9m / 1.35m | y=173 / y=332 |
| Back-bar shelf | 1.18m | y=380 |
| Zinc counter top (bullnose lip) | 1.05m | y=418 (lip ~y=406) |
| Parapet / quai wall top | 0.95m | y=446 |
| Wrought-iron rail top | 1.15m | y=418 |
| Bistro table top (round marble) | 0.70-0.72m | y=507-513 |
| Bistro chair seat | 0.45-0.46m | y=590 |
| Floor datum | 0.00m | y=720 |

### Signature elements (need >=6)
- [ ] Striped awning (red-and-cream or green-and-cream - NOT brown/tan) with a
      scalloped valance, cafe name lettered in a thin gold serif
- [ ] Zinc bar counter: curved/bullnose front lip, brass foot rail, bottles or
      glasses visible on top - a flat blank rectangle reads as a fridge, not a bar
- [ ] Round marble-top bistro tables on a single BLACK WROUGHT-IRON pedestal,
      never wood - the iron is what makes it read as European street furniture
- [ ] Bentwood (Thonet-style) or caned bistro chairs
- [ ] Black-and-white or red-and-white checker tile floor
- [ ] Haussmannian mansard-roof skyline across the river: a tall flat-fronted
      body, a shallow sloped roof band, a small dormer bump - NOT a pointed
      cottage roof, which reads as a generic village rather than Paris
- [ ] A named landmark (Eiffel Tower, etc.) built from its real silhouette -
      e.g. the Tower's splayed, arched legs with visible negative space at the
      base, not a solid tapering cone
- [ ] Small round wall mirror, brass/gilt frame - near-universal in real bistro
      interiors and an easy way to break up a flat wall

### Materials & palette
Cream stone + black wrought iron + brass + white/grey marble + zinc grey. Put the
awning and floor tile in ONE saturated accent - a true red (`#A3293A` family) or
bottle green - not a muddy warm brown-burgundy, which reads Americana diner rather
than Paris. Exterior: dusk or daylight sky, water in cool violet/blue-grey. Reserve
warm browns for wood trim only (shelf, chair); the counter and table legs must NOT
be brown - that single substitution is the fastest way to lose "Paris."

### Failure modes
Zinc counter drawn as a flat rectangle (always give it a bullnose top, a rail, and
visible bottles or it reads as an appliance); table legs in wood instead of black
iron; skyline buildings with pointed cottage roofs instead of mansard silhouettes
(the single biggest tell that breaks "Paris" besides the landmark itself); awning/
floor palette drifting warm-brown instead of a true saturated red or green; a named
landmark drawn from a generic "tower" template instead of its real silhouette -
the shape itself is what makes it recognizable, not the label in a comment.

---

## Adding a typology later
Requirements: sourced dimension table, >=6 signature elements, material list,
palette anchor, failure modes. One typology per build session; verify every metric
against a real source (Neufert-class reference or manufacturer spec) before it lands here.
