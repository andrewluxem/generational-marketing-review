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

## Worked evaluation examples

The `evals/scenarios/` directory holds five worked, inspectable evaluations you can read directly in this repository. Each scenario captures one review end to end: a frozen `input.md`, a `baseline-output.md` produced without the skill and a `skill-output.md` produced with it, the `assertions.yaml` checked against that output, the `grader-output.json` results, and a `run-metadata.json` recording how the run was produced.

- [`media-plan-millennials`](evals/scenarios/media-plan-millennials/): full media-plan review.
- [`email-gen-x`](evals/scenarios/email-gen-x/): lifecycle-email asset review.
- [`social-asset-gen-z`](evals/scenarios/social-asset-gen-z/): paid-social creative review, with safety and accessibility considerations.
- [`cross-generation-adults-25-54`](evals/scenarios/cross-generation-adults-25-54/): broad-age-band review of what can stay shared versus what should be adapted.
- [`insufficient-evidence`](evals/scenarios/insufficient-evidence/): Quick scan showing when the reviewer should withhold a fit judgment.

These fixtures are repository evidence only. They are deliberately excluded from the `.skill` package, which ships only the ten allowlisted files; see [`docs/RELEASING.md`](docs/RELEASING.md).

Across the current suite the recorded verdicts include `Promising but needs revision`, `Weak fit`, and `Insufficient evidence`. The suite does not yet include a `Strong fit` positive-control scenario; that gap is recorded under Deferred in [`CHANGELOG.md`](CHANGELOG.md).

## Packaging

Run:

```bash
python scripts/validate_structure.py
python scripts/scan_public_claims.py
python scripts/build_skill.py
```

The build script creates a deterministic `.skill` archive from an explicit allowlist.

## Versioning and releases

This project is **pre-1.0**. It follows [Semantic Versioning](https://semver.org/), with release tags of the form `vMAJOR.MINOR.PATCH`. The planned first public release is `v0.1.0`. No public release has been tagged yet.

- Changelog: [`CHANGELOG.md`](CHANGELOG.md)
- Versioning policy and release process: [`docs/RELEASING.md`](docs/RELEASING.md)

Reproduce the build and validation locally:

```bash
python3 scripts/validate_structure.py
python3 scripts/scan_public_claims.py
python3 -m unittest discover -s tests
python3 scripts/validate_eval.py
python3 scripts/build_skill.py
```

The `.skill` archive is written to `dist/`, which is generated and untracked (git-ignored). The intended distributable is the `.skill` asset attached to a GitHub release, not the entire repository checkout: the repository also holds evaluation fixtures, scripts, and tests that are deliberately excluded from the package.

## License

Apache-2.0. See `LICENSE`.

Third-party screenshots and source materials used during private planning are not included and are not licensed by this repository.

## Built by Andrew Luxem

CRM architect and lifecycle marketer. 20+ years building retention systems, behavioral automation, and customer engagement programs at Amazon, Ancestry, Stanley Black & Decker, Overstock.com, Bed Bath & Beyond, and Big Dill Pickleball Co., with applied engagement architecture for commerce, sports, and entertainment organizations.

[LinkedIn](https://www.linkedin.com/in/andrewluxem) · [andrew@andrewluxem.com](mailto:andrew@andrewluxem.com)

This is an independent personal project. It is not affiliated with, sponsored by, or endorsed by any current or former employer, and it contains no proprietary employer material.
