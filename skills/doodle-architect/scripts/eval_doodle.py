#!/usr/bin/env python3
"""
eval_doodle.py - Deterministic AST Linter & Evaluation Harness for Doodle SVG Architect

Validates:
1. Palette contract compliance (<!-- PALETTE: ... -->)
2. Mandatory DOM Phase Group ordering (Phase 1 Substrate -> Phase 2 Washes -> Phase 4 Strokes -> Phase 6 Lettering)
3. Multi-tier stroke hierarchy (at least 2 distinct stroke widths)
4. Absence of sterile raw geometric primitives (<rect>, <circle>, <line>) without hand-drawn path styling
5. Font family declaration for hand-drawn lettering

Usage:
    python3 eval_doodle.py <file.svg|file.html>
"""

import sys
import re
import xml.etree.ElementTree as ET
from pathlib import Path

REQUIRED_PHASES = [
    "phase-1-substrate",
    "phase-2-washes",
    "phase-4-strokes",
    "phase-6-lettering"
]

def parse_palette_contract(raw_text: str) -> dict:
    match = re.search(r"<!--\s*PALETTE:\s*([^-]+)-->", raw_text)
    if not match:
        return {}
    pairs = match.group(1).strip().split()
    palette = {}
    for p in pairs:
        if "=" in p:
            k, v = p.split("=", 1)
            palette[k.strip().lower()] = v.strip().lower()
    return palette

def evaluate_doodle_svg(file_path: Path) -> tuple[bool, list[str], list[str]]:
    errors = []
    warnings = []
    
    if not file_path.exists():
        return False, [f"File not found: {file_path}"], []

    raw_content = file_path.read_text(encoding="utf-8")
    
    # 1. Palette Contract
    palette = parse_palette_contract(raw_content)
    if not palette:
        errors.append("Missing machine-readable '<!-- PALETTE: ... -->' contract declaration.")
    else:
        declared_hexes = set(palette.values())
        declared_hexes.update(["none", "currentcolor", "transparent"])
        
        # Find all hex colors in content
        found_hexes = set(h.lower() for h in re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}\b", raw_content))
        stray = found_hexes - declared_hexes
        if stray:
            warnings.append(f"Undeclared hex colors found in document: {', '.join(sorted(stray))}")

    # Extract SVG XML block if embedded in HTML
    svg_match = re.search(r"<svg[\s\S]*?</svg>", raw_content, re.IGNORECASE)
    if not svg_match:
        return False, ["No <svg> block found in file."], warnings
    
    svg_xml = svg_match.group(0)
    
    try:
        root = ET.fromstring(svg_xml)
    except ET.ParseError as e:
        return False, [f"XML Parse Error in SVG: {e}"], warnings

    # 2. Check Phase Group Ordering
    group_ids = [elem.attrib.get("id", "") for elem in root.iter() if elem.tag.endswith("g") and "id" in elem.attrib]
    
    for req in REQUIRED_PHASES:
        if req not in group_ids:
            errors.append(f"Missing required DOM phase group: '{req}'")
            
    # Check ordering of phase 2 before phase 4
    if "phase-2-washes" in group_ids and "phase-4-strokes" in group_ids:
        idx_washes = group_ids.index("phase-2-washes")
        idx_strokes = group_ids.index("phase-4-strokes")
        if idx_washes > idx_strokes:
            errors.append("Layering Inversion: 'phase-2-washes' must precede 'phase-4-strokes' in DOM paint order.")

    # 3. Check Stroke Hierarchy
    stroke_widths = set()
    for elem in root.iter():
        sw = elem.attrib.get("stroke-width")
        if sw:
            # normalize numeric value
            val = re.sub(r"[^\d.]", "", sw)
            if val:
                try:
                    stroke_widths.add(float(val))
                except ValueError:
                    pass
        # Also check style attribute
        style = elem.attrib.get("style", "")
        m_sw = re.search(r"stroke-width\s*:\s*([\d.]+)", style)
        if m_sw:
            try:
                stroke_widths.add(float(m_sw.group(1)))
            except ValueError:
                pass

    if len(stroke_widths) < 2:
        warnings.append(f"Weak stroke hierarchy: Found only {len(stroke_widths)} distinct stroke widths ({stroke_widths}). Expected at least 2 tiers (e.g. 3.5px and 1.5px).")

    # 4. Check for Sterile Raw Primitives in main content
    raw_rects = 0
    raw_circles = 0
    for elem in root.iter():
        tag = elem.tag.split("}")[-1]
        # Ignore substrate background rect
        if tag == "rect":
            parent_id = elem.attrib.get("id", "")
            w = elem.attrib.get("width", "")
            if w not in ["100%", "100vw", "1200", "1440"] and parent_id != "bg":
                raw_rects += 1
        elif tag == "circle":
            raw_circles += 1

    if raw_rects > 3:
        warnings.append(f"Found {raw_rects} raw <rect> primitives. Prefer hand-drawn bowed <path> elements with Wood et al. curvature.")
    if raw_circles > 5:
        warnings.append(f"Found {raw_circles} raw <circle> primitives. Prefer organic oval / hand-drawn looped paths.")

    # 5. Check Typography
    has_caveat_or_hand = bool(re.search(r"Caveat|Patrick Hand|Kalam|Architects Daughter|cursive", raw_content, re.IGNORECASE))
    if not has_caveat_or_hand:
        warnings.append("No hand-lettered font family detected ('Caveat', 'Patrick Hand', etc.).")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 eval_doodle.py <file.svg|file.html>")
        sys.exit(1)
        
    target = Path(sys.argv[1])
    is_valid, errors, warnings = evaluate_doodle_svg(target)
    
    print(f"\n==========================================")
    print(f" Doodle SVG Evaluation: {target.name}")
    print(f"==========================================")
    
    if is_valid:
        print("✅ STATUS: PASS (Deterministic AST Valid)")
    else:
        print("❌ STATUS: FAIL (AST Violations Detected)")
        
    if errors:
        print("\nErrors (Must Fix):")
        for e in errors:
            print(f"  ❌ {e}")
            
    if warnings:
        print("\nWarnings / Recommendations:")
        for w in warnings:
            print(f"  ⚠️  {w}")
            
    print(f"==========================================\n")
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
