#!/usr/bin/env node
// Generates SVG placeholders for OG cards + chart screenshots.
// Real screenshots come from a Playwright/kaleido pipeline later (see scripts/build_screenshots.py).
// These exist so dev preview / build doesn't 404 and the site has fallback imagery.

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const canonical = JSON.parse(await readFile(path.join(root, '../data/canonical.json'), 'utf8'));

await mkdir(path.join(root, 'public/og'), { recursive: true });
await mkdir(path.join(root, 'public/screenshots'), { recursive: true });

const ground = '#0B0E13';
const accent = '#7DA3FF';
const text = '#E8ECF2';
const tertiary = '#5C6478';

function ogCard({ title, subtitle, accentColor = accent }) {
  // 1200×630 OG card
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" preserveAspectRatio="xMidYMid meet">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="${ground}"/>
      <stop offset="1" stop-color="#141821"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <text x="80" y="100" fill="${tertiary}" font-family="ui-monospace, Menlo, monospace" font-size="20" letter-spacing="2" text-transform="uppercase">MINDSPACEOS</text>
  <text x="80" y="280" fill="${text}" font-family="Inter, system-ui, sans-serif" font-size="72" font-weight="700" letter-spacing="-2">${escape(title.slice(0, 50))}</text>
  ${title.length > 50 ? `<text x="80" y="360" fill="${text}" font-family="Inter, system-ui, sans-serif" font-size="72" font-weight="700" letter-spacing="-2">${escape(title.slice(50, 100))}</text>` : ''}
  <text x="80" y="${title.length > 50 ? 460 : 380}" fill="${tertiary}" font-family="Source Serif 4, Georgia, serif" font-style="italic" font-size="32">${escape(subtitle)}</text>
  <line x1="80" y1="540" x2="1120" y2="540" stroke="${accentColor}" stroke-width="2"/>
  <text x="80" y="580" fill="${tertiary}" font-family="Inter, system-ui, sans-serif" font-size="20">mindspaceos.com · A field guide to the emotional shape of online meditation</text>
</svg>`;
}

function chartPlaceholder({ title, accentColor }) {
  // 1600×1200 chart preview placeholder. Replace via Playwright pipeline.
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1200" preserveAspectRatio="xMidYMid meet">
  <rect width="1600" height="1200" fill="${ground}"/>
  ${Array.from({ length: 80 }, () => {
    const x = Math.random() * 1400 + 100;
    const y = Math.random() * 900 + 150;
    const r = Math.random() * 6 + 3;
    return `<circle cx="${x}" cy="${y}" r="${r}" fill="${accentColor}" opacity="${0.2 + Math.random() * 0.4}"/>`;
  }).join('\n  ')}
  <text x="80" y="100" fill="${tertiary}" font-family="ui-monospace, Menlo, monospace" font-size="22" letter-spacing="3">PREVIEW · ${title.toUpperCase()}</text>
  <text x="80" y="1140" fill="${tertiary}" font-family="Inter, system-ui, sans-serif" font-size="22">Live interactive view available on desktop · mindspaceos.com</text>
</svg>`;
}

function escape(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Default OG (landing)
await writeFile(path.join(root, 'public/og/default.svg'), ogCard({
  title: "Meditation isn't peaceful.",
  subtitle: "It's persistent.",
}));

// Per-page OGs
for (const page of canonical.pages) {
  const archetype = canonical.archetypes[canonical.pages.indexOf(page) % canonical.archetypes.length];
  await writeFile(path.join(root, `public/og/${page.slug}.svg`), ogCard({
    title: page.title,
    subtitle: page.callout,
    accentColor: archetype.color_dark,
  }));
  await writeFile(path.join(root, `public/screenshots/${page.slug}.svg`), chartPlaceholder({
    title: page.title,
    accentColor: archetype.color_dark,
  }));
}

// About OG
await writeFile(path.join(root, 'public/og/about.svg'), ogCard({
  title: 'About',
  subtitle: 'Methodology, limitations, citations.',
}));

console.log('OG + screenshot placeholders generated.');
console.log('Real chart screenshots come from scripts/build_screenshots.py (Playwright + kaleido) — wire in week 3.');
