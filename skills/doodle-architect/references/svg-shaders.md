# Zero-JS SVG Shaders & Filter Graphs

Rather than relying on heavy client-side JavaScript canvas engines (like Rough.js or Paper.js), all tactile paper textures, pencil jitter, and watercolor bleeds can be executed **natively on the browser GPU via declarative SVG filters**.

---

## 1. Cotton-Rag Paper Texture

Simulates textured archival paper with subtle diffuse surface lighting:

```xml
<filter id="paper-texture" x="0%" y="0%" width="100%" height="100%">
  <!-- Generate multi-octave Perlin fractal noise -->
  <feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="4" result="noise" />
  
  <!-- Diffuse lighting calculates realistic surface normals -->
  <feDiffuseLighting in="noise" lighting-color="#fef6e4" surfaceScale="2" diffuseConstant="1.1" result="light">
    <feDistantLight azimuth="55" elevation="45" />
  </feDiffuseLighting>
  
  <!-- Multiply light texture onto the base element -->
  <feBlend mode="multiply" in="SourceGraphic" in2="light" />
</filter>
```

**Usage:**
```xml
<rect width="100%" height="100%" fill="#fef6e4" filter="url(#paper-texture)" />
```

---

## 2. Hand-Drawn Stroke Jitter (`feDisplacementMap`)

Displaces vector paths along high-frequency noise coordinates to produce subtle ink bleed and pen friction:

```xml
<filter id="sketch-stroke" x="-20%" y="-20%" width="140%" height="140%">
  <feTurbulence type="fractalNoise" baseFrequency="0.06 0.04" numOctaves="3" seed="42" result="noise" />
  <feDisplacementMap in="SourceGraphic" in2="noise" scale="3.0" xChannelSelector="R" yChannelSelector="G" />
</filter>
```

**Usage:**
```xml
<g id="phase-4-strokes" filter="url(#sketch-stroke)">
  <!-- Clean Bézier curves will be rendered with authentic pen friction -->
</g>
```

---

## 3. Watercolor Wash Bleed

Creates soft, bleeding edges typical of wet watercolor pigments or broad-nib chisel markers:

```xml
<filter id="watercolor-wash" x="-20%" y="-20%" width="140%" height="140%">
  <!-- Low frequency organic warping -->
  <feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="3" seed="17" result="warp" />
  <feDisplacementMap in="SourceGraphic" in2="warp" scale="8.0" result="warped" />
  <feGaussianBlur in="warped" stdDeviation="1.2" />
</filter>
```

**Usage:**
```xml
<g id="phase-2-washes" filter="url(#watercolor-wash)">
  <path d="..." fill="#8bd3dd" opacity="0.35" />
  <path d="..." fill="#f582ae" opacity="0.40" />
</g>
```

---

## 4. Drop Shadow / Marker Stikers

For sticky notes and highlighted card components:

```xml
<filter id="sticker-shadow" x="-10%" y="-10%" width="125%" height="125%">
  <feDropShadow dx="2" dy="4" stdDeviation="3" flood-color="#001858" flood-opacity="0.12" />
</filter>
```
