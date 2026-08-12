# poker-isomorphisms

`poker-isomorphisms` normalises three-card poker flops and enumerates their
suit-isomorphic representations.

Two flops are suit-isomorphic when one global renaming of the four suits turns
one flop into the other. Ranks do not change, and card order does not matter.
For example, `Kh9s3h` and `Kd9c3d` are isomorphic under the mapping `h -> d`
and `s -> c`.

A 52-card deck has 22,100 distinct unordered flops. Grouping those flops by
suit isomorphism produces 1,755 classes.

## Features

- Produce one deterministic normal form for any legal flop.
- Enumerate unique physical flops or every ordered string representation.
- Compare two flops directly for suit isomorphism.
- Normalise batches and list all 1,755 canonical flops.
- Accept compact notation such as `AsKhQd`.
- Accept separated notation such as `As Kh Qd`.
- Customise rank and suit ordering without changing poker semantics.
- Reject malformed cards and impossible flops with clear errors.
- Use only the Python standard library at runtime.

## Requirements

Use Python 3.10 or later.

## Installation

Install the package from the Python Package Index (PyPI):

```console
python -m pip install poker-isomorphisms
```

## Quick start

```python
from poker_isomorphisms import (
    flop_isomorphism_class,
    flop_normalise,
    flops_are_isomorphic,
)

normal = flop_normalise("7cQc3s")
print(normal)
# Qs7s3h

physical_flops = flop_isomorphism_class("Ac 8d 3d")
print(len(physical_flops))
# 12

print(flops_are_isomorphic("Kh9s3h", "Kd9c3d"))
# True
```

The package exposes its installed version as `poker_isomorphisms.__version__`.

## Card notation

Each card has a one-character rank followed by a one-character suit.

- Ranks: `A`, `K`, `Q`, `J`, `T`, `9`, `8`, `7`, `6`, `5`, `4`, `3`, `2`
- Suits: `s`, `h`, `d`, `c`

Notation is case-sensitive. A flop must contain exactly three distinct cards.
Use either compact notation or separate all three cards with whitespace. Spaces
and tabs are both accepted as separators.

Valid inputs include:

```text
AsKhQd
As Kh Qd
```

Invalid inputs include duplicate cards, partial separators, unknown ranks,
unknown suits, or text after the third card.

## API

### `flop_normalise`

```python
flop_normalise(
    flop,
    with_spaces=None,
    suits_order="shdc",
    rank_order="AKQJT98765432",
)
```

Return the deterministic representative of the flop's isomorphism class. The
default rank order is descending. The default suit preference is spades,
hearts, diamonds, then clubs.

When `with_spaces` is `None`, the result preserves whether the input used
separators. Set it to `True` or `False` to select the output format explicitly.

```python
flop_normalise("Ac 8d 3d")
# 'As 8h 3h'

flop_normalise("Ac 8d 3d", with_spaces=False)
# 'As8h3h'
```

### `flop_isomorphisms`

```python
flop_isomorphisms(
    flop,
    with_spaces=None,
    suits_order="shdc",
    rank_order="AKQJT98765432",
)
```

Return every distinct string obtained through a global suit permutation and a
permutation of the three card positions. The function returns a deterministic
list and removes duplicates caused by board symmetry.

The result contains 24, 72, or 144 strings, depending on the flop's rank and
suit symmetries. These totals include card-order permutations. The physical
flop itself remains unordered.

This function retains its original ordered-string behaviour for compatibility.
Use `flop_isomorphism_class` when card-order permutations are not required.

### `flop_isomorphism_class`

```python
flop_isomorphism_class(
    flop,
    with_spaces=None,
    suits_order="shdc",
    rank_order="AKQJT98765432",
)
```

Return each unique physical flop in the isomorphism class once. Cards in each
result use canonical rank and suit order. The result contains 4, 12, or 24
boards, depending on the flop's symmetries.

```python
flop_isomorphism_class("AsKhQd")[:3]
# ['AsKhQd', 'AsKhQc', 'AsKdQh']
```

### `flops_are_isomorphic`

```python
flops_are_isomorphic(
    flop_a,
    flop_b,
    *,
    suits_order="shdc",
    rank_order="AKQJT98765432",
)
```

Return `True` when the two flops differ only by a global suit permutation and
card ordering. Input spacing does not affect the comparison. Invalid inputs
raise the same clear errors as the normalisation functions, prefixed with
`flop_a` or `flop_b`.

### `normalise_flops`

```python
normalise_flops(
    flops,
    *,
    with_spaces=False,
    suits_order="shdc",
    rank_order="AKQJT98765432",
)
```

Normalise any non-string iterable of flops. The result preserves input order
and duplicates. Compact output is the default so mixed input styles produce a
uniform result. Pass `with_spaces=None` to preserve each input's style.

The function stops at the first invalid item. Its error starts with the item's
zero-based position, such as `flops[2]`. The American spelling
`normalize_flops` is an alias.

```python
normalise_flops(["7cQc3s", "Ac 8d 3d", "7cQc3s"])
# ['Qs7s3h', 'As8h3h', 'Qs7s3h']
```

### `all_flop_normal_forms`

```python
all_flop_normal_forms(
    *,
    with_spaces=False,
    suits_order="shdc",
    rank_order="AKQJT98765432",
)
```

Return all 1,755 canonical representatives in deterministic order. Every call
returns a fresh list. The package caches internal immutable catalogues for
reuse.

```python
normal_forms = all_flop_normal_forms()
len(normal_forms)
# 1755
```

### Custom ordering

Pass each standard rank or suit exactly once. A custom order affects the normal
form and result ordering. It does not change which flops are isomorphic.

```python
flop_normalise("7cQc3s", suits_order="cdhs")
# 'Qc7c3d'

flop_normalise("7cQc3s", rank_order="23456789TJQKA")
# '3s7hQh'
```

## How normalisation works

The normaliser applies every bijection of the four suits. It sorts the cards
under the requested rank and suit order for each bijection. It then selects the
first candidate under that same ordering.

This definition handles monotone, two-tone, rainbow, paired, and three-of-a-kind
flops without separate special cases.

## Scope

The package handles three-card community flops only. It does not compare hole
cards, turn cards, river cards, betting ranges, or game trees.

## Compatibility

Version 1 establishes the documented public API. Compatible 1.x releases can
add functionality, but they will preserve existing public signatures, default
behaviour, and valid-input result ordering. A necessary breaking change will
require a new major version.

The American spelling `flop_normalize` remains an alias of `flop_normalise`.
See the
[changelog](https://github.com/Thurpan/poker_isomorphisms/blob/main/CHANGELOG.md)
for release details.

For broader background, see the explanations from
[GTO Wizard](https://gtowizard.com/glossary/isomorphic/) and
[PioSOLVER](https://piosolver.com/blog/2015-11-05-flop-subsets/).

## Development

Install the repository in editable mode:

```console
python -m pip install -e .
```

Run the test suite:

```console
python -m unittest discover -s tests -v
```

Install the release-validation tools:

```console
python -m pip install build twine
```

Build and validate the wheel and source distribution:

```console
python -m build
python -m twine check dist/*
```

The tests compare representative flops with an independent suit-permutation
implementation. They also verify that all 22,100 legal flops produce exactly
1,755 normal forms. GitHub Actions tests the installed package on Python 3.10
through 3.14. It also builds, validates, and uploads candidate release
artefacts. Publish only the `python-distributions` artefact from the successful
run for the release commit. Do not rebuild the distributions after validation.
GitHub Actions does not publish to PyPI.

## Licence

This project uses the
[MIT Licence](https://github.com/Thurpan/poker_isomorphisms/blob/main/LICENSE).

## Author

Euan McNicholas ([Thurpan on GitHub](https://github.com/Thurpan))
