"""Tests for the public poker-isomorphisms API."""

import unittest
from itertools import combinations, permutations

from poker_isomorphisms import (
    flop_isomorphisms,
    flop_normalise,
    flop_normalize,
)

RANKS = tuple("AKQJT98765432")
SUITS = tuple("shdc")
DECK = tuple(rank + suit for rank in RANKS for suit in SUITS)


def reference_isomorphisms(flop: str) -> set[str]:
    """Generate the mathematical orbit without using package internals."""
    cards = (flop[0:2], flop[2:4], flop[4:6])
    results = set()
    for target_suits in permutations(SUITS):
        suit_mapping = dict(zip(SUITS, target_suits))
        renamed_cards = tuple(
            card[0] + suit_mapping[card[1]] for card in cards
        )
        results.update("".join(order) for order in permutations(renamed_cards))
    return results


class FlopNormaliseTests(unittest.TestCase):
    def test_normalises_documented_examples(self) -> None:
        examples = {
            "2dAd2s": "As2s2h",
            "7cQc3s": "Qs7s3h",
            "AhKhQh": "AsKsQs",
            "Ac8d3h": "As8h3d",
        }

        for flop, expected in examples.items():
            with self.subTest(flop=flop):
                self.assertEqual(flop_normalise(flop), expected)

    def test_preserves_or_overrides_spacing(self) -> None:
        self.assertEqual(flop_normalise("Ac 8d 3d"), "As 8h 3h")
        self.assertEqual(flop_normalise("Ac\t8d\t3d"), "As 8h 3h")
        self.assertEqual(
            flop_normalise("Ac 8d 3d", with_spaces=False), "As8h3h"
        )
        self.assertEqual(
            flop_normalise("Ac8d3d", with_spaces=True), "As 8h 3h"
        )

    def test_supports_custom_rank_and_suit_orders(self) -> None:
        self.assertEqual(
            flop_normalise("7cQc3s", suits_order="cdhs"), "Qc7c3d"
        )
        self.assertEqual(
            flop_normalise("7cQc3s", rank_order="23456789TJQKA"),
            "3s7hQh",
        )

    def test_american_spelling_is_an_alias(self) -> None:
        self.assertIs(flop_normalize, flop_normalise)

    def test_all_legal_flops_have_1755_normal_forms(self) -> None:
        normal_forms = {
            flop_normalise("".join(cards)) for cards in combinations(DECK, 3)
        }

        self.assertEqual(len(normal_forms), 1755)


class FlopIsomorphismsTests(unittest.TestCase):
    def test_matches_reference_suit_permutations(self) -> None:
        representatives = (
            "AsKsQs",
            "AsKhQh",
            "AsKhQd",
            "AsAhKs",
            "AsAhKd",
            "AsAhAd",
        )

        for flop in representatives:
            with self.subTest(flop=flop):
                actual = flop_isomorphisms(flop)
                expected = reference_isomorphisms(flop)
                self.assertEqual(set(actual), expected)
                self.assertEqual(len(actual), len(expected))

    def test_every_result_has_the_same_normal_form(self) -> None:
        expected = flop_normalise("2dAd2s")

        self.assertTrue(
            all(
                flop_normalise(result) == expected
                for result in flop_isomorphisms("2dAd2s")
            )
        )

    def test_preserves_existing_deterministic_order(self) -> None:
        self.assertEqual(
            flop_isomorphisms("2dAd2s")[:6],
            [
                "As2s2h",
                "As2h2s",
                "2sAs2h",
                "2s2hAs",
                "2hAs2s",
                "2h2sAs",
            ],
        )

    def test_formats_all_results_consistently(self) -> None:
        results = flop_isomorphisms("Ac 8d 3d")

        self.assertTrue(all(result.count(" ") == 2 for result in results))

    def test_custom_suit_order_controls_result_order(self) -> None:
        results = flop_isomorphisms("7cQc3s", suits_order="cdhs")

        self.assertEqual(results[0], "Qc7c3d")
        self.assertEqual(set(results), reference_isomorphisms("7cQc3s"))


class InputValidationTests(unittest.TestCase):
    def test_rejects_malformed_or_impossible_flops(self) -> None:
        invalid_flops = (
            "",
            "AsKh",
            "As KhQd",
            "AsKhQd extra",
            "AsAsKh",
            "asKhQd",
            "AS Kh Qd",
        )

        for function in (flop_normalise, flop_isomorphisms):
            for flop in invalid_flops:
                with self.subTest(function=function.__name__, flop=flop):
                    with self.assertRaises(ValueError):
                        function(flop)

    def test_rejects_non_string_flops(self) -> None:
        for function in (flop_normalise, flop_isomorphisms):
            with self.subTest(function=function.__name__):
                with self.assertRaisesRegex(TypeError, "flop must be a string"):
                    function(None)  # type: ignore[arg-type]

    def test_rejects_invalid_with_spaces_values(self) -> None:
        for value in (0, 1, "yes"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(TypeError, "with_spaces"):
                    flop_normalise(
                        "AsKhQd", with_spaces=value  # type: ignore[arg-type]
                    )

    def test_rejects_invalid_orders(self) -> None:
        with self.assertRaisesRegex(ValueError, "suits_order"):
            flop_normalise("AsKhQd", suits_order="shds")
        with self.assertRaisesRegex(ValueError, "rank_order"):
            flop_normalise("AsKhQd", rank_order="AKQJT9876543")
        with self.assertRaisesRegex(TypeError, "suits_order"):
            flop_normalise("AsKhQd", suits_order=None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
