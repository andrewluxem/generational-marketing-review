# Changelog

All notable changes to this project will be documented in this file.

The project follows Semantic Versioning. Release tags use the form `vMAJOR.MINOR.PATCH`.

## [Unreleased]

## [0.1.0] - 2026-07-13

### Added

- Public generational marketing review skill (`SKILL.md`) that reviews marketing
  plans and assets for fit with a specified generational audience while
  separating evidence from assumptions and avoiding stereotypes.
- Four supported review workflows: quick scan, full marketing-plan review,
  marketing-asset review, and cross-generation comparison.
- Evidence, stereotype, accessibility, privacy, trust, and nondiscrimination
  safeguards, expressed as governing principles and reference guidance.
- Deterministic `.skill` package build from an explicit ten-file allowlist.
- Public-content and repository-structure validation
  (`scripts/scan_public_claims.py`, `scripts/validate_structure.py`).
- GitHub Actions validation that runs the tests, validators, evaluation checks,
  and packaging on every push and pull request.
- Reusable review-report and evidence-register templates under `assets/`.
- Five inspectable baseline-versus-skill evaluation scenarios under
  `evals/scenarios/`:
  - `media-plan-millennials`;
  - `email-gen-x`;
  - `social-asset-gen-z`;
  - `cross-generation-adults-25-54`;
  - `insufficient-evidence`.
- Cryptographic binding of each evaluation's artifacts and grader prompts, so a
  recorded grader result cannot be silently reused against a changed input,
  output, assertion set, or grader prompt.
- Explicit support for `Insufficient evidence` as a valid review verdict, with a
  dedicated thin-brief control scenario that verifies the skill withholds a fit
  judgment rather than inventing missing context.

### Deferred

- Cursor-, ChatGPT-, and Gemini-specific adapters or installation wrappers are
  intentionally deferred until after `v0.1.0`. The first release ships the
  canonical `.skill` package and the documented repository workflow.
- A `Strong fit` positive-control evaluation is intentionally deferred until
  after `v0.1.0`. The existing five-scenario suite validates problem detection,
  revision guidance, safety behavior, cross-generation reasoning, and the
  `Insufficient evidence` verdict, but does not yet include a favorable-fit
  control.

[Unreleased]: https://github.com/andrewluxem/generational-marketing-review/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/andrewluxem/generational-marketing-review/releases/tag/v0.1.0
