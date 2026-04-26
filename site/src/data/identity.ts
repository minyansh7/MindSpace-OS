// Single source of truth for Minyan Labs / Minyan Shi identity.
// Imported by Footer, About page, JsonLd component, llms.txt generator.
// When credentials, links, or bio change: edit here, render-everywhere updates.
// Mirror this file's bio paragraphs into the resume site at minyanlabs.com.

export const identity = {
  person: {
    name: 'Minyan Shi',
    pronoun: 'she/her',
    title: 'Founder, Minyan Labs',
    location: 'Sydney, Australia',
    email: 'minyanshi@proton.me',
    bio_short:
      'Minyan Shi is the founder of Minyan Labs, a one-person studio doing editorial data storytelling and AI work. Available for select 2026 consulting engagements.',
    bio_long:
      "Minyan Shi (she/her) is the founder of Minyan Labs, a one-person studio doing editorial data storytelling and AI work, based in Sydney. A decade of audience and data strategy across McDonald's, Pfizer, Adobe, Audi, and Didi at Digitas (Publicis Group), Didi Beijing, and Newmark Knight Frank Chicago. Won SXSW Sydney AI 2024 (Build Club × National AI Centre) and the 2023 GPT Hackathon. Harvard Business School Data Privacy and Technology certificate (2024).",
    awards: [
      'SXSW Sydney AI 2024 winner (Build Club × National AI Centre)',
      '2023 GPT Hackathon Winner — GPT-based sentiment model for ASX stock prediction',
    ],
    education: [
      { school: 'Harvard Business School', credential: 'Data Privacy and Technology · Certificate', year: 2024 },
      { school: 'State University of New York at Buffalo', credential: 'M.S. Geography · GIS', year_range: '2011–2014' },
      { school: 'Beijing Forestry University', credential: 'B.S. GIS', year_range: '2007–2011' },
    ],
  },
  org: {
    name: 'Minyan Labs',
    legal_name: 'Minyan Labs',
    tagline: 'Maps turned metrics. Data, strategy, and AI built in Sydney.',
    founded: 2026,
    location: 'Sydney, Australia',
  },
  links: {
    resume: 'https://minyanlabs.com', // post-DNS-cutover; pre-cutover use resume_fallback
    resume_fallback: 'https://minyan-personal-site.shminyan.workers.dev',
    project_mindspaceos: 'https://mindspaceos.com', // post-DNS-cutover
    project_mindspaceos_fallback: 'https://minyansh7-mindspace-os-publi-xcqs.mindspace-os.pages.dev',
    substack: 'https://minyansh.substack.com',
    linkedin: 'https://www.linkedin.com/in/minyanshi/',
    github_user: 'https://github.com/minyansh7',
    github_project: 'https://github.com/minyansh7/MindSpace-OS',
    x: 'https://x.com/MinyanLabs',
  },
  writing: [
    {
      title: 'Meditation Communities Are Not as Calm as they Look',
      subtitle: 'What 2,899 Reddit posts on r/meditation actually feel like.',
      url: 'https://minyansh.substack.com/p/the-emotion-map-of-meditation-online',
      published: '2026-04',
      venue: 'Substack',
    },
    {
      title: 'What 48,000 Reddit posts on meditation reveal',
      subtitle: "The dominant emotion isn't peace. It's struggle, returned to with curiosity.",
      url: 'https://minyansh.substack.com/p/what-48000-reddit-posts-on-meditation',
      published: '2026-04',
      venue: 'Substack',
    },
  ],
} as const;

export type Identity = typeof identity;
