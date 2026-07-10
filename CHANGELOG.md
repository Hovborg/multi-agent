# Changelog

All notable changes to this project are documented in this file.

## Unreleased

### Added

- Strict catalog schema, slug, duplicate-name, ambiguity, and cross-reference validation.
- `multiagent validate` for local and CI catalog verification.
- Additive route `policy` output with control mode, bounded delegation, delegation contracts,
  trust boundaries, approval requirements, and stop conditions.
- Routing-eval policy expectations and `--min-policy-score`.
- Distribution and isolated-installation tests for the complete packaged catalog.
- Least-privilege, SHA-pinned GitHub Actions with artifact smoke testing.

### Fixed

- Include all agent and enhancement YAML files in wheels and source distributions.
- Resolve seven invalid `works_with` references in bundled agent definitions.
- Return non-zero status for invalid agent names instead of printing an error and succeeding.
- Load prompt enhancements from the installed package instead of a source-checkout path.
- Correct README examples that implied framework-neutral patterns execute models directly.

### Changed

- The authoritative catalog source moved from `catalog/` to
  `src/multiagent/catalog_data/` so editable and installed behavior are identical.
- Route JSON remains backward compatible and gains an additive `policy` object.
