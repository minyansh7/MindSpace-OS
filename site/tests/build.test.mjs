// Build-output smoke test. Asserts every expected route exists in dist/
// and that essential meta tags are present.
//
// Run: bun build && bun test tests/build.test.mjs

import { test, expect } from 'bun:test';
import { readFile, stat } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

const DIST = 'dist';

const expectedRoutes = [
  'index.html',
  'about/index.html',
  'explore/emotion-pulse/index.html',
  'explore/community-dynamics/index.html',
  'explore/community-weather-report/index.html',
  'explore/inner-life-currents/index.html',
];

const expectedAssets = [
  'og/default.svg',
  'og/emotion-pulse.svg',
  'og/community-dynamics.svg',
  'og/community-weather-report.svg',
  'og/inner-life-currents.svg',
  'og/about.svg',
  'screenshots/emotion-pulse.svg',
  'screenshots/community-dynamics.svg',
  'screenshots/community-weather-report.svg',
  'screenshots/inner-life-currents.svg',
  'robots.txt',
  'favicon.svg',
  'sitemap-index.xml',
  'charts/emotion-pulse.html',
  'charts/community-dynamics.html',
  'charts/inner-life-currents.html',
  'charts/community-weather-report.html',
];

if (!existsSync(DIST)) {
  throw new Error(`No dist/ — run 'bun run build' before tests`);
}

// Read each rendered HTML and chart HTML once at module load. Tests below
// reference the cached strings; saves ~10 MB of redundant disk reads across
// the suite (chart HTMLs alone are ~3.5 MB combined).
const CHART_SLUGS = ['emotion-pulse', 'community-dynamics', 'inner-life-currents', 'community-weather-report'];
const routeHtml = Object.fromEntries(
  await Promise.all(expectedRoutes.map(async (r) => [r, await readFile(path.join(DIST, r), 'utf8')]))
);
const chartHtml = Object.fromEntries(
  await Promise.all(CHART_SLUGS.map(async (s) => [s, await readFile(path.join(DIST, `charts/${s}.html`), 'utf8')]))
);
const indexHtml = routeHtml['index.html'];
const aboutHtml = routeHtml['about/index.html'];

for (const route of expectedRoutes) {
  test(`route exists: ${route}`, async () => {
    const s = await stat(path.join(DIST, route));
    expect(s.size).toBeGreaterThan(500);
  });
}

for (const asset of expectedAssets) {
  test(`asset exists: ${asset}`, () => {
    expect(existsSync(path.join(DIST, asset))).toBe(true);
  });
}

test('landing has thesis H1', () => {
  expect(indexHtml).toContain('Confusion');
  expect(indexHtml).toContain('Compassion');
});

test('landing has updated thesis copy', () => {
  expect(indexHtml).toContain('struggle closely wrapped around curiosity');
});

test('GoEmotions citation includes Google Research prefix', () => {
  // "GoEmotions" is wrapped in an <a> linking to Google Research's blog. Match
  // tolerantly: "Google Research's" must precede "GoEmotions" with only HTML
  // tags / whitespace between.
  expect(indexHtml).toMatch(/Google Research's[^A-Za-z]*<a[^>]*>\s*GoEmotions/);
});

test('brand mark renders as MINDSPACE OS with space', () => {
  expect(indexHtml).toContain('MINDSPACE OS');
  expect(indexHtml).not.toContain('MINDSPACEOS');
});

test('landing has Schema.org Dataset JSON-LD', () => {
  expect(indexHtml).toContain('"@type":"Dataset"');
  expect(indexHtml).toContain('"@context":"https://schema.org"');
});

test('all pages have og:image meta', () => {
  for (const route of expectedRoutes) {
    expect(routeHtml[route]).toMatch(/<meta property="og:image" content="[^"]+"/);
    expect(routeHtml[route]).toMatch(/<meta name="twitter:card" content="summary_large_image"/);
  }
});

test('all pages have canonical link', () => {
  for (const route of expectedRoutes) {
    expect(routeHtml[route]).toMatch(/<link rel="canonical" href="[^"]+"/);
  }
});

test('about page has methodology + limitations sections', () => {
  expect(aboutHtml).toContain('id="methodology"');
  expect(aboutHtml).toContain('id="limitations"');
  expect(aboutHtml).toContain('id="ethics"');
  expect(aboutHtml).toContain('id="cite"');
});

test('chart pages link to GoEmotions methodology', () => {
  const html = routeHtml['explore/emotion-pulse/index.html'];
  expect(html.toLowerCase()).toContain('goemotions');
  expect(html).toContain('/about#methodology');
});

for (const slug of CHART_SLUGS) {
  test(`${slug} page embeds the static chart, not Streamlit`, () => {
    const html = routeHtml[`explore/${slug}/index.html`];
    expect(html).toContain(`/charts/${slug}.html`);
    expect(html).not.toContain('streamlit.app');
  });
}

test('all four static chart HTMLs are self-contained (no Streamlit references)', () => {
  for (const slug of CHART_SLUGS) {
    expect(chartHtml[slug]).not.toContain('streamlit.app');
    expect(chartHtml[slug]).not.toContain('streamlit.io');
  }
});

test('all four static chart HTMLs include mobile breakpoints', () => {
  // MOBILE_CSS in scripts/build_chart_figures.py injects @media (max-width: 768px)
  // and @media (max-width: 480px) into every chart's <style>. Re-run the bake
  // script if these break.
  for (const slug of CHART_SLUGS) {
    expect(chartHtml[slug]).toContain('@media (max-width: 768px)');
    expect(chartHtml[slug]).toContain('@media (max-width: 480px)');
    expect(chartHtml[slug]).toContain('min-height: 44px');
  }
});

test('explore page renders responsive iframe heights via StaticChart', () => {
  // StaticChart.astro injects desktop (768+) and mobile (<768) heights via CSS
  // custom properties. Astro/Vite minifies, so the @media rule loses the space
  // and the selector gets a data-astro-cid suffix.
  const html = routeHtml['explore/emotion-pulse/index.html'];
  expect(html).toMatch(/@media\s*\(min-width:\s*768px\)/);
  expect(html).toMatch(/--mobileHeight:\s*\d+px/);
  expect(html).toMatch(/--desktopHeight:\s*\d+px/);
});

test('Plotly-based static charts load Plotly.js from CDN', () => {
  // Weather Report uses pure HTML/CSS — no Plotly. The other three use Plotly.
  for (const slug of ['emotion-pulse', 'community-dynamics', 'inner-life-currents']) {
    expect(chartHtml[slug]).toContain('cdn.plot.ly/plotly');
  }
});

test('inner-life-currents static chart embeds all 6 quarters of data', () => {
  const html = chartHtml['inner-life-currents'];
  for (const q of ['2024Q1', '2024Q2', '2024Q3', '2024Q4', '2025Q1', '2025Q2']) {
    expect(html).toContain(q);
  }
  expect(html).toContain('Previous Quarter');
  expect(html).toContain('Next Quarter');
});

test('robots.txt allows all and points to sitemap', async () => {
  const robots = await readFile(path.join(DIST, 'robots.txt'), 'utf8');
  expect(robots).toMatch(/User-agent: \*/);
  expect(robots).toMatch(/Allow: \//);
  expect(robots).toContain('Sitemap: https://mindspaceos.com/sitemap-index.xml');
});

test('sitemap includes all routes', async () => {
  // sitemap-index.xml may reference one or more sitemap-N.xml files
  const indexXml = await readFile(path.join(DIST, 'sitemap-index.xml'), 'utf8');
  expect(indexXml).toContain('<sitemap>');
  const match = indexXml.match(/<loc>([^<]+sitemap-0\.xml)<\/loc>/);
  if (match) {
    const sitemapPath = match[1].replace('https://mindspaceos.com/', '');
    const sitemap = await readFile(path.join(DIST, sitemapPath), 'utf8');
    for (const slug of CHART_SLUGS) {
      expect(sitemap).toContain(`/explore/${slug}/`);
    }
    expect(sitemap).toContain('/about/');
  }
});
