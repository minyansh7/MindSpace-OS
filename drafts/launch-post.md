# MindSpace OS — Launch Drafts

Launch copy for Substack + X/Twitter, ready to paste or drive via Playwright.

---

## Substack Post

**Publish URL:** https://minyansh.substack.com/publish/post?type=newsletter

### Title
What 48,000 Reddit Meditators Actually Sound Like

### Subtitle
I built MindSpace OS to map the emotional shape of r/meditation. The center of gravity isn't peace — it's struggle.

### Body

Most meditation content online is prescriptive: *here's how to sit, here's how to breathe, here's what you should feel.*

I wanted to see the opposite. What do people actually say, unprompted, when they talk to each other about meditation?

So I pulled **48,000+ posts from r/meditation** (Jan 2024 – Jun 2025), ran them through emotion classification and UMAP clustering, and built **MindSpace OS** — six interactive views of that archive.

**What's inside:**

- **Emotion Pulse** — a UMAP map where posts cluster by emotional vocabulary. Frustration sits in one region, awe in another; the in-between is where it gets interesting.
- **Meditation Weather Report** — sentiment trends rendered as weather (sunny days, storms) across topics over 18 months.
- **Theme Pathways** — a Sankey diagram of how broad themes branch into specific discussions.
- **Narrative Trees** — filterable co-occurrence trees, sliced by quarter.
- **Theme Web** — the full static co-occurrence network.
- **Theme Currents** — how those connections *shift* over time.

**The finding that surprised me:** the dominant emotional register in r/meditation isn't peace. It's *struggle*, tightly coupled with *curiosity*. The community's shared vocabulary is closer to "trying again" than "finding bliss."

That's not a failure mode. That's what a practice community actually sounds like when nobody's selling anything.

---

**Built with:** Python · Streamlit · Plotly · DuckDB · UMAP · GoEmotions. Mobile-optimized (which was its own meditation practice).

Live: *[deployment URL]*
Code: https://github.com/minyansh7/mindfulness-space-l0

— Min · MinyanLabs © 2026

---

## Twitter / X Posts

**Compose URL:** https://x.com/compose/post

### Option A — The finding

```
Built MindSpace OS: 48k r/meditation posts → 6 interactive maps.

Turns out the dominant emotion isn't peace. It's struggle + curiosity.

That's what a practice community sounds like when no one's selling anything.

→ [link]
```

### Option B — Quiet

```
MindSpace OS is live.

A visual field guide to 48k Reddit meditation posts — what people actually say, not what gurus tell them to say.

Go wander: [link]
```

### Option C — Thread opener

```
I scraped 48,000 r/meditation posts and built 6 interactive views of what I found.

MindSpace OS is live.

The dominant emotion isn't what you'd expect. 🧵
```

**Follow-up tweets for the thread (if using C):**

```
Emotion Pulse: UMAP map of those 48k posts, clustered by emotional vocabulary.

Frustration in one region. Awe in another. The neighborhoods between are where the real practice lives.
```

```
Meditation Weather Report: 18 months of sentiment trends, rendered as weather.

Sunny days. Storms. A lot of overcast.
```

```
The surprise: peace isn't the dominant emotional register in r/meditation.

Struggle + curiosity is.

A practice community sounds like people trying again, not people arriving.
```

```
Built with Python · Streamlit · Plotly · DuckDB · UMAP · GoEmotions. Mobile-optimized last week.

Wander: [link]
Code: github.com/minyansh7/mindfulness-space-l0
```
