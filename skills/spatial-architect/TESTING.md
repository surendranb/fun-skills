# How to test that the rules are working

The skill has three kinds of rule and each needs a different test. Running the
eval on a few good scenes tests none of them properly - it only shows the checks
are quiet, never that they are alive.

| Rule kind | Example | Test | Command |
|---|---|---|---|
| Deterministic check in code | contact, phases, palette compliance, footprint physics | fixture suite: one violation per rule | `python3 scripts/test_rules.py` |
| Instruction only a model follows | "derive the palette per scene", "pick the camera height" | corpus spread metrics | `python3 scripts/corpus_report.py builds/` |
| Judgement | "does it read as Paris", "does the rim light look like a scratch" | scored review vs goldens | `references/quality-rubric.md` |

## 1. Fixture suite - proves each check FIRES

`scripts/test_rules.py` builds one clean scene and ~29 mutations, each violating
exactly one rule, and asserts the matching check fires. It also asserts the clean
scene raises nothing.

**Why both directions matter.** For most of this project every check was only
ever tested by running it on scenes that passed. That proves the absence of false
positives and nothing else. A check that can never fire - because of a typo in a
regex, a wrong key name, an early return - is indistinguishable from a working
one under that test. The path-parser bug survived the whole project that way: it
was mis-parsing every shorthand SVG command, and the only symptom was a phantom
collision nobody traced back.

Rule of thumb: **a check without a failing fixture is not a check, it is a
comment.** When you add a rule to the eval, add its mutation to `CASES` in the
same commit. Current state: 29/29 rules fire, clean fixture quiet.

## 2. Corpus report - proves the DERIVATION rules bite

`scripts/corpus_report.py` reads every built scene and measures the spread of
things the skill claims to derive per scene: implied camera height (F1), palette
hue/saturation/value signature, declared light rig, density, size.

**Why per-scene checking cannot do this.** The failure mode of a "derive it per
scene" instruction is not an invalid scene - it is a corpus of individually valid
scenes that are all the same. Every scene passes; the rule is dead anyway. Both
real regressions in this project were exactly that shape, and both were caught by
eye, late:

- five scenes briefed for five different hours all came out warm daylight;
- seven scenes came out with cameras 1.18-1.49m up, a seated eye level nobody
  chose, because the horizon was placed by feel until F1 existed.

A third shape is worse still and no *spread* metric catches it either: a rule can
be **absent** rather than dead. Until F7, nothing anywhere tied an object's drawn
WIDTH and HEIGHT to a real dimension - only its position. Every check passed on a
laundromat whose washers were drawn at 0.35 x 0.49m, because a scene can be
perfectly self-consistent and absolutely wrong. The corpus would not have flagged
it: the sizes were varied, just uniformly too small. The only detector was a
person saying "the machines should be huge". When that happens, the fix is a new
law with its own declaration and its own fixture - not a tighter threshold on an
existing one.

Read it as: **if a derivation rule is working, the outputs must spread.**
Clustering is the alarm. Today's run flags a third instance I had not noticed by
eye - the Fuji teahouse at noon and the construction site in overcast rain have
palette signatures 0.05 apart, which no honest derivation from "light temperature
x material truth x identity accent" could produce.

## 3. Scored review - the part that stays human

Everything above is necessary and none of it is sufficient. No metric in this
repo can tell you the cook's headband reads as a blindfold, that a magenta rim
line reads as a scratch through a leaf, or that a zinc counter reads as a fridge.
That is `references/quality-rubric.md`: seven axes, written scorecards, two
consecutive clean rounds, compared against the goldens, plus owner sign-off for
new work. Its calibration protocol is the test of the *rubric* - agent scores are
recorded before the owner's verdicts, and disagreements are treated as rubric
bugs to be reworded, not verdicts to be argued.

## 4. What to run, when

```bash
python3 scripts/test_rules.py            # every time eval_scene.py changes
python3 scripts/eval_scene.py f.html --render   # every scene, in the fix loop
python3 scripts/corpus_report.py builds/ # after adding scenes, and before release
```

A release is ready when: `test_rules.py` is 29/29 with a quiet clean fixture,
every scene in `builds/` exits 0, `corpus_report.py` reports no clustering, and
the rubric scorecards carry owner sign-off.

## 5. Known gaps in the testing itself

- The corpus thresholds (palette distance 0.35, camera span 0.35m) are guesses
  from nine scenes. They will need re-fitting once the corpus is larger; treat a
  borderline CLUSTERED as a prompt to look, not a verdict.
- Writing the fixture is often what finds the bug. The F8 envelope check
  silently swallowed the *next* declaration into its sum on its first run - every
  scene would have mis-added, and the clean fixture caught it within a minute.
  Treat "the fixture failed on clean input" as information, not as a fixture bug.
- Nothing tests the *reference documents*. If a rule is written in
  `art-direction.md` but no builder ever reads that file, every test above still
  passes. The only detector for that today is the corpus report going flat.
- The vision-judge tier is described in the rubric but not automated. When it is,
  it must produce findings, never a gate - it is non-deterministic and will
  disagree with itself between runs.
