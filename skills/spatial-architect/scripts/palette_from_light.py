"""Palette by physics, not by feel (lessons.md #4).

ALBEDO IS A SPECTRUM, NOT A SCALAR. The first version of this script used one
reflectance number per material. That works only when the illuminant carries all
the colour - under a 2100K oven it produced a convincing amber scene, which was
luck. Point it at a neutral 5600K sun and every material collapses to grey:
"cobalt blue" came out #464648. Reflectance is per-channel; cobalt means high
reflectance in blue and almost none in red. Model it that way or the formula
only works in firelight.

Every surface colour = illuminant spectrum x material albedo. Two illuminants
(the oven mouth, and a dim cold ambient), so every material gets a lit value and
a shadow value and the two CANNOT drift toward the same look, because the
Kelvin numbers are different.
"""
import math

def kelvin_rgb(K):
    """Tanner Helland's blackbody approximation, 1000-40000K."""
    t = K / 100.0
    if t <= 66:
        r = 255
        g = 99.4708025861 * math.log(t) - 161.1195681661
        b = 0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307
    else:
        r = 329.698727446 * (t - 60) ** -0.1332047592
        g = 288.1221695283 * (t - 60) ** -0.0755148492
        b = 255
    return tuple(max(0.0, min(255.0, v)) / 255.0 for v in (r, g, b))

def adapt(c, white, exposure=1.0):
    """von Kries chromatic adaptation to the KEY illuminant.

    The eye (and a camera) normalises to the dominant light, so a scene lit by a
    2100K oven does not read as uniformly orange - the key reads NEUTRAL and
    everything lit by the cooler ambient reads BLUE by comparison. This is the
    physical cause of the rule of thumb "warm light, cool shadows"; deriving it
    instead of asserting it is what stops every scene converging on one hue ramp
    (lessons.md #4). Skipping this step produced a 14-swatch monochrome and an
    ink of #040302, which the no-pure-black law forbids.
    """
    w = tuple(white[i] ** D for i in range(3))   # partial, not complete
    return tuple(min(1.0, (c[i] / max(w[i], 1e-6)) * exposure) for i in range(3))

def hexof(c):
    return "#" + "".join("%02X" % round(ch * 255) for ch in c)

KEY  = kelvin_rgb(4300)   # 16:40 sun, low and west, raking through the arch
AMB  = kelvin_rgb(9500)   # open sky + sea bounce: the shadow illuminant
D    = 0.50               # eye adapts hard to full sun; shadows go frankly blue
print("key 5600K", hexof(KEY), " sky-ambient 11000K", hexof(AMB))

# material, albedo, how much key it receives (0-1), how much ambient
# material: (per-channel reflectance), key factor, ambient factor
MATERIALS = [
    ("sky",           (1.00, 1.00, 1.00), 0.00, 2.30),
    ("sea-far",       (0.10, 0.30, 0.44), 0.00, 1.55),
    ("sea-deep",      (0.05, 0.18, 0.34), 0.00, 1.30),
    ("plaster-sun",   (0.90, 0.89, 0.85), 1.05, 0.35),
    ("plaster-half",  (0.90, 0.89, 0.85), 0.45, 0.45),
    ("plaster-shade", (0.90, 0.89, 0.85), 0.03, 0.70),
    ("stone-sun",     (0.60, 0.56, 0.48), 1.00, 0.30),
    ("stone-shade",   (0.60, 0.56, 0.48), 0.03, 0.62),
    ("cobalt-sun",    (0.07, 0.20, 0.62), 1.05, 0.35),
    ("cobalt-shade",  (0.07, 0.20, 0.62), 0.04, 0.70),
    ("wood-sun",      (0.46, 0.34, 0.20), 0.95, 0.28),
    ("wood-shade",    (0.46, 0.34, 0.20), 0.03, 0.55),
    ("brass",         (0.66, 0.50, 0.18), 1.15, 0.25),
    ("terracotta",    (0.52, 0.24, 0.14), 0.95, 0.30),
    ("olive",         (0.20, 0.26, 0.13), 0.85, 0.35),
    ("bougainvillea", (0.66, 0.10, 0.32), 1.00, 0.35),
    ("ink",           (0.06, 0.06, 0.07), 0.05, 0.40),
]
out = []
for name, alb, kf, af in MATERIALS:
    raw = tuple(alb[i] * (KEY[i] * kf + AMB[i] * af) for i in range(3))
    c = adapt(raw, KEY, exposure=0.86)
    c = tuple(0.055 + 0.945 * ch for ch in c)      # ambient floor: nothing is black
    out.append((name, hexof(c)))
    print(f"{name:16s} R{alb[0]:.2f}/{alb[1]:.2f}/{alb[2]:.2f}  key x{kf:.2f}  amb x{af:.2f}   {hexof(c)}")
print("\nPALETTE:", " ".join(h for _, h in out))
