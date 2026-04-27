# Performance Upgrade Plan — mindspaceos.com

> **Goal:** Champion tier page load — first-time visitors <2s LCP on every route, repeat visitors <500ms. The live site IS the developer demo; if it loads slow, fork-curious devs and editorial readers both bounce.

> **Source review:** `/plan-devex-review` 2026-04-28. Persona: indie dev / data-journalist forking the template (10-min tolerance). Mode: DX EXPANSION.

---

## Baseline (measured 2026-04-28 from residential network, cold cache)

| Asset | Size | Cold-load | TTFB | CF Edge Cache |
|---|---|---|---|---|
| `/` (landing) | 67 KB | 1.24s | 1.16s | **DYNAMIC** ❌ |
| `/explore/emotion-pulse/` | 47 KB | 0.75s | 0.70s | DYNAMIC ❌ |
| `/charts/emotion-pulse.html` | **1,711 KB** | **2.19s** + 308 redirect | — | DYNAMIC ❌ |
| `/charts/community-dynamics.html` | 25 KB | 1.09s + redirect | — | DYNAMIC ❌ |
| `/charts/inner-life-currents.html` | **567 KB** | **1.60s** + redirect | — | DYNAMIC ❌ |
| `/charts/community-weather-report.html` | 67 KB | 1.06s + redirect | — | DYNAMIC ❌ |

Repeat visitor: every asset re-downloaded because landing has `cache-control: max-age=0, must-revalidate` (no `_headers` rule for HTML routes). Net: same as first visit for HTML, fonts/JS hit immutable cache only.

## Target (post-implementation)

| Metric | First visit | Repeat visit |
|---|---|---|
| Landing LCP | <1.5s | <300ms |
| Chart page LCP | <2.0s | <500ms |
| Mobile 4G LCP (chart pages) | <3s | <800ms |
| TTFB (any route) | <100ms (CF edge HIT) | <50ms |
| 308 redirects on chart fetch | 0 | 0 |
| Lighthouse perf | ≥95 desktop, ≥90 mobile | (same) |

---

## Five Smoking Guns (root causes, ranked by impact)

### G1. CRITICAL — Cloudflare Pages bypassing edge cache on every asset

**Evidence:** `cf-cache-status: DYNAMIC` returns on `/`, `/charts/*`, `/explore/*`. Despite `_headers` setting `s-maxage=86400` for `/charts/*`, edge cache is not honoring it.

**Root cause hypothesis:**
- HTML routes: no `_headers` rule → CF Pages applies its no-cache default for HTML
- Chart routes: extension-stripping 308 redirect breaks cache key (CF caches the 308, not the 200)
- Possibly missing `CDN-Cache-Control` separately from `Cache-Control` (CF Pages prefers the former for edge directives in some configurations)

**Fix:** Add HTML-route rules + `CDN-Cache-Control` separate from browser `Cache-Control`. After ship, verify `curl -I` shows `cf-cache-status: HIT` (after first warm-up request).

**Estimated impact:** TTFB 1.16s → <100ms on every cached route. Repeat visit becomes near-instant.

### G2. CRITICAL — emotion-pulse.html is 1.7MB single-payload

**Evidence:** All 2,899 records' `hover_text` strings + UMAP coordinates + radar `customdata` baked into one HTML by `scripts/build_chart_figures.py`. Network tab shows 1,711,202 bytes for one chart.

**Root cause:** Build script writes a self-contained HTML with all data inlined, then iframes it. No streaming, no shell-then-data split, no progressive reveal.

**Fix:** Split into `emotion-pulse-shell.html` (~30KB: layout + Plotly + empty trace) and `emotion-pulse-data.json` (~700KB compressed). Shell renders skeleton instantly; data fetches in parallel and hydrates the trace.

**Estimated impact:** First-paint on chart from ~2s to ~400ms. Mobile 4G from ~10s to ~2s.

### G3. HIGH — 308 redirects on every chart fetch

**Evidence:** `/charts/emotion-pulse.html` → 308 → `/charts/emotion-pulse`. Adds 600ms per chart load on cold cache (extra round-trip + DNS + TLS reuse). Iframe `src` in `StaticChart.astro` writes `.html` URL, CF strips it.

**Fix:** Two options:
- (Preferred) Update `StaticChart.astro` to write the extension-stripped URL directly, eliminating the redirect entirely.
- Add `_redirects` rules that 200-rewrite (not 308-redirect) the `.html` form internally.

**Estimated impact:** -600ms per chart page. Combined with G2 makes chart pages feel native.

### G4. HIGH — 9 fonts loaded eagerly, ~225KB before paint

**Evidence:** `Base.astro:3-12` imports Inter 400/500/600/700, Source Serif 400/400i/600, JetBrains Mono 400/500. All eagerly loaded across every page.

**Above-the-fold audit:**
- Landing hero: Inter 700 (H1), Source Serif 400 italic (pull-quote at scroll). Inter 500 in nav. **3 fonts above fold.**
- Chart pages: Inter 700 (H1), Inter 500/600 (intros), JetBrains 400 (eyebrow). **4 fonts above fold.**
- Source Serif 600, Source Serif italic, JetBrains 500 are below-fold or used only on About page.

**Fix:** Critical-CSS the above-fold fonts via `@font-face` with `font-display: swap` and `<link rel="preload" as="font" crossorigin>` for Inter 700 + Inter 500 only. Other faces use lazy `@font-face` (browser fetches when first character renders).

**Estimated impact:** First paint moves up ~150-200ms on slow networks. Removes ~150KB from critical path.

### G5. HIGH — Plotly.js loaded from CDN with no preconnect

**Evidence:** Static chart HTMLs load `https://cdn.plot.ly/plotly-2.35.2.min.js`. Adds DNS lookup + TLS handshake per first-visit chart (~200-400ms before JS even starts downloading).

**Fix:**
- Self-host: copy `plotly.js-dist-min` (~970KB) to `site/public/vendor/plotly-2.35.2.min.js`. Same domain, served by CF edge cache, immutable max-age=31536000.
- Or keep CDN but add `<link rel="preconnect" href="https://cdn.plot.ly" crossorigin>` in `Base.astro` head — eliminates the DNS/TLS roundtrip on chart-page navigation.

**Estimated impact:** -200-400ms on first chart render. Bundles into shared cache across all 3 Plotly-using charts (after first load, instant).

---

## Plan — 4 phases, shippable independently

### Phase 1 — Cache + redirect fixes (~1 hour CC time)

The cheapest wins. Pure config, no app code changes. Recovers ~70% of repeat-visitor pain.

**Diff scope:**
1. **`site/public/_headers`** — add HTML-route rules:
   ```
   /
     Cache-Control: public, max-age=300, s-maxage=86400, stale-while-revalidate=604800
     CDN-Cache-Control: public, max-age=86400

   /explore/*
     Cache-Control: public, max-age=300, s-maxage=86400, stale-while-revalidate=604800
     CDN-Cache-Control: public, max-age=86400

   /about
     Cache-Control: public, max-age=300, s-maxage=86400, stale-while-revalidate=604800
     CDN-Cache-Control: public, max-age=86400

   /charts/*
     Cache-Control: public, max-age=3600, s-maxage=86400, stale-while-revalidate=604800
     CDN-Cache-Control: public, max-age=2592000

   /_astro/*
     Cache-Control: public, max-age=31536000, immutable
     CDN-Cache-Control: public, max-age=31536000, immutable
   ```

2. **`site/src/components/StaticChart.astro`** — change iframe `src` from `/charts/${slug}.html` to `/charts/${slug}` (extension-stripped to match CF Pages output). Eliminates the 308.

3. **`site/public/_redirects`** — new file, only if step 2 missed any references:
   ```
   /charts/:slug.html /charts/:slug 200
   ```
   (`200` makes it a rewrite, not a 308 redirect, preserving the cache key.)

4. **Cloudflare dashboard config** — verify Pages project has "Cache Rules" not just "Cache Reserve." Some accounts need a Cache Rule explicitly to honor `s-maxage` on Pages. If `cf-cache-status` still shows DYNAMIC after step 1, add a Cache Rule: `Hostname eq mindspaceos.com → Cache eligibility: Eligible for cache → Edge TTL: respect origin headers`.

**Test plan:** After deploy, run:
```bash
curl -sI https://mindspaceos.com/ | grep cf-cache-status
curl -sI https://mindspaceos.com/charts/emotion-pulse | grep cf-cache-status
# First request: DYNAMIC. Second: HIT.
```
Add as `bun test` assertion: `tests/perf-headers.test.mjs` polls the deployed URL post-CI and fails if `cf-cache-status` doesn't reach HIT within 2 retries.

**Expected gain:** Repeat visit landing TTFB 1.16s → <100ms. First-visit TTFB unchanged (CF still has to populate its cache from origin first time), but subsequent visitors from the same region hit the warm edge.

### Phase 2 — Critical-CSS font diet (~1.5 hours CC time)

**Diff scope:**
1. **`site/src/layouts/Base.astro`** — replace the 9 eager fontsource imports with:
   - Inline `@font-face` CSS for Inter 700 + Inter 500 with `font-display: swap` and `unicode-range: U+0000-024F` (Latin only)
   - `<link rel="preload" as="font" type="font/woff2" crossorigin href="/_astro/inter-latin-700-normal.Yt3aPRUw.woff2">` for the H1 font
   - Lazy `@font-face` for Source Serif 400/400i/600, JetBrains 400/500, Inter 400/600 — declared but not preloaded
2. **`site/src/styles/global.css`** — verify no rules force-load below-fold fonts above-fold (e.g., a `body { font-family: 'Source Serif 4' }` rule would defeat the whole optimization)
3. **Drop `.woff` legacy fallback** from imports — `@fontsource` ships both, but every browser supporting Astro dev tools also supports woff2. Saves ~half the font bytes.

**Test plan:** Lighthouse mobile audit. Target: "Avoid an excessive DOM size" + "Reduce unused CSS" stay green. "Largest Contentful Paint element" should still be the H1 (don't FOIT it).

**Expected gain:** First paint -150-200ms on slow networks. Removes ~150KB from critical path.

### Phase 3 — Chart shell-data split (~3 hours CC time, biggest perf win)

**Diff scope:**
1. **`scripts/build_chart_figures.py`** — refactor `build_emotion_pulse_payload` (and the other three) to emit two files:
   - `emotion-pulse-shell.html` (~30KB: layout, Plotly tag, empty trace placeholder, hydration script)
   - `emotion-pulse-data.json` (the 1.7MB payload, gzipped to ~600KB on the wire by CF)

   Hydration script in shell:
   ```js
   fetch('/charts/emotion-pulse-data.json')
     .then(r => r.json())
     .then(payload => {
       Plotly.react('chart', payload.traces, payload.layout, payload.config);
       document.getElementById('skeleton').remove();
     });
   ```

2. **`site/src/components/StaticChart.astro`** — iframe still points at `*-shell.html`. The shell paints skeleton immediately, fetches data in parallel.

3. **`site/public/_headers`** — add aggressive cache for `*-data.json`:
   ```
   /charts/*-data.json
     Cache-Control: public, max-age=86400, s-maxage=2592000, stale-while-revalidate=31536000
     CDN-Cache-Control: public, max-age=2592000, immutable
   ```
   (Data is content-addressed by hash of the parquet inputs; safe to immutable-cache for a long time. Bake script writes a fresh hash on data changes.)

4. **Skeleton state** — shell shows a content-shaped placeholder (axes, legend stub) so the layout doesn't shift when data arrives. CLS stays 0.

**Test plan:** Repeat visitor benchmark — second visit to `/explore/emotion-pulse/` should show `<150ms` to interactive (shell + JSON both cached). First visit `<800ms` to skeleton paint, `<2s` to interactive chart.

**Expected gain:** First-visit chart LCP 2.2s → 0.8s (shell paint) / 1.8s (interactive). Mobile 4G chart 8-10s → 3-4s.

### Phase 4 — Plotly self-hosting + service worker (~2 hours CC time)

**Diff scope:**
1. **Self-host Plotly:**
   - Add `plotly.js-dist-min@2.35.2` to `site/package.json`
   - `scripts/build_chart_figures.py` writes shell HTMLs that `<script src="/_astro/plotly-2.35.2.min.js">` instead of CDN
   - Add Astro build hook that copies `node_modules/plotly.js-dist-min/plotly.min.js` to `site/public/vendor/plotly-2.35.2.min.js` with a hashed filename
2. **Service worker** — minimal stale-while-revalidate worker (~50 lines):
   - Pre-caches `/`, `/explore/*/`, `/about/` shells on install
   - Runtime-caches `/charts/*-shell.html`, `/charts/*-data.json`, `/_astro/*` with stale-while-revalidate
   - Activates on next page load after first visit
   - Versioned by build commit hash (cache busts on deploy)

**Test plan:** Open DevTools → Application → Service Workers, confirm registration. Reload landing page offline (after first visit) — should still render. Lighthouse PWA audit hits 100.

**Expected gain:** Repeat visitor on any route → instant (`<100ms` from SW cache). Charts hydrate from cached JSON. Effectively zero network for the entire site after first visit.

---

## NOT in scope (deferred, with rationale)

- **Mobile chart interactivity changes** — locked decision per `upgrade-plan.md`. Static screenshots + "view on desktop" CTA. Re-eval at +30 days.
- **Edge SSR / dynamic OG cards** — Phase 5 territory. Plan §8 already says Satori-via-Worker stub deferred to v1.1.
- **Migrating off Plotly to Observable Plot or D3** — `upgrade-plan.md` decided NO. Re-eval if a specific chart blocks design.
- **Dropping `cdn.plot.ly` entirely** — handled in Phase 4 self-host. Mentioned for clarity; not a separate item.
- **Image optimization** — current `narrative_web_clean.png` is small (~80KB). OG images are pre-rendered PNGs. No images on hot path.
- **HTTP/3 / QUIC** — Cloudflare handles automatically; no app-level work.

## What already exists (Phase 0, before any code change)

- `site/public/_headers` exists with rules for `/charts/*`, `/_astro/*`, `/fonts/*`, `/og/*`, `/screenshots/*`. We extend it, don't replace it.
- `astro.config.mjs:11` has `inlineStylesheets: 'always'` — CSS is already inlined (good, no extra request).
- 4 chart HTMLs are already static (`site/public/charts/*.html`) — Phase 1 of the prior Streamlit migration solved the runtime cold-start. Now we attack the file size + cache hit rate.
- `.devcontainer/` exists — Codespaces config can be wired in Phase 5 (DX, not perf).
- Tests at `site/tests/build.test.mjs` already pass on 52 assertions; Phase 1's perf-headers test slots in cleanly.

## Sequencing

```
Week 0 (today)      Phase 1: cache + redirects  →  ship → measure → assert HIT
Week 0+1d           Phase 2: font diet          →  ship → Lighthouse mobile ≥90
Week 1              Phase 3: chart split        →  ship → measure first-vis chart LCP
Week 1+2d           Phase 4: SW + Plotly host   →  ship → repeat-vis offline check
```

Total: ~7 hours CC time, ~5 days calendar (overnight CF cache populates between phases).

## Success criteria

- [ ] `cf-cache-status: HIT` on every route after warm-up (Phase 1)
- [ ] No 308 redirects on chart fetches (Phase 1)
- [ ] Lighthouse mobile perf ≥90 on landing + all 4 chart pages (Phase 2)
- [ ] First-visit chart LCP <2s (Phase 3)
- [ ] Repeat-visit any route <500ms TTI (Phase 4)
- [ ] Lighthouse PWA score 100 (Phase 4)
- [ ] `bun run perf:budget` CI gate passes (auto-fails PR if any payload grows >10%)

## DX Implementation Checklist (perf-relevant)

- [ ] Time to first chart paint <2s on first visit
- [ ] Time to repeat any page <500ms
- [ ] CF edge cache HIT verified post-deploy
- [ ] Critical fonts inlined, others lazy
- [ ] Plotly self-hosted (no third-party cold connect)
- [ ] Service worker registered, offline-capable for shells
- [ ] Perf budget enforced in CI (Lighthouse CI or custom assertion)
- [ ] Web Vitals beacon → Plausible / CF Web Analytics for ongoing measurement (Phase 8 of DX scorecard)

## Open decisions

| # | Decision | Default | Re-eval trigger |
|---|---|---|---|
| 1 | Self-host Plotly vs preconnect-only | Self-host (Phase 4) | If `vendor/plotly.min.js` + 4 chart shells exceeds 10MB total deploy |
| 2 | Service worker scope (full SPA vs shells only) | Shells + JSON only | If users complain about stale data; SW would need versioning bump |
| 3 | RUM (Cloudflare Web Analytics vs Plausible vs both) | CF Analytics (free, server-side) | If CF doesn't expose Web Vitals — re-eval Plausible |
| 4 | Above-fold fonts (preload Inter 700 only vs 700+500) | 700+500 | Mobile audit shows nav links FOIT more than 100ms |

## Review log

`/plan-devex-review` 2026-04-28 — DX EXPANSION mode, persona = indie-dev-fork, target = Champion tier (<2s first-visit LCP, <500ms repeat). Initial DX score 5.25/10. Target post-implementation: 9/10 (perf dimensions only).
