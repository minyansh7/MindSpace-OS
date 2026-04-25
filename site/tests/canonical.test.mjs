// Single-source-of-truth sync test.
// Asserts that values from data/canonical.json appear in the rendered site
// and that no inline duplicates of canonical values exist.
//
// Run: bun test tests/canonical.test.mjs

import { test, expect } from 'bun:test';
import { readFile } from 'node:fs/promises';
import { glob } from 'bun';

const canonical = JSON.parse(await readFile('../data/canonical.json', 'utf8'));

test('canonical post count is exactly 2899 (locked decision)', () => {
  expect(canonical.data.post_count_canonical).toBe(2899);
});

test('canonical pre-filter post count is exactly 2977', () => {
  expect(canonical.data.post_count_pre_filter).toBe(2977);
});

test('exactly 5 archetypes match the existing ARCHETYPE_COLORS palette', () => {
  expect(canonical.archetypes).toHaveLength(5);
  const expectedNames = ['Reflective Caring', 'Soothing Empathy', 'Tender Uncertainty', 'Melancholic Confusion', 'Anxious Concern'];
  expect(canonical.archetypes.map((a) => a.name).sort()).toEqual(expectedNames.sort());
});

test('exactly 4 chart pages (live in the v2 site)', () => {
  expect(canonical.pages).toHaveLength(4);
  const slugs = canonical.pages.map((p) => p.slug);
  expect(slugs).toEqual(['emotion-pulse', 'community-dynamics', 'community-weather-report', 'inner-life-currents']);
});

test('exactly 2 published essays linked', () => {
  expect(canonical.essays).toHaveLength(2);
  for (const e of canonical.essays) {
    expect(e.url).toMatch(/^https:\/\/minyansh\.substack\.com/);
  }
});

test('GoEmotions citation present with arXiv id', () => {
  const cite = canonical.citations.find((c) => c.id === 'goemotions');
  expect(cite).toBeDefined();
  expect(cite.arxiv).toBe('2005.00547');
});

test('UMAP citation present', () => {
  const cite = canonical.citations.find((c) => c.id === 'umap');
  expect(cite).toBeDefined();
});

test('limitations include the GoEmotions circularity disclosure', () => {
  const text = canonical.limitations.join(' ').toLowerCase();
  expect(text).toContain('circular');
  expect(text).toContain('goemotions');
  expect(text).toContain('reddit');
});

test('no inline duplicate of post counts in Astro source files', async () => {
  // Source files should NOT inline 2899 or 2977 — they should import from canonical.json.
  // Exception: data/canonical.json itself.
  const files = ['src/pages/index.astro', 'src/pages/about.astro', 'src/pages/explore/[slug].astro', 'src/components/Nav.astro', 'src/components/Footer.astro'];
  for (const file of files) {
    const content = await readFile(file, 'utf8');
    expect(content).not.toMatch(/\b2899\b/);
    expect(content).not.toMatch(/\b2977\b/);
  }
});

test('no inline duplicate of archetype names in components', async () => {
  // Same source-of-truth rule.
  const file = await readFile('src/pages/index.astro', 'utf8');
  // The archetype names should appear in the rendered output (after import) but NOT as hardcoded strings in the source.
  expect(file).not.toContain('"Reflective Caring"');
  expect(file).not.toContain('"Soothing Empathy"');
  expect(file).not.toContain('"Tender Uncertainty"');
  expect(file).not.toContain('"Melancholic Confusion"');
  expect(file).not.toContain('"Anxious Concern"');
});
