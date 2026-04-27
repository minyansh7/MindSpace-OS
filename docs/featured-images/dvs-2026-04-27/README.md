# DVS / Substack featured image — 2026-04-27

Featured image for the v2 launch. Magazine-modernist (Information+) aesthetic. Three findings combined: emotional shape (radar), curiosity as the through-line (stat block), reply dynamics (Sankey).

Headline: **Five shapes. One Curiosity. Reassurance flows.**

## Output sizes

All sizes are sourced from a 3× native HiDPI render (`html { zoom: 3 }`) and downsampled with PIL LANCZOS for crisp text at every scale. No bitmap upscaling.

| File | Dimensions | Use |
|---|---|---|
| **`featured-image-3x-square.png`** | **3600 × 3600** | **Print / archival source — 12in @ 300 DPI** |
| **`featured-image-3x-landscape.png`** | **4368 × 2448** | **Print / archival source landscape — 14.6in × 8.16in @ 300 DPI** |
| `featured-image-2x.png` | 2400 × 2400 | DVS / Nightingale submission |
| `featured-image-landscape-2x.png` | 2912 × 1632 | High-res Substack hero / oversized landscape |
| `featured-image-square.png` | 1200 × 1200 | square base (web) |
| `featured-image-landscape.png` | 1456 × 816 | Substack hero (default) |
| `featured-image-ig.png` | 1080 × 1080 | Instagram |

## Source HTML

- `source-square.html` — 1200 × 1200 base layout. Edit this and re-render the others.
- `source-landscape.html` — 1456 × 816 layout (true landscape redesign, not just a scale of square).
- `source-square-hq.html` — same as `source-square.html` plus `html { zoom: 3 }` injected. Render at 3600 × 3600 viewport for native HiDPI.
- `source-landscape-hq.html` — landscape + `zoom: 3`. Render at 4368 × 2448 viewport.
- `source-retina.html` — legacy iframe-scale-2 wrapper. Soft text. **Do not use for new renders.**

## Source data figures

- `source-dynamics.png` — Sankey of poster archetype → commenter archetype.
- `source-radar-v2.png` — emotion radar across 5 archetypes with WARM CLUSTER / FEAR SPIKE / DARK BASE callouts.

## Re-rendering

For best quality, render the `*-hq.html` source at the matching viewport, then downsample with LANCZOS (PIL or ImageMagick) for smaller targets. The Google Fonts CDN (Inter Tight, Inter, DM Mono) is the only external dependency.

```bash
# Example with browse + Python PIL
browse viewport 3600x3600
browse goto file://path/source-square-hq.html
browse screenshot --viewport featured-image-3x-square.png
python3 -c "from PIL import Image; img = Image.open('featured-image-3x-square.png'); \
  for w in [2400, 1200, 1080]: img.resize((w,w), Image.Resampling.LANCZOS).save(f'featured-image-{w}.png')"
```

## Voice / data lineage

- Anchor numbers come from `precomputed/emotion_clusters.parquet` (n=2,899).
- Curiosity stats: rank #3 of 28, mean intensity 0.63, 82% of posts ≥ 0.50, 2.15× joy.
- Reply dynamics: 1 in 4 grief replies mirror, 7 of 100 anxiety replies mirror.
- Reference: Reddit · Jan 2024 – Jun 2025 · Google Research's GoEmotions (Demszky et al. 2020) · UMAP + GMM.
