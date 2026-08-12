# Repository guidance

## Project purpose

This package normalises three-card poker flops under global suit permutations.
It also enumerates every equivalent card-string representation.

## Design invariants

- A flop contains exactly three distinct cards.
- A suit isomorphism applies one bijection to every card.
- A suit isomorphism never changes a rank.
- Card order does not affect a flop's normal form.
- Default valid-input results must remain deterministic.
- The 22,100 legal flops must produce exactly 1,755 normal forms.
- The physical isomorphism class contains 4, 12, or 24 unordered boards.
- The package has no runtime dependencies.

## Validation

Run the complete test suite after a source change:

```console
python -m unittest discover -s tests -v
```

Install release-validation tools before packaging work:

```console
python -m pip install build twine
```

Build and validate both distribution formats:

```console
python -m build
python -m twine check dist/*
```

Validate Markdown after a documentation change:

```console
npx --yes markdownlint-cli2 README.md AGENTS.md CHANGELOG.md
```

## Generated artefacts

Do not commit `build`, `dist`, `*.egg-info`, `__pycache__`, or coverage output.
Generate release artefacts from a clean source checkout.
Publish only the `python-distributions` artefact from the successful CI run for
the release commit. Do not rebuild validated distributions before publication.
Do not publish to PyPI from automated validation or without explicit approval.
