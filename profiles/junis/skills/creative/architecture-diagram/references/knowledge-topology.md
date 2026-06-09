# Knowledge Topology Diagrams (知识拓扑图)

Adapting the dark-tech architecture-diagram aesthetic for knowledge/philosophical frameworks.

## When to Use

- User asks for a "拓扑图" (topology map) of their knowledge system
- Need to visualize layered knowledge architecture (e.g., 道·法·术 framework)
- Showing how multiple knowledge modules connect and feed into each other

## Semantic Color Mapping

Instead of tech-infra colors (Frontend/Backend/Database), remap for knowledge layers:

| Knowledge Layer | Fill | Stroke | Hex Stroke |
|:---------------|:----:|:------:|:----------:|
| **道 (Foundation)** | rgba(167,139,250,0.15) | Deep Violet | #a78bfa |
| **法 (Method/OS)** | rgba(34,211,238,0.15) | Cyan | #22d3ee |
| **术 (Practice/Tools)** | rgba(52,211,153,0.10) | Emerald | #34d399 |
| **桥 (Integration)** | rgba(251,191,36,0.12) | Amber | #fbbf24 |
| **输入 (Input/Feed)** | rgba(251,113,133,0.08) | Rose | #fb7185 |
| **Core Pillars** | rgba(250,204,21,0.08) | Gold | #facc15 |
| **External/Users** | rgba(148,163,184,0.10) | Slate | #94a3b8 |

## Layout Pattern (5-Layer Stack)

```
viewBox="0 0 1200 1000"

Layer 0 (y:90-250):    道 — Single large entity (e.g. 王阳明心学)
  ├── Four sub-pillars as individual boxes
  └── Connection arrows from main entity to each pillar

Layer 1 (y:280-490):   法 — Hub-and-spoke (e.g. 太极双螺旋)
  ├── Central OS hub (left:right symmetry)
  ├── Left spiral, right spiral
  └── Central switches/controls below

Layer 2 (y:510-710):   术 — Three equal columns (modules)
  ├── Module 1 (left): Category with sub-items
  ├── Module 2 (center): Category with sub-items
  └── Module 3 (right): Category with sub-items

Layer 3 (y:730-860):   桥 — Wide integration layer
  ├── Central decision bridge
  ├── Left: case library
  └── Right: control dashboard

Layer 4 (y:910-975):   输入 — Pipeline flow (horizontal)
  └── Stages shown with right-arrow → chain
```

## Layer Boundary

Each layer gets a dashed rect boundary with its semantic color and low opacity:

```svg
<rect x="100" y="90" width="1070" height="160" rx="16"
      fill="rgba(167,139,250,0.03)" stroke="#a78bfa"
      stroke-width="0.8" stroke-dasharray="8,4" opacity="0.5"/>
```

## Side Labels

Each layer gets a left-side label (Layer number + Chinese name):

```svg
<text x="30" y="170" fill="#a78bfa" font-size="13" font-weight="700">LAYER 0</text>
<text x="30" y="188" fill="#a78bfa" font-size="20" font-weight="900">道</text>
<text x="30" y="206" fill="#6b7280" font-size="9">哲学根基</text>
```

## Vertical Connectors

Use dashed lines with arrow markers for cross-layer connections:

```svg
<path d="M 320 230 L 320 260 Q 320 270 330 270 L 550 270 L 560 270 Q 570 270 570 280 L 570 296"
      fill="none" stroke="#a78bfa" stroke-width="1.5"
      marker-end="url(#arr-violet)" stroke-dasharray="4,3" opacity="0.7"/>
```

## Info Cards (4 cards)

Below the SVG diagram, place 4 cards matching the 4 content layers (道·法·术·桥):

```html
<div class="card">
  <div class="card-header">
    <div class="card-dot violet"></div>
    <h3>⛩️ 道层 · 哲学根基</h3>
  </div>
  <ul>
    <li>• 王阳明心学 v3.0（452行·28KB·21条原文引用）</li>
    <li>• 四柱：心即理 → 知行合一 → 致良知 → 事上磨练</li>
  </ul>
</div>
```

## Font Choice

- Headings: JetBrains Mono (monospace) — for layer labels and tech feel
- Body: Noto Sans SC (sans-serif) — for Chinese text readability
- Mix by specifying CSS `font-family: 'Noto Sans SC', 'JetBrains Mono', monospace;`

## Reference Case

`决断之桥拓扑图.html` — Complete 5-layer knowledge topology with:
- 15+ component nodes
- 6 cross-layer connection arrows
- 4 summary info cards
- Semantic 5-color mapping
- Motto banner + paradigm indicator (观→决→断)
