---
name: generational-marketing-review
description: Review marketing plans and assets for fit with a specified generational audience while separating evidence from assumptions and avoiding stereotypes.
license: Apache-2.0
compatibility: Works with Agent Skills-compatible clients, including Claude Code, Cursor, Gemini CLI, ChatGPT, Codex, and similar agents. No external network access is required.
---

# Generational Marketing Review

## Purpose

Review a marketing plan, campaign, customer experience, or marketing asset for fit with a user-specified generational audience.

Produce a practical answer to:

> Is this likely to work for the specified audience, why, what is weak or unsupported, and what should change or be tested?

Use generation as one audience lens. Do not treat a cohort label as a complete persona or as proof of behavior.

## Use this skill when the user asks to

- review a marketing plan for Gen Z, Zillennials, Millennials, Xennials, Gen X, or another age-defined cohort;
- assess whether creative, copy, offers, channels, or customer experience fit a generation;
- compare one campaign across generations;
- adapt an asset for a different generation;
- identify stereotypes, dated assumptions, or unsupported audience claims;
- create a generation-fit scorecard and test plan.

## Required context

Use the information supplied by the user. Before issuing a definitive verdict, identify whether the following are known:

- target cohort and birth-year or life-stage definition;
- geography and language;
- product or service category;
- customer state or journey stage;
- campaign objective;
- channel and placement;
- asset format;
- offer, price, delivery, returns, and fulfillment constraints;
- brand voice and accessibility requirements;
- source of audience claims;
- success metric.

Do not invent missing information. When context is incomplete, make the smallest reasonable assumption, label it, and reduce confidence.

## Choose a workflow

### Quick scan

Use when the user wants a fast opinion.

Read:

- `references/review-rubric.md`
- `references/evidence-and-safety.md`

Return:

- verdict;
- three strengths;
- three risks;
- three priority changes;
- confidence and missing evidence.

### Full marketing-plan review

Use for campaign plans, briefs, channel plans, launch plans, or lifecycle plans.

Read:

- `references/plan-review.md`
- `references/review-rubric.md`
- `references/generation-lenses.md`
- `references/evidence-and-safety.md`

Use:

- `assets/review-report-template.md`
- `assets/evidence-register-template.md`

### Marketing-asset review

Use for copy, email, landing pages, product pages, images, video, creator briefs, ads, SMS, push, direct mail, or social posts.

Read:

- `references/asset-review.md`
- `references/review-rubric.md`
- `references/generation-lenses.md`
- `references/evidence-and-safety.md`

Use:

- `assets/review-report-template.md`

### Cross-generation comparison

Review the same plan or asset separately through each requested lens. Then identify:

- shared strengths;
- shared weaknesses;
- conflicting needs;
- what can remain common;
- what should be adapted;
- what requires testing rather than assumption.

## Governing principles

1. **Generation is a lens, not a verdict.**
2. **Behavior, customer state, category, geography, and context can matter more than age.**
3. **Separate fact, observation, inference, assumption, recommendation, and unknown.**
4. **Do not present uncited percentages, platform rankings, posting times, or birth ranges as current facts.**
5. **Do not repeat stereotypes merely because they appeared in source material.**
6. **Translate broad claims into testable hypotheses.**
7. **Do not recommend deceptive, discriminatory, inaccessible, privacy-invasive, or noncompliant marketing.**
8. **A serious legal, privacy, accessibility, trust, or evidence problem can override a high average score.**
9. **Preserve “insufficient evidence” as a valid outcome.**
10. **Prefer specific revisions and experiments over vague advice.**

## Review method

1. Identify the requested audience definition.
2. Identify the objective, customer state, channel, format, and conversion action.
3. Extract every explicit audience claim.
4. Classify each claim as provided fact, observation, inference, assumption, recommendation, or unknown.
5. Review the plan or asset against the rubric.
6. Apply the relevant generation lens as a hypothesis set, not a stereotype set.
7. Identify critical risks and contradictions.
8. Prioritize changes by impact and effort.
9. Propose measurable tests.
10. Return a clear verdict and confidence level.

## Output contract

For a full review, include:

1. **Verdict**
   - Strong fit
   - Promising but needs revision
   - Weak fit
   - Insufficient evidence

2. **Confidence**
   - High
   - Medium
   - Low

3. **Audience-definition check**

4. **Scorecard**
   - dimension;
   - score from 0 to 4;
   - evidence;
   - concern;
   - recommended action.

5. **What works**

6. **What may fail**

7. **Stereotype, evidence, and freshness flags**

8. **Priority fixes**
   - critical;
   - high;
   - medium.

9. **Test plan**
   - hypothesis;
   - variant;
   - primary metric;
   - guardrail;
   - decision rule.

10. **Final recommendation**
    - proceed;
    - revise and retest;
    - gather more evidence;
    - do not proceed.

## Scoring

Use the 0–4 scale defined in `references/review-rubric.md`.

Do not convert the total into a precise probability of success. Use the scorecard to structure judgment, not to create false certainty.

## Public-safe behavior

Do not expose private source material, internal company names, personal data, third-party screenshots, or confidential metrics. Do not copy source language when an independent, neutral formulation is possible.
