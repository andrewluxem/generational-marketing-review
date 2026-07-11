# Generational Marketing Review

A portable, vendor-neutral Agent Skill for reviewing marketing plans and assets through a specified generational audience lens.

It helps answer:

> Is this plan or asset likely to work for the specified generation, why, what is weak or unsupported, and what should change or be tested?

## What it reviews

- campaign and channel plans;
- email, landing pages, product pages, social posts, video, display, SMS, and direct mail;
- creator and influencer briefs;
- offers, checkout, returns, delivery, loyalty, and customer experience;
- audience claims, evidence quality, stereotypes, and freshness;
- cross-generation adaptation.

## What it does not do

- treat generation as a deterministic persona;
- invent current platform statistics;
- present unsupported birth ranges or percentages as facts;
- replace customer research or first-party testing;
- provide discriminatory targeting guidance;
- redistribute third-party source screenshots.

## Repository structure

```text
SKILL.md
references/
assets/
evals/
scripts/
.github/workflows/
```

`SKILL.md` is the router. Detailed methods live in `references/`, and report templates live in `assets/`.

## Installation

Prefer project-local installation or manual copying into the skill directory supported by your client.

Generic approach:

1. Clone or download this repository.
2. Copy the repository folder into your agent's project-local or user-selected skills directory.
3. Ask the agent to use the `generational-marketing-review` skill.

Avoid unreviewed `curl | bash` installers, automatic updates, and installers that write outside the directory you selected.

## Example prompts

- Review this paid-social plan for Gen Z. Separate evidence from assumptions and give me the five highest-impact changes.
- Assess this email and landing page for Gen X. Include trust, value, delivery, returns, and accessibility.
- Compare this campaign for Millennials and Xennials. Tell me what can remain common and what should be adapted.
- Review these three assets for the specified audience and create a prioritized test plan.

## Packaging

Run:

```bash
python scripts/validate_structure.py
python scripts/scan_public_claims.py
python scripts/build_skill.py
```

The build script creates a deterministic `.skill` archive from an explicit allowlist.

## License

Apache-2.0. See `LICENSE`.

Third-party screenshots and source materials used during private planning are not included and are not licensed by this repository.

## Built by Andrew Luxem

CRM architect and lifecycle marketer. 20+ years building retention systems, behavioral automation, and customer engagement programs at Amazon, Ancestry, Stanley Black & Decker, Overstock.com, Bed Bath & Beyond, and Big Dill Pickleball Co., with applied engagement architecture for commerce, sports, and entertainment organizations.

[LinkedIn](https://www.linkedin.com/in/andrewluxem) · [andrew@andrewluxem.com](mailto:andrew@andrewluxem.com)

This is an independent personal project. It is not affiliated with, sponsored by, or endorsed by any current or former employer, and it contains no proprietary employer material.
