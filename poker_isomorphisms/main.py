"""Utilities for identifying suit-isomorphic poker flops."""

from collections.abc import Sequence
from itertools import permutations

_RANKS = tuple("AKQJT98765432")
_SUITS = tuple("shdc")


def _validate_order(
    order: Sequence[str], expected_values: tuple[str, ...], name: str
) -> tuple[str, ...]:
    """Return a validated rank or suit order."""
    if not isinstance(order, Sequence):
        raise TypeError(f"{name} must be a sequence")

    values = tuple(order)
    contains_single_characters = all(
        isinstance(value, str) and len(value) == 1 for value in values
    )
    if (
        len(values) != len(expected_values)
        or not contains_single_characters
        or set(values) != set(expected_values)
    ):
        required_values = "".join(expected_values)
        raise ValueError(
            f"{name} must contain each character in {required_values!r} exactly once"
        )

    return values


def _parse_flop(
    flop: str, rank_order: tuple[str, ...], suits_order: tuple[str, ...]
) -> tuple[tuple[str, str, str], bool]:
    """Parse and validate a compact or whitespace-separated flop."""
    if not isinstance(flop, str):
        raise TypeError("flop must be a string")

    tokens = flop.split()
    if len(tokens) == 1 and len(tokens[0]) == 6:
        compact_flop = tokens[0]
        input_has_spaces = False
    elif len(tokens) == 3 and all(len(token) == 2 for token in tokens):
        compact_flop = "".join(tokens)
        input_has_spaces = True
    else:
        raise ValueError(
            "flop must contain exactly three cards in 'AsKhQd' or "
            "'As Kh Qd' format"
        )

    cards = (
        compact_flop[0:2],
        compact_flop[2:4],
        compact_flop[4:6],
    )
    valid_ranks = set(rank_order)
    valid_suits = set(suits_order)
    invalid_card = next(
        (
            card
            for card in cards
            if card[0] not in valid_ranks or card[1] not in valid_suits
        ),
        None,
    )
    if invalid_card is not None:
        raise ValueError(
            f"flop contains invalid card {invalid_card!r}; use ranks "
            f"{''.join(_RANKS)!r} and suits {''.join(_SUITS)!r}"
        )

    if len(set(cards)) != 3:
        raise ValueError("flop must contain three distinct cards")

    return cards, input_has_spaces


def _get_separator(with_spaces: bool | None, input_has_spaces: bool) -> str:
    """Select the requested output separator."""
    if with_spaces is None:
        return " " if input_has_spaces else ""
    if type(with_spaces) is not bool:
        raise TypeError("with_spaces must be True, False, or None")
    return " " if with_spaces else ""


def _normalise_cards(
    cards: tuple[str, str, str],
    rank_order: tuple[str, ...],
    suits_order: tuple[str, ...],
) -> tuple[str, str, str]:
    """Find the first sorted representative across all suit renamings."""
    card_positions = {
        rank + suit: position
        for position, (rank, suit) in enumerate(
            (rank, suit) for rank in rank_order for suit in suits_order
        )
    }

    candidates = []
    for renamed_suits in permutations(suits_order):
        suit_mapping = dict(zip(suits_order, renamed_suits))
        renamed_cards = tuple(
            sorted(
                (card[0] + suit_mapping[card[1]] for card in cards),
                key=card_positions.__getitem__,
            )
        )
        candidates.append(renamed_cards)

    return min(
        candidates,
        key=lambda candidate: tuple(card_positions[card] for card in candidate),
    )


def flop_isomorphisms(
    flop: str,
    with_spaces: bool | None = None,
    suits_order: Sequence[str] = _SUITS,
    rank_order: Sequence[str] = _RANKS,
) -> list[str]:
    """Return every ordered representation in a flop's suit-isomorphism class.

    A result can differ from the input by a global permutation of the four suits
    and by the order of its three cards. Duplicate strings are removed.

    Args:
        flop: Three distinct cards in compact or whitespace-separated notation.
        with_spaces: Add spaces, remove spaces, or preserve the input style with
            ``None``.
        suits_order: A permutation of ``shdc`` used to order results.
        rank_order: A permutation of ``AKQJT98765432`` used to order results.

    Returns:
        The isomorphic flop strings in deterministic order.

    Raises:
        TypeError: An argument has the wrong type.
        ValueError: The flop or an ordering argument is invalid.
    """
    validated_suits = _validate_order(suits_order, _SUITS, "suits_order")
    validated_ranks = _validate_order(rank_order, _RANKS, "rank_order")
    cards, input_has_spaces = _parse_flop(
        flop, validated_ranks, validated_suits
    )
    separator = _get_separator(with_spaces, input_has_spaces)
    normalised_cards = _normalise_cards(
        cards, validated_ranks, validated_suits
    )
    used_suits = tuple(dict.fromkeys(card[1] for card in normalised_cards))

    results = []
    seen_results = set()
    for target_suits in permutations(validated_suits, len(used_suits)):
        suit_mapping = dict(zip(used_suits, target_suits))
        renamed_cards = tuple(
            card[0] + suit_mapping[card[1]] for card in normalised_cards
        )
        for ordered_cards in permutations(renamed_cards):
            result = separator.join(ordered_cards)
            if result not in seen_results:
                results.append(result)
                seen_results.add(result)

    return results


def flop_normalise(
    flop: str,
    with_spaces: bool | None = None,
    suits_order: Sequence[str] = _SUITS,
    rank_order: Sequence[str] = _RANKS,
) -> str:
    """Return the canonical representative of a flop's isomorphism class.

    Args:
        flop: Three distinct cards in compact or whitespace-separated notation.
        with_spaces: Add spaces, remove spaces, or preserve the input style with
            ``None``.
        suits_order: A permutation of ``shdc`` used for canonical ordering.
        rank_order: A permutation of ``AKQJT98765432`` used for card ordering.

    Returns:
        The canonical flop string.

    Raises:
        TypeError: An argument has the wrong type.
        ValueError: The flop or an ordering argument is invalid.
    """
    validated_suits = _validate_order(suits_order, _SUITS, "suits_order")
    validated_ranks = _validate_order(rank_order, _RANKS, "rank_order")
    cards, input_has_spaces = _parse_flop(
        flop, validated_ranks, validated_suits
    )
    separator = _get_separator(with_spaces, input_has_spaces)
    normalised_cards = _normalise_cards(
        cards, validated_ranks, validated_suits
    )
    return separator.join(normalised_cards)


flop_normalize = flop_normalise

__all__ = ["flop_isomorphisms", "flop_normalise", "flop_normalize"]
