// Single source of truth for Minyan Labs / Minyan Shi identity.
// Imported by Footer, About page, JsonLd component, llms.txt generator.
// When credentials, links, or bio change: edit here, render-everywhere updates.
// Mirror this file's bio paragraphs into the resume site at minyanlabs.com.

export const identity = {
  person: {
    name: 'Minyan Shi',
    pronoun: 'she/her',
    title: 'Founder, Minyan Labs',
    title_canonical: 'Founder, Minyan Labs · ex-Publicis',
    location: 'Sydney, Australia',
    location_display: 'Sydney, Australia / Remote',
    email: 'minyanshi@proton.me',
    bio_micro:
      'Founder of Minyan Labs. Building in generative AI search optimisation. Decade of audience strategy at Publicis and Didi spanning US, Australia and China.',
    bio_short:
      "Minyan Shi is founder of Minyan Labs and is building in generative intelligence search optimisation. With a decade of data and audience strategy at Publicis and Didi — across McDonald's, Pfizer, Adobe, Audi, and Tourism Australia — she's worked across the US, Australia, and China. Winner of SXSW Sydney AI 2024 and the 2023 GPT Hackathon. Harvard Business School Data Privacy and Technology certificate (2024).",
    bio_long:
      "Minyan Shi founded Minyan Labs to solve one of generative AI's most urgent problems: how brands get found in an era where search is being rewritten from scratch. She brings a decade of audience and data strategy to that question — built across McDonald's, Pfizer, Adobe, Audi, and Tourism Australia at Publicis and Didi, spanning the US, Australia, and China. A data storyteller by instinct, Minyan and her team took first place at SXSW Sydney AI 2024 (Build Club × National AI Centre) and won the 2023 GPT Hackathon. She holds a Harvard Business School certificate in Data Privacy and Technology (2024).",
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
    short_description:
      'A one-person studio doing editorial data storytelling and generative-AI search optimization, based in Sydney.',
    founded: 2026,
    location: 'Sydney, Australia',
  },
  links: {
    // resume: workers.dev is the canonical resume URL (custom minyanlabs.com dropped from v1 per IDENTITY_SOT 2026-04-28)
    resume: 'https://minyan-personal-site.shminyan.workers.dev',
    resume_legacy: 'https://minyanlabs.com', // dropped from v1, kept for if/when reactivated
    project_mindspaceos: 'https://mindspaceos.com', // live since 2026-04-26
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
