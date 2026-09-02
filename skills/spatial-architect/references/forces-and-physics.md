# Physical Forces & Invariants for Vector Graphics

To generate believable, physically coherent vector scenes, an agent must enforce four physical force fields across all SVG elements.

---

## 1. Force Field: Gravity & Structural Mechanics ($\vec{g} = [0, 9.8]$)

### A. The Support Plane Rule
Every solid entity must declare its base coordinate equal to the supporting plane beneath it:
* Ground-standing items: $y_{\text{base}} = y_{\text{datum}}$
* Tabletop items: $y_{\text{base}} = y_{\text{table\_surface}}$

### B. Catenary Wire & Cable Physics
Wires, strings, and power cables hanging between point $A(x_1, y_1)$ and point $B(x_2, y_2)$ do not form straight diagonal lines. They sag under gravity into hyperbolic cosines ($y = a \cosh(x/a)$).

In SVG, approximate this via a quadratic Bézier curve:
$$\text{SVG Path: } \text{M } x_1\ y_1\ \text{Q } x_c\ y_c\ x_2\ y_2$$

Where the control point is derived as:
$$x_c = \frac{x_1 + x_2}{2}, \quad y_c = \max(y_1, y_2) + \kappa \cdot |x_2 - x_1|$$
*(Where $\kappa \approx 0.12 \text{ to } 0.18$ represents cable tension and weight).*

```xml
<!-- Example: Ethernet Cable hanging between server chassis (500, 520) and desk (700, 504) -->
<path d="M 500 520 Q 600 560 700 504" fill="none" stroke="#2A241A" stroke-width="2.5" stroke-linecap="round"/>
```

---

## 2. Force Field: Optics & Multi-Light Hierarchy ($\vec{L}$)

### A. Primary Directional Light (Sunlight / Moonlight)
Declare the primary illumination angle $\theta$ (e.g., $34^\circ$ azimuth):
* **Shadow Length Formula:**
  $$\text{Shadow Length } L = \frac{H_{\text{object}}}{\tan \theta}$$
* **Shadow Offset Vector:**
  $$\vec{S} = (\Delta x, \Delta y) = \left(L \cdot \cos \phi,\ L \cdot \sin \phi\right)$$

All cast shadows on the floor plane must share the exact same projection angle.

### B. Secondary Localized Light (Indoor Task Lamps / Pendants)
Indoor artificial point lights cast radial illumination with inverse-square falloff:
```xml
<radialGradient id="taskLampGlow" cx="50%" cy="0%" r="90%">
  <stop offset="0%" stop-color="#FCE8C6" stop-opacity="0.65"/>
  <stop offset="60%" stop-color="#F8F1E4" stop-opacity="0.2"/>
  <stop offset="100%" stop-color="#F8F1E4" stop-opacity="0"/>
</radialGradient>
```

### C. Color Temperature Hierarchy
* **Outdoor Ambient (Sky):** Cool $6500\text{K}$ (slate blue `#BAC7D5`, crisp white `#FDFAF3`).
* **Indoor Task Lighting:** Warm $2700\text{K}$ (tungsten amber `#F4D06F`, terracotta `#E0A458`).
* **Emissive Displays:** Cold phosphor / LED indicators (emerald green `#6FA06B`, amber standby `#E0A458`, alert red `#C05030`).

---

## 3. Force Field: Aerodynamics & Thermal Convection ($\vec{W}$)

When a window is open, a fan is running, or a warm beverage is steaming, elements deform according to the **Global Wind Vector $\vec{W} = (W_x, W_y)$**:

### A. Curtain & Textile Billow
Curtains suspended from a rod at $(x_0, y_0)$ deflect horizontally when subject to wind:
$$\Delta x_{\text{hem}} = H_{\text{curtain}} \cdot \sin \alpha \quad (\text{where } \alpha \propto \|\vec{W}\|)$$

In SVG, draw the billowed curtain using cubic Bézier curves that bow outward along $\vec{W}$:
```xml
<!-- Left curtain blowing rightward into room (Wind W_x = +20) -->
<path d="M 40 100 Q 65 240 90 400 L 70 400 Q 45 240 30 100 Z" fill="#FDFAF3" stroke="#2A241A" stroke-width="2"/>
```

### B. Thermal Steam & Smoke Plumes
Steam rises due to thermal buoyancy ($-\vec{g}$) while shearing horizontally along the wind vector $\vec{W}$:
$$\vec{V}_{\text{plume}} = (W_x, -V_{\text{buoyancy}})$$

```xml
<!-- Animated Steam Plume deflecting with wind -->
<path class="steam" d="M 520 490 Q 528 470 535 450" fill="none" stroke="#6F6656" stroke-width="2" stroke-linecap="round"/>
```

### C. Rotational Kinematics (Ceiling Fans / Desk Fans)
A ceiling fan rotating in 2D space exhibits foreshortening:
* A circular sweep of radius $R$ flattens into an ellipse with semi-minor axis $r_y \approx 0.28 \cdot R$.
* Rotating blades cast intermittent shadow bars across the floor plane beneath the fixture.

---

## 4. Force Field: Fluid Precipitation & Weather Dynamics

### A. Raindrop Velocity Vector
Raindrops falling in open air are the vector sum of gravity and crosswind:
$$\vec{V}_{\text{rain}} = \vec{g} + \vec{W} = (W_x, V_{\text{terminal}})$$

For standard rain ($V_{\text{terminal}} \approx 35\text{px}$, $W_x \approx -10\text{px}$):
```xml
<line class="raindrop" x1="100" y1="120" x2="90" y2="155" stroke="#BFD7EA" stroke-width="1.8" stroke-linecap="round"/>
```
