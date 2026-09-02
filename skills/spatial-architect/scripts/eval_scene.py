#!/usr/bin/env python3
"""Deterministic evaluator for spatial-svg-architect scenes.

Usage: python3 eval_scene.py scene.html [--render] [--selftest]
stdout: pure JSON report. stderr: human summary. Exit 0 = zero errors.
"""
import sys, os, re, json, math, subprocess, tempfile, shutil
import xml.etree.ElementTree as ET

SVG_BYTES_LIMIT = 20480
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

# Real SVG path walker. The old version regex-paired every number in `d`, which
# silently mangled shorthand/relative commands ("v10 h8" was read as the absolute
# point (10,8)) and produced bogus bounding boxes -> phantom collision errors.
_PATH_TOKEN = re.compile(r"([MmZzLlHhVvCcSsQqTtAa])|(-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)")
_ARGC = {"m": 2, "l": 2, "h": 1, "v": 1, "c": 6, "s": 4, "q": 4, "t": 2, "a": 7, "z": 0}

def num_pairs_from_path(d):
    """Return every on-path and control point in absolute user units.

    Control points can overestimate a curve's bbox by a few px; that is
    acceptable at CONTACT_TOL granularity and always errs toward "larger".
    """
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
            cmd = "L" if cmd == "M" else "l"   # subsequent pairs are implicit lineto
    return pts

# crude but deterministic element bounds; ponytail: path control points may
# overestimate a bbox by a few px - acceptable at CONTACT_TOL granularity
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
    if tag in ("g", "a", "switch"):  # container: union of children
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
    return None  # use/text/g: unknown metrics, skip

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

    # declarations
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
        E("svg_present", "no <svg> block found", "scene must contain one root <svg>"); 
        return errs, warns, datum, pal
    if len(svg.encode()) > SVG_BYTES_LIMIT:
        E("file_size", f"svg is {len(svg.encode())}B > {SVG_BYTES_LIMIT}B",
          "simplify paths, reuse <defs>/<use>; see typologies notes")

    try:
        root = ET.fromstring(re.sub(r"<!--.*?-->", "", svg, flags=re.S))
    except ET.ParseError as e:
        E("xml_valid", f"SVG does not parse: {e}", "fix malformed markup"); 
        return errs, warns, datum, pal

    # color discipline
    used, bad_black, nonhex = set(), [], []
    defs_ids = set()
    for el in walk(root):
        tag = el.tag.split("}")[-1]
        if tag == "linearGradient" or tag == "radialGradient" or tag == "filter":
            gid = el.get("id");  defs_ids.add(gid) if gid else None
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

    # gradients
    rich = sum(1 for el in walk(root)
               if el.tag.split("}")[-1].endswith("Gradient")
               and len([c for c in el if c.tag.split("}")[-1] == "stop"]) >= 3)
    if rich < GRADIENT_MIN:
        E("gradients_rich", f"only {rich} gradient(s) with >=3 stops (need {GRADIENT_MIN})",
          "art-direction.md §4: walls, floor, sky, big surfaces get multi-stop gradients")

    # grain
    if not any(el.tag.split("}")[-1] == "feTurbulence" for el in walk(root)):
        E("grain_filter", "no feTurbulence grain filter defined",
          "art-direction.md §6: define #grain once and overlay at opacity 0.04-0.06")

    # phases
    phases = []
    for el in walk(root):
        gid = el.get("id") or ""
        m = re.match(r"phase-(\d+)", gid) if el.tag.split("}")[-1] == "g" else None
        if m: phases.append((int(m.group(1)), el))
    nums = [n for n, _ in phases]
    if len(nums) < MIN_PHASES:
        E("phases_present", f"only {len(nums)} phase groups (need >= {MIN_PHASES})",
          "SKILL.md Stage 6: group DOM into <g id=\"phase-N-name\"> build order")
    elif nums != sorted(nums):
        E("phases_ordered", f"phase ids out of order: {nums}",
          "DOM order = build order = z-order; renumber/reorder")
    elif len(nums) != 8:
        W("phases_full", f"{len(nums)} phases found, spec defines 8",
          "merge only when a phase is genuinely empty for this scene")

    # density floor
    n_draw = sum(1 for el in walk(root) if local(el) in DRAWABLE)
    if n_draw < MIN_ELEMENTS:
        E("density", f"only {n_draw} drawn elements (need >= {MIN_ELEMENTS})",
          "SKILL.md Stage 5: sparse scenes read as voids; add props from shape-library.md")

    defs_map = {el.get("id"): el for el in walk(root) if el.get("id")}

    # wall-mount collisions: phase 3 x phase 6 elements may not overlap
    by_phase = {}
    for n, el in phases:
        by_phase[n] = [c for c in list(el) if local(c) in DRAWABLE]
    if all(p in by_phase for p in WALL_PHASES):
        hits = []
        for a in by_phase[WALL_PHASES[0]]:
            ba = element_bbox(a, defs_map)
            if not ba: continue
            for b in by_phase[WALL_PHASES[1]]:
                bb = element_bbox(b, defs_map)
                if not bb: continue
                ox = min(ba[2], bb[2]) - max(ba[0], bb[0])
                oy = min(ba[3], bb[3]) - max(ba[1], bb[1])
                if ox > COLLIDE_EPS and oy > COLLIDE_EPS:
                    hits.append(f"{a.get('id') or local(a)} x {b.get('id') or local(b)}")
        if hits:
            E("wall_collisions", f"phases 3/6 overlap: {', '.join(hits[:3])}",
              "wall-mounted elements must not intersect; reposition one of the pair")

    # floor contact in furniture-and-later phases
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

    # F1: the horizon sits exactly one camera-height above the reference plane,
    # in scaled pixels (R = k * H_cam). Solving for H_cam turns a free-hand
    # horizon into a checkable claim about where the camera is standing.
    km = re.search(r"SCALE:\s*([\d.]+)\s*px", cm)
    hm = re.search(r"horizon\s*y\s*=\s*([\d.]+)", cm, re.I)
    if km and hm and datum is not None:
        k_px, y_h = float(km.group(1)), float(hm.group(1))
        R = datum - y_h
        if k_px > 0 and R > 0:
            H_cam = R / k_px
            if not (0.5 <= H_cam <= 2.4):
                E("camera_height",
                  f"horizon implies a camera {H_cam:.2f}m above the reference "
                  f"plane (R={R:.0f}px / k={k_px:.0f})",
                  "perspective-and-depth.md F1: R = k * H_cam. Move the horizon "
                  "to k*H for the eye height you want (standing 1.6m -> R=461 at "
                  "k=288), or change k.")
            elif not (1.5 <= H_cam <= 1.8):
                W("camera_height",
                  f"camera sits {H_cam:.2f}m up - that is "
                  + ("a seated/child eye level" if H_cam < 1.5 else "above standing eye level"),
                  "perspective-and-depth.md F1: fine if deliberate, but say so in "
                  "the brief; standing adult eye level is 1.5-1.7m (R = k*H_cam).")

    if metrics is None: metrics = {}
    room_checks(html, errs, warns, metrics)
    variation_checks(root, warns, metrics)
    light_checks(html, root, errs, warns, metrics)
    size_checks(html, root, errs, warns, metrics)

    return errs, warns, datum, pal

# ---------------- render tier (warnings only) ----------------

def find_chrome():
    for c in ("chromium", "google-chrome",
              "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        p = shutil.which(c) or (c if os.path.exists(c) else None)
        if p: return p
    return None

def render_checks(html_path, tmpdir):
    out = {"available": False}
    chrome, png = find_chrome(), os.path.join(tmpdir, "shot.png")
    try:
        from PIL import Image
    except ImportError:
        out["reason"] = "Pillow not installed (pip3 install pillow)"; return out
    if not chrome:
        out["reason"] = "no Chromium/Chrome binary found"; return out
    url = "file://" + os.path.abspath(html_path)
    # headless chrome reserves ~87px of the window for UI, so a --window-size of
    # 1440x900 only paints an 813px-tall viewport and the rest of the shot is page
    # background. Render taller, then crop back to the true 1440x900 frame.
    VIEW_W, VIEW_H, CHROME_H = 1440, 900, 87
    r = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={VIEW_W},{VIEW_H + CHROME_H}",
                        f"--screenshot={png}", url],
                       capture_output=True, timeout=60)
    if r.returncode != 0 or not os.path.exists(png):
        out["reason"] = "screenshot failed"; return out
    img = Image.open(png).convert("RGB")
    if img.size[1] > VIEW_H:
        img = img.crop((0, 0, min(VIEW_W, img.size[0]), VIEW_H))
    L = img.convert("L")
    hist = L.histogram(); total = sum(hist)
    bins16 = [sum(hist[i*16:(i+1)*16]) / total * 100 for i in range(16)]
    occupied = [i for i, pct in enumerate(bins16) if pct >= 1.5]
    mean = sum(hist[i]*i for i in range(256)) / total
    std = math.sqrt(sum(hist[i]*(i-mean)**2 for i in range(256)) / total)
    hsv = img.convert("HSV")
    raw = hsv.tobytes()                          # H,S,V byte triplets
    h_ch, s_ch = raw[0::3], raw[1::3]
    seen = set()
    for h, s in zip(h_ch[::37], s_ch[::37]):     # sample every 37th pixel
        if s > 60: seen.add(h // (256 // HUE_BUCKETS))
    # exposure structure. A picture reads as luminous when it OWNS its range:
    # true darks to sit on, a broad middle, and a decisive area of near-white.
    # Mean brightness is not the measure - a scene can average mid-grey and still
    # be gloomy because nothing in it is actually bright.
    pct = lambda lo, hi: sum(hist[lo:hi]) / total * 100
    out.update(available=True,
               metrics={"value_bins_occupied": len(occupied),
                        "value_span": f"{min(occupied)}..{max(occupied)}" if occupied else "-",
                        "luminance_std": round(std, 1),
                        "luminance_mean": round(mean, 1),
                        "shadow_pct": round(pct(0, 51), 1),
                        "highlight_pct": round(pct(154, 256), 1),
                        "specular_pct": round(pct(218, 256), 1),
                        "hue_buckets_used": len(seen)})
    # coverage: 6x4 grid, flag cells that are ~pure background
    px = img.load(); W, H = img.size
    from collections import Counter
    samples = [px[x, y] for y in range(0, H, 13) for x in range(0, W, 13)]
    bg = Counter((r//16, g//16, b//16) for r, g, b in samples).most_common(1)[0][0]
    def is_bg(p):
        return (p[0]//16, p[1]//16, p[2]//16) == bg
    voids = []
    cw, ch = W // GRID[0], H // GRID[1]
    for gy in range(GRID[1]):
        for gx in range(GRID[0]):
            pts = [px[x, y]
                   for y in range(gy*ch, min((gy+1)*ch, H), 11)
                   for x in range(gx*cw, min((gx+1)*cw, W), 11)]
            ink = sum(0 if is_bg(p) else 1 for p in pts) / max(len(pts), 1) * 100
            if ink < CELL_INK_MIN:
                voids.append(f"cell({gx},{gy})={ink:.1f}%")
    out["metrics"]["void_cells"] = voids
    out["_img"] = img
    return out

# ---------------- light-geometry tier ----------------
# Needs the scene to declare its rig:
#   <!-- LIGHTS: sun=sun@1300,430 | bar1=tube@620,300;axis=0;pool=620,700 |
#                lamp=point@150,150;pool=150,520 -->
# kinds: sun|moon (distant disc), point (bulb/pendant), tube (linear strip),
#        window (aperture), area. axis is the tube's long axis in degrees
#        (0 = horizontal on screen). pool is where its light lands.
DISC_ASPECT_MAX = 1.6     # blob this round counts as a "disc" (a sun-like source)
DISC_FILL_MIN = 0.5       # area / bbox area, to separate discs from ragged glows
TUBE_ASPECT_MIN = 1.8     # a linear emitter's footprint must be at least this long
TUBE_ANGLE_TOL = 25.0     # degrees its major axis may differ from the declared axis
BLOB_MIN_AREA = 700       # px; below this a bright spot is a specular, not a source
EXPLAIN_RADIUS = 110      # px a blob centroid may sit from a declared point

def parse_lights(html):
    cm = comments_of(html)
    m = re.search(r"LIGHTS:(.*?)(?:-->|$)", cm, re.S)
    if not m: return None
    lights = []
    for chunk in m.group(1).split("|"):
        chunk = chunk.strip().rstrip(",")
        if not chunk: continue
        head, *rest = chunk.split(";")
        hm = re.match(r"\s*(\w+)\s*=\s*(\w+)\s*@\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)", head)
        if not hm: continue
        L = {"name": hm.group(1), "kind": hm.group(2).lower(),
             "pos": (float(hm.group(3)), float(hm.group(4))),
             "axis": None, "pool": None}
        for opt in rest:
            am = re.match(r"\s*axis\s*=\s*(-?[\d.]+)", opt)
            pm = re.match(r"\s*pool\s*=\s*([A-Za-z][\w:.-]*)", opt)
            if am: L["axis"] = float(am.group(1))
            if pm: L["pool"] = pm.group(1)
        lights.append(L)
    return lights

def bright_blobs(img):
    """Advisory census of bright regions. Reported as a metric, never an error:
    pixel thresholds are scene-dependent and produced false 'suns' from desk
    highlights in testing. The enforceable physics lives in light_checks()."""
    try:
        import numpy as np
        from scipy import ndimage
    except ImportError:
        return None
    from scipy import ndimage as ndi
    a = np.asarray(img.convert("L"), dtype=float)
    # local contrast, so the operator works on a dark greenhouse and a bright
    # classroom alike, plus an absolute gate so mid-tone highlights are not sources
    diff = a - ndi.gaussian_filter(a, 55)
    gate = max(185.0, float(np.percentile(a, 99.2)))
    mask = (diff >= max(6.0, 2.2 * diff.std()))
    lab, n = ndimage.label(mask)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        area = xs.size
        if area < BLOB_MIN_AREA or a[ys, xs].mean() < gate: continue
        cx, cy = xs.mean(), ys.mean()
        dx, dy = xs - cx, ys - cy
        mu20, mu02, mu11 = (dx * dx).mean(), (dy * dy).mean(), (dx * dy).mean()
        common = math.sqrt(max((mu20 - mu02) ** 2 + 4 * mu11 * mu11, 0.0))
        l1, l2 = (mu20 + mu02 + common) / 2, (mu20 + mu02 - common) / 2
        aspect = math.sqrt(l1 / l2) if l2 > 1e-9 else 99.0
        theta = math.degrees(0.5 * math.atan2(2 * mu11, mu20 - mu02)) % 180.0
        bw, bh = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        out.append({"c": (cx, cy), "area": int(area), "aspect": round(aspect, 2),
                    "angle": round(theta, 1), "fill": round(area / (bw * bh), 2)})
    return sorted(out, key=lambda b: -b["area"])

SIZE_TOL = 0.30           # fraction an object's implied real size may drift
UNDECLARED_M = 0.60       # anything this big in metres must declare its real size

def parse_sizes(html):
    """<!-- SIZES: washer=0.85x1.10 | chair=0.50x0.89 --> in metres (w x h)."""
    cm = comments_of(html)
    m = re.search(r"SIZES:(.*?)(?:PALETTE:|LIGHTS:|SCALE:|DATUM|STYLE:|$)", cm, re.S)
    if not m: return None
    out = {}
    for chunk in m.group(1).split("|"):
        hm = re.match(r"\s*([\w:.-]+)\s*=\s*([\d.]+)\s*x\s*([\d.]+)", chunk)
        if hm: out[hm.group(1)] = (float(hm.group(2)), float(hm.group(3)))
    return out or None

def _data_real(el):
    """data-real="0.45x1.70" on ANY element - the declaration that works for
    objects drawn inline. Keying sizes off <use href> alone left every inline
    object unchecked, which is how the laundromat's human - the single best
    scale reference in the scene - was never measured."""
    v = el.get("data-real")
    if not v: return None
    m = re.match(r"\s*([\d.]+|\?)\s*x\s*([\d.]+|\?)", v)
    if not m: return None
    # "?" = not frontal on this axis. F7's drawn_px = real_m*k*s holds for a face
    # square to the camera; an object receding toward the VP has a foreshortened
    # screen extent that is NOT its real size, and demanding a number there would
    # only teach the builder to invent one.
    f = lambda g: None if g == "?" else float(g)
    return (f(m.group(1)), f(m.group(2)))

def _use_transform(el):
    tr = el.get("transform", "") or ""
    tx = ty = 0.0; sc = 1.0
    for m in re.finditer(r"(translate|scale)\s*\(([^)]*)\)", tr):
        a = [float(v) for v in re.split(r"[\s,]+", m.group(2).strip()) if v]
        if m.group(1) == "translate":
            tx += a[0]; ty += a[1] if len(a) > 1 else 0.0
        elif m.group(1) == "scale":
            sc = abs(a[0])
    try: tx += float(el.get("x", 0)); ty += float(el.get("y", 0))
    except (TypeError, ValueError): pass
    return tx, ty, sc

def size_checks(html, root, errs, warns, metrics):
    """Metric truth for EXTENTS, not just positions.

    Stage 4 derives every y from a real height, but an object's drawn WIDTH and
    HEIGHT come from a shape-library local box times a chosen scale. If that base
    size is never tied to reality the whole scene can be internally consistent and
    absolutely wrong - perspective-correct machines that are half size next to a
    correctly sized human. Declaring real sizes makes it checkable:

        drawn_px = real_m * k * s(y_anchor)      =>      scale = real_m*k*s / local_box
    """
    E = lambda c, d, h: errs.append({"check": c, "detail": d, "hint": h})
    W = lambda c, d, h: warns.append({"check": c, "detail": d, "hint": h})
    cm = comments_of(html)
    km = re.search(r"SCALE:\s*([\d.]+)\s*px", cm)
    hm = re.search(r"horizon\s*y\s*=\s*([\d.]+)", cm, re.I)
    dm = re.search(r"DATUM\s*y\s*=\s*([\d.]+)", cm)
    k = float(km.group(1)) if km else None
    y_h = float(hm.group(1)) if hm else None
    y_ref = float(dm.group(1)) if dm else None
    defs_map = {el.get("id"): el for el in walk(root) if el.get("id")}
    sizes = parse_sizes(html)
    metrics["_declared_ids"] = set(sizes or ())
    if sizes is None:
        W("sizes_declared", "no SIZES comment - object extents are not checked",
          "SKILL.md Stage 4: declare each recipe's real size, e.g. "
          "<!-- SIZES: washer=0.85x1.10 | chair=0.50x0.89 -->, or data-real=\"WxH\" "
          "on any group drawn inline. Objects not standing on the floor add "
          "data-floor=<the row their support stands on>.")
        undeclared_extents(root, defs_map, k, y_h, y_ref, warns, metrics)
        return
    if not km: return
    metrics["sizes_checked"] = 0
    seen = set()

    def s_of(el, ty):
        # s is a property of DEPTH, not screen row. Anything not standing on the
        # floor declares the row its support chain reaches.
        try:
            ground = float(el.get("data-floor")) if el.get("data-floor") else ty
        except (TypeError, ValueError):
            ground = ty
        if y_h is None or y_ref is None or y_ref <= y_h: return 1.0
        return (ground - y_h) / (y_ref - y_h)

    for el in walk(root):
        want = _data_real(el)
        href = ""
        if local(el) == "use":
            href = (el.get("href") or el.get("{http://www.w3.org/1999/xlink}href") or "").lstrip("#")
            if want is None: want = sizes.get(href)
        if want is None: continue
        if local(el) == "use":
            target = defs_map.get(href)
            if target is None: continue
            bb = element_bbox(target, defs_map)
            if not bb: continue
            lw, lh = bb[2] - bb[0], bb[3] - bb[1]
            tx, ty, sc = _use_transform(el)
        else:
            bb = element_bbox(el, defs_map)
            if not bb: continue
            lw, lh = bb[2] - bb[0], bb[3] - bb[1]
            tx, ty, sc = bb[0], bb[3], 1.0     # inline: box IS the drawn size, feet at bb[3]
            href = el.get("id") or local(el)
        if lw <= 0 or lh <= 0: continue
        s = s_of(el, ty)
        if s <= 0.02: continue
        real_w, real_h = want
        if real_w is None and real_h is None: continue
        got_w, got_h = lw * sc / (k * s), lh * sc / (k * s)
        metrics["sizes_checked"] += 1
        for label, got, want in (("width", got_w, real_w), ("height", got_h, real_h)):
            if want is None or want <= 0: continue
            drift = abs(got - want) / want
            if drift > SIZE_TOL and (href, label) not in seen:
                seen.add((href, label))
                E("object_scale",
                  f"'{href}' drawn {got:.2f}m {label} but declared {want:.2f}m "
                  f"({drift:.0%} off) at y={ty:.0f}",
                  f"perspective-and-depth.md F7: scale = real_m*k*s/local_box. "
                  f"Here scale should be "
                  f"{want * k * s / (lw if label == 'width' else lh):.3f}, not {sc:g}. "
                  "Deriving position from metric truth but eyeballing size is how a "
                  "scene ends up internally consistent and absolutely wrong.")

    undeclared_extents(root, defs_map, k, y_h, y_ref, warns, metrics)

def _size_loop_done(root, defs_map, k, y_h, y_ref, warns, metrics):
    undeclared_extents(root, defs_map, k, y_h, y_ref, warns, metrics)

def undeclared_extents(root, defs_map, k, y_h, y_ref, warns, metrics):
    """Silence must not read the same as correctness.

    A declared object gets measured; an undeclared one is simply invisible to the
    check, and those two states looked identical in the report. So: sweep the
    object phases and warn about anything furniture-sized that never said how big
    it is. This is the rule that would have caught the laundromat's human, who is
    drawn inline and so was never measured at all.
    """
    if not k or y_h is None or y_ref is None or y_ref <= y_h: return
    W = lambda c, d, h: warns.append({"check": c, "detail": d, "hint": h})
    OBJECT_PHASES = ("5", "6", "8")            # furniture, millwork, foreground
    offenders = []
    for g in walk(root):
        if local(g) != "g": continue
        gid = g.get("id") or ""
        m = re.match(r"phase-(\d+)", gid)
        if not m or m.group(1) not in OBJECT_PHASES: continue
        for child in list(g):
            if local(child) not in ("g", "use", "rect", "path", "polygon", "ellipse", "circle"):
                continue
            if _data_real(child): continue
            # objects have extents; light does not. A bloom, a glow or any
            # blurred element is part of the light story, not the inventory.
            if child.get("filter"): continue
            if local(child) == "use":
                href = (child.get("href") or
                        child.get("{http://www.w3.org/1999/xlink}href") or "").lstrip("#")
                if href in (metrics.get("_declared_ids") or set()): continue
            bb = element_bbox(child, defs_map)
            if not bb: continue
            h_px = bb[3] - bb[1]
            try:
                ground = float(child.get("data-floor")) if child.get("data-floor") else bb[3]
            except (TypeError, ValueError):
                ground = bb[3]
            sc = (ground - y_h) / (y_ref - y_h)
            if sc <= 0.02: continue
            real_h = h_px / (k * sc)
            if real_h >= UNDECLARED_M:
                offenders.append((real_h, child.get("id") or local(child), gid))
    if not offenders: return
    offenders.sort(reverse=True)
    metrics["undeclared_objects"] = len(offenders)
    top = ", ".join(f"{n} in {ph} (~{h:.1f}m tall)" for h, n, ph in offenders[:4])
    W("extents_undeclared",
      f"{len(offenders)} object(s) >= {UNDECLARED_M}m carry no declared real size: {top}",
      "perspective-and-depth.md F7: add data-real=\"WxH\" (metres) to the group, "
      "or list it in SIZES if it is a <use>. An undeclared object is not a passing "
      "object - it is an unmeasured one, and the biggest thing in the frame is "
      "exactly where a scale error does the most damage.")

def variation_checks(root, warns, metrics):
    """Density is a COUNT. Realism is DIFFERENCE.

    The density floor is satisfied by 80 identical circles, and a wall of twelve
    <use> clones of one washer is exactly that: it passes every structural check
    and reads as a rendering of a spreadsheet. Real repeated objects differ in
    three ways - STATE (door open, machine running), AGE (wear, discolouration)
    and CONTENT (loaded, empty, occupied) - and it is those differences, not the
    element count, that make a row of things look photographed rather than
    tiled.

    What is measurable here is whether the instances differ at all. A clone that
    varies only in position and uniform scale is the same object drawn twice.
    """
    W = lambda c, d, h: warns.append({"check": c, "detail": d, "hint": h})
    # a <use> inside <defs> is part of a symbol's construction, not an instance
    # of it in the scene; counting those inflates the instance count and lets a
    # wall of clones slip under the threshold.
    in_defs = set()
    for d in walk(root):
        if local(d) in ("defs", "symbol"):
            for c in walk(d): in_defs.add(id(c))
    groups = {}
    for el in walk(root):
        if local(el) != "use" or id(el) in in_defs: continue
        href = (el.get("href") or
                el.get("{http://www.w3.org/1999/xlink}href") or "").lstrip("#")
        if not href: continue
        tr = el.get("transform", "") or ""
        sig = (el.get("fill"), el.get("opacity"), el.get("filter"),
               "rotate" in tr, "-" in re.sub(r"translate\([^)]*\)", "", tr))
        groups.setdefault(href, []).append(sig)

    flat = []
    for href, sigs in sorted(groups.items()):
        n = len(sigs)
        if n < 4: continue
        distinct = len(set(sigs))
        need = 1 + n // 4
        metrics.setdefault("repeats", {})[href] = f"{distinct}/{n} variants"
        if distinct < need:
            flat.append((href, n, distinct, need))
    if not flat: return
    worst = ", ".join(f"{h} x{n} with {d} variant(s), want >={w}"
                      for h, n, d, w in flat)
    W("repeat_variation",
      f"repeated objects are identical clones: {worst}",
      "art-direction.md: repeats must vary in STATE (door open/ajar, running/idle), "
      "AGE (wear, discolouration, a replaced panel) and CONTENT (loaded, empty, "
      "occupied). Give the symbol variants, or override fill/opacity per instance. "
      "The density floor counts elements; it cannot tell a crowd from a tiling, "
      "and a wall of identical clones is the single loudest tell that a scene was "
      "generated rather than observed.")

def room_checks(html, errs, warns, metrics):
    """F8 - the envelope must close.

    Stage 0 declares the room in metres and how the floor is spent across it.
    The arithmetic either closes or it does not, and it closes or fails BEFORE
    any coordinate exists. This is the cheapest possible check and it catches the
    class of error no pixel measurement can: a plan that is not physically
    possible in the room it claims to be in.

        <!-- ROOM: 4.20w x 6.00d x 2.70h -->
        <!-- SPAN width: washers=0.85 aisle=2.40 washers=0.85 -->
    """
    E = lambda c, d, h: errs.append({"check": c, "detail": d, "hint": h})
    W = lambda c, d, h: warns.append({"check": c, "detail": d, "hint": h})
    cm = comments_of(html)
    rm = re.search(r"ROOM:\s*([\d.]+)\s*w\s*x\s*([\d.]+)\s*d\s*x\s*([\d.]+)\s*h", cm, re.I)
    if not rm:
        W("room_declared", "no ROOM comment - the envelope is not stated",
          "SKILL.md Stage 0: declare the room in metres, "
          "<!-- ROOM: 4.20w x 6.00d x 2.70h -->. A scene with no stated envelope "
          "cannot be checked for whether its plan physically fits.")
        return
    room = {"width": float(rm.group(1)), "depth": float(rm.group(2)),
            "height": float(rm.group(3))}
    metrics["room_m"] = [room["width"], room["depth"], room["height"]]
    if not (1.5 <= room["height"] <= 12.0):
        E("room_plausible", f"ceiling {room['height']:.2f}m is not a room",
          "domestic 2.4-2.7m, commercial 3.0-4.5m, industrial up to ~12m")

    STOP = r"(?=ROOM:|SPAN\s|SIZES:|PALETTE:|LIGHTS:|SCALE:|DATUM|STYLE:|PERSPECTIVE:|$)"
    for sm in re.finditer(r"SPAN\s+(width|depth)\s*:\s*(.*?)" + STOP, cm, re.I | re.S):
        axis = sm.group(1).lower()
        parts = re.findall(r"([\w-]+)\s*=\s*([\d.]+)", sm.group(2))
        if not parts: continue
        total = sum(float(v) for _, v in parts)
        have = room[axis]
        drift = abs(total - have) / have
        detail = " + ".join(f"{n} {v}" for n, v in parts)
        if drift > 0.05:
            E("envelope_closes",
              f"{axis} span sums to {total:.2f}m but ROOM says {have:.2f}m "
              f"({detail})",
              "perspective-and-depth.md F8: the floor is fully spent - every metre "
              "of the room is either an object footprint or circulation. If the sum "
              "does not close, the plan is not possible in this room; change the "
              "room or change the plan, before placing a single coordinate.")
        else:
            metrics.setdefault("spans_closed", []).append(axis)

    circ = [float(v) for sm in re.finditer(r"SPAN\s+(?:width|depth)\s*:\s*(.*?)" + STOP,
                                           cm, re.I | re.S)
            for n, v in re.findall(r"([\w-]+)\s*=\s*([\d.]+)", sm.group(1))
            if re.search(r"aisle|walk|circulation|gap", n, re.I)]
    for c in circ:
        if c < 0.75:
            W("circulation", f"a {c:.2f}m aisle is below walking width",
              "a person needs ~0.75m to pass and ~1.10m for two-way traffic; "
              "an aisle narrower than that is a plan error, not a tight composition")

def _pool_geometry(el):
    """Screen-space (aspect, major-axis angle deg) of a drawn pool element."""
    tag = local(el)
    rot = 0.0
    rm = re.search(r"rotate\s*\(\s*(-?[\d.]+)", el.get("transform", "") or "")
    if rm: rot = float(rm.group(1))
    def num(a, d=0.0):
        try: return float(el.get(a, d))
        except (TypeError, ValueError): return d
    if tag == "ellipse":
        rx, ry = num("rx"), num("ry")
    elif tag == "circle":
        rx = ry = num("r")
    elif tag == "rect":
        rx, ry = num("width") / 2, num("height") / 2
    else:
        bb = element_bbox(el)
        if not bb: return None
        rx, ry = (bb[2] - bb[0]) / 2, (bb[3] - bb[1]) / 2
    if rx <= 0 or ry <= 0: return None
    aspect = max(rx, ry) / min(rx, ry)
    angle = (0.0 if rx >= ry else 90.0) + rot
    return aspect, angle % 180.0, tag

def light_checks(html, root, errs, warns, metrics):
    """Physics of footprints, checked on the SVG source - no pixels, no thresholds.

    The footprint of a light is its emitter's shape projected along the light
    direction onto the receiving surface, then foreshortened by the camera. Two
    consequences are deterministic and therefore enforceable:
      * a linear emitter's pool is elongated ALONG the emitter's projected axis;
        a circular pool from a strip light is physically impossible;
      * on a floor seen in perspective every pool is compressed perpendicular to
        the horizon, so a pool's major axis is horizontal unless the emitter's
        own shape overrides it.
    How MANY sources a scene has is semantics, not physics - that is a rule in
    perspective-and-depth.md section 8 and a job for the visual review, not this.
    """
    E = lambda c, d, h: errs.append({"check": c, "detail": d, "hint": h})
    W = lambda c, d, h: warns.append({"check": c, "detail": d, "hint": h})
    lights = parse_lights(html)
    if lights is None:
        W("lights_declared", "no LIGHTS comment - footprint physics not checked",
          "SKILL.md Stage 3: declare the rig, e.g. <!-- LIGHTS: "
          "sun=sun@1300,430 | bar=tube@620,300;axis=0;pool=pool-bar -->")
        return
    metrics["lights"] = [f"{L['name']}:{L['kind']}" for L in lights]
    by_id = {el.get("id"): el for el in walk(root) if el.get("id")}

    for L in lights:
        if L["kind"] in ("sun", "moon"):
            continue                       # distant sources: no local footprint
        pid = L.get("pool")
        if not pid:
            W("pool_undeclared",
              f"light '{L['name']}' ({L['kind']}) declares no pool element",
              "every emitter lands light on something - draw the pool, give it "
              "id=\"pool-<name>\", and add pool=<that id> to LIGHTS")
            continue
        el = by_id.get(pid)
        if el is None:
            E("pool_missing",
              f"light '{L['name']}' names pool '{pid}' but no element has that id",
              "add the pool element, or correct the id in the LIGHTS comment")
            continue
        g = _pool_geometry(el)
        if g is None:
            W("pool_unmeasurable", f"pool '{pid}' has no measurable extent",
              "give the pool element explicit geometry"); continue
        aspect, angle, tag = g
        if L["kind"] == "tube":
            axis = (L["axis"] or 0.0) % 180.0
            # A tube perpendicular to the view direction (axis near horizontal on
            # screen) has its own length AND the floor's foreshortening pulling the
            # same way, so its pool must be clearly elongated. A tube running away
            # toward the vanishing point foreshortens instead, so only its
            # orientation is enforceable.
            perpendicular = min(axis, 180.0 - axis) <= 30.0
            if perpendicular and aspect < TUBE_ASPECT_MIN:
                E("pool_shape_mismatch",
                  f"tube '{L['name']}' (axis {axis:g}deg) has a round pool "
                  f"'{pid}' (aspect {aspect:.2f}, need >= {TUBE_ASPECT_MIN})",
                  "perspective-and-depth.md section 8: a strip light's footprint is "
                  "its own length projected onto the surface, then flattened by the "
                  "camera - both stretch it sideways. A circle is impossible here; "
                  "only a point source makes one.")
            d = abs((angle - axis + 90) % 180 - 90)
            if aspect >= 1.3 and d > TUBE_ANGLE_TOL:
                E("pool_angle_mismatch",
                  f"tube '{L['name']}' pool '{pid}' runs at {angle:g}deg but the "
                  f"tube axis is {axis:g}deg (off by {d:.0f}deg)",
                  "the pool's long axis stays parallel to the emitter's projected "
                  "axis; the light's direction of travel skews it, never rotates it "
                  "square to the tube.")
        elif L["kind"] in ("point", "area"):
            if aspect >= 1.3 and abs((angle + 90) % 180 - 90) > 40.0:
                W("pool_angle_odd",
                  f"{L['kind']} light '{L['name']}' has an elongated pool '{pid}' "
                  f"tilted {angle:g}deg",
                  "a compact source on a floor foreshortens into a HORIZONTAL "
                  "ellipse; a steeply tilted one implies a shape the emitter "
                  "does not have.")
        elif L["kind"] == "window":
            if tag in ("ellipse", "circle"):
                E("pool_shape_mismatch",
                  f"window '{L['name']}' casts an elliptical pool '{pid}'",
                  "a rectangular aperture projects to a QUADRILATERAL (a skewed "
                  "rectangle), not an ellipse - use a polygon/path.")

def judge_render(rc, warns):
    if not rc.get("available"):
        warns.append({"check": "render_tier", "detail": rc.get("reason", "unavailable"),
                      "hint": "install Pillow + Chrome for value/hue analysis"})
        return
    m = rc["metrics"]
    if m["value_bins_occupied"] < 6:
        warns.append({"check": "value_structure",
                      "detail": f"only {m['value_bins_occupied']} tonal bins populated "
                                f"(span {m['value_span']})",
                      "hint": "art-direction.md §1: separate background/mid/foreground tones more"})
    # L9 - exposure: own the range. Thresholds are the floor of what reads as lit,
    # not a target; a deliberately crushed scene resolves this in writing.
    if m.get("specular_pct", 0) < 0.8:
        warns.append({"check": "no_highlights",
                      "detail": f"only {m.get('specular_pct', 0)}% of the frame is above 85% "
                                f"luminance (mean {m.get('luminance_mean')})",
                      "hint": "perspective-and-depth.md L9: a frame with no near-white reads "
                              "as gloomy whatever its subject - a 2100K oven interior scored "
                              "0.0% and looked it. Give the key something bright to land on: a "
                              "lit plane facing the source, a specular edge, a bright opening. "
                              "Not a global brightness lift - a decisive small area."})
    elif m.get("highlight_pct", 0) < 6:
        warns.append({"check": "no_highlights",
                      "detail": f"only {m.get('highlight_pct', 0)}% of the frame is above 60% "
                                f"luminance - the upper range is nearly unused",
                      "hint": "perspective-and-depth.md L9: widen the lit territory, or say in "
                              "writing why this scene is deliberately low-key."})
    if m.get("shadow_pct", 0) < 1.5:
        warns.append({"check": "no_darks",
                      "detail": f"only {m.get('shadow_pct', 0)}% of the frame is below 20% "
                                f"luminance - nothing anchors the value scale",
                      "hint": "perspective-and-depth.md L9: without true darks a bright scene "
                              "reads as washed rather than sunlit. Occlusion contact, a doorway, "
                              "a deep shadow side."})
    if m["hue_buckets_used"] > 6:
        warns.append({"check": "palette_discipline_pixels",
                      "detail": f"{m['hue_buckets_used']} hue families visible (>6)",
                      "hint": "cut accent colors; art-direction.md §2"})
    for v in m.get("void_cells", []):
        warns.append({"check": "coverage_void", "detail": v,
                      "hint": "Stage 5 density: add a prop, texture band, or shift composition"})

# ---------------- self test ----------------

def selftest():
    pad = "".join(f'<circle cx="{20+i*14}" cy="{40+(i%3)*20}" r="4" fill="#FEF6E4"/>'
                  for i in range(24))
    good = f"""<!DOCTYPE html><html><body><!-- SCALE: 288px = 1m --><!-- DATUM y=720 -->
<!-- PALETTE: #FEF6E4 #001858 #2B2B5C -->
<svg viewBox="0 0 1440 900" xmlns="http://www.w3.org/2000/svg"><defs>
<linearGradient id="w"><stop offset="0%" stop-color="#FEF6E4"/><stop offset="50%" stop-color="#FEF6E4"/><stop offset="100%" stop-color="#FEF6E4"/></linearGradient>
<linearGradient id="w2"><stop offset="0%" stop-color="#FEF6E4"/><stop offset="50%" stop-color="#FEF6E4"/><stop offset="100%" stop-color="#FEF6E4"/></linearGradient>
<linearGradient id="w3"><stop offset="0%" stop-color="#FEF6E4"/><stop offset="50%" stop-color="#FEF6E4"/><stop offset="100%" stop-color="#FEF6E4"/></linearGradient>
<linearGradient id="w4"><stop offset="0%" stop-color="#FEF6E4"/><stop offset="50%" stop-color="#FEF6E4"/><stop offset="100%" stop-color="#FEF6E4"/></linearGradient>
<filter id="g"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="2"/><feColorMatrix type="saturate" values="0"/></filter></defs>
<g id="phase-1-shell"><rect width="1440" height="900" fill="url(#w)"/></g>
<g id="phase-2-portals"><rect x="1000" y="100" width="300" height="400" fill="#FEF6E4"/></g>
<g id="phase-3-fixtures"><rect x="10" y="150" width="80" height="80" fill="#FEF6E4"/>{pad}</g>
<g id="phase-4-volumetrics"><polygon points="0,100 200,100 300,720 100,720" fill="#FEF6E4" opacity="0.15"/></g>
<g id="phase-5-furniture"><rect x="500" y="504" width="300" height="16" fill="#001858"/><line x1="520" y1="520" x2="520" y2="720" stroke="#001858" stroke-width="4"/></g>
<g id="phase-6-millwork"><rect x="900" y="600" width="120" height="120" fill="#001858"/></g>
<g id="phase-7-occlusion"><ellipse cx="650" cy="721" rx="90" ry="8" fill="#2B2B5C" opacity="0.16"/></g>
<g id="phase-8-foreground"><rect x="1100" y="600" width="60" height="120" fill="#001858"/></g>
</svg></body></html>"""
    e, w, datum, pal = static_checks(good)
    assert datum == 720 and len(pal) == 3, (datum, pal)
    phase_errs = [x for x in e if x["check"].startswith("phases_")]
    assert not phase_errs, phase_errs          # regression: namespaced <g> must be found
    contact = [x for x in e if x["check"] == "floor_contact"]
    assert not contact, contact
    density = [x for x in e if x["check"] == "density"]
    assert not density, density                # 24 pad + ~12 base >= MIN_ELEMENTS
    assert not [x for x in e if x["check"] == "wall_collisions"], e

    # regression: shorthand/relative path commands must not blow up the bbox.
    # "M572 443 v10 h8" spans x 572..580, y 443..453 - the old regex pairing
    # read it as the point (10,8) and invented collisions far from the shape.
    bb = num_pairs_from_path("M572 443 v10 h8")
    xs, ys = [p[0] for p in bb], [p[1] for p in bb]
    assert (min(xs), max(xs), min(ys), max(ys)) == (572, 580, 443, 453), bb
    rel = num_pairs_from_path("m10 10 l5 0 l0 5 z")
    assert (max(p[0] for p in rel), max(p[1] for p in rel)) == (15, 15), rel

    collide = good.replace('<rect x="900" y="600" width="120" height="120" fill="#001858"/>',
                           '<rect x="40" y="170" width="60" height="40" fill="#001858"/>')
    e2, _, _, _ = static_checks(collide)
    checks2 = {x["check"] for x in e2}
    assert "wall_collisions" in checks2, e2    # phase-3 rect (10,150,80x80) vs phase-6 (40,170)
    bad = good.replace("#2B2B5C", "#000000").replace("DATUM y=720", "")
    e3, _, _, _ = static_checks(bad)
    checks3 = {x["check"] for x in e3}
    assert "no_pure_black" in checks3 and "datum_declared" in checks3, e3
    print("selftest OK", file=sys.stderr)

# ---------------- main ----------------

def main():
    args = sys.argv[1:]
    if "--selftest" in args:
        selftest(); return
    if not args or args[0].startswith("-"):
        die("usage: eval_scene.py scene.html [--render]")
    path = args[0]
    if not os.path.exists(path): die(f"not found: {path}")
    html = open(path, encoding="utf-8").read()
    smetrics = {}
    errs, warns, datum, pal = static_checks(html, smetrics)
    smetrics = {k: v for k, v in smetrics.items() if not k.startswith("_")}
    do_render = "--render" in args
    rc = {"available": False}
    if do_render:
        with tempfile.TemporaryDirectory() as td:
            rc = render_checks(path, td)
            judge_render(rc, warns)
            if rc.get("available"):
                b = bright_blobs(rc.pop("_img"))
                if b is not None:
                    rc["metrics"]["bright_blobs"] = len(b)
        rc.pop("_img", None)
    report = {"file": path, "errors": errs, "warnings": warns,
              "metrics": smetrics, "render": rc, "pass": len(errs) == 0}
    print(json.dumps(report, indent=2))
    status = "PASS" if not errs else f"FAIL ({len(errs)} errors)"
    print(f"\n{status} | errors={len(errs)} warnings={len(warns)}", file=sys.stderr)
    for x in errs:
        print(f"  ERROR {x['check']}: {x['detail']}\n         -> {x['hint']}", file=sys.stderr)
    for x in warns:
        print(f"  warn  {x['check']}: {x['detail']} -> {x['hint']}", file=sys.stderr)
    if not errs:
        print(
            "\n  NOTE: this PASS is a STRUCTURAL check only - math, contact, phase\n"
            "  order, gradient/grain presence, density, collisions, and that every\n"
            "  color used is in the declared PALETTE comment. It does not know what\n"
            "  a real Parisian cafe, a specific mountain, or any named place actually\n"
            "  looks like, and it cannot judge material quality, proportion, or\n"
            "  cultural authenticity. Do not treat this exit code as a quality\n"
            "  sign-off: render the file, look at it critically, and for any real or\n"
            "  named place verify the props/palette against real reference before\n"
            "  calling the scene done (SKILL.md Stage 6).", file=sys.stderr)
    sys.exit(0 if not errs else 1)

if __name__ == "__main__":
    main()
