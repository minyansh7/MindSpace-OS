# DVS / Substack featured image — 2026-04-27

Featured image for the v2 launch. Magazine-modernist (Information+) aesthetic. Three findings combined: emotional shape (radar), curiosity as the through-line (stat block), reply dynamics (Sankey).

Headline: **Five shapes. One Curiosity. Reassurance flows.**

## Output sizes

| File | Dimensions | Use |
|---|---|---|
| `featured-image-landscape.png` | 1456 × 816 | Substack hero |
| `featured-image-2x.png` | 2400 × 2400 | DVS / Nightingale / archival |
| `featured-image-square.png` | 1200 × 1200 | square base |
| `featured-image-ig.png` | 1080 × 1080 | Instagram |

## Source HTML

- `source-square.html` — 1200×1200 base. Edit this and re-render the others.
- `source-landscape.html` — 1456×816 redesign for landscape aspect.
- `source-retina.html` — 2× wrapper that scales the square layout to 2400×2400 via `transform: scale(2)`.

## Source data figures

- `source-dynamics.png` — Sankey of poster archetype → commenter archetype.
- `source-radar-v2.png` — emotion radar across 5 archetypes with WARM CLUSTER / FEAR SPIKE / DARK BASE callouts.

## Re-rendering

Open the HTML in a 1200×1200 browser viewport and screenshot. The HTML is self-contained (Google Fonts CDN: Inter Tight, Inter, DM Mono).

## Voice / data lineage

- Anchor numbers come from `precomputed/emotion_clusters.parquet` (n=2,899).
- Curiosity stats: rank #3 of 28, mean intensity 0.63, 82% of posts ≥ 0.50, 2.15× joy.
- Reply dynamics: 1 in 4 grief replies mirror, 7 of 100 anxiety replies mirror.
- Reference: Reddit · Jan 2024 – Jun 2025 · Google Research's GoEmotions (Demszky et al. 2020) · UMAP + GMM.
