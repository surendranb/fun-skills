#!/usr/bin/env python3
"""Deterministic evaluator for spatial-svg-architect scenes.

Usage: python3 eval_spatial.py scene.html [--render] [--selftest]
stdout: pure JSON report. stderr: human summary. Exit 0 = zero errors.
"""
import sys, os, re, json, math, subprocess, tempfile, shutil
import xml.etree.ElementTree as ET

SVG_BYTES_LIMIT = 25600
CONTACT_TOL = 4          # px an element bottom may sit above datum and still "touch"
MIN_PHASES = 6           # spec wants 8; fewer than MIN_PHASES is an error
GRADIENT_MIN = 4         # scenes need at least this many >=3-stop gradients
HUE_BUCKETS = 12
MIN_ELEMENTS = 30        # density floor - sparse scenes read as voids
COLLIDE_EPS = 4          # px overlap in BOTH axes to count as a collision
WALL_PHASES = (3, 6)     # wall-mounted groups must not overlap each other
GRID = (6, 4)            # coverage grid cells across the render
CELL_INK_MIN = 1.0       # % non-background pixels per cell
DRAWABLE = {"rect", "circle", "ellipse", "line", "path", "polygon", "polyline",
            "text", "use"}

def die(msg):
    print(msg, file=sys.stderr); sys.exit(2)

def extract_svg(html):
    m = re.search(r"<svg[\s\S]*?</svg>", html)
    return m.group(0) if m else None

def comments_of(html):
    return " ".join(re.findall(r"<!--(.*?)-->", html, re.S))

_PATH_TOKEN = re.compile(r"([MmZzLlHhVvCcSsQqTtAa])|(-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)")
_ARGC = {"m": 2, "l": 2, "h": 1, "v": 1, "c": 6, "s": 4, "q": 4, "t": 2, "a": 7, "z": 0}

def num_pairs_from_path(d):
    toks = [(c, n) for c, n in _PATH_TOKEN.findall(d or "")]
    pts, nums, cmd = [], [], None
    cx = cy = sx = sy = 0.0
    i = 0
    while i < len(toks):
        c, n = toks[i]
        if c:
            cmd = c; i += 1
            if cmd in "Zz":
                cx, cy = sx, sy
                cmd = None
            continue
        if cmd is None:
            i += 1; continue
        low = cmd.lower()
        argc = _ARGC[low]
        nums = []
        while len(nums) < argc and i < len(toks) and not toks[i][0]:
            nums.append(float(toks[i][1])); i += 1
        if len(nums) < argc:
            break
        rel = cmd.islower()
        if low == "h":
            cx = cx + nums[0] if rel else nums[0]
        elif low == "v":
            cy = cy + nums[0] if rel else nums[0]
        elif low == "a":
            ex, ey = nums[5], nums[6]
            cx, cy = (cx + ex, cy + ey) if rel else (ex, ey)
        else:
            for j in range(0, argc, 2):
                px = cx + nums[j] if rel else nums[j]
                py = cy + nums[j + 1] if rel else nums[j + 1]
                pts.append((px, py))
            cx, cy = pts[-1]
        pts.append((cx, cy))
        if low == "m":
            sx, sy = cx, cy
            cmd = "L" if cmd == "M" else "l"
    return pts

def local(el):
    return el.tag.split("}")[-1]

def element_bottom(el, defs=None):
    b = element_bbox(el, defs)
    return b[3] if b else None

def element_bbox(el, defs=None, depth=0):
    if depth > 4: return None
    tag = local(el)
    def f(v, d=None):
        try: return float(el.get(v, d))
        except (TypeError, ValueError): return None
    if tag in ("g", "a", "switch"):
        boxes = [b for c in list(el) if (b := element_bbox(c, defs, depth + 1))]
        if not boxes: return None
        bb = (min(b[0] for b in boxes), min(b[1] for b in boxes),
              max(b[2] for b in boxes), max(b[3] for b in boxes))
        tr = el.get("transform", "") or ""
        if not tr: return bb
        if "rotate" in tr or "matrix" in tr or "skew" in tr: return None
        tx = ty = 0.0; sc = 1.0
        for m in re.finditer(r"(translate|scale)\s*\(([^)]*)\)", tr):
            args = [float(v) for v in re.split(r"[\s,]+", m.group(2).strip()) if v]
            if m.group(1) == "translate":
                tx += args[0]; ty += args[1] if len(args) > 1 else 0
            elif m.group(1) == "scale":
                sc = args[0]
        return (tx + bb[0]*sc, ty + bb[1]*sc, tx + bb[2]*sc, ty + bb[3]*sc)
    if tag == "use":
        href = el.get("href") or el.get("{http://www.w3.org/1999/xlink}href") or ""
        target = (defs or {}).get(href.lstrip("#"))
        if target is None: return None
        bb = element_bbox(target, defs, depth + 1)
        if bb is None: return None
        tx, ty, s = f("x", 0), f("y", 0), 1.0
        tr = el.get("transform", "")
        for m in re.finditer(r"(translate|scale)\s*\(([^)]*)\)", tr):
            args = [float(v) for v in re.split(r"[\s,]+", m.group(2).strip()) if v]
            if m.group(1) == "translate":
                tx += args[0]; ty += args[1] if len(args) > 1 else 0
            elif m.group(1) == "scale":
                s = args[0]
        if "rotate" in tr or "matrix" in tr or "skew" in tr: return None
        return (tx + bb[0]*s, ty + bb[1]*s, tx + bb[2]*s, ty + bb[3]*s)
    if tag == "rect":
        x, y, w, h = f("x", 0), f("y", 0), f("width"), f("height")
        if None in (w, h): return None
        return (x, y, x + w, y + h)
    if tag == "circle":
        cx, cy, r = f("cx"), f("cy"), f("r")
        return None if None in (cx, cy, r) else (cx-r, cy-r, cx+r, cy+r)
    if tag == "ellipse":
        cx, cy, rx, ry = f("cx"), f("cy"), f("rx"), f("ry")
        return None if None in (cx, cy, rx, ry) else (cx-rx, cy-ry, cx+rx, cy+ry)
    if tag == "line":
        xs, ys = [f("x1"), f("x2")], [f("y1"), f("y2")]
        if None in xs or None in ys: return None
        return (min(xs), min(ys), max(xs), max(ys))
    if tag in ("polygon", "polyline"):
        pts = re.findall(r"-?\d+(?:\.\d+)?", el.get("points", ""))
        vals = [float(v) for v in pts]
        if len(vals) < 4: return None
        xs, ys = vals[0::2], vals[1::2]
        return (min(xs), min(ys), max(xs), max(ys))
    if tag == "path":
        pts = num_pairs_from_path(el.get("d", ""))
        if not pts: return None
        xs, ys = [x for x, _ in pts], [y for _, y in pts]
        return (min(xs), min(ys), max(xs), max(ys))
    return None

def walk(svg_root):
    yield svg_root
    for c in svg_root.iter():
        yield c

def norm_hex(v):
    v = v.strip().strip("'\"")
    if not v.startswith("#"): return None
    h = v[1:].lower()
    if len(h) == 3: h = "".join(c*2 for c in h)
    return h if len(h) == 6 and all(c in "0123456789abcdef" for c in h) else None

COLOR_ATTRS = ("fill", "stroke", "stop-color")

def static_checks(html, metrics=None):
    errs, warns = [], []
    E = lambda check, detail, hint: errs.append({"check": check, "detail": detail, "hint": hint})
    W = lambda check, detail, hint: warns.append({"check": check, "detail": detail, "hint": hint})
    cm = comments_of(html)

    if not re.search(r"\d+(\.\d+)?\s*px\s*=\s*1\.?\d*\s*m", cm):
        E("scale_declared", "no '<N>px = 1m' SCALE comment found",
          "SKILL.md Stage 2: add <!-- SCALE: 288px = 1m -->")
    dm = re.search(r"DATUM\s*y\s*=\s*(\d+)", cm)
    if not dm:
        E("datum_declared", "no DATUM comment found",
          "SKILL.md Stage 2: add <!-- DATUM y=720 -->")
    datum = int(dm.group(1)) if dm else None

    pal = sorted(set(norm_hex(h) for h in
                     re.findall(r"(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})", cm.split("PALETTE:")[-1])
                     ) - {None})
    if not pal:
        E("palette_declared", "no PALETTE comment with hex colors",
          "art-direction.md §2: declare <!-- PALETTE: ... --> from an anchor palette")

    svg = extract_svg(html)
    if not svg:
        E("svg_present", "no <svg> block found", "scene must contain one root <svg>")
        return errs, warns, datum, pal
    if len(svg.encode()) > SVG_BYTES_LIMIT:
        E("file_size", f"svg is {len(svg.encode())}B > {SVG_BYTES_LIMIT}B",
          "simplify paths, reuse <defs>/<use>")

    try:
        root = ET.fromstring(re.sub(r"<!--.*?-->", "", svg, flags=re.S))
    except ET.ParseError as e:
        E("xml_valid", f"SVG does not parse: {e}", "fix malformed markup")
        return errs, warns, datum, pal

    used, bad_black, nonhex = set(), [], []
    for el in walk(root):
        tag = el.tag.split("}")[-1]
        for attr in COLOR_ATTRS:
            v = el.get(attr)
            if not v or v in ("none", "transparent"): continue
            if v.startswith("url("): continue
            h = norm_hex(v)
            if h:
                used.add(h)
                if h == "000000":
                    bad_black.append(f"{tag}@{attr}")
            else:
                nonhex.append(f"{tag}@{attr}={v}")
    if bad_black:
        E("no_pure_black", f"pure black used: {', '.join(bad_black[:4])}",
          "art-direction.md §3: shadows tinted toward indigo; outlines use ink color")
    if nonhex:
        E("palette_compliance", f"non-hex/named colors: {', '.join(nonhex[:4])}",
          "use only hex colors from the declared palette")
    off = sorted(used - set(pal))
    if pal and off:
        E("palette_compliance", f"{len(off)} colors not in PALETTE comment (e.g. #{off[0]})",
          "add missing colors to the PALETTE declaration or switch fills to palette hexes")

    rich = sum(1 for el in walk(root)
               if el.tag.split("}")[-1].endswith("Gradient")
               and len([c for c in el if c.tag.split("}")[-1] == "stop"]) >= 3)
    if rich < GRADIENT_MIN:
        E("gradients_rich", f"only {rich} gradient(s) with >=3 stops (need {GRADIENT_MIN})",
          "art-direction.md §4: walls, floor, sky, big surfaces get multi-stop gradients")

    if not any(el.tag.split("}")[-1] == "feTurbulence" for el in walk(root)):
        E("grain_filter", "no feTurbulence grain filter defined",
          "art-direction.md §6: define #grain once and overlay at opacity 0.04-0.06")

    phases = []
    for el in walk(root):
        gid = el.get("id") or ""
        m = re.match(r"phase-(\d+)", gid) if el.tag.split("}")[-1] == "g" else None
        if m: phases.append((int(m.group(1)), el))
    nums = [n for n, _ in phases]
    if len(nums) < MIN_PHASES:
        E("phases_present", f"only {len(nums)} phase groups (need >= {MIN_PHASES})",
          "group DOM into <g id=\"phase-N-name\"> build order")
    elif nums != sorted(nums):
        E("phases_ordered", f"phase ids out of order: {nums}",
          "DOM order = build order = z-order; renumber/reorder")

    n_draw = sum(1 for el in walk(root) if local(el) in DRAWABLE)
    if n_draw < MIN_ELEMENTS:
        E("density", f"only {n_draw} drawn elements (need >= {MIN_ELEMENTS})",
          "sparse scenes read as voids; add authored detail")

    defs_map = {el.get("id"): el for el in walk(root) if el.get("id")}

    if datum is not None:
        furn = [el for n, el in phases if n >= 5]
        touching_groups = 0
        for gel in furn:
            bottoms = [b for el in gel.iter() if (b := element_bottom(el, defs_map)) is not None]
            if any(abs(b - datum) <= CONTACT_TOL for b in bottoms):
                touching_groups += 1
        if furn and touching_groups == 0:
            E("floor_contact",
              f"no element in phases 5+ reaches datum y={datum} (+/-{CONTACT_TOL}px)",
              "standing objects must rest ON the datum line; check leg/table bottoms")

    return errs, warns, datum, pal

def main():
    if len(sys.argv) < 2:
        die("usage: eval_spatial.py scene.html [--render]")
    path = sys.argv[1]
    if not os.path.exists(path): die(f"not found: {path}")
    html = open(path, encoding="utf-8").read()
    smetrics = {}
    errs, warns, datum, pal = static_checks(html, smetrics)
    report = {"file": path, "errors": errs, "warnings": warns,
              "metrics": smetrics, "pass": len(errs) == 0}
    print(json.dumps(report, indent=2))
    status = "PASS" if not errs else f"FAIL ({len(errs)} errors)"
    print(f"\n{status} | errors={len(errs)} warnings={len(warns)}", file=sys.stderr)
    for x in errs:
        print(f"  ERROR {x['check']}: {x['detail']}\n         -> {x['hint']}", file=sys.stderr)
    for x in warns:
        print(f"  warn  {x['check']}: {x['detail']} -> {x['hint']}", file=sys.stderr)
    sys.exit(0 if not errs else 1)

if __name__ == "__main__":
    main()
