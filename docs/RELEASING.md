# Releasing

This document defines the versioning policy and the manual, human-gated process
for publishing a release of `generational-marketing-review`. Nothing here is
automated: tags and GitHub releases are created only by an authorized human.

## Versioning policy

The project uses [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.
Release tags use the form `vMAJOR.MINOR.PATCH` (for example `v0.1.0`).

The first planned public release is `v0.1.0`. This documentation does not create
it.

- **`0.x` releases are pre-1.0.** The public contract is still stabilizing, and
  a `0.MINOR` bump may include meaningful interface or guidance changes.
- **Minor releases** (`0.x.0`, and after 1.0 `X.MINOR.0`) may add workflows,
  references, templates, evaluation scenarios, or guidance, and may change the
  review contract in a documented way.
- **Patch releases** (`X.Y.PATCH`) are reserved for backward-compatible
  corrections: documentation fixes, validation improvements, and packaging
  fixes that do not change the review contract.
- **`1.0.0`** should be cut only when the public contract is considered stable
  and after an intentional compatibility review.

Two clarifications specific to this repository:

- The evaluation fixtures under `evals/` are repository evidence. They are **not**
  shipped inside the `.skill` package (the package ships only the ten allowlisted
  files: `SKILL.md`, `LICENSE`, `NOTICE.md`, the five `references/` files, and
  the two `assets/` templates).
- Changing an evaluation's frozen artifacts (`input.md`, `assertions.yaml`,
  `grader-prompt.md`, the model outputs, `grader-output.json`, or
  `run-metadata.json`) is **not** a patch-level documentation edit. Frozen
  artifacts are cryptographically bound, and any change must follow the
  evaluation-integrity process (re-freeze the assertions, regenerate the grader
  prompts, rerun both blind graders, and recompute all bindings), not a casual
  edit.

`SKILL.md` intentionally carries no version field: the current validator and
packaging contract neither require nor consume one. The release version lives in
the git tag, this changelog, and the GitHub release, not in the skill frontmatter.

## Release principles

- Releases originate from a clean, synchronized `main`.
- All tests, validators, evaluations, and package checks must pass before a
  release.
- A release must never alter frozen evaluation artifacts merely to improve
  results.
- The generated `dist/generational-marketing-review.skill` file is a release
  asset. It is generated on demand and remains untracked (`dist/` is
  git-ignored).
- Tags and GitHub releases require explicit human authorization.
- Releases must be performed as the `andrewluxem` GitHub account.

## Version selection

- **Patch (`X.Y.Z+1`)**: backward-compatible documentation, validation, or
  packaging corrections only. No change to the review contract or the shipped
  guidance semantics.
- **Minor (`X.Y+1.0`)**: new workflow, reference, template, or evaluation
  scenario, or a documented change to the review contract or guidance.
- **Major (`X+1.0.0`)**: a breaking change to the public contract, cut only
  after an intentional compatibility review. Reserved for `1.0.0` and later.
- **Pre-1.0 minor (`0.Y+1.0`)**: while the project is pre-1.0, a `0.MINOR` bump
  is the normal vehicle for both additive and contract-affecting changes; there
  is no compatibility guarantee across `0.x` minors.

The planned first public release is `v0.1.0`. This document does not create it.

## Pre-release gate

Run from a clean checkout and confirm every check passes before tagging.

```bash
git switch main
git fetch origin --prune
git pull --ff-only origin main

git status --short
git rev-parse HEAD
git rev-parse origin/main

python3 -m unittest discover -s tests -v
python3 scripts/validate_structure.py
python3 scripts/scan_public_claims.py
python3 scripts/validate_eval.py
python3 scripts/build_skill.py
git diff --check
```

Require:

- the working tree is clean;
- local `main` equals `origin/main`;
- all checks pass;
- zero required evaluation failures;
- every advisory warning is reviewed and documented (the known advisory warnings
  are recorded in the pull request and changelog history, not silenced);
- the deterministic package SHA-256 printed by `build_skill.py` is captured and
  recorded for the release notes.

## Changelog preparation

1. Move the relevant entries from `## [Unreleased]` in `CHANGELOG.md` to a new
   versioned heading, for example `## [0.1.0] - YYYY-MM-DD`.
2. Use the actual release date in `YYYY-MM-DD` form.
3. Leave a fresh, empty `## [Unreleased]` section above the versioned heading.
4. Review the wording for unsupported claims (no invented dates, download counts,
   performance claims, user counts, endorsements, or adoption claims).
5. Merge the changelog update into `main` through a normal pull request **before**
   tagging, so the tag points at a commit whose changelog already describes the
   release.

## Tag procedure

Create an annotated tag on the verified `main` commit.

```bash
git tag -a vX.Y.Z -m "generational-marketing-review vX.Y.Z"
git show --no-patch --decorate vX.Y.Z
git push origin vX.Y.Z
```

The tagged commit must equal the intended verified `main` commit (confirm with
`git rev-parse vX.Y.Z^{commit}` against `git rev-parse origin/main`). Do not
execute these commands as part of release-preparation documentation; they belong
to a separately authorized release task.

## GitHub release procedure

Build the package from the tagged commit, inspect it, then create the release.

```bash
gh release create vX.Y.Z \
  dist/generational-marketing-review.skill \
  --title "generational-marketing-review vX.Y.Z" \
  --notes-file <RELEASE_NOTES_FILE>
```

Require:

- the release notes are derived from the changelog entry for this version;
- the `.skill` asset is attached;
- the package SHA-256 captured during the pre-release gate is included in the
  release notes;
- the package contents are inspected before upload
  (`unzip -Z1 dist/generational-marketing-review.skill` should list exactly the
  ten allowlisted files);
- the asset contains no repository-only evaluation, grader, test, script, README,
  contact, or local-path content;
- the release is created as a **draft** (add `--draft`) whenever a final human
  review is still required before it goes public.

Do not run `gh release create` as part of release-preparation documentation.

## Post-release verification

After publishing, verify:

- the tag target matches the intended `main` commit;
- the GitHub release URL resolves and shows the correct version;
- the `.skill` asset is attached;
- the downloaded asset SHA-256 matches the SHA captured during the pre-release
  gate;
- the packaged file list is exactly the ten allowlisted files;
- `main` is clean and synchronized with `origin/main`;
- no repository file was changed as a side effect of the release.

## Rollback and correction

- Never silently move or overwrite a published tag. A published tag is immutable
  in practice; consumers may already depend on it.
- Correct a released mistake with a new patch release (`X.Y.Z+1`), not by
  editing history.
- An unpublished **draft** release may be deleted and recreated before it is
  published.
- Treat a published artifact-integrity issue (for example a package that shipped
  unintended content) as a security and release incident: document it, publish a
  corrected release, and note the correction in the changelog.
- Preserve prior release records. Do not delete published releases or tags to
  hide a mistake; supersede them.
