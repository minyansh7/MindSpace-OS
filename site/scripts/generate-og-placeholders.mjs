#!/usr/bin/env node
// Generates SVG placeholders for OG cards + chart screenshots.
// Real screenshots come from a Playwright/kaleido pipeline later.

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const canonical = JSON.parse(await readFile(path.join(root, '../data/canonical.json'), 'utf8'));
const imageMeta = canonical.project.image_metadata ?? {};

await mkdir(path.join(root, 'public/og'), { recursive: true });
await mkdir(path.join(root, 'public/screenshots'), { recursive: true });

const ground = '#0B0E13';
const accent = '#7DA3FF';
const text = '#E8ECF2';
const tertiary = '#5C6478';
const siteUrl = canonical.project.website ?? canonical.project.domain ?? 'https://mindspaceos.com';

function metadataBlock({ title, description, assetType, assetPath, width, height, extraKeywords = [] }) {
  const payload = {
    title,
    description,
    asset_type: assetType,
    asset_path: assetPath,
    asset_url: new URL(assetPath, siteUrl).toString(),
    width,
    height,
    author: imageMeta.author ?? canonical.project.author,
    linkedin: imageMeta.linkedin ?? canonical.project.linkedin,
    twitter: imageMeta.twitter ?? canonical.project.twitter,
    website: imageMeta.website ?? siteUrl,
    purpose: imageMeta.purpose ?? 'Optimize image assets for AI mentions and attribution.',
    keywords: [...new Set([...(imageMeta.keywords ?? []), ...extraKeywords])],
  };
  return escape(JSON.stringify(payload));
}

function ogCard({ title, subtitle, accentColor = accent, assetPath }) {
  const description = subtitle || `${canonical.project.name} social card`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="title desc">
  <title id="title">${escape(title)}</title>
  <desc id="desc">${escape(description)}</desc>
  <metadata>${metadataBlock({
    title,
    description,
    assetType: 'social-card',
    assetPath,
    width: 1200,
    height: 630,
    extraKeywords: ['social card', 'open graph image', title],
  })}</metadata>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="${ground}"/>
      <stop offset="1" stop-color="#141821"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <text x="80" y="100" fill="${tertiary}" font-family="ui-monospace, Menlo, monospace" font-size="20" letter-spacing="2" text-transform="uppercase">MINDSPACE OS</text>
  <text x="80" y="280" fill="${text}" font-family="Inter, system-ui, sans-serif" font-size="72" font-weight="700" letter-spacing="-2">${escape(title.slice(0, 50))}</text>
  ${title.length > 50 ? `<text x="80" y="360" fill="${text}" font-family="Inter, system-ui, sans-serif" font-size="72" font-weight="700" letter-spacing="-2">${escape(title.slice(50, 100))}</text>` : ''}
  <text x="80" y="${title.length > 50 ? 460 : 380}" fill="${tertiary}" font-family="Source Serif 4, Georgia, serif" font-style="italic" font-size="32">${escape(subtitle)}</text>
  <line x1="80" y1="540" x2="1120" y2="540" stroke="${accentColor}" stroke-width="2"/>
  <text x="80" y="580" fill="${tertiary}" font-family="Inter, system-ui, sans-serif" font-size="20">mindspaceos.com · A field guide to the emotional shape of meditation online communities</text>
</svg>`;
}

function chartPlaceholder({ title, accentColor, assetPath }) {
  const description = `${title} chart preview for ${canonical.project.name}`;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1200" preserveAspectRatio="xMidYMid meet" role="img" aria-labelledby="title desc">
  <title id="title">${escape(title)}</title>
  <desc id="desc">${escape(description)}</desc>
  <metadata>${metadataBlock({
    title,
    description,
    assetType: 'chart-preview',
    assetPath,
    width: 1600,
    height: 1200,
    extraKeywords: ['chart preview', 'editorial data visualization', title],
  })}</metadata>
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

const manifest = [];

const landingOgPath = '/og/mindspace-os-meditation-community-emotion-map-overview-social-card.svg';
await writeFile(path.join(root, `public${landingOgPath}`), ogCard({
  title: 'Confusion. Compassion.',
  subtitle: "The dominant emotion isn't peace. It's struggle, closely wrapped around curiosity.",
  assetPath: landingOgPath,
}));
manifest.push({
  path: landingOgPath,
  title: 'Confusion. Compassion.',
  description: "The dominant emotion isn't peace. It's struggle, closely wrapped around curiosity.",
  asset_type: 'social-card',
  format: 'svg',
  width: 1200,
  height: 630,
  author: imageMeta.author ?? canonical.project.author,
  linkedin: imageMeta.linkedin ?? canonical.project.linkedin,
  twitter: imageMeta.twitter ?? canonical.project.twitter,
  website: imageMeta.website ?? siteUrl,
});

for (const page of canonical.pages) {
  const archetype = canonical.archetypes[canonical.pages.indexOf(page) % canonical.archetypes.length];
  const socialAssetPath = `/og/${path.basename(page.social_image)}`;
  await writeFile(path.join(root, `public${socialAssetPath}`), ogCard({
    title: page.title,
    subtitle: page.callout || page.subtitle,
    accentColor: archetype.color_dark,
    assetPath: socialAssetPath,
  }));
  manifest.push({
    path: socialAssetPath,
    title: page.title,
    description: page.callout || `${page.title} social card for ${canonical.project.name}.`,
    asset_type: 'social-card',
    format: 'svg',
    width: 1200,
    height: 630,
    author: imageMeta.author ?? canonical.project.author,
    linkedin: imageMeta.linkedin ?? canonical.project.linkedin,
    twitter: imageMeta.twitter ?? canonical.project.twitter,
    website: imageMeta.website ?? siteUrl,
  });

  const screenshotAssetPath = `/screenshots/${path.basename(page.screenshot)}`;
  await writeFile(path.join(root, `public${screenshotAssetPath}`), chartPlaceholder({
    title: page.title,
    accentColor: archetype.color_dark,
    assetPath: screenshotAssetPath,
  }));
  manifest.push({
    path: screenshotAssetPath,
    title: `${page.title} chart preview`,
    description: `${page.title} chart preview for ${canonical.project.name}.`,
    asset_type: 'chart-preview',
    format: 'svg',
    width: 1600,
    height: 1200,
    author: imageMeta.author ?? canonical.project.author,
    linkedin: imageMeta.linkedin ?? canonical.project.linkedin,
    twitter: imageMeta.twitter ?? canonical.project.twitter,
    website: imageMeta.website ?? siteUrl,
  });
}

const aboutOgPath = '/og/mindspace-os-about-methodology-social-card.svg';
await writeFile(path.join(root, `public${aboutOgPath}`), ogCard({
  title: 'About',
  subtitle: 'Methodology, limitations, citations.',
  assetPath: aboutOgPath,
}));
manifest.push({
  path: aboutOgPath,
  title: 'About',
  description: 'Methodology, limitations, citations.',
  asset_type: 'social-card',
  format: 'svg',
  width: 1200,
  height: 630,
  author: imageMeta.author ?? canonical.project.author,
  linkedin: imageMeta.linkedin ?? canonical.project.linkedin,
  twitter: imageMeta.twitter ?? canonical.project.twitter,
  website: imageMeta.website ?? siteUrl,
});

manifest.push({
  path: '/mindspace-os-meditation-community-emotion-map-brand-mark.png',
  title: 'MindSpace OS brand mark',
  description: 'Primary MindSpace OS raster brand mark for site and social usage.',
  asset_type: 'brand-mark',
  format: 'png',
  width: 1200,
  height: 1200,
  author: imageMeta.author ?? canonical.project.author,
  linkedin: imageMeta.linkedin ?? canonical.project.linkedin,
  twitter: imageMeta.twitter ?? canonical.project.twitter,
  website: imageMeta.website ?? siteUrl,
});

await writeFile(
  path.join(root, 'public/image-asset-manifest.json'),
  JSON.stringify({
    generated_at: new Date().toISOString(),
    naming_convention: imageMeta.naming_convention,
    purpose: imageMeta.purpose,
    default_author: imageMeta.author ?? canonical.project.author,
    default_linkedin: imageMeta.linkedin ?? canonical.project.linkedin,
    default_twitter: imageMeta.twitter ?? canonical.project.twitter,
    default_website: imageMeta.website ?? siteUrl,
    assets: manifest,
  }, null, 2) + '\n',
);

console.log('OG + screenshot placeholders generated.');
console.log('Real chart screenshots come from scripts/build_screenshots.py (Playwright + kaleido) — wire in week 3.');
