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
- Enumerate the complete suit-isomorphism class.
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
from poker_isomorphisms import flop_isomorphisms, flop_normalise

normal = flop_normalise("7cQc3s")
print(normal)
# Qs7s3h

equivalent_flops = flop_isomorphisms("Ac 8d 3d")
print(equivalent_flops[:3])
# ['As 8h 3h', 'As 3h 8h', '8h As 3h']
```

The American spelling `flop_normalize` is an alias of `flop_normalise`.

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

Build a wheel in the ignored `dist` directory:

```console
python -m pip wheel --no-deps --wheel-dir dist .
```

The tests compare representative flops with an independent suit-permutation
implementation. They also verify that all 22,100 legal flops produce exactly
1,755 normal forms.

## Licence

This project uses the [MIT Licence](LICENSE).

## Author

Euan McNicholas ([Thurpan on GitHub](https://github.com/Thurpan))
