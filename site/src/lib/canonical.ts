import canonical from '../../../data/canonical.json';

export type Archetype = {
  slug: string;
  name: string;
  color: string;
  color_dark: string;
  symbol: string;
  sketch: string;
};

export type Page = {
  slug: string;
  title: string;
  subtitle: string;
  intro: string;
  callout: string;
  streamlit_path: string;
  screenshot: string;
};

export type Essay = {
  title: string;
  subtitle: string;
  url: string;
  published: string;
  summary: string;
};

export type Citation = {
  id: string;
  label: string;
  authors: string;
  year: number;
  title: string;
  venue?: string;
  arxiv?: string;
  url: string;
  huggingface?: string;
};

export const project = canonical.project;
export const data = canonical.data;
export const archetypes = canonical.archetypes as Archetype[];
export const clusters = canonical.clusters as Array<{ name: string; color: string; color_dark: string }>;
export const pages = canonical.pages as Page[];
export const essays = canonical.essays as Essay[];
export const citations = canonical.citations as Citation[];
export const limitations = canonical.limitations as string[];

export const STREAMLIT_BASE = 'https://mindspaceos.streamlit.app';
