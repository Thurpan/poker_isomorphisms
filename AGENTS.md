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

## Validation

Run the complete test suite after a source change:

```console
python -m unittest discover -s tests -v
```

Build the package after a packaging or metadata change:

```console
python -m pip wheel --no-deps --wheel-dir dist .
```

## Generated artefacts

Do not commit `build`, `dist`, `*.egg-info`, `__pycache__`, or coverage output.
Generate release artefacts from a clean source checkout.
