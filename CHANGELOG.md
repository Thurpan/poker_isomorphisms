# Changelog

This file records notable changes to the project.

## Unreleased

### Maintenance

- Made the Python version matrix test the installed package.
- Added independent regression checks for public signatures and result order.
- Corrected documentation links in the Python Package Index description.
- Required future releases to publish the exact distributions validated by CI.

## 1.0.0 - 2026-07-31

### Added

- Added unique physical-flop enumeration with `flop_isomorphism_class`.
- Added direct comparison with `flops_are_isomorphic`.
- Added batch normalisation with British and American spellings.
- Added the complete 1,755-form catalogue with `all_flop_normal_forms`.
- Added distributable type information and an exposed package version.
- Added continuous integration for Python 3.10 through 3.14.
- Added wheel and source-distribution validation without automatic publishing.

### Changed

- Declared the documented public API stable at version 1.0.0.
- Replaced legacy packaging with `pyproject.toml` metadata.
- Reworked normalisation around explicit suit permutations.
- Expanded input validation, tests, documentation, and repository guidance.

### Removed

- Removed committed build output, bytecode, package metadata, and old archives.

### Compatibility

- Preserved `flop_normalise`, `flop_normalize`, and `flop_isomorphisms`.
- Preserved valid-input results and default deterministic ordering.
