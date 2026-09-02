# Lessons - what this skill learned the hard way

Every law in this skill exists because a scene failed without it. This file is
the reasoning, kept because the reasoning generalizes further than the SVG does:
most of it applies to any generator that has an eval attached.

If you are extending this skill, read this before adding a rule. Several of the
mistakes below were made *twice*.

---

## 1. Describe the space before you draw it

The first failure of every scene was upstream of any geometry: nothing ever
asked what the room *was*.

Given "a laundromat", a model produces `[washers, bench, cart]` and distributes
them along whatever surfaces exist. What it does not produce, unprompted, is the
observation that a laundromat is **a narrow aisle between two walls of large
machines** - which is the only fact that matters for whether the picture reads.
The props were all correct. The topology was never stated, so it was never built.

**The generalization:** a list of parts is not a description of a thing. Before
generating, force a statement of the artifact's *structure* - what dominates,
what faces what, what the arrangement is for. Stage 0 exists for this.

## 2. Derive the constraints this instance imposes

The skill's laws are generic: gravity, contact, light, perspective. Generic laws
cannot know that washing machines need plumbing and therefore stand against
walls and never free-standing; that their doors swing into the aisle; that
classroom desks face one way because attention has a direction.

That reasoning never happened because nothing asked for it. A generic rule set
gives you a room that obeys physics and still looks like a showroom.

**The generalization:** ask the model to enumerate the constraints *this* case
imposes, in addition to applying the constraints you shipped. The instance
always knows things the framework cannot.

## 3. A passing check means "no known violation", never "good"

For most of this project the loop was: run the eval, fix what it says, stop when
green. Four iterations, every time. The eval is a structural floor - it knows
nothing about what real places look like - and it was being read as a verdict.

The fix is not a better eval. It is a **stopping rule that lives outside the
eval**: a written scorecard against a rubric, two consecutive clean rounds, and
owner sign-off. If the only thing that can end the loop is the thing being
optimized, the loop optimizes for the metric.

## 4. Encode causes, not consequences

Compare two rules that describe the same phenomenon:

- *"Shadows should be soft."*
- *`p = S * g / D`* - penumbra from source size, gap, and distance.

The first is a taste statement, and taste statements **converge**: every scene
gets the same soft shadow, because there is nothing in the rule that varies with
the scene. The second is a formula whose inputs come from the scene, so it
produces a different answer for a strip light over a bench than for the sun.

The palette rule is still in the broken state as of this writing - "light
temperature x material truth x one identity accent" is taste, and the corpus
report duly shows a noon mountain teahouse and an overcast construction site
with palette signatures 0.05 apart, which no honest derivation could produce.

**Test for this:** if you cannot write the rule as an expression with scene
inputs, you have not finished understanding it. Ship the expression.

## 5. A check without a failing fixture is a comment

Every check in this project was, for months, validated only by running it on
scenes that passed. That proves the absence of false positives and *nothing
else*. A check that can never fire - a typo'd regex, a wrong key, an early
return - is indistinguishable from a working one under that test.

Two bugs survived a long time this way. The SVG path parser was mis-reading
every shorthand command (`v10 h8` read as the point `(10,8)`), inventing
collisions nobody traced back. And the very first version of the F8 envelope
check silently swallowed the *next* declaration into its sum, so every scene
would have mis-added - caught within a minute of writing its fixture, and not
before.

**Rule:** when you add a check, add a fixture that violates exactly it, in the
same commit. `test_rules.py`, and both directions every time.

## 6. Self-consistency is not truth

F1-F6 are all *relational*: they constrain how quantities relate to each other.
Nothing anchored an absolute. So a scene could satisfy every check while every
object in a class was drawn at a third of its real size - the laundromat's
washers came out 0.35 x 0.49m, mini-fridges, and a seated human out-scaled a
commercial machine by 2x. The arithmetic was flawless. The picture was absurd.

**The generalization:** for every quantity your rules govern, ask whether they
constrain its *ratio* or its *value*. A system of ratios has a free parameter,
and a free parameter will drift. F7 nails it down.

## 7. Silence must not read like correctness

Worse than a wrong measurement is no measurement that looks like a passing one.
F7 originally keyed off `<use href>` elements listed in `SIZES`, so any object
drawn inline was simply invisible to it - including the laundromat's human, the
single best scale reference in any interior. The report said `PASS, 0 warnings`.

**Fix the report, not just the check:** emit coverage, not only violations.
`sizes_checked: 14` and a warning naming every furniture-sized object that
declared nothing. "Unmeasured" and "correct" must never render the same.

## 8. Verify the instrument before editing the work

Headless Chrome reserves ~87px of the window for UI, so `--window-size=1440,900`
paints an 813px viewport and the bottom of every screenshot was page background.
Three separate agents "fixed" the resulting dark band by matching the page
background to it - baking a fake shadow into the artwork to satisfy a broken
camera.

**When output looks wrong, check the measuring apparatus first.** A magenta
probe rendered into the gap settles it in one shot.

## 9. Some rules can only be tested across a corpus

The failure mode of "derive X per scene" is never an invalid scene. It is a set
of individually valid scenes that are all the same. Every scene passes; the rule
is dead anyway.

Two regressions had exactly this shape - five scenes briefed for five different
hours all came out warm daylight, and seven scenes came out with cameras
1.18-1.49m up, a seated eye level nobody chose. Both were caught by eye, late.

**If a rule says "derive per scene", it needs a spread metric.** Clustering is
the alarm. `corpus_report.py`.

## 10. Research proportions, not just props

Place research reliably returned *what is in* a laundromat, a Kaffeehaus, a
ramen counter. It did not return *how big those things are next to a person*,
because nothing asked.

**Make the dimension table the deliverable of research**, and state every
dimension as a ratio to the human. A stored shape recipe without its real-world
size will be used at the wrong size - a local box and a free `scale` is an
invitation to tune until it looks right, which is precisely how #6 happened.

## 11. Density is a count; realism is difference

A density floor of 80 elements is satisfied by 80 identical circles. Twelve
`<use>` clones of one washer pass every structural check and read as a
spreadsheet rendering. What separates a photograph from a tiling is that real
repeated objects differ - in **state** (door open, machine running), **age**
(wear, a replaced panel) and **content** (loaded, empty, occupied).

**Count what varies, not what exists.**

## 12. An unasserted edit is a silent no-op

Halfway through the bakery build a whitespace pass changed the file, and the
next three string replacements matched nothing. They did not fail - they
returned the input unchanged, the eval stayed green, and the render simply had
no arms on the figure. The bug was found by *looking*, two turns later.

This is #5 wearing another hat. `s.replace(old, new)` returning `s` is
indistinguishable from success unless you check. Every scripted edit in this
project now asserts the anchor exists before replacing, and every one that has
ever silently no-opped did so after some earlier pass reformatted the file.

**Assert the anchor, or you are not editing, you are hoping.**

## 13. The corpus metric had the same disease as the eval

`corpus_report.py` scored each palette by one saturation-weighted circular mean
hue. That cannot distinguish a uniformly warm daylight palette from a warm-key /
cool-shadow one, because the cool half partly cancels the warm half and both
land on the same mean. It duly reported a 2100K oven interior and a noon
mountain teahouse as near-duplicate palettes - a 0.16 distance between the two
most different scenes in the corpus.

The fix was to split the hue circle at its largest gap and carry both cluster
centroids plus the warm/cool balance. The bakery immediately dropped off the
near-duplicate list, and every remaining cluster turned out to be a pre-law
scene.

**The measuring tool needs the same audit as the thing measured** - and the
specific failure is the one from #11 again: it reported the middle of a
distribution and called it the distribution. When a metric surprises you, check
the metric before you accept the verdict or change the work.

## 14. Known limits of the laws as they stand

Honest boundaries, so nobody mistakes a gap for a pass:

- **F7 assumes a frontal face.** An object receding toward the vanishing point
  has a foreshortened screen extent that is not its real size; declare that axis
  as `?` (`data-real="?x0.90"`) rather than inventing a number.
- **F7 cannot see a cropped object.** Something running out of frame measures
  short and there is no way to tell that from being drawn too small. Declare
  the parent, leave the cropped fragment undeclared.
- **The variation check counts declared difference, not perceived difference.**
  Four variants that all look alike will pass.
- **Nothing checks atmospheric decay**, so a scene can still have far objects as
  bright as near ones. Written in perspective-and-depth.md section 4, enforced
  nowhere.

## 15. Gloom is measurable; "stunning" is not the same axis

Five scenes in, the owner said nothing looked stunning and that "indoor" had
drifted toward "hearth". Measuring the corpus before arguing turned that into
two separate findings.

The first is arithmetic. Share of frame above 85% luminance: daylight classroom
**33%**, Fuji teahouse **26%**, laundromat 6.8%, greenhouse 0.1%, bakery
**0.0%**. The bakery had *literally nothing near-white in it*. That is L9, and
it is a check, not an opinion.

The second is not about brightness at all: the laundromat averages 141 and is
not stunning either. The real drift was **archetype**. "Interior" had come to
mean a sealed enclosure lit by one small warm source, in a skill whose own
description says *interiors, often with a view outside* - and the last two
builds had no window, one of them by construction. Low key is seductive because
it hides weak material rendering: everything falls into shadow and nothing has
to be modelled. That is L10, and eight archetypes are listed there precisely so
the choice has to be made rather than defaulted into.

**And the honest part:** fixing both got a scene from 0.0% to 20% specular and
from gloomy to sunlit, and it still is not stunning. It reads as competent flat
vector. Exposure and archetype are necessary and nowhere near sufficient; what
is missing is craft - edge quality, material behaviour, the difference between a
shape filled with a colour and a surface. No check in this repo touches that
axis, and pretending a metric could would be the mistake this whole file is
about.

## 16. Paint the lit surface, not the light

The sun patch on the taverna floor was painted white. Sunlight landing on a
terracotta floor is not white - it is bright *orange*, because the floor's
reflectance is (0.52, 0.24, 0.14) and light does not overwrite albedo, it
multiplies it. Only the limewash, at 0.90 across all three channels, clips to
white in the same sun.

The same error in the same session, one layer down: the palette script used a
scalar albedo per material. That works only when the illuminant carries all the
colour - it produced a convincing 2100K bakery by luck, and under a neutral
5600K sun every material collapsed to grey, "cobalt blue" arriving as `#464648`.
**Reflectance is per-channel or the model only works in firelight.**

---

## The pattern behind the list

Twelve of these sixteen are the same mistake wearing different clothes: **measuring
the thing that is easy to measure and treating it as the thing that matters.**
Element count for density. Ratios for scale. Green for good. Passing scenes for
working checks.

The defense is not more checks. It is being explicit, in the report and in the
docs, about what each check *does not* cover - and keeping one tier of judgement
that no metric can close.
