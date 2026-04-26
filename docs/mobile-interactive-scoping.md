# Mobile-Interactive Scoping (deferred to day-30 gate)

**Status:** SCOPING ONLY. Not approved for implementation.
**Trigger:** the v1 plan (`docs/upgrade-plan.md` §4A.6, §4B.7) committed to
re-evaluating mobile chart interactivity at +30 days post-launch, gated on
Cloudflare Web Analytics data.
**Re-eval gate criteria (from upgrade-plan.md):**
- Mobile share ≥ 30% of sessions over rolling 14-day window
- Engagement rate ≥ 40% on mobile over the same window
- 30 days minimum since launch

**Launch date:** 2026-04-26.
**Earliest gate-eval date:** 2026-05-26.
**Today:** 2026-04-27 (day 2 of 30).

This doc captures the question and premises now while context is fresh, so
when the gate fires (or doesn't), the team can autoplan implementation
without re-deriving the question.

---

## 1. Problem statement (one sentence)

Should the four chart pages render their charts as interactive Plotly
visualizations on mobile (with hover-equivalent tap interactions, touch
filters, and the Time Travel slider), or stay on the v1 static-screenshot
+ "view interactive on desktop" CTA path?

## 2. The desired user outcome

A mobile reader who lands on `/explore/emotion-pulse/` from a Twitter
share can:
- See the chart (currently: yes, as a static image)
- Tap a point or region to see what's behind it (currently: no — must
  switch to desktop)
- Filter by quarter, archetype, or emotion without leaving the page
  (currently: no)
- Read the editorial copy around the chart (currently: yes)
- Share back to social with the right OG card (currently: yes)

The gap is the middle two. Whether closing that gap is worth the
engineering cost depends on whether mobile readers actually arrive,
linger, and drop off at the "view on desktop" CTA — which is exactly
what the day-30 Plausible/CF Analytics signal will show.

## 3. What changed since UC2 was locked (THE BIG ONE)

This is the most important update vs the original cost calculation.

UC2 (the original "cut mobile interactivity" decision) was made on
2026-04-25 with the following cost assumptions:

| UC2 cost assumption                          | Still true? |
|----------------------------------------------|-------------|
| 4 chart pages × 2 render paths (iframe vs PNG) | **NO** — single render path now |
| Streamlit iframe height sizing battle (postMessage) | **NO** — no Streamlit at runtime |
| Streamlit cold-start hibernation (10-30s)    | **NO** — static HTML, instant |
| Streamlit chrome leakage (sidebar, footer)   | **NO** — gone |
| 16 visual permutations to QA per chart change | Cut roughly in half |
| Plotly tap-to-pin tooltips                   | Still a real cost |
| Pinch-zoom-vs-page-scroll handling           | Still a real cost |
| Tooltip overflow clamping at narrow viewport | Still a real cost |
| Real-device QA matrix (iOS Safari + Android) | Still a real cost |
| Mobile-specific Lighthouse perf tuning       | Still a real cost |
| Plotly.js bundle weight on mobile (~900KB)   | **NEW concern** — was paid by Streamlit before, now ours |

**Net delta:** roughly half of UC2's "this is too expensive" argument is
no longer true. The static-HTML migration deleted the iframe orchestration
cost. The remaining costs are touch-UI specific, not architecture-specific.

Concretely: Plotly.js running natively in our static chart HTMLs handles
touch events out of the box. Tap shows tooltip. Pinch zoom works on plotly
scatter charts (Emotion Pulse). The Time Travel slider in Inner Life
Currents is already JS-driven, no iframe involved. The Sankey in
Community Dynamics is touch-clickable already.

The grep above shows each chart file already references touch/pointer/hover
events (4-28 occurrences each). Plotly's defaults already cover the basics.

**The honest current state:** mobile already kind of works for the chart
HTMLs. What we're hiding behind the "view on desktop" CTA is partially a
choice, not a technical block.

## 4. Premises to challenge at the gate

When day-30 Plausible/CF data arrives, these are the premises the
implementation autoplan must re-examine:

**P1.** Mobile share is meaningful (≥30%).
*If false:* keep v1 static-CTA. Don't pay the touch-UI cost for <30% of
sessions.

**P2.** Mobile engagement is real (≥40%).
*If false:* mobile readers bounce regardless. The CTA isn't the bottleneck.

**P3.** The "view on desktop" CTA is converting badly.
*Measure:* clicks on the CTA / mobile sessions on chart pages. If <5%,
the CTA is dead weight; mobile readers aren't using it. Either replace
with interactive or remove the CTA and let the static screenshot stand.

**P4.** Plotly.js bundle weight is acceptable on mobile.
*Currently:* Emotion Pulse chart HTML is 1.5MB (the chart data is mostly
the bulk; Plotly.js itself is CDN-cached). Lighthouse mobile perf currently
≥85 on chart pages with iframe pattern. Re-test after enabling
interactivity.

**P5.** Touch UI doesn't degrade desktop.
*Risk:* adding touch handlers can break desktop hover. Need parallel
desktop QA, not assume "mobile additions are mobile-only."

**P6.** The implementation cost is now bounded.
*Original UC2 estimate:* 8-10 weeks slip if mobile-interactive included.
*Revised estimate (post-static-migration):* the iframe-orchestration
costs are gone. Remaining costs are per-page touch-UI tuning. Probably
1-2 weeks CC time, not 6-8.

## 5. Alternatives at the gate (what implementation autoplan would compare)

Order by ambition, low to high:

**A. Selective enable.**
Pick the 2 highest-mobile-traffic chart pages (probably Emotion Pulse
and Community Dynamics — the share-friendliest). Enable native Plotly
touch on those only. Leave Inner Life Currents and Community Weather
Report on static-CTA. Lowest risk, highest ROI on the chart pages
people actually arrive at via social.

**B. Full enable, single render path.**
Drop the static-screenshot fallback entirely. Charts render interactive
on every viewport. One render path, one source of truth. Simpler to
maintain. Slight bundle weight cost on mobile.

**C. Full enable, progressive enhancement.**
Static screenshot loads first (LCP boost), tap to interact swaps in
the live chart. The CTA stays but becomes "tap to interact" instead
of "view on desktop." Best perceived performance but two render paths
return.

**D. Defer further.**
If day-30 data shows mobile share <30% or engagement <40%, defer
again to day-60.

## 6. Forcing questions for day-30

When the gate fires, the autoplan needs hard answers to:

1. **Who is the mobile reader?** Niche-research audience (HCI, CSCW
   researchers) was specced as desktop-first. If mobile traffic is
   actually general-public Twitter shares, the audience target itself
   is shifting.
2. **Which chart page draws mobile?** If 80% of mobile traffic lands
   on Emotion Pulse via OG card, only that page needs touch UI.
3. **What's the CTA conversion rate?** Sub-5% means the CTA is dead.
   Sub-15% means readers don't have desktops nearby. Above 30% means
   the CTA works fine, leave it alone.
4. **What's the engagement delta vs desktop?** If mobile sessions are
   60-80s and desktop sessions are 240s+, mobile readers are sampling,
   not exploring. Touch UI won't change that.
5. **Real-device QA matrix size.** iOS Safari, Android Chrome, both
   orientations, four chart pages = 16 permutations. Acceptable cost
   given the static migration deleted the other 16.
6. **Bundle weight budget.** Emotion Pulse HTML is already 1.5MB. Adding
   touch interaction is +0KB (Plotly.js handles it). Adding a touch UI
   layer (custom tap-to-pin, slider styling) is +20-50KB JS. Mobile
   3G LCP budget?

## 7. NOT in scope for this scoping doc

- Implementation. We're at day 2 of 30.
- Picking option A/B/C/D. Wait for the data.
- Designing the touch UI for any specific chart.
- Bundling/perf optimization.

## 8. NOT in scope for the day-30 autoplan (when it fires)

- Re-litigating the static-vs-Streamlit migration. That's locked.
- Mobile chrome / responsive layout. That's already shipped.
- Adding mobile chart features that don't exist on desktop. Parity first.

## 9. Trigger conditions to autoplan implementation

Run autoplan when ANY of:

- 30 days post-launch AND P1+P2 both ≥ thresholds
- An external event forces the question earlier (press hit, viral share,
  partner asks "where's mobile")
- Plausible / CF Analytics shows mobile share ≥ 50% earlier than 30 days
  (override the time gate; data wins)

Otherwise: hold. The original gate stands.

---

## Saved for day-30

This doc lives at `docs/mobile-interactive-scoping.md`. When the gate
fires, run:

```
/autoplan implementation of mobile-interactive (read docs/mobile-interactive-scoping.md and Cloudflare Analytics for the 14-day window)
```

That input is enough for the autoplan pipeline to skip the scoping
phase and go straight to architecture/design/eng review of the
selected option.
