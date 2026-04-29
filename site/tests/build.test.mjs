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
  'og/mindspace-os-meditation-community-emotion-map-overview-social-card.svg',
  'og/mindspace-os-emotion-pulse-social-card.svg',
  'og/mindspace-os-community-dynamics-social-card.svg',
  'og/mindspace-os-community-weather-report-social-card.svg',
  'og/mindspace-os-inner-life-currents-social-card.svg',
  'og/mindspace-os-about-methodology-social-card.svg',
  'screenshots/mindspace-os-emotion-pulse-chart-preview.svg',
  'screenshots/mindspace-os-community-dynamics-chart-preview.svg',
  'screenshots/mindspace-os-community-weather-report-chart-preview.svg',
  'screenshots/mindspace-os-inner-life-currents-chart-preview.svg',
  'mindspace-os-meditation-community-emotion-map-brand-mark.png',
  'image-asset-manifest.json',
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

for (const route of expectedRoutes) {
  test(`route exists: ${route}`, async () => {
    const full = path.join(DIST, route);
    expect(existsSync(full)).toBe(true);
    const s = await stat(full);
    expect(s.size).toBeGreaterThan(500);
  });
}

for (const asset of expectedAssets) {
  test(`asset exists: ${asset}`, () => {
    expect(existsSync(path.join(DIST, asset))).toBe(true);
  });
}

test('landing has thesis H1', async () => {
  const html = await readFile(path.join(DIST, 'index.html'), 'utf8');
  expect(html).toContain('Confusion');
  expect(html).toContain('Compassion');
});

test('landing has updated thesis copy', async () => {
  const html = await readFile(path.join(DIST, 'index.html'), 'utf8');
  expect(html).toContain('struggle closely wrapped around curiosity');
});

test('GoEmotions citation includes Google Research prefix', async () => {
  const html = await readFile(path.join(DIST, 'index.html'), 'utf8');
  expect(html).toMatch(/Google Research's[^A-Za-z]*<a[^>]*>\s*GoEmotions/);
});

test('brand mark renders as MINDSPACE OS with space', async () => {
  const html = await readFile(path.join(DIST, 'index.html'), 'utf8');
  expect(html).toContain('MINDSPACE OS');
  expect(html).not.toContain('MINDSPACEOS');
});

test('landing has Schema.org Dataset JSON-LD', async () => {
  const html = await readFile(path.join(DIST, 'index.html'), 'utf8');
  expect(html).toContain('"@type":"Dataset"');
  expect(html).toContain('"@context":"https://schema.org"');
});

test('all pages have og:image meta', async () => {
  for (const route of expectedRoutes) {
    const html = await readFile(path.join(DIST, route), 'utf8');
    expect(html).toMatch(/<meta property="og:image" content="[^"]+"/);
    expect(html).toMatch(/<meta property="og:image:alt" content="[^"]+"/);
    expect(html).toMatch(/<meta name="twitter:card" content="summary_large_image"/);
  }
});

test('landing includes author and social metadata', async () => {
  const html = await readFile(path.join(DIST, 'index.html'), 'utf8');
  expect(html).toContain('<meta name="author" content="Minyan Shi"');
  expect(html).toContain('<meta name="creator" content="Minyan Shi"');
  expect(html).toContain('<meta name="application-name" content="MindSpaceOS"');
  expect(html).toContain('<meta name="twitter:creator" content="@minyansh"');
  expect(html).toContain('https://www.linkedin.com/in/minyanshi/');
  expect(html).toContain('https://x.com/minyansh');
});

test('generated OG assets include embedded image attribution metadata', async () => {
  const svg = await readFile(path.join(DIST, 'og/mindspace-os-emotion-pulse-social-card.svg'), 'utf8');
  expect(svg).toContain('<metadata>');
  expect(svg).toContain('"author":"Minyan Shi"');
  expect(svg).toContain('"linkedin":"https://www.linkedin.com/in/minyanshi/"');
  expect(svg).toContain('"twitter":"https://x.com/minyansh"');
  expect(svg).toContain('"website":"https://mindspaceos.com"');
});

test('image asset manifest includes attribution fields for brand and social assets', async () => {
  const manifest = JSON.parse(await readFile(path.join(DIST, 'image-asset-manifest.json'), 'utf8'));
  expect(Array.isArray(manifest.assets)).toBe(true);
  expect(manifest.assets.length).toBeGreaterThanOrEqual(7);
  const brandMark = manifest.assets.find((asset) => asset.path === '/mindspace-os-meditation-community-emotion-map-brand-mark.png');
  expect(brandMark).toBeTruthy();
  expect(brandMark.author).toBe('Minyan Shi');
  expect(brandMark.linkedin).toBe('https://www.linkedin.com/in/minyanshi/');
  expect(brandMark.twitter).toBe('https://x.com/minyansh');
  expect(brandMark.website).toBe('https://mindspaceos.com');
});

test('all pages have canonical link', async () => {
  for (const route of expectedRoutes) {
    const html = await readFile(path.join(DIST, route), 'utf8');
    expect(html).toMatch(/<link rel="canonical" href="[^"]+"/);
  }
});

test('about page has methodology + limitations sections', async () => {
  const html = await readFile(path.join(DIST, 'about/index.html'), 'utf8');
  expect(html).toContain('id="methodology"');
  expect(html).toContain('id="limitations"');
  expect(html).toContain('id="ethics"');
  expect(html).toContain('id="cite"');
});

test('chart pages link to GoEmotions methodology', async () => {
  const html = await readFile(path.join(DIST, 'explore/emotion-pulse/index.html'), 'utf8');
  expect(html.toLowerCase()).toContain('goemotions');
  expect(html).toContain('/about#methodology');
});

test('community-dynamics page embeds the static chart, not Streamlit', async () => {
  const html = await readFile(path.join(DIST, 'explore/community-dynamics/index.html'), 'utf8');
  expect(html).toContain('/charts/community-dynamics');
  expect(html).not.toContain('mindspaceos.streamlit.app/Community_Dynamics');
});

test('emotion-pulse page embeds the static chart, not Streamlit', async () => {
  const html = await readFile(path.join(DIST, 'explore/emotion-pulse/index.html'), 'utf8');
  expect(html).toContain('/charts/emotion-pulse');
  expect(html).not.toContain('mindspaceos.streamlit.app/Emotion_Pulse');
});

test('inner-life-currents page embeds the static chart, not Streamlit', async () => {
  const html = await readFile(path.join(DIST, 'explore/inner-life-currents/index.html'), 'utf8');
  expect(html).toContain('/charts/inner-life-currents');
  expect(html).not.toContain('mindspaceos.streamlit.app/Inner_Life_Currents');
});

test('community-weather-report page embeds the static chart, not Streamlit', async () => {
  const html = await readFile(path.join(DIST, 'explore/community-weather-report/index.html'), 'utf8');
  expect(html).toContain('/charts/community-weather-report');
  expect(html).not.toContain('mindspaceos.streamlit.app/Community_Weather_Report');
});

test('no chart page falls back to Streamlit iframe (Phase 2 complete)', async () => {
  for (const slug of ['emotion-pulse', 'community-dynamics', 'community-weather-report', 'inner-life-currents']) {
    const html = await readFile(path.join(DIST, `explore/${slug}/index.html`), 'utf8');
    expect(html).not.toContain('streamlit.app');
  }
});

test('all four static chart HTMLs are self-contained (no Streamlit references)', async () => {
  for (const slug of ['emotion-pulse', 'community-dynamics', 'inner-life-currents', 'community-weather-report']) {
    const html = await readFile(path.join(DIST, `charts/${slug}.html`), 'utf8');
    expect(html).not.toContain('streamlit.app');
    expect(html).not.toContain('streamlit.io');
  }
});

test('Plotly-based static charts load Plotly.js from CDN', async () => {
  for (const slug of ['emotion-pulse', 'community-dynamics', 'inner-life-currents']) {
    const html = await readFile(path.join(DIST, `charts/${slug}.html`), 'utf8');
    expect(html).toContain('cdn.plot.ly/plotly');
  }
});

test('inner-life-currents static chart embeds all 6 quarters of data', async () => {
  const html = await readFile(path.join(DIST, 'charts/inner-life-currents.html'), 'utf8');
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
  const indexXml = await readFile(path.join(DIST, 'sitemap-index.xml'), 'utf8');
  expect(indexXml).toContain('<sitemap>');
  const match = indexXml.match(/<loc>([^<]+sitemap-0\.xml)<\/loc>/);
  if (match) {
    const sitemapPath = match[1].replace('https://mindspaceos.com/', '');
    const sitemap = await readFile(path.join(DIST, sitemapPath), 'utf8');
    for (const slug of ['emotion-pulse', 'community-dynamics', 'community-weather-report', 'inner-life-currents']) {
      expect(sitemap).toContain(`/explore/${slug}/`);
    }
    expect(sitemap).toContain('/about/');
  }
});
