# The Physics of Human Inking

Why LLMs generate "vector slop" when asked to draw a diagram: **autoregressive 1D sequence models have no innate kinematics of human motor control**.

A human holding a fine-liner or fountain pen does not emit Euclidean geometric primitives. The hand is an articulated mechanical system (fingers, wrist pivot, forearm radius) operating with friction against textured paper.

---

## 1. Wood et al. Chord-Normal Bowing (2012)

Based on visualization research by Wood, Isenberg, et al. (2012) on sketch-based styling, human lines bow perpendicular to the direction of motion due to wrist rotation.

For a line segment connecting endpoints $P_1(x_1, y_1)$ and $P_2(x_2, y_2)$ with Euclidean span $L = \sqrt{\Delta x^2 + \Delta y^2}$:

### Step A: Compute Unit Tangent and Normal
$$\mathbf{u} = \left(\frac{\Delta x}{L}, \frac{\Delta y}{L}\right)$$
$$\mathbf{n} = \left(-\mathbf{u}_y, \mathbf{u}_x\right) = \left(-\frac{\Delta y}{L}, \frac{\Delta x}{L}\right)$$

### Step B: Compute Bowing Displacement
The peak midpoint deflection $d_{\text{bow}}$ scales with segment length:
$$d_{\text{bow}} = \kappa \cdot \left(\frac{L}{200}\right) \cdot \mathcal{N}(0, 1)$$
where $\kappa \approx 3\text{--}6\text{px}$ is the bowing coefficient.

### Step C: Generate SVG Quadratic / Cubic Curve
Instead of `<line x1="x1" y1="y1" x2="x2" y2="y2" />`, emit a curved `<path>`:
- **Quadratic approximation:** Control point $CP = M + d_{\text{bow}}\cdot\mathbf{n}$ (where $M = (P_1 + P_2)/2$).
  ```xml
  <path d="M x1 y1 Q cpx cpy x2 y2" fill="none" stroke="#001858" stroke-width="3" stroke-linecap="round" />
  ```
- **Cubic Bézier for long spans:**
  $$CP_1 = P_1 + \frac{1}{3}(P_2 - P_1) + d_{\text{bow}}\cdot\mathbf{n} + \mathbf{J}_1$$
  $$CP_2 = P_1 + \frac{2}{3}(P_2 - P_1) + d_{\text{bow}}\cdot\mathbf{n} + \mathbf{J}_2$$
  where $\mathbf{J}_1, \mathbf{J}_2 \sim \text{Uniform}(-1.5, 1.5)\text{px}$ is stochastic finger jitter.

---

## 2. Endpoint Overshoot & Vertex Jitter

In freehand sketching, strokes almost never terminate exactly at corners:
- **Corner Overshoot:** A horizontal top bar starts $2\text{--}3\text{px}$ to the left of the left wall and extends $2\text{--}3\text{px}$ past the right wall.
- **Double-Corner T-Junctions:** The intersecting vertical line begins $1\text{--}2\text{px}$ above the top bar.

### Box Path Transformation Recipe

To draw a rectangle $(x, y, w, h)$:
```xml
<!-- DO NOT USE: <rect x="100" y="100" width="200" height="120" /> -->

<!-- USE HAND-DRAWN CLOSED PATH: -->
<path d="M 98 102 
         Q 200 97 304 101 
         Q 306 160 302 223 
         Q 198 226 96 221 
         Q 94 160 98 102 Z" 
      fill="#ffffff" stroke="#001858" stroke-width="3.5" 
      stroke-linecap="round" stroke-linejoin="round" />
```

---

## 3. Dual-Pass Retracing

In authentic sketches, focal elements feature a primary ink pass plus a secondary, lighter, offset hair-line pass:

```xml
<!-- Main bold contour -->
<path d="M 100 100 Q 200 96 300 100 Q 302 160 300 220 Q 200 224 100 220 Z" 
      fill="#ffffff" stroke="#001858" stroke-width="3.5" stroke-linecap="round" />

<!-- Retrace sketchy pass (slightly offset, thinner) -->
<path d="M 98 102 Q 200 98 303 99 Q 299 158 301 222 Q 202 221 97 218 Z" 
      fill="none" stroke="#001858" stroke-width="1.2" opacity="0.45" stroke-linecap="round" />
```

---

## 4. Offset Watercolor Washes

Color in sketchnotes behaves like watercolor wash or chisel-tip markers:
- Washes **do not align perfectly** with stroke boundaries.
- They are offset by $4\text{--}8\text{px}$ (giving the authentic human "imperfect fill" feel).
- They have semi-transparency (`opacity="0.30"` to `0.55"`).
- They are placed in `<g id="phase-2-washes">` to ensure ink lines are crisp on top.
