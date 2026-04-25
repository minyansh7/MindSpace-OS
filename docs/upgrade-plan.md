# MindSpace OS — Site Upgrade Plan (san-antonio)

> Single source of truth for the next pass on https://mindspaceos.streamlit.app.
> Goal: upgrade the site across **design, engineering, storytelling, and distribution**
> so the data work reaches a meaningfully larger audience than r/dataisbeautiful niche.

---

## 0. What we're working with

- **Live:** https://mindspaceos.streamlit.app (Streamlit Cloud, free tier)
- **Repo:** https://github.com/minyansh7/MindSpace-OS
- **Stack:** Streamlit 1.25+, Plotly, DuckDB, Pandas, Python 3.11
- **Pages:** 4 live (Emotion Pulse, Community Dynamics, Community Weather Report, Inner Life Currents)
- **Data:** 2,977 r/meditation posts, Jan 2024 – Jun 2025
- **Existing assets:**
  - Sophisticated editorial layer in `CLAUDE.md` (naming family, palette, typography conventions)
  - Precomputed perf tier (slim parquet, prebuilt Plotly JSON)
  - Launch automation in `drafts/` (Substack + Twitter Playwright runners)
  - Substack ([open.substack.com/pub/minyansh](https://open.substack.com/pub/minyansh)) + LinkedIn already linked
- **Audience reached so far:** unknown — no analytics in place; launch automation exists but no published evidence of broad reach

---

## 1. The thesis (one sentence that has to travel)

> **The dominant emotional register on r/meditation isn't peace. It's struggle tightly coupled with curiosity.**

This is the line. Everything in the upgrade serves this thesis traveling further.
The plan is structured around the question: *what stops this thesis from reaching
100k people?*

---

## 2. Premises (the things this plan rests on — challenge these first)

1. **Niche-first audience. General-interest as stretch.** Primary target: HCI researchers (CHI, CSCW), computational social science (ICWSM), meditation teachers/clinicians, data-viz practitioners (Observable, Nightingale, Data Visualization Society). General-interest outlets (Atlantic/Vox/Pudding) are stretch goals, not the primary audience. *Resolved 2026-04-25 after CEO review flagged "Atlantic readers" as unsupported by the existing two essays' reach.*
2. **Streamlit's chrome is the distribution ceiling.** The `streamlit.app` subdomain, the cold-start spinner, the lack of OG images, and the desktop-only stance are what's currently capping reach — not the data work itself.
3. **The data analysis is complete AND the editorial canon already exists.** No new charts. No new clusters. Two published Substack essays already crystallize the voice and the findings:
   - *"What 3,000 Reddit Posts on Meditation Actually Sound Like"* (Apr 21, 2026) — establishes the thesis: struggle wrapped around curiosity
   - *"Meditation Communities Are Not as Calm as They Look"* (Apr 24, 2026) — adds the response-pattern findings (grief gets mirrored, anxiety gets reassurance, lurkers do the emotional work)
   The upgrade is UX + distribution + harvesting the existing prose into the site itself, not re-writing it.
4. **Substack + Twitter/X + LinkedIn are sufficient distribution surfaces.** Plus targeted press outreach. No paid ads.
5. **Mobile RESPONSIVE, not mobile interactive.** Landing page, page intros, essays, About, archetype cards, OG previews — all must reflow and read cleanly on phones. **Charts on mobile are static high-res screenshots with "View interactive on desktop" CTA, NOT interactive Plotly/iframe.** *Resolved 2026-04-25 after all 3 reviews flagged mobile chart interactivity as the same scope-overrun pattern that caused the original revert in commit `62b4a11b`.* The static-screenshot-first iframe loading pattern serves both desktop AND mobile from a single source of truth. Re-evaluation criterion: post-launch Plausible data shows mobile share ≥30% and engagement ≥40% over a rolling 14-day window, 30 days post-launch → consider re-introducing for v1.1.
6. **One person, ~6 weeks of evening/weekend time.** Solo developer, with Claude Code + gstack. Not a team project.

If any of these is wrong, the plan needs reshaping.

---

## 3. Target state

**Three months from now:**
- Custom domain (e.g. `mindspaceos.com`)
- Landing page reads in 30 seconds, hooks the thesis in 10
- Each interactive page has an editorial intro + "what to look for"
- Mobile: landing + intros + essays + About all render cleanly. Charts are responsive static screenshots with "View interactive on desktop" CTA (no Plotly/iframe interactivity on mobile in v1)
- OG images for every page (chart preview + thesis line)
- One published long-form essay on Substack tied to the site
- Press coverage in at least one general-interest outlet OR a quote/blurb from a respected meditation researcher
- Plausible analytics installed; baseline traffic tracked

**Concrete success metrics:**
- 25k+ unique visitors in first 30 days post-relaunch (current baseline: unknown, likely <2k)
- Avg session ≥ 90s (data viz is exploration; under 90s = hook failed)
- 1+ inbound press mention or 5+ inbound newsletter subscribers/day for 2 weeks
- Mobile bounce rate < 60%

---

## 4. Scope — by axis

**Five axes** (one was added 2026-04-25 after CEO review): Design, Engineering, Storytelling, Distribution, **Research & Partner**.

### 4A. Design

**Problem:** Streamlit chrome (sidebar, hamburger, "Made with Streamlit" footer that's been hidden but the deploy URL still leaks it) signals "internal tool" not "publication." The time-of-day color gradient on the homepage is cute but reads as gimmick. Hover states and animations are uneven across pages.

**Direction:**
1. **New shell, same charts.** Build a static landing + chrome in **Astro** (or Next.js — open question, see Decisions). Keep the four interactive Streamlit pages embedded via iframe or migrate selectively to Observable Plot. Decide per-page based on shareability.
2. **Editorial typography.** Serif body (e.g. EB Garamond or Source Serif) for prose, sans (Inter — already used) for UI, mono (JetBrains Mono) for data labels. Fixes the "internal tool" feel.
3. **Dark-mode first.** Data viz pops on dark. Light mode optional. Replaces the time-of-day gradient with one stable, considered palette anchored on the existing cluster colors.
4. **Hero chart treatment.** Landing leads with ONE chart (likely Emotion Pulse) at hero scale. Below the fold: thesis statement. Below that: card grid for the four pages. Removes the meditation-circle ripple animation (cute but doesn't tell the story).
5. **OG image system.** Every page generates a 1200×630 OG card with chart preview + page H1 + thesis line. Use Vercel OG / Satori or pre-rendered PNGs. **This is what makes the site shareable.**
6. **Mobile responsive (chrome only), not interactive (charts).** *Updated 2026-04-25.* Landing, page intros, essays, About, archetype cards reflow cleanly on phones (Tailwind responsive breakpoints in Astro shell — sm/md/lg/xl, mobile-first). **Charts on mobile = high-res static screenshot + "View interactive on desktop" CTA.** No Plotly mobile branch. No iframe `@media` blocks. The static-screenshot-first iframe loading pattern (see 4B-1) serves mobile AND desktop pre-interaction; mobile users just don't progress past the static state. This collapses the "16 visual permutations × 2 paths × 4 pages" QA matrix to a single set of responsive layouts + 4 static screenshots. Win.

### 4B. Engineering

**Problem:** Streamlit Cloud free tier cold-starts (~10–30s) kill the landing page. There's no analytics. There's no OG generation. There's no CDN. The deploy URL is `*.streamlit.app`.

**Direction:**
1. **Hybrid architecture.** Astro/Next.js static site on Vercel (or Cloudflare Pages) for the landing, page intros, essays. Streamlit Cloud continues to host the four interactive pages, embedded via iframe at `/explore/emotion-pulse` etc. Cold start now hits an iframe that's only loaded when the user clicks "Explore" — landing renders instantly.
2. **Custom domain.** Register **`mindspaceos.com` on Cloudflare Registrar** (~$10.44/year). Wire Cloudflare DNS, set up 301 redirects from `mindspaceos.streamlit.app` → `mindspaceos.com` for SEO carryover. Cloudflare Registrar requires Cloudflare DNS which is what we want anyway for Pages hosting.
3. **OG image generation.** Static PNGs in `public/og/` to start (one per page + one default). Upgrade to Satori-rendered if pages start needing dynamic data in the card.
4. **Analytics.** *Resolved 2026-04-25:* **Cloudflare Web Analytics** as primary (FREE, already in stack, server-side / no JS / ad-blocker-resistant — critical for niche-research audience that runs aggressive blockers). Tracks: pageviews, referrers, country, device, top pages. **Plausible deferred to v1.1** trigger: when an actual event needs tracking (OG share clicks, "Tap to interact" conversion, scroll depth past hero). Saves ~$108/yr and avoids consent-banner debate (CF is GDPR-compliant by default, no cookies). Upgrade path: drop in Plausible's 1-line script when v1.1 needs event-level data.
5. **Performance.** Apply the existing precomputed-parquet pattern to remaining pages (Community Weather Report, Inner Life Currents) so cold start drops further. Audit iframe pages in Lighthouse — target LCP < 2.5s on the landing.
6. **CI/CD.** GitHub Actions to deploy Astro on push to main. Keep Streamlit Cloud's auto-deploy for the Streamlit pages.
7. **Mobile path: responsive shell only.** *Updated 2026-04-25.* No `mobile.py` helper. No Plotly mobile branch. No iframe `@media` blocks. The Streamlit chart pages stay desktop-only (per existing `CLAUDE.md` "Target viewport: desktop only" — that decision stands). Mobile experience is owned entirely by the Astro shell:
   - Tailwind mobile-first responsive breakpoints (`sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`).
   - Landing, page intros, essays, About, archetype cards all reflow cleanly at 375px.
   - Each `/explore/<page>` route on mobile shows: page intro + quotable line + static chart screenshot (1600×1200, WebP) + "View interactive on desktop" CTA button.
   - Each `/explore/<page>` on desktop shows: page intro + quotable line + iframe-embedded Streamlit chart (with static-screenshot-first loading pattern from 4B-1).
   - Single set of responsive layouts. Lighthouse mobile target: ≥85 (achievable because no live iframe on mobile means no cold-start LCP penalty).
   - Re-evaluation criterion (committed): post-launch Plausible data → if mobile share ≥30% AND engagement rate ≥40% over rolling 14-day window 30 days post-launch, plan v1.1 with mobile chart interactivity. Otherwise stay where we are.

### 4C. Storytelling

**Problem:** The site shows charts. It doesn't tell a story. A first-time visitor who lands on Emotion Pulse without context sees a UMAP scatter and bounces. Meanwhile, two strong Substack essays already exist with the prose, the thesis, and the findings — but the site doesn't reference them or excerpt them. The story exists; it's just not on the site.

**Editorial source material (already written, harvest don't rewrite):**
- *"What 3,000 Reddit Posts on Meditation Actually Sound Like"* — the thesis essay
- *"Meditation Communities Are Not as Calm as They Look"* — the response-patterns essay

**Voice spec (extracted from the existing essays):**
Conversational + poetic, sparse on technical jargon despite sophisticated analysis. Contrast-driven openings ("Promises calm, delivers confusion"). Grounds abstract findings in actual human language ("This can happen," "You are not broken"). Treats data analysis as a lens for understanding human connection, not metrics. **Every new line written for the site must pass: would this fit alongside the existing essays without sounding like a different person wrote it?**

**Direction:**

1. **Lead with the thesis on the landing page.** *Resolved 2026-04-25:* H1 emphasizes **emotions** rather than meditation. The thesis "struggle wrapped around curiosity" is the hook. Drafted candidates (pick one):
   - *"The emotional shape of online meditation: struggle wrapped around curiosity."*
   - *"Joy ranks 25th of 28. The dominant emotion is curiosity."*
   - *"What an emotion map of 2,899 meditation posts actually shows."*
   - *"The emotions inside an online meditation community."*
   Subhead pattern: short specificity line. Brand "MINDSPACEOS" is mono mark top-left, not the headline.

2. **Two anchor quotes, used everywhere.** These are the lines that travel:
   - *"The vocabulary that dominates is 'I'm trying again.'"* — the lived-experience version of the thesis
   - *"Comments pull people inward toward intimacy rather than amplification."* — the social-fabric finding
   Print them on the landing page. Embed them in OG cards. Use them as section dividers in the scroll-tell. Quote-screenshot them for Twitter.

3. **Scroll-tell mode for first-time readers — 4 scenes themed on "struggle wrapped with curiosity."** *Resolved 2026-04-25:* Cut to 4, theme around archetypes + the central thesis. Each scene = one chart preview + one paragraph + one quotable line. ~60s end to end.
   - Scene 1 — **Hook:** *"Joy ranks 25th of 28 emotions. Amusement is dead last."* → Emotion Pulse preview. Set up the surprise.
   - Scene 2 — **Archetypes:** Introduce the 5 emotional archetypes as the structure inside that surprise. *"Five recurring emotional archetypes — from Anxious Concern to Soothing Empathy."* Card-grid preview, lead into Community Dynamics.
   - Scene 3 — **Mechanism:** *"Grief gets mirrored. Anxiety gets reassurance. The community has unwritten response rules."* → Community Dynamics preview. The struggle-curiosity dynamic in action.
   - Scene 4 — **Invitation:** *"Watch the conversation drift, quarter by quarter."* → Inner Life Currents preview. Sets up the click-through to interactive.
   - End: "Open any of the four for the full interactive view (desktop)."

4. **Per-page editorial intro.** Every chart page gets a 2–3 paragraph intro above the fold pulled or adapted from the essays. Specifically:
   - **Emotion Pulse** intro: lead with *"Joy ranks 25th of 28. The vocabulary is 'I'm trying again.'"* Explain the UMAP map in plain English. Name the 5 archetypes inline.
   - **Community Dynamics** intro: lead with *"25% mirror grief. Only 7% mirror anxiety."* Explain the Sankey is poster→commenter emotional flow. Mention "the community has unwritten response rules."
   - **Community Weather Report** intro: lead with the weather metaphor, then the finding ("which topics run sunny, which run stormy").
   - **Inner Life Currents** intro: lead with *"Watch the conversation drift, quarter by quarter."* Explain co-occurrence. Tease the time-travel slider.

5. **Five emotional archetypes — keep the existing names from the codebase.** *Resolved 2026-04-25.* No renaming. Use the `ARCHETYPE_COLORS` palette in `pages/0_Emotion_Pulse.py` as the canonical source (extracted into `data/canonical.json`). Write a 2-sentence character sketch for each existing archetype, voiced to match the published essays. Display as a card grid on the Emotion Pulse page (and as a scroll-tell scene). Each archetype = a character a reader can identify with: *"I'm an [archetype] poster, [archetype] commenter."* Click any card → URL changes to `/explore/emotion-pulse#<archetype-slug>`, custom OG card per archetype.

6. **Quotable lines per page.** Each chart page surfaces one screenshot-friendly line in a designed pull-quote block (oversized typography, signed "MindSpace OS"). Designed for the Twitter quote-tweet workflow. Drafted candidates:
   - Emotion Pulse: *"Joy ranks 25th of 28. Amusement is last."*
   - Community Dynamics: *"Grief gets mirrored. Anxiety gets reassurance."*
   - Community Weather Report: *"Eighteen months of community mood, drawn as weather."*
   - Inner Life Currents: *"The conversation drifts. Watch it."*

7. **About / methodology page.** Re-purpose the methodology notes from both essays. Disclose limitations honestly (sample bias of self-selected Reddit posters, GoEmotions trained on Reddit so somewhat circular, anonymization approach). Earns trust with press.

8. **Cross-link both essays from the landing page.** Right under the hero. *"Read the deeper writing →"* with two cards linking to the published Substack posts. The site is the *interactive* surface; the essays are the *narrative* surface; they should explicitly point at each other.

9. **Data count: canonical = 2,899.** *Resolved 2026-04-25.* All site surfaces use **2,899** as the post-and-comment count. Update README's "2,977" to match. Document the prior pre-filter number in `CLAUDE.md` for reference. Single canonical value lives in `mindspace-os/data/canonical.json`, imported by both Python (Streamlit) and JS/TS (Astro shell + OG generator).

10. **Bias notation as inline footnote, not hero disclaimer.** *Resolved 2026-04-25.* The GoEmotions-trained-on-Reddit issue is acknowledged in a small methodology callout BELOW each chart (not above hero, not as a banner), with a link to the About/methodology page. ~2 sentences, framed as "what this analysis can and can't tell you," cites the GoEmotions paper. Honest, not defensive.

11. **Citations to add (per UC5 resolution).** Every methodology surface (per-page footnote, About page, HuggingFace dataset card, Substack essays going forward) cites:
    - **GoEmotions** — Demszky, D., Movshovitz-Attias, D., Ko, J., Cowen, A., Nemade, G., & Ravi, S. (2020). *GoEmotions: A Dataset of Fine-Grained Emotions.* Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics. arXiv:2005.00547. HuggingFace: [google-research-datasets/go_emotions](https://huggingface.co/datasets/google-research-datasets/go_emotions).
    - **UMAP** — McInnes, L., Healy, J., & Melville, J. (2018). *UMAP: Uniform Manifold Approximation and Projection for Dimension Reduction.* arXiv:1802.03426.
    - **MindSpace OS dataset (this project)** — once published on HuggingFace in week 5, becomes self-citable with a stable DOI.

### 4D. Distribution

**Problem:** The site exists. The launch automation exists in `drafts/`. But there's no evidence of a coordinated launch that reached general-interest readers. "Build it and they will come" is not a distribution strategy.

**Reframe:** This is NOT a first launch. Two essays are already published (Apr 21, Apr 24, 2026). There is a warmed Substack audience. The "launch" we're planning is a **v2 relaunch / consolidation moment** — new domain, new shell, new design — anchored on a third capstone essay that ties the project together.

**Direction:**
1. **Pre-launch warm-up (2 weeks).** Repost the strongest single-finding artifacts from the two existing essays as standalone Twitter/LinkedIn images. Each artifact = one quotable line + one chart preview. Goal: re-warm the audience and signal "something new is coming." Drafted artifacts:
   - *"Joy ranks 25th of 28."* + Emotion Pulse preview
   - *"7 of 10 posters post exactly once."* + community-structure callout
   - *"25% mirror grief. Only 7% mirror anxiety."* + Community Dynamics preview
   - *"The vocabulary that dominates is 'I'm trying again.'"* + thesis card
2. **Launch day cascade** (anchored on a NEW capstone Substack essay that introduces the redesigned site).
   - 8am ET: Capstone Substack post goes live (cross-references the two earlier essays as "the findings"; this post is the "the project, finished")
   - 9am ET: Show HN submission ("Show HN: I mapped what r/meditation actually sounds like — joy ranks 25th of 28")
   - 10am ET: Twitter/X thread (posted manually — automation in `drafts/` is dropped from scope)
   - 11am ET: LinkedIn post
   - 12pm ET: r/dataisbeautiful submission
   - 2pm ET: r/meditation submission (with mod permission, framed as "research about this community")
   - 3pm ET: Hacker News if HN traction works; otherwise wait 24h and try a different angle
3. **Press outreach (1 week before launch).** Personal emails to:
   - Vox (Sigal Samuel — covers psychology/mindfulness)
   - The Atlantic (data desk, plus Derek Thompson)
   - The Pudding (data viz publication — natural fit)
   - Information Is Beautiful Awards (submit when entry window opens)
   - Stratechery / The Diff (data-savvy newsletter readers)
   - Mindful.org (mainstream meditation pub — obvious fit)
4. **Researcher blurb.** Reach out to 3–5 academic researchers in mindfulness or computational social science (e.g. Cushman, Gunaratana scholars, Reddit data folks). Get one quote that says "this matters" — gold for press.
5. **Newsletter cross-promotion.** Already on Substack. Find 5 mindfulness/data-adjacent Substacks to cross-promote with.
6. **Artifact strategy.** Pre-render one shareable image per chart (1200×675, dark mode, with thesis tagline). Each image stands alone as a tweet. Schedule them as a drip campaign for the post-launch month.
7. **Permanent home.** "About this project" page documenting methodology, data source, ethical considerations (Reddit data is public but still sensitive). Earns trust with press.

---

### 4E. Research & Partner (added 2026-04-25)

**Problem:** Niche-first audience means HCI researchers, computational social scientists, meditation clinicians, and data-viz practitioners don't read Substack first — they read papers, datasets, and conference talks. The plan needs distribution surfaces native to that audience.

**Direction:**
1. **Publish the dataset on HuggingFace.** 2,899-post processed corpus (with the precomputed parquet artifacts already built — `emotion_clusters.parquet`, `main_topics.parquet`, etc.) under a permissive CC license. Dataset card cites GoEmotions (Demszky et al. 2020), UMAP (McInnes et al. 2018), and the project site. Stable DOI via Zenodo integration → permanent academic citation surface.
2. **Methodology note as a separate artifact.** Short (4-6 page) writeup of pipeline + caveats + GoEmotions-bias acknowledgment, formatted for arXiv submission OR posted as a permanent page at `/methodology` with a download link. Not a full peer-reviewed paper — a citable artifact.
3. **Conference lightning-talk submissions** as windows open: ICWSM, CSCW, Information+. 5-minute talk → recording with 2-year tail.
4. **Mindfulness-app research-team outreach.** Personal email to research leads at Waking Up, Calm, Ten Percent Happier, Headspace. They have research budgets and citation appetites. One newsletter mention from any of them = bigger reach than 5 cold press pitches.
5. **Data Visualization Society + Observable / Nightingale.** Submit to DVS member showcase. Pitch a Nightingale piece. Submit to Observable's gallery if format fits. These communities cite each other.
6. **No paid ads in v1.** Re-evaluate post-launch.

## 5. Sequencing — what ships when

| Week | Track | Output |
|---|---|---|
| 0 (now) | Eng | Pull Substack analytics from both essays (baseline); cleanup `~/.playwright-profiles/`. (No Plausible — Cloudflare Web Analytics replaces it, set up in week 1 after domain registration.) |
| 1 | Eng | mindspaceos.com registered (Cloudflare Registrar); DNS active with DNSSEC + null MX + SPF + DMARC `p=reject`; **Cloudflare Web Analytics enabled** (free); Astro scaffold (`@astrojs/cloudflare` adapter + Tailwind); `mindspace-os/data/canonical.json` created (archetypes + counts: 2,899 canonical); `essays.mindspaceos.com` Substack custom domain mapped |
| 1 | Design | Typography locked (Inter Display H1, Source Serif body, Inter UI, JetBrains Mono labels); dark palette locked (ground `#0B0E13` etc.); cluster colors brightened for dark ground |
| 2 | Eng | Landing page (Astro): typographic hero (no chart), thesis H1, quotable line, anchor essay cards, page card grid, footer with methodology + data license + GitHub. Sentence case throughout. |
| 2 | Story | Editorial intros for all 4 chart pages (1 paragraph + 1 designed callout each, 80–120 words); inline bias notation as a footnote-style callout BELOW each chart (not above hero), referencing GoEmotions paper |
| 3 | Eng | `scripts/build_screenshots.py` (Playwright → 4 chart PNGs at 1600×1200 WebP, single source of truth for both scrolltell + OG cards); 5 static OG cards generated; Satori-via-Worker stub wired (deferred dynamic OG); iframe embedding with static-screenshot-first loading pattern (postMessage height calc) |
| 3 | Eng | Sentry installed (free tier); UptimeRobot 4 monitors; Cloudflare Web Analytics as Plausible backup |
| 3 | Eng | Test suite: smoke (`tests/test_pages_smoke.py`), canonical sync (`tests/test_canonical.py`), OG presence (`astro/tests/og.spec.ts`), Lighthouse CI gate (≥85 mobile, ≥90 desktop), redirect chain test, axe-core accessibility |
| 4 | Story | Capstone Substack draft (the third essay, anchored on niche-research framing); archetype card grid using **existing** archetype names (no renaming) |
| 4 | Story | `docs/data-provenance.md` (collection date, ToS posture, paraphrase policy, takedown email) |
| 4 | Story | Bias notation: short inline disclosure (footnote style, ~2 sentences) on each chart page methodology callout, citing GoEmotions paper (Demszky et al. 2020, arXiv:2005.00547) |
| 5 | Distribution | **HuggingFace dataset publication** — 2,899-post processed corpus published with DOI, README citing GoEmotions + linking to project site; arXiv-style methodology note |
| 5 | Distribution | Niche outreach (HCI/CSS researchers, meditation clinicians, data-viz practitioners); ICWSM/CSCW lightning-talk submission if windows open; mindfulness-app research-team outreach (Waking Up, Calm) |
| 5 | Distribution | Pre-launch warm-up posts week 1 of 2 (drip on Twitter/LinkedIn from existing essay quotes) |
| 6 | Eng | `staging.mindspaceos.com` cert/DNS dry run; TTL drop to 300s 24h before launch; final QA all surfaces; `docs/launch-runbook.md` (rollback commands, DNS/Cloudflare access) |
| 6 | Distribution | Pre-launch warm-up week 2; capstone Substack post finalized |
| 6 | Launch day | Decoupled cascade (NOT one-day): Capstone Substack Tuesday → HN Wednesday peak window → r/dataisbeautiful + r/meditation Thursday (mod approval pre-secured) → Twitter as 4-week drip not launch-day post → LinkedIn researcher-targeted post on launch day. **No paid promotion in v1** (re-evaluate post-launch). |
| 7+ | Distribution | Press follow-ups; HuggingFace download counter watch; researcher inbound triage; metrics review at +30 days |

Total: ~6 weeks evening/weekend after the week-0 instrumentation pass.

---

## 6. NOT in scope (explicitly deferred)

- **No new data analysis or research.** No new charts, no new clusters, no extending the date range, no control-subreddit comparison run. Bias acknowledged inline via methodology footnote citing GoEmotions paper.
- **No mobile chart interactivity.** Mobile = responsive shell + static screenshots. Re-evaluate v1.1 based on Plausible data.
- **No paid ads in v1.** Re-evaluate post-launch.
- **No native app, no PWA.**
- **No user accounts, no email capture beyond the existing Substack.**
- **No A/B testing.** One opinionated direction, ship it.
- **No SEO content marketing strategy.** SEO comes from being good and being shared, not from keyword pages.
- **No multi-language.** English only.
- **No archetype renaming.** Use existing names from `pages/0_Emotion_Pulse.py` `ARCHETYPE_COLORS`.

---

## 6.5 Engineering additions (auto-decided per autoplan reviews 2026-04-25)

These were not in the v0 plan but were universally flagged across reviews. All approved as auto-decided unless overridden:

1. **`mindspace-os/data/canonical.json`** — single source of truth for archetype names + colors + post counts (2,899 canonical, 2,977 pre-filter). Python (Streamlit) and JS/TS (Astro shell + OG generator) both import from it. CI test asserts no inline duplicates.
2. **Sentry** (free 5k errors/mo) — JS error tracking on Astro shell, capture iframe `error` events.
3. **UptimeRobot** (free, 50 monitors, 5-min interval) — `mindspaceos.com`, `mindspaceos.streamlit.app/Emotion_Pulse`, `cloudflareinsights.com` (synthetic). Email + SMS on 2 consecutive failures.
4. **DNS hardening day 1.** SPF (`v=spf1 -all`), DMARC (`v=DMARC1; p=reject; rua=mailto:minyanshi@proton.me`), null MX (`0 .` per RFC 7505), DNSSEC enabled in Cloudflare.
5. **iframe loading state spec.** `scripts/build_screenshots.py` (Playwright → 1600×1200 WebP per chart). Static screenshot loads first; "Tap to interact" overlay swaps to live iframe on click. Streamlit page emits `postMessage({type:'height', value: scrollHeight})`, parent Astro shell sets iframe height. Same screenshots feed OG cards (one source).
6. **Test suite (minimal but real).** `tests/test_canonical.py` (single-source-of-truth sync), `tests/test_pages_smoke.py` (Streamlit imports), `astro/tests/og.spec.ts` (every route has matching OG), `astro/tests/redirects.spec.ts`, Lighthouse CI gate (≥85 mobile, ≥90 desktop), axe-core accessibility. GitHub Actions runs all on PR.
7. **`docs/data-provenance.md`** — collection date, ToS posture, paraphrase-vs-verbatim policy, takedown contact (`takedown@mindspaceos.com` → forward to inbox). Earns press/researcher credibility.
8. **`docs/launch-runbook.md`** — DNS rollback commands, Cloudflare API token location, Streamlit Cloud access, Plausible dashboard URL, social account credentials reference.
9. ~~Cloudflare Web Analytics as Plausible backup~~ — *promoted to primary analytics; see section 4B item 4.*
10. **`sitemap.xml` + `robots.txt` + Schema.org JSON-LD** (`@type: Dataset` for the chart pages).
11. **Audit `precomputed/emotion_clusters_slim.parquet` `hover_text` column** — confirm no traceable verbatim quotes; paraphrase or anonymize if needed.
12. **Cleanup:** `rm -rf ~/.playwright-profiles/{substack-*,twitter}` (orphaned credentials from dropped automation).
13. **`staging.mindspaceos.com`** as cert/DNS dry run in week 4 (preview deploy on Cloudflare Pages).

## 7. What already exists (don't rebuild)

- Editorial naming and design intent (`CLAUDE.md`) — keep, extend
- Precomputed parquet/Plotly JSON pattern — keep, extend to remaining pages
- ~~Substack + Twitter posting automation in `drafts/`~~ — **DROPPED from engineering scope** per user decision. The Playwright-based automation is a maintenance burden that doesn't pay off for a manual launch. Posts will be published manually on launch day (copy/paste from finalized markdown). The `drafts/` folder stays in the repo for reference but no further engineering investment.
- The 4 chart pages — keep functionally, freshen visually only inside iframes
- `proposed_plans.md` — already has subtitle candidates and per-chart decluttering ideas; merge into intro block work

---

## 8. Open decisions (the things this plan can't pre-answer)

1. **Astro vs Next.js for the shell.** RESOLVED: **Astro** with `@astrojs/cloudflare` adapter + Tailwind CSS. Static OG cards in v1 (`public/og/*.png`). Satori-via-Worker stub wired in week 1 so future dynamic-OG migration is a config flip, not a framework rewrite. *Resolved 2026-04-25.*
2. **Chart library: stay on Plotly.** *Resolved 2026-04-25.* All 4 charts remain in Plotly for v1. Reasons: (a) the iframe loads Plotly only AFTER user clicks "Tap to interact" on the static screenshot — bundle size doesn't penalize LCP; (b) Sankey for Community Dynamics is native to Plotly, would need `d3-sankey` glue in Observable Plot; (c) Plotly's `kaleido` exporter feeds the static-screenshot pipeline that ALSO feeds OG cards and scrolltell visuals — single source of truth; (d) migration cost is ~2 weeks solo, overlapping the riskiest week in the timeline. v1.1 trigger for migrating a specific chart: a design direction blocks on Plotly's defaults AND Plausible/CF data shows that chart drives ≥40% of engagement. Don't migrate all 4 at once; migrate one when forced.
3. **Custom domain name.** RESOLVED: **`mindspaceos.com`**. Confirmed available via WHOIS check. Registering on **Cloudflare Registrar** (~$10.44/year, at-cost, no markup, integrates with Cloudflare Pages hosting). Backup if any issue: Porkbun (~$11/year, no DNS lock-in).
4. **Mobile interactivity for charts.** RESOLVED: **NO for v1.** Mobile responsive shell only (Tailwind breakpoints in Astro); chart pages on mobile show static screenshot + "View interactive on desktop" CTA. Re-evaluate post-launch with Plausible data. *Resolved 2026-04-25 after all 3 reviews flagged it as scope-overrun. Inner Life Currents slider sub-decision moot.*
5. **Long-form platform: stay on Substack + custom subdomain.** *Resolved 2026-04-25.* Two essays already published, audience partially warmed, native discovery (Substack reader cross-recommendations) is a moat. Mirror (web3-native crowd) wrong audience. Custom blog adds CMS + email infra + paywall + comments maintenance — not worth it for v1. **Add `essays.mindspaceos.com` Substack custom domain** ($50 one-time) for brand cohesion. Cross-link both ways: main site → Substack, Substack footer → main site.
6. **Methodology limitations: 3-tier disclosure (notation, not banner).** *Resolved 2026-04-25.* Explicit, but never as hero/banner.
   - **Tier 1 — Inline footnote per chart** (12-13px, tertiary text, below chart): ~2 sentences citing GoEmotions paper + linking to /about#methodology.
   - **Tier 2 — About/methodology page** (`/about#methodology`, ~600 words): explicit on sample bias (self-selecting Reddit posters, not "all meditators"), self-selection (posters ≠ lurkers), GoEmotions circularity (trained on Reddit, applied to Reddit), 18-month time window limits, English-only, anonymization approach (paraphrase-vs-verbatim policy), takedown contact.
   - **Tier 3 — HuggingFace dataset card** (week 5): full academic-grade limitations section using HF's standard template (intended use, out-of-scope use, biases, ethics).

---

## 9. Risks

- **Time blow-out.** 6 weeks evening/weekend is optimistic. Launch could slip to 8–10 weeks. Risk-mitigate by shipping the Astro shell + landing in week 2 so even a slipped launch has a real artifact.
- **Streamlit cold start in iframe.** If the iframe spinner is too painful, users bounce before reaching the chart. Mitigation: first-paint placeholder (high-quality static screenshot) that swaps to live iframe when loaded.
- **HN/Reddit might not bite.** The thesis is sharp but the topic (meditation) doesn't always land on HN. Mitigation: angle the HN submission around the data/analysis side (UMAP, GoEmotions), not the meditation side.
- **Press doesn't respond.** Press response rate to cold pitches is single digits. Mitigation: warm intros where possible; lead with the researcher blurb; have the long-form essay as a finished artifact, not a pitch.
- **The thesis turns out to be controversial.** Saying "meditation isn't peaceful" might trigger pushback from the meditation community. Mitigation: lead with curiosity, not provocation. The framing is "look what people *actually* talk about," not "meditation doesn't work."
- **Mobile chart UX is a known-hard problem.** Plotly on small viewports has tooltip overflow, tap-vs-hover ambiguity, and pinch-zoom conflicts with page scroll. Iframe charts have the same issues plus iframe-height calculation. Mitigation: real-device QA gate before launch (not emulator-only); accept that the temporal network on Inner Life Currents may need a fundamentally different mobile representation (e.g., quarter-by-quarter swipe through static frames) rather than the desktop slider.
- **Mobile path drift.** The previous mobile pass was reverted because "the cost of maintaining two render paths wasn't justified by the mobile traffic the site was actually getting" (per `CLAUDE.md`). If we re-introduce mobile and traffic still doesn't materialize, we've taken on permanent maintenance debt. Mitigation: instrument mobile traffic from week 1 via Plausible; commit to keeping the mobile path only if mobile share ≥ 30% post-launch; otherwise plan a clean revert with documented rationale.
- **Legal / ethical pushback.** Reddit data is public but using it for a public project invites scrutiny. Mitigation: methodology page is honest about source, anonymizes specifics, doesn't surface specific quotes that could be traced back to individual users (or only with explicit permission).

---

## 10. Definition of done

This plan is "done" when:
- A reader on a phone can land on the homepage in <3 seconds and understand the thesis in <30 seconds
- A first-time desktop reader can finish the scroll-tell tour and explore one chart in <5 minutes
- The site has a domain that fits in a tweet and an OG card that makes someone click
- A general-interest outlet has either covered the project or scheduled coverage
- Analytics confirms 25k+ unique visitors in first 30 days

Anything short of all five above = ship a follow-up pass.
