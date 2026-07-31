"""Utilities for identifying suit-isomorphic poker flops."""

from collections.abc import Iterable, Iterator, Sequence
from functools import lru_cache
from itertools import combinations, permutations

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
    _validate_with_spaces(with_spaces)
    if with_spaces is None:
        return " " if input_has_spaces else ""
    return " " if with_spaces else ""


def _validate_with_spaces(with_spaces: bool | None) -> None:
    """Validate the shared output-format option."""
    if with_spaces is not None and type(with_spaces) is not bool:
        raise TypeError("with_spaces must be True, False, or None")


@lru_cache(maxsize=16)
def _card_positions(
    rank_order: tuple[str, ...], suits_order: tuple[str, ...]
) -> dict[str, int]:
    """Return card positions for a validated rank and suit order."""
    return {
        rank + suit: position
        for position, (rank, suit) in enumerate(
            (rank, suit) for rank in rank_order for suit in suits_order
        )
    }


def _normalise_cards(
    cards: tuple[str, str, str],
    rank_order: tuple[str, ...],
    suits_order: tuple[str, ...],
) -> tuple[str, str, str]:
    """Find the first sorted representative across all suit renamings."""
    card_positions = _card_positions(rank_order, suits_order)

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


def _normalise_validated_flop(
    flop: str,
    with_spaces: bool | None,
    rank_order: tuple[str, ...],
    suits_order: tuple[str, ...],
) -> str:
    """Normalise one flop after validating the ordering arguments."""
    cards, input_has_spaces = _parse_flop(flop, rank_order, suits_order)
    separator = _get_separator(with_spaces, input_has_spaces)
    normalised_cards = _normalise_cards(cards, rank_order, suits_order)
    return separator.join(normalised_cards)


def _renamed_card_sets(
    normalised_cards: tuple[str, str, str], suits_order: tuple[str, ...]
) -> Iterator[tuple[str, str, str]]:
    """Yield suit-renamed card tuples in the legacy deterministic order."""
    used_suits = tuple(dict.fromkeys(card[1] for card in normalised_cards))
    for target_suits in permutations(suits_order, len(used_suits)):
        suit_mapping = dict(zip(used_suits, target_suits))
        yield (
            normalised_cards[0][0] + suit_mapping[normalised_cards[0][1]],
            normalised_cards[1][0] + suit_mapping[normalised_cards[1][1]],
            normalised_cards[2][0] + suit_mapping[normalised_cards[2][1]],
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

    results = []
    seen_results = set()
    for renamed_cards in _renamed_card_sets(normalised_cards, validated_suits):
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
    return _normalise_validated_flop(
        flop, with_spaces, validated_ranks, validated_suits
    )


def flop_isomorphism_class(
    flop: str,
    with_spaces: bool | None = None,
    suits_order: Sequence[str] = _SUITS,
    rank_order: Sequence[str] = _RANKS,
) -> list[str]:
    """Return each unique physical flop in a suit-isomorphism class.

    Unlike :func:`flop_isomorphisms`, this function returns each unordered
    three-card board once. Cards within each result use the requested canonical
    rank and suit order.

    Args:
        flop: Three distinct cards in compact or whitespace-separated notation.
        with_spaces: Add spaces, remove spaces, or preserve the input style with
            ``None``.
        suits_order: A permutation of ``shdc`` used to order results.
        rank_order: A permutation of ``AKQJT98765432`` used to order results.

    Returns:
        The unique physical flops in deterministic order.

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
    card_positions = _card_positions(validated_ranks, validated_suits)

    results = []
    seen_results = set()
    for renamed_cards in _renamed_card_sets(normalised_cards, validated_suits):
        ordered_cards = tuple(
            sorted(renamed_cards, key=card_positions.__getitem__)
        )
        result = separator.join(ordered_cards)
        if result not in seen_results:
            results.append(result)
            seen_results.add(result)

    return results


def flops_are_isomorphic(
    flop_a: str,
    flop_b: str,
    *,
    suits_order: Sequence[str] = _SUITS,
    rank_order: Sequence[str] = _RANKS,
) -> bool:
    """Return whether two flops differ only by suit and card permutations.

    Args:
        flop_a: The first flop to compare.
        flop_b: The second flop to compare.
        suits_order: A permutation of ``shdc`` used for normalisation.
        rank_order: A permutation of ``AKQJT98765432`` used for normalisation.

    Returns:
        ``True`` when both flops have the same canonical representative.

    Raises:
        TypeError: An argument has the wrong type.
        ValueError: A flop or an ordering argument is invalid.
    """
    validated_suits = _validate_order(suits_order, _SUITS, "suits_order")
    validated_ranks = _validate_order(rank_order, _RANKS, "rank_order")

    normal_forms = []
    for name, flop in (("flop_a", flop_a), ("flop_b", flop_b)):
        try:
            cards, _ = _parse_flop(flop, validated_ranks, validated_suits)
        except (TypeError, ValueError) as error:
            raise type(error)(f"{name}: {error}") from error
        normal_forms.append(
            _normalise_cards(cards, validated_ranks, validated_suits)
        )

    return normal_forms[0] == normal_forms[1]


def normalise_flops(
    flops: Iterable[str],
    *,
    with_spaces: bool | None = False,
    suits_order: Sequence[str] = _SUITS,
    rank_order: Sequence[str] = _RANKS,
) -> list[str]:
    """Normalise a sequence of flops while preserving its order and duplicates.

    Invalid items raise the same error as :func:`flop_normalise`, prefixed with
    their zero-based position in ``flops``.

    Args:
        flops: A non-string iterable of flop strings.
        with_spaces: Use spaces, omit spaces, or preserve each input style with
            ``None``.
        suits_order: A permutation of ``shdc`` used for normalisation.
        rank_order: A permutation of ``AKQJT98765432`` used for normalisation.

    Returns:
        One normal form for every input, in input order.

    Raises:
        TypeError: An argument or flop has the wrong type.
        ValueError: A flop or an ordering argument is invalid.
    """
    if isinstance(flops, (str, bytes)):
        raise TypeError("flops must be a non-string iterable")
    try:
        iterator = iter(flops)
    except TypeError as error:
        raise TypeError("flops must be a non-string iterable") from error

    validated_suits = _validate_order(suits_order, _SUITS, "suits_order")
    validated_ranks = _validate_order(rank_order, _RANKS, "rank_order")
    _validate_with_spaces(with_spaces)

    results = []
    for index, flop in enumerate(iterator):
        try:
            result = _normalise_validated_flop(
                flop, with_spaces, validated_ranks, validated_suits
            )
        except (TypeError, ValueError) as error:
            raise type(error)(f"flops[{index}]: {error}") from error
        results.append(result)

    return results


@lru_cache(maxsize=16)
def _all_flop_normal_forms(
    rank_order: tuple[str, ...], suits_order: tuple[str, ...]
) -> tuple[str, ...]:
    """Build and cache the complete unspaced normal-form catalogue."""
    deck = tuple(rank + suit for rank in rank_order for suit in suits_order)
    normal_forms = {
        "".join(_normalise_cards(cards, rank_order, suits_order))
        for cards in combinations(deck, 3)
    }
    card_positions = _card_positions(rank_order, suits_order)
    return tuple(
        sorted(
            normal_forms,
            key=lambda flop: tuple(
                card_positions[flop[index : index + 2]]
                for index in range(0, 6, 2)
            ),
        )
    )


def all_flop_normal_forms(
    *,
    with_spaces: bool = False,
    suits_order: Sequence[str] = _SUITS,
    rank_order: Sequence[str] = _RANKS,
) -> list[str]:
    """Return all 1,755 canonical flop representatives.

    A fresh list is returned on every call. Internal unspaced catalogues are
    cached for reuse.

    Args:
        with_spaces: Add one space between cards when ``True``.
        suits_order: A permutation of ``shdc`` used for canonical ordering.
        rank_order: A permutation of ``AKQJT98765432`` used for card ordering.

    Returns:
        The complete normal-form catalogue in deterministic order.

    Raises:
        TypeError: An argument has the wrong type.
        ValueError: An ordering argument is invalid.
    """
    if type(with_spaces) is not bool:
        raise TypeError("with_spaces must be True or False")
    validated_suits = _validate_order(suits_order, _SUITS, "suits_order")
    validated_ranks = _validate_order(rank_order, _RANKS, "rank_order")
    normal_forms = _all_flop_normal_forms(validated_ranks, validated_suits)
    if not with_spaces:
        return list(normal_forms)
    return [" ".join((flop[0:2], flop[2:4], flop[4:6])) for flop in normal_forms]


flop_normalize = flop_normalise
normalize_flops = normalise_flops

__all__ = [
    "all_flop_normal_forms",
    "flop_isomorphism_class",
    "flop_isomorphisms",
    "flop_normalise",
    "flop_normalize",
    "flops_are_isomorphic",
    "normalise_flops",
    "normalize_flops",
]
