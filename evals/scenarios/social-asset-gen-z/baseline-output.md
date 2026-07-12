# Loopwell Sling Carousel — Review

## Bottom line

As written, this campaign is **unlikely to hit its stated goal (first purchases from new customers) — and, just as important, it is built so you won't be able to tell whether it did.** Almost every structural decision optimizes for reach and views, not purchases, and the two places where a cold buyer actually converts — the destination and the checkout — are the two most broken parts of the funnel. There are also real compliance landmines (targeting minors, an unsupported sustainability claim, missing creator disclosure).

There's a good product and a genuinely strong demo card in here. But the plan spends its energy on vibe and vanity metrics and neglects the mechanics of getting a first-time buyer from "scrolling" to "paid."

Below, grouped by impact.

---

## 1. The funnel leaks where it matters most (highest priority)

These three items will suppress purchases regardless of how good the creative is:

- **Destination is the homepage, not a Sling page.** Cold prospects who tap "Shop now" land on a general homepage and have to *find* the product themselves. For a one-product brand running a one-product ad, this is an unforced error. **Send traffic to a dedicated Sling product/landing page** that mirrors the ad (same product, offer, and risk-reducers above the fold).
- **Forced account creation before first purchase, no guest checkout.** Requiring email + password from a first-time, cold, mobile buyer on a $34 impulse-adjacent product is one of the most reliable ways to kill conversion. **Add guest checkout.** Collect the email at/after purchase, not as a gate.
- **The measurement plan measures the wrong thing.** The objective is first purchases; the "success metrics" are impressions, reach, and 3-second video views. You will almost certainly generate impressions and views and declare victory while learning nothing about whether anyone bought. Saves/shares as secondary don't fix this.

On measurement specifically, the gaps are severe for a paid-acquisition campaign:
- **Purchases aren't the primary metric.** Make completed first purchase the headline number.
- **No CAC / ROAS / contribution margin.** At $34 with 15% off, free shipping, *and* free two-way returns, your margin per unit is thin and your downside on returns is real. You need unit economics or you can't know if this is profitable acquisition or expensive noise.
- **No return-/refund-rate tracking**, despite a 30-day no-questions policy — the single biggest threat to the economics of a low-price physical product.
- **No holdout / incrementality design.** You can't distinguish incremental purchases from ones that would've happened anyway. At minimum consider a geo holdout or ghost-ads style test.
- **No repeat/retention measure**, so you can't tell if these buyers are worth acquiring.

---

## 2. Targeting is off-brief and partly non-compliant

- **The ad set is 13–65+, not 18–29.** This directly violates two explicit constraints: the audience is *adults 18–29*, and there must be *no targeting directed at minors*. The 13–17 slice is a compliance/ethics problem; the 30–65+ slice is wasted spend on a Gen-Z acquisition test. **Set 18–29 and exclude under-18.** This is not a "test it" item — fix it before launch.
- **"Target all Gen Z, we don't want to over-narrow" contradicts the objective.** Broad targeting suits awareness, not cold conversion of a specific product. Let the platform optimize toward the purchase event within 18–29 rather than deliberately widening.
- **"Nearly all Gen Z discover products through Instagram, so Instagram alone is enough" is an unsupported assumption**, presented as fact with no data or test. It may be fine to *start* on IG, but don't treat single-channel as proven. This is a claim to validate, not to build a plan on.

---

## 3. The creative buries the job-to-be-done and leads with vibe

For **cold** traffic, the first card has to answer "what is this and why do I care?" in a second. This carousel front-loads mood and back-loads substance.

- **Card 1 (Hook) is all vibe, no product.** "the most authentic bottle strap on your FYP fr" plus a wall of slang tells a first-time viewer almost nothing about what the Sling *does*. "Most authentic" is also an unsupportable superlative that means nothing.
- **Card 3 is your best asset and it's buried third.** The clip literally shows clip-on → sling crossbody → drop phone/key in pocket. That *is* the value proposition. **Lead with this** (or with a clear "carry your bottle hands-free" statement), and let vibe support it, not replace it.
- **Card 2 (Options) creates decision friction before comprehension.** You're asking people to "pick your fit" before they understand the product. Consider moving option choice onto the landing page, or at least after the demo.
- **Card 4 (Details) hides the decision-relevant info in the least readable place.** The actual purchase drivers — $34, 15% off, free shipping, ships in 2 days, 30-day no-questions returns with prepaid label — are strong for cold traffic, but they're crammed as dense, light-on-light overlay text over a busy festival photo. **These risk-reducers should be surfaced earlier, larger, and legibly** — ideally split across cards and repeated on the CTA card. Also, hashtags don't belong baked into overlay image text.
- **Card 5 (Sustainability + CTA) pivots away from the value prop at the moment of the ask** and stakes the close on an unsupported green claim (see compliance below). The CTA card should reinforce the core benefit + offer + risk-reversal, not introduce a new, weaker theme.

**On the "authenticity" bet itself:** the strategy treats "Gen Z is obsessed with authenticity" as settled fact and then executes in ways that read as the opposite of authentic — a superlative "most authentic" claim, heavy slang cosplay ("delulu," "periodt," "cop," "no cap," "it's giving"), and six creators told to post *identical brand-written copy*. Nothing signals "brand trying too hard" faster than a wall of trend slang and cloned captions. Use slang sparingly and let the product demo and the honest offer carry the authenticity. Slang also dates fast; some of this may read as stale by the time it's live.

---

## 4. Compliance / truthful-advertising risks

- **Unsupported environmental claim (Card 5 + caption).** "sustainable by design," "ditch single-use — the planet will thank you" with *no* material, recycled-content, lifecycle, durability, or certification support. Under FTC Green Guides, unqualified environmental benefit claims need substantiation. **Either substantiate with specifics or cut the sustainability framing.**
- **False scarcity.** "before they're gone" / "tap shop now before they sell out" implies limited stock. If it isn't actually limited, that's a deceptive urgency claim. Drop it or make it true.
- **Missing paid-partnership disclosure.** The creator plan doesn't specify FTC disclosure. Every seeded creator post needs a clear, conspicuous disclosure (e.g., paid-partnership label + #ad). This is required, not optional.
- **Targeting minors** (see §2) — also a compliance issue, not just a waste one.

---

## 5. Accessibility (a stated requirement, currently unmet)

The plan requires accessibility and then provides none of it:

- **No alt text on any card** — add descriptive alt text for all five.
- **No captions/transcript for the Card 3 video** — feed video autoplays muted, so an uncaptioned demo loses much of its value even for sighted users. Add burned-in or platform captions + a transcript.
- **Color-only meaning on Card 2** — the recommended/best-value option is signaled *only* by a green ring (fails WCAG "use of color"). Add a text label or badge ("Best value / Most popular") that doesn't depend on color.
- **Card 4 contrast + density** — light-on-light text over a busy image at small mobile sizes is unreadable for many. Set contrast minimums, cap overlay text, and put dense details on the landing page instead.

---

## 6. Creator / UGC strategy

- **Selecting on follower count (250k+) + grid aesthetic only is a weak basis** for a conversion campaign. No vetting for audience fit, engagement quality, comment sentiment, or brand-values alignment means you may buy reach with little purchase intent behind it.
- **Audience-age skew is unvetted** — a large-following creator may skew heavily to minors, which collides with your no-minors constraint. Vet audience age composition explicitly.
- **Identical reused copy across six creators** undercuts the authenticity bet and can trigger user/platform backlash. Give creators the product, the offer, and the disclosure requirement, and let them speak in their own voice.

---

## What to change before launch (non-negotiable)

1. **Age → 18–29, exclude minors.**
2. **Destination → dedicated Sling landing page**, not homepage.
3. **Add guest checkout.**
4. **Make purchase the primary metric; add CAC/ROAS/contribution margin and return-rate tracking.**
5. **Add FTC paid-partnership disclosure to all creator posts.**
6. **Substantiate or remove the sustainability claim; remove false scarcity.**
7. **Add accessibility basics:** alt text, video captions/transcript, non-color signal on Card 2, fix Card 4 contrast/density.

## What to test (after the fixes)

- **Hook A/B:** demo/clarity-led (current Card 3 logic) vs. vibe-led (current Card 1).
- **Copy register:** heavy slang vs. plainer, benefit-led — measured on purchases, not saves.
- **Card order:** demo-first vs. current order.
- **Offer emphasis:** which risk-reducer moves conversion most (free returns vs. free shipping vs. 15% off) — surface the winner earlier.
- **Age bands within 18–29**, and — before committing to Instagram-only — a small test to validate the single-channel assumption rather than asserting it.

---

**Net:** keep the product demo and the honest offer; they're the real strengths. Fix the funnel (destination, checkout), the targeting, the compliance items, and the measurement so the campaign actually pursues — and can prove — first purchases. Right now it's engineered to generate views and slang, not sales, and to leave you unable to tell the difference.
