# spatial-svg-architect

A skill that gets a language model to build **realistic, art-directed SVG
interior scenes** as self-contained, web-ready HTML — and, more usefully, a
worked example of how to stop a generative skill from producing plausible
garbage.

The premise: *most of what makes an interior look real is arithmetic, and the
arithmetic should be in the skill rather than in the model's taste.* Perspective,
scale, light footprints, shadow length, palette, exposure — all of it derives
from a small set of declared numbers. What's left over for judgement is what
actually needs judgement.

| | |
|---|---|
| **Shipped scenes** | `builds/` — three, each with its render in `shots/` |
| **The laws** | `references/perspective-and-depth.md` (F1–F8, L1–L10) |
| **How it's tested** | `TESTING.md` — 31 rules, each with a failing fixture |
| **What it learned the hard way** | `references/lessons.md` — **read this first if you're extending it** |

---

## Quick start

```bash
# 1. put the folder where your agent looks for skills, e.g.
cp -r spatial-svg-architect ~/.claude/skills/

# 2. check the eval runs (needs python3; Pillow + Chrome/Chromium for --render)
python3 scripts/test_rules.py                  # -> 31/31 rules provably fire
python3 scripts/eval_scene.py builds/15-taverna-arch-1640.html --render
```

Then ask for a scene: *"build a hero illustration of a Lisbon pastelaria at
opening time."* The skill runs a six-stage pipeline and a fix loop against the
eval; the eval exiting 0 is a **floor, not a verdict**, and the skill says so in
its own output.

## What is actually in here

**`SKILL.md`** — the pipeline. Stage 0 physical brief → place research + plan →
art direction → world rules → coordinate map → emission → eval + scorecard loop.

**`references/`**
- `perspective-and-depth.md` — the formulas and the light laws. The core file.
- `art-direction.md` — palette derivation, value planes, composition.
- `quality-rubric.md` — seven axes, scorecards, the part no metric reaches.
- `lessons.md` — sixteen things that went wrong and what they generalise to.
- `typologies.md`, `shape-library.md`, `architectural-math.md`,
  `forces-and-physics.md`, `telemetry-bindings.md`, `theoretical-foundations.md`

**`scripts/`**
- `eval_scene.py` — the deterministic checker. `--render` adds the pixel tier.
- `test_rules.py` — one violating fixture per rule, plus a clean fixture.
- `corpus_report.py` — cross-scene spread; catches convergence.
- `palette_from_light.py` — illuminant × per-channel reflectance → palette.

## The laws, in one table

Hardcoded, machine-checkable where possible. Full statements and worked
examples in `references/perspective-and-depth.md`.

| | law | why it exists |
|---|---|---|
| **F1** | `R = k · H_cam` — the horizon is one camera-height above the reference plane | seven scenes came out at 1.18–1.49m, a seated eye level nobody chose |
| **F2** | floor foreshortening `f = H_cam / d0` | pools on a floor are flat ellipses, never circles |
| **F3** | emitter footprint from the emitter's own shape | a strip light cannot cast a round pool |
| **F4** | offset and shadow length from sun elevation | every shadow shares one elevation and azimuth |
| **F5** | penumbra `p = S · g / D` | crisp where things touch, soft where they don't |
| **F6** | inverse-square for local sources | the far lamp is a quarter as bright, not "slightly dimmer" |
| **F7** | extents: `drawn_px = real_m · k · s` on **both** axes | a scene can be perfectly self-consistent and absolutely wrong |
| **F8** | the envelope closes: footprints + circulation = room dimension | catches an impossible floor plan before any coordinate exists |
| **L9** | own the value range — true darks, broad middle, decisive near-white | a frame with 0.0% near-white reads as gloom whatever its subject |
| **L10** | pick the light archetype; "sealed box, one warm source" is the default failure | low key hides weak material rendering |

Scenes declare their claims in machine-readable comments, and the eval measures
the drawing back against them:

```html
<!-- SCALE: 288px = 1m -->  <!-- DATUM y=820 -->
<!-- ROOM: 4.20w x 6.00d x 3.20h -->
<!-- SPAN width: washers=0.85 aisle=2.40 washers=0.85 -->
<!-- PERSPECTIVE: horizon y=345, VP (600,345)  [F1: R=475=288*1.65 -> 1.65m] -->
<!-- LIGHTS: mouth=window@517,442;pool=pool-mouth -->
<!-- SIZES: washer=0.85x1.10 | bench=1.60x0.89 -->
```

## How it's tested

Three tiers, because the three kinds of rule fail in three different ways.

| rule kind | failure mode | test |
|---|---|---|
| deterministic check | the check silently never fires | `test_rules.py` — one violating fixture each |
| instruction to a model | every scene valid, whole corpus identical | `corpus_report.py` — spread metrics |
| judgement | a rim light reads as a scratch | `quality-rubric.md` — written scorecards |

**A check without a failing fixture is not a check, it is a comment.** Add the
mutation in the same commit as the rule. Two bugs survived months here by being
tested only against scenes that passed.

## Honest limitations

- **Craft is unmeasured.** The current scenes are metrically sound and read as
  competent flat vector, not as photographs. Edge quality, material behaviour,
  the difference between a filled shape and a surface — nothing here touches
  that axis, and it is the largest remaining gap.
- **F7 assumes a frontal face.** Receding or frame-cropped objects declare the
  affected axis as `?` (`data-real="?x0.90"`).
- **Atmospheric decay** is written in `perspective-and-depth.md` §4 and enforced
  nowhere, so far objects can still be as bright as near ones.
- **The variation check counts declared difference, not perceived difference.**
- **Corpus thresholds** were fitted on ~11 scenes and will need refitting.
- **`corpus_report.py` still reports CLUSTERED** — honestly. The clustered pairs
  are the pre-law builds, now in the sibling archive folder rather than deleted.
- **Nothing tests the reference documents.** If a rule is written in
  `art-direction.md` and no builder ever reads that file, every test still passes.

## Provenance

The quality rubric was calibrated against reference images supplied by the
owner. Those are **not** included — they were third-party watermarked photos and
live outside this folder. `references/quality/` keeps only renders produced by
this skill. If you want to recalibrate, drop your own anchors into
`references/quality/` and follow the protocol in `quality-rubric.md`.

## Licence

MIT — see `LICENSE`.
