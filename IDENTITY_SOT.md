# IDENTITY_SOT — Minyan Shi · Minyan Labs

**Single source of truth for identity facts that appear on both `mindspaceos.com` and the Minyan Labs personal site.**

This file lives at the root of BOTH repos:
- `github.com/minyansh7/MindSpace-OS` — mirrors the values in `site/src/data/identity.ts`
- `github.com/minyansh7/minyan-personal-site` — manually mirrored when this file is updated

When ANY field below changes:
1. Update the canonical value here in BOTH repos (or in `identity.ts` and copy here)
2. Re-deploy both sites
3. Re-run the LLM citation baseline (`.context/llm-baseline-prompts.md`) within 7 days to verify AI engines re-index

Last reviewed: 2026-04-28.

---

## The 8 fields

### 1. Name
- **Full name:** Minyan Shi
- **Pronouns:** she/her (RENDER VISIBLY on resume site hero — confirmed 2026-04-28)
- **Display name (for bylines + nav):** Minyan Shi
- **First-person reference (in copy):** I'm Minyan

### 2. Title
- **Canonical (resume hero, About bios, Person JSON-LD `description`):** Founder, Minyan Labs · ex-Publicis
- **Short form (nav, footers, tweet bios, JSON-LD `jobTitle`):** Founder, Minyan Labs
- **Org short_description (1-sentence "what is Minyan Labs?"):** A one-person studio doing editorial data storytelling and generative-AI search optimization, based in Sydney.
- **Note for ex-Publicis framing:** include in resume bio paragraph + Person JSON-LD `description` field; omit from short-form contexts (nav, OG cards, taglines).

### 3. Email
- **Public contact:** minyanshi@proton.me
- **Project takedown:** minyanshi@proton.me (consolidated 2026-04-28 — drops `takedown@mindspaceos.com`; saves needing a real mailbox at the project domain)
- **Do NOT publish:** any other personal address

### 4. Location
- Sydney, Australia / Remote (Remote availability added 2026-04-28 — agency-buyer signal that you're not Sydney-locked)
- (Schema.org PostalAddress: `addressLocality: "Sydney"`, `addressCountry: "AU"`. The `/Remote` is rendered in display copy, NOT in structured address — schema.org expects a real city.)

### 5. Awards (display in this exact order, most recent first)
- SXSW Sydney AI 2024 winner (Build Club × National AI Centre)
- 2023 GPT Hackathon Winner — GPT-based sentiment model for ASX stock prediction

### 6. Education (display in this exact order, most recent first)
- Harvard Business School — Data Privacy and Technology · Certificate · 2024
- State University of New York at Buffalo — M.S. Geography · GIS · 2011–2014
- Beijing Forestry University — B.S. GIS · 2007–2011

### 7. sameAs links (Schema.org `Person.sameAs` array — these are the canonical "this is the same person" surfaces; order matters for LLM trust signaling)
1. https://www.linkedin.com/in/minyanshi/  ← canonical "who is Minyan" (most LLM-trusted)
2. https://github.com/minyansh7  ← canonical "what does Minyan build"
3. https://x.com/MinyanLabs  ← canonical "what does Minyan say"
4. https://minyansh.substack.com  ← canonical "what does Minyan write"
5. https://mindspaceos.com  ← canonical project artifact

(Resume site URL `minyan-personal-site.shminyan.workers.dev` is NOT in sameAs — it's the page hosting this Person entity, so it appears as the JSON-LD canonical `url` field instead. Custom domain `minyanlabs.com` was dropped from v1 on 2026-04-28; reconsider post-launch.)

### 8. Bio paragraphs

**bio_micro (~25 words, ~150 chars — used in og:description, Twitter card description, LinkedIn preview):**

> Founder of Minyan Labs. Building in generative AI search optimisation. Decade of audience strategy at Publicis and Didi spanning US, Australia and China.

**bio_short (~60 words — used in JSON-LD `description`, About page intro, Substack author block):**

> Minyan Shi is founder of Minyan Labs and is building in generative intelligence search optimisation. With a decade of data and audience strategy at Publicis and Didi — across McDonald's, Pfizer, Adobe, Audi, and Tourism Australia — she's worked across the US, Australia, and China. Winner of SXSW Sydney AI 2024 and the 2023 GPT Hackathon. Harvard Business School Data Privacy and Technology certificate (2024).

**bio_long (~110 words — used in About pages, capstone author block, press bio requests):**

> Minyan Shi founded Minyan Labs to solve one of generative AI's most urgent problems: how brands get found in an era where search is being rewritten from scratch. She brings a decade of audience and data strategy to that question — built across McDonald's, Pfizer, Adobe, Audi, and Tourism Australia at Publicis and Didi, spanning the US, Australia, and China.
>
> A data storyteller by instinct, Minyan and her team took first place at SXSW Sydney AI 2024 (Build Club × National AI Centre) and won the 2023 GPT Hackathon. She holds a Harvard Business School certificate in Data Privacy and Technology (2024).

---

## 9. Canonical client list (for bio + experience drift checks)

**Currently named in bios:** McDonald's, Pfizer, Adobe, Audi, Tourism Australia, Publicis (group), Didi.

**Dropped 2026-04-28** (do NOT re-add to bio prose without explicit decision):
- Newmark Knight Frank Chicago — dropped from bio prose AND from resume site `experience.tsx`. Historical experience, not load-bearing for current positioning.

**Variants to standardize:**
- "Publicis" or "Publicis Group" — use **Publicis** in bio_short and bio_micro (terser); use **Publicis Group** when context allows in bio_long if you want the formal name. Currently bio_long uses "Publicis" — keep simple.
- "Didi" not "Didi Beijing" — geo specificity dropped for tighter copy.
- "Tourism Australia" — confirm with Minyan that this should ALSO be added to resume site `experience.tsx` if it isn't already (currently bio names it but resume hero copy doesn't).

---

## Drift policy

When the same field appears in multiple files, this file is authoritative. Audit quarterly:

```bash
# From either repo:
grep -E "Founder.*Minyan Labs|Minyan Shi|minyanshi@proton" -r src/ public/ docs/
# Cross-reference each match against this file. Anything that disagrees gets updated to match.
```

Specific files to check:
- **MindSpace-OS repo:** `site/src/data/identity.ts`, `site/public/llms.txt`, `site/src/pages/about.astro`, `site/src/components/Footer.astro`, README.md, CLAUDE.md
- **minyan-personal-site repo:** `src/components/hero.tsx`, `src/components/footer.tsx`, `src/components/experience.tsx`, `src/app/layout.tsx` (metadata + Person JSON-LD), `IDENTITY_SOT.md` (this file)

## Version history

- **2026-04-28** — Initial. Created from `identity.ts` + 2026-04-28 autoplan decisions. Key changes from `identity.ts` baseline:
  - Title: added `· ex-Publicis` to canonical form (resume + JSON-LD description only)
  - Bio: rewritten to lead with GEO positioning ("building in generative intelligence search optimisation"); added Tourism Australia; dropped Newmark Knight Frank; added (2024) HBS year
  - Email: takedown consolidated to `minyanshi@proton.me`
  - Location: added `/Remote` for agency-buyer signal
  - sameAs: removed resume URL (it's the canonical page, not a sameAs target)
  - Pronouns: now rendered visibly on resume hero (was JSON-LD only)
  - bio_micro: NEW field for OG cards / social previews (~25 words)
  - bio_long: rewritten with GEO opener
  - Org tagline: dropped — `org.short_description` carries the "what is Minyan Labs?" load instead
