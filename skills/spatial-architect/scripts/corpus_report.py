#!/usr/bin/env python3
"""Corpus report - tests the rules a unit test cannot reach.

Some rules are instructions to a model, not code: "derive the palette per scene",
"pick the camera height", "the light setting is a (key, ambient, shadow) triple".
A per-scene check can never tell you whether those are working, because the
failure mode is CONVERGENCE - every scene individually valid, the whole corpus
identical. Both real regressions in this project were of that kind and both were
caught by eye, late.

This measures the corpus instead: if a "derive it per scene" rule is working, the
outputs must SPREAD. Clustering is the failure signal.

Run: python3 corpus_report.py <dir-of-scenes>
"""
import re, sys, os, glob, math, colorsys

def parse(path):
    s = open(path, encoding="utf-8").read()
    cm = " ".join(re.findall(r"<!--(.*?)-->", s, re.S))
    g = lambda p, d=None, f=str: (f(m.group(1)) if (m := re.search(p, cm, re.I)) else d)
    svg = re.search(r"<svg[\s\S]*?</svg>", s)
    pal = [h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}", cm.split("PALETTE:")[-1])]
    return {
        "name": os.path.basename(path).replace(".html", ""),
        "k": g(r"SCALE:\s*([\d.]+)\s*px", None, float),
        "datum": g(r"DATUM\s*y\s*=\s*([\d.]+)", None, float),
        "horizon": g(r"horizon\s*y\s*=\s*([\d.]+)", None, float),
        "style": g(r"STYLE:\s*([\w-]+)", "unset"),
        "lights": re.findall(r"(\w+)=(\w+)@", cm.split("LIGHTS:")[-1]) if "LIGHTS:" in cm else [],
        "palette": pal,
        "elements": len(re.findall(r"<(rect|circle|ellipse|line|path|polygon|polyline|use|text)\b",
                                   svg.group(0))) if svg else 0,
        "bytes": len(svg.group(0).encode()) if svg else 0,
    }

def hue_signature(pal):
    """Palette signature as CLUSTERS, not a centroid.

    The first version took one saturation-weighted circular mean, and it could
    not tell a uniformly warm daylight palette from a warm-key/cool-shadow one:
    the cool half partly cancels the warm half and both land on the same mean.
    It duly reported a 2100K oven interior and a noon mountain teahouse as
    near-duplicates. Same disease the eval had - measuring the middle of a
    distribution and calling it the distribution (lessons.md #11).

    So: split the hue circle at its largest gap, take each arc's own circular
    mean, and carry the warm/cool balance as part of the signature.
    """
    pts = []
    s_sum = v_sum = 0.0
    n = 0
    for h in pal:
        r, g, b = (int(h[i:i+2], 16) / 255 for i in (1, 3, 5))
        hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
        s_sum += ss; v_sum += vv; n += 1
        if ss >= 0.08: pts.append((hh * 360, ss))
    if not n: return None
    if not pts: return (0.0, 0.0, 0.0, s_sum / n, v_sum / n)
    d = sorted(p[0] for p in pts)
    gaps = [((d[(i + 1) % len(d)] - d[i]) % 360, i) for i in range(len(d))]
    _, cut = max(gaps)
    order = d[cut + 1:] + d[:cut + 1]
    # second-largest gap splits the remaining arc into two clusters
    inner = [((order[i + 1] - order[i]) % 360, i) for i in range(len(order) - 1)]
    if inner:
        _, k = max(inner)
        a, b = order[:k + 1], order[k + 1:]
    else:
        a, b = order, []
    def cmean(xs):
        if not xs: return None
        x = sum(math.cos(math.radians(v)) for v in xs)
        y = sum(math.sin(math.radians(v)) for v in xs)
        return math.degrees(math.atan2(y, x)) % 360
    ha, hb = cmean(a), cmean(b)
    if hb is None: hb = ha
    frac = len(a) / max(1, len(a) + len(b))
    lo, hi = (ha, hb) if len(a) >= len(b) else (hb, ha)
    return (lo, hi, frac, s_sum / n, v_sum / n)

def hue_gap(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    files = sorted(glob.glob(os.path.join(root, "**", "*.html"), recursive=True))
    scenes = [parse(f) for f in files]
    scenes = [s for s in scenes if s["k"] and s["datum"]]
    if not scenes:
        print("no scenes with SCALE/DATUM found under", root); return 1

    print(f"corpus report - {len(scenes)} scenes under {root}\n")
    print(f"{'scene':34s} {'H_cam':>6} {'hues':>9} {'sat':>5} {'val':>5} {'elems':>6} {'bytes':>6}  lights")
    sigs = []
    for s in scenes:
        H = (s["datum"] - s["horizon"]) / s["k"] if s["horizon"] else float("nan")
        sig = hue_signature(s["palette"])
        sigs.append((s["name"], H, sig))
        hue, hue2, frac, sat, val = sig if sig else (float('nan'),) * 5
        kinds = ",".join(sorted({k for _, k in s["lights"]})) or "-"
        print(f"{s['name'][:34]:34s} {H:6.2f} {hue:4.0f}/{hue2:<4.0f} {sat:5.2f} {val:5.2f} "
              f"{s['elements']:6d} {s['bytes']:6d}  {kinds}")

    print("\n--- spread checks (a 'derive per scene' rule works only if these spread) ---")
    ok = True

    hs = [H for _, H, _ in sigs if H == H]
    if hs:
        lo, hi = min(hs), max(hs)
        span = hi - lo
        seated = sum(1 for H in hs if H < 1.5)
        verdict = "OK" if span >= 0.35 else "CLUSTERED"
        if span < 0.35: ok = False
        print(f"[{verdict}] camera height: {lo:.2f}-{hi:.2f}m (span {span:.2f}m); "
              f"{seated}/{len(hs)} below standing eye level")
        if seated == len(hs):
            print("         every camera is seated/low - F1 is being inherited, not chosen")
            ok = False

    pairs = []
    for i in range(len(sigs)):
        for j in range(i + 1, len(sigs)):
            (n1, _, s1), (n2, _, s2) = sigs[i], sigs[j]
            if not (s1 and s2): continue
            d = math.sqrt((hue_gap(s1[0], s2[0]) / 180) ** 2 * 2
                          + (hue_gap(s1[1], s2[1]) / 180) ** 2 * 2
                          + (s1[2] - s2[2]) ** 2
                          + (s1[3] - s2[3]) ** 2 + (s1[4] - s2[4]) ** 2)
            pairs.append((d, n1, n2))
    pairs.sort()
    if pairs:
        near = [p for p in pairs if p[0] < 0.35]
        verdict = "OK" if not near else "CLUSTERED"
        if near: ok = False
        print(f"[{verdict}] palette spread: closest pair distance {pairs[0][0]:.2f} "
              f"({pairs[0][1]} vs {pairs[0][2]})")
        for d, a, b in near[:5]:
            print(f"         near-duplicate palettes ({d:.2f}): {a} / {b}")

    declared = sum(1 for s in scenes if s["lights"])
    print(f"[{'OK' if declared == len(scenes) else 'GAP'}] light rig declared: "
          f"{declared}/{len(scenes)} scenes")
    if declared != len(scenes): ok = False

    styles = {s["style"] for s in scenes}
    print(f"[{'OK' if len(styles) > 1 else 'NOTE'}] style presets in use: {', '.join(sorted(styles))}")

    print("\n" + ("corpus looks healthy" if ok else
                  "corpus shows convergence - the derivation rules are not biting"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
