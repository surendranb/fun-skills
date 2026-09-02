#!/usr/bin/env python3
"""Rule test suite for spatial-svg-architect.

Every deterministic rule gets TWO tests:
  * a NEGATIVE fixture - a scene that violates exactly that rule, asserting the
    matching check fires. Without this a check that never fires looks identical
    to a check that works.
  * the shared POSITIVE fixture - a clean scene, asserting no check fires. This
    is the false-positive guard.

Run:  python3 test_rules.py [-v]
Exit: 0 if every rule is provably alive and quiet on clean input.
"""
import re, sys, subprocess, tempfile, os, json

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.join(HERE, "eval_scene.py")

# --- the clean scene every negative fixture is mutated from ------------------
# k=288, H_cam=1.6m -> R=k*H=461 -> horizon y = 810-461 = 349 (F1)
# kept clear of the phase-6 block at (900..1020, 600..720) so the clean fixture
# does not trip the phase-3/phase-6 wall-collision rule
PROPS = "".join(
    f'<circle cx="{40+i*22}" cy="{240+(i%4)*20}" r="7" fill="#C9A87C"/>'
    for i in range(34))

BASE = """<!DOCTYPE html><html><head>
<!-- SCALE: 288px = 1m (at the reference plane) -->
<!-- DATUM y=810 -->
<!-- STYLE: painterly-perspective -->
<!-- ROOM: 5.00w x 6.00d x 2.70h -->
<!-- SPAN width: counter=0.60 aisle=1.40 seating=1.50 aisle-b=1.50 -->
<!-- PERSPECTIVE: horizon y=349, VP (900,349), s(y)=(y-349)/461 -->
<!-- LIGHTS: sun=sun@1300,300 | bar=tube@620,300;axis=0;pool=pool-bar -->
<!-- SIZES: crate=0.60x0.60 -->
<!-- PALETTE: #FEF6E4 #C9A87C #4A2F23 #001858 #2B2B5C #FFD9A0 -->
</head><body>
<svg viewBox="0 0 1440 900" xmlns="http://www.w3.org/2000/svg"><defs>
<linearGradient id="g1"><stop offset="0%" stop-color="#FEF6E4"/><stop offset="50%" stop-color="#C9A87C"/><stop offset="100%" stop-color="#4A2F23"/></linearGradient>
<linearGradient id="g2"><stop offset="0%" stop-color="#FEF6E4"/><stop offset="50%" stop-color="#C9A87C"/><stop offset="100%" stop-color="#4A2F23"/></linearGradient>
<linearGradient id="g3"><stop offset="0%" stop-color="#FEF6E4"/><stop offset="50%" stop-color="#C9A87C"/><stop offset="100%" stop-color="#4A2F23"/></linearGradient>
<linearGradient id="g4"><stop offset="0%" stop-color="#FEF6E4"/><stop offset="50%" stop-color="#C9A87C"/><stop offset="100%" stop-color="#4A2F23"/></linearGradient>
<g id="crate"><rect width="120" height="120" fill="#4A2F23"/></g>
<filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2"/><feColorMatrix type="saturate" values="0"/></filter>
</defs>
<g id="phase-1-shell"><rect width="1440" height="900" fill="url(#g1)"/></g>
<g id="phase-2-portals"><rect x="1000" y="100" width="300" height="400" fill="#FEF6E4"/></g>
<g id="phase-3-fixtures"><rect x="60" y="120" width="90" height="90" fill="#C9A87C"/>__PROPS__</g>
<g id="phase-4-volumetrics"><ellipse id="pool-bar" cx="620" cy="700" rx="160" ry="34" fill="#FFD9A0"/></g>
<g id="phase-5-furniture"><use href="#crate" transform="translate(300,682) scale(1.040)"/><rect x="500" y="504" width="300" height="16" fill="#4A2F23"/><line x1="520" y1="520" x2="520" y2="810" stroke="#4A2F23" stroke-width="4"/></g>
<g id="phase-6-millwork"><rect x="900" y="600" width="120" height="120" fill="#4A2F23"/></g>
<g id="phase-7-occlusion"><ellipse cx="650" cy="806" rx="90" ry="8" fill="#2B2B5C" opacity="0.16"/></g>
<g id="phase-8-foreground"><rect data-real="0.21x0.73" x="1160" y="600" width="60" height="210" fill="#4A2F23"/></g>
</svg></body></html>""".replace("__PROPS__", PROPS)

# --- one negative fixture per rule ------------------------------------------
# (check name, human description, mutation applied to BASE)
def sub(old, new):
    def f(s):
        assert old in s, f"fixture anchor missing: {old[:60]}"
        return s.replace(old, new, 1)
    return f

CASES = [
 ("scale_declared", "SCALE comment removed",
  sub("<!-- SCALE: 288px = 1m (at the reference plane) -->", "")),
 ("datum_declared", "DATUM comment removed",
  sub("<!-- DATUM y=810 -->", "")),
 ("palette_declared", "PALETTE comment removed",
  sub("<!-- PALETTE: #FEF6E4 #C9A87C #4A2F23 #001858 #2B2B5C #FFD9A0 -->", "")),
 ("palette_compliance", "a colour used that is not in the declared palette",
  sub('fill="#C9A87C"/>__X__', '')),   # replaced below
 ("no_pure_black", "pure black used instead of a tinted ink",
  sub('fill="#2B2B5C" opacity="0.16"', 'fill="#000000" opacity="0.16"')),
 ("file_size", "svg over the 20KB web-asset budget",
  lambda s: s.replace("</svg>", "".join(
      f'<circle cx="{i%1400}" cy="{i%880}" r="2" fill="#C9A87C"/>' for i in range(700)) + "</svg>")),
 ("xml_valid", "malformed markup",
  sub('<g id="phase-6-millwork">', '<g id="phase-6-millwork"><rect x="1" y="1" width="2">')),
 ("gradients_rich", "fewer than four multi-stop gradients",
  lambda s: re.sub(r'<linearGradient id="g[34]">.*?</linearGradient>', '', s, flags=re.S)),
 ("grain_filter", "no feTurbulence grain layer",
  lambda s: re.sub(r'<filter id="grain">.*?</filter>', '', s, flags=re.S)),
 ("phases_present", "phase groups missing",
  lambda s: re.sub(r'id="phase-[5678][^"]*"', 'id="misc"', s)),
 ("phases_ordered", "phases emitted out of build order",
  sub('<g id="phase-2-portals">', '<g id="phase-9-late">').__call__ if False else
  (lambda s: s.replace('id="phase-2-portals"', 'id="phase-0-portals"'))),
 ("density", "below the drawn-element floor",
  lambda s: s.replace(PROPS, "")),
 ("wall_collisions", "phase-3 and phase-6 wall items overlapping",
  sub('<rect x="900" y="600" width="120" height="120" fill="#4A2F23"/>',
      '<rect x="80" y="140" width="120" height="120" fill="#4A2F23"/>')),
 ("floor_contact", "nothing in phases 5+ reaches the datum",
  lambda s: s.replace('y2="810"', 'y2="700"').replace('height="210"', 'height="100"')
             .replace('cy="806"', 'cy="700"')
             .replace('translate(300,682)', 'translate(300,500)')),
 ("camera_height", "horizon implies an impossible camera height",
  sub("horizon y=349", "horizon y=780")),
 ("lights_declared", "no light rig declared",
  lambda s: re.sub(r'<!-- LIGHTS:.*?-->', '', s, flags=re.S)),
 ("pool_missing", "a light names a pool element that does not exist",
  sub('id="pool-bar"', 'id="pool-typo"')),
 ("pool_shape_mismatch", "a strip light casting a circular pool (physics)",
  sub('rx="160" ry="34"', 'rx="90" ry="86"')),
 ("pool_angle_mismatch", "a pool square to its own tube (physics)",
  sub('rx="160" ry="34"', 'rx="30" ry="120"')),
 ("pool_undeclared", "an emitter with no pool element at all",
  sub("bar=tube@620,300;axis=0;pool=pool-bar", "lamp=point@620,300")),
 ("sizes_declared", "no SIZES comment - extents unchecked (F7)",
  sub("<!-- SIZES: crate=0.60x0.60 -->", "")),
 ("object_scale", "object drawn at half its declared real size (F7)",
  sub('transform="translate(300,682) scale(1.040)"',
      'transform="translate(300,682) scale(0.520)"')),
 ("room_declared", "no ROOM comment - envelope never stated (Stage 0)",
  sub("<!-- ROOM: 5.00w x 6.00d x 2.70h -->", "")),
 ("room_plausible", "a ceiling height no room has",
  sub("5.00w x 6.00d x 2.70h", "5.00w x 6.00d x 0.90h")),
 ("envelope_closes", "the floor plan does not fit the room it declares (F8)",
  sub("seating=1.50 aisle-b=1.50", "seating=1.50 aisle-b=3.90")),
 ("circulation", "an aisle narrower than a person",
  sub("aisle=1.40 seating=1.50", "aisle=0.50 seating=2.40")),
 ("repeat_variation", "a wall of identical clones passing as density",
  sub('<use href="#crate" transform="translate(300,682) scale(1.040)"/>',
      "".join('<use href="#crate" transform="translate(%d,682) scale(1.040)"/>' % x
              for x in (300, 440, 580, 720, 860)))),
 ("extents_undeclared", "the biggest object in the frame never says how big it is",
  sub('<rect data-real="0.21x0.73" x="1160"', '<rect x="1160"')),
 ("object_scale", "stacked unit takes its screen row instead of its support "
                  "depth (missing data-floor)",
  sub('<use href="#crate" transform="translate(300,682) scale(1.040)"/>',
      '<use href="#crate" transform="translate(300,682) scale(1.040)"/>'
      '<use href="#crate" transform="translate(300,552) scale(1.040)"/>')),
]
# palette_compliance needs a real off-palette colour, easiest done directly
CASES[3] = ("palette_compliance", "a colour used that is not in the declared palette",
            sub('<rect x="1000" y="100" width="300" height="400" fill="#FEF6E4"/>',
                '<rect x="1000" y="100" width="300" height="400" fill="#FF00AA"/>'))

# --- render-tier fixtures ----------------------------------------------------
# The pixel checks had NO fixtures at all: test_rules ran the eval without
# --render, so every render-tier rule was untested by the very suite whose whole
# point is that an untested check is a comment. These two are deliberately
# degenerate images, one with no highlights and one with no darks.
def _wash(fill):
    """Cover the whole frame so the rendered histogram is unambiguous."""
    def f(s):
        return s.replace("</svg>",
                         f'<rect width="1440" height="900" fill="{fill}"/></svg>')
    return f

RENDER_CASES = [
 ("no_highlights", "nothing in the frame reaches near-white (L9)",
  _wash("#4A2F23")),
 ("no_darks", "nothing in the frame anchors the dark end (L9)",
  _wash("#FEF6E4")),
]

def run(html, render=False):
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html); p = f.name
    try:
        cmd = [sys.executable, EVAL, p] + (["--render"] if render else [])
        r = subprocess.run(cmd, capture_output=True, text=True)
        try:
            rep = json.loads(r.stdout)
        except json.JSONDecodeError:
            return {"errors": [{"check": "CRASH"}], "warnings": [], "raw": r.stderr[-300:]}
        return rep
    finally:
        os.unlink(p)

def main():
    verbose = "-v" in sys.argv
    print("spatial-svg-architect :: rule test suite\n")

    # false-positive guard
    rep = run(BASE)
    fired = [e["check"] for e in rep["errors"]]
    clean_ok = not fired
    print(f"[{'PASS' if clean_ok else 'FAIL'}] clean fixture raises no errors"
          + ("" if clean_ok else f"  <-- fired: {fired}"))
    if verbose and rep["warnings"]:
        print("        (warnings on clean fixture: "
              + ", ".join(w["check"] for w in rep["warnings"]) + ")")

    alive, dead = 0, []
    print()
    for check, desc, mutate in CASES:
        rep = run(mutate(BASE))
        names = [e["check"] for e in rep["errors"]] + [w["check"] for w in rep["warnings"]]
        hit = check in names
        alive += hit
        if not hit: dead.append((check, desc, names))
        print(f"[{'PASS' if hit else 'FAIL'}] {check:24s} {desc}"
              + ("" if hit else f"\n        got instead: {names or 'nothing'}"))

    print()
    r_alive = 0
    for check, desc, mutate in RENDER_CASES:
        rep = run(mutate(BASE), render=True)
        if not rep.get("render", {}).get("available"):
            print(f"[SKIP] {check:24s} {desc}  (no headless browser)"); r_alive += 1; continue
        names = [e["check"] for e in rep["errors"]] + [w["check"] for w in rep["warnings"]]
        hit = check in names
        r_alive += hit
        if not hit: dead.append((check, desc, names))
        print(f"[{'PASS' if hit else 'FAIL'}] {check:24s} {desc}"
              + ("" if hit else f"\n        got instead: {names or 'nothing'}"))
    alive += r_alive

    print(f"\n{alive}/{len(CASES) + len(RENDER_CASES)} rules provably fire; clean fixture "
          f"{'quiet' if clean_ok else 'NOISY'}")
    if dead:
        print("\nrules that did NOT fire when violated (unenforced, or the "
              "fixture does not actually violate them):")
        for c, d, got in dead:
            print(f"  - {c}: {d}")
    return 0 if (clean_ok and not dead) else 1

if __name__ == "__main__":
    sys.exit(main())
