# Architectural Math & Metric Conversion Matrices

## 1. Master Canvas Multipliers

| Viewport Aspect Ratio | Canvas Dimensions | Floor Datum ($y_{\text{datum}}$) | Wall Height | Metric Scale Multiplier ($k$) |
|---|---|---|---|---|
| **16:10 Laptop (Default)** | **`1440 × 900`** | **`y = 720 px`** (80%) | **`720 px`** | **`288 px = 1.00 m`** |
| **16:9 Desktop Full HD** | **`1920 × 1080`** | **`y = 864 px`** (80%) | **`864 px`** | **`345.6 px = 1.00 m`** (or `384 px/m`) |
| **4:3 Classic / Tablet** | **`1024 × 768`** | **`y = 614 px`** (80%) | **`614 px`** | **`245.76 px = 1.00 m`** |

---

## 2. Standard Metric Reference Table (`288px = 1.00m` on `1440 × 900`)

Master Formula:
$$y_{\text{top}} = 720 - (\text{Real Metric Height in Metres} \times 288)$$

| Architectural Object | Metric Standard (ISO/DIN/BIFMA) | Calculated Canvas Offset | Exact Canvas $y_{\text{top}}$ |
|---|---|---|---|
| **Room Ceiling Datum** | $2.50\text{ m}$ ($8.2\text{ ft}$) | $720\text{ px}$ | **`y = 0 px`** |
| **Overhead Cable Tray / Track Lighting** | $2.25\text{ m}$ | $648\text{ px}$ | **`y = 72 px`** |
| **Wall Clock / High Artwork Center** | $2.00\text{ m}$ | $576\text{ px}$ | **`y = 144 px`** |
| **Studio Door Frame Top** | $1.96\text{ m}$ | $564\text{ px}$ | **`y = 156 px`** |
| **42U Standard Server Rack Top** | $2.00\text{ m}$ | $576\text{ px}$ | **`y = 144 px`** |
| **Human Eye Line / Wall Thermostat** | $1.50\text{ m}$ ($5.0\text{ ft}$) | $432\text{ px}$ | **`y = 288 px`** |
| **Window Top Header** | $2.20\text{ m}$ | $633\text{ px}$ | **`y = 87 px`** |
| **Window Bottom Sill** | $0.97\text{ m}$ | $280\text{ px}$ | **`y = 440 px`** |
| **Standing Bar / Workshop Bench Surface** | $0.90\text{ m}$ ($90\text{ cm}$) | $259\text{ px}$ | **`y = 461 px`** |
| **Standard Work Desk Surface** | $0.75\text{ m}$ ($75\text{ cm}$) | $216\text{ px}$ ($\frac{3}{4} \times 288$) | **`y = 504 px`** |
| **Drafting Stool Seat** | $0.65\text{ m}$ ($65\text{ cm}$) | $187\text{ px}$ | **`y = 533 px`** |
| **Office Task Chair Seat** | $0.45\text{ m}$ ($45\text{ cm}$) | $130\text{ px}$ | **`y = 590 px`** |
| **Lounge / Sofa Seat** | $0.40\text{ m}$ ($40\text{ cm}$) | $115\text{ px}$ | **`y = 605 px`** |
| **Floor Baseboard Trim Top** | $0.045\text{ m}$ ($4.5\text{ cm}$) | $13\text{ px}$ | **`y = 707 px`** |
| **Floor Datum Baseline** | **`0.00 m`** | **`0 px`** | **`y = 720 px`** |
| **Foreground Floor Perspective Boundary** | $-0.625\text{ m}$ | $-180\text{ px}$ | **`y = 900 px`** |

---

## 3. Why 288 Prevents Sub-Pixel Blur

The integer $288$ is a highly composite number ($2^5 \times 3^2$) with **16 clean integer divisors**:
$$1, 2, 3, 4, 6, 8, 9, 12, 16, 18, 24, 32, 36, 48, 72, 96, 144, 288$$

| Metric Fraction | Real-World Dimension | Exact Pixel Value ($288\text{px/m}$) |
|---|---|---|
| $1\text{ m}$ | $100\text{ cm}$ | $288\text{ px}$ |
| $\frac{1}{2}\text{ m}$ | $50\text{ cm}$ | $144\text{ px}$ |
| $\frac{1}{3}\text{ m}$ | $33.3\text{ cm}$ | $96\text{ px}$ |
| $\frac{1}{4}\text{ m}$ | $25\text{ cm}$ | $72\text{ px}$ |
| $\frac{1}{6}\text{ m}$ | $16.6\text{ cm}$ | $48\text{ px}$ |
| $\frac{1}{8}\text{ m}$ | $12.5\text{ cm}$ | $36\text{ px}$ |
| $\frac{1}{12}\text{ m}$ | $8.33\text{ cm}$ | $24\text{ px}$ |
| $\frac{1}{16}\text{ m}$ | $6.25\text{ cm}$ | $18\text{ px}$ |

Because metric subdivisions evaluate to exact integers, strokes and fills rasterize with crisp single-pixel boundaries across $1\times$ standard and $2\times$ Retina displays without blurry fractional antialiasing.
