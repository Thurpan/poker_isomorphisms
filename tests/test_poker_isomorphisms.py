"""Tests for the public poker-isomorphisms API."""

import unittest
from itertools import combinations, permutations
from pathlib import Path

import poker_isomorphisms
from poker_isomorphisms import (
    __version__,
    all_flop_normal_forms,
    flop_isomorphism_class,
    flop_isomorphisms,
    flop_normalise,
    flop_normalize,
    flops_are_isomorphic,
    normalise_flops,
    normalize_flops,
)

RANKS = tuple("AKQJT98765432")
SUITS = tuple("shdc")
DECK = tuple(rank + suit for rank in RANKS for suit in SUITS)
CARD_POSITIONS = {card: position for position, card in enumerate(DECK)}


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


def reference_physical_flops(flop: str) -> set[str]:
    """Generate each physical board once without package internals."""
    cards = (flop[0:2], flop[2:4], flop[4:6])
    results = set()
    for target_suits in permutations(SUITS):
        suit_mapping = dict(zip(SUITS, target_suits))
        renamed_cards = sorted(
            (card[0] + suit_mapping[card[1]] for card in cards),
            key=CARD_POSITIONS.__getitem__,
        )
        results.add("".join(renamed_cards))
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


class FlopIsomorphismClassTests(unittest.TestCase):
    def test_returns_each_physical_board_once(self) -> None:
        expected_sizes = {
            "AsKsQs": 4,
            "AsKhQh": 12,
            "AsKhQd": 24,
            "AsAhKd": 12,
            "AsAhAd": 4,
        }

        for flop, expected_size in expected_sizes.items():
            with self.subTest(flop=flop):
                actual = flop_isomorphism_class(flop)
                self.assertEqual(set(actual), reference_physical_flops(flop))
                self.assertEqual(len(actual), expected_size)

    def test_physical_boards_expand_to_legacy_results(self) -> None:
        flop = "AsAhKd"
        normal_form = flop_normalise(flop)
        physical_boards = flop_isomorphism_class(flop)
        legacy_results = set(flop_isomorphisms(flop))

        self.assertEqual(len(legacy_results), 6 * len(physical_boards))
        for board in physical_boards:
            with self.subTest(board=board):
                self.assertEqual(flop_normalise(board), normal_form)
                cards = (board[0:2], board[2:4], board[4:6])
                self.assertTrue(
                    all(
                        "".join(order) in legacy_results
                        for order in permutations(cards)
                    )
                )

    def test_preserves_spacing_and_custom_order(self) -> None:
        spaced_results = flop_isomorphism_class("Ac 8d 3d")
        compact_results = flop_isomorphism_class(
            "Ac 8d 3d", with_spaces=False
        )
        custom_results = flop_isomorphism_class(
            "7cQc3s", suits_order="cdhs"
        )

        self.assertTrue(all(result.count(" ") == 2 for result in spaced_results))
        self.assertTrue(all(" " not in result for result in compact_results))
        self.assertEqual(custom_results[0], "Qc7c3d")


class FlopComparisonTests(unittest.TestCase):
    def test_compares_suit_isomorphism(self) -> None:
        self.assertTrue(flops_are_isomorphic("Kh9s3h", "Kd9c3d"))
        self.assertTrue(flops_are_isomorphic("Kh 9s 3h", "3d Kd 9c"))
        self.assertFalse(flops_are_isomorphic("AsKhQd", "AsKhQh"))

    def test_comparison_is_independent_of_custom_order(self) -> None:
        self.assertTrue(
            flops_are_isomorphic(
                "Kh9s3h",
                "Kd9c3d",
                suits_order="cdhs",
                rank_order="23456789TJQKA",
            )
        )

    def test_identifies_which_comparison_input_is_invalid(self) -> None:
        with self.assertRaisesRegex(ValueError, "flop_a"):
            flops_are_isomorphic("AsAsKh", "AsKhQd")
        with self.assertRaisesRegex(TypeError, "flop_b"):
            flops_are_isomorphic("AsKhQd", None)  # type: ignore[arg-type]


class BatchNormalisationTests(unittest.TestCase):
    def test_normalises_iterables_in_order_with_duplicates(self) -> None:
        inputs = (flop for flop in ("7cQc3s", "Ac 8d 3d", "7cQc3s"))

        self.assertEqual(
            normalise_flops(inputs),
            ["Qs7s3h", "As8h3h", "Qs7s3h"],
        )

    def test_controls_batch_spacing(self) -> None:
        inputs = ["Ac8d3d", "Ac 8d 3d"]

        self.assertEqual(normalise_flops(inputs), ["As8h3h", "As8h3h"])
        self.assertEqual(
            normalise_flops(inputs, with_spaces=None),
            ["As8h3h", "As 8h 3h"],
        )
        self.assertEqual(
            normalise_flops(inputs, with_spaces=True),
            ["As 8h 3h", "As 8h 3h"],
        )

    def test_american_spelling_is_an_alias(self) -> None:
        self.assertIs(normalize_flops, normalise_flops)

    def test_rejects_non_iterables_and_strings(self) -> None:
        for value in (None, "AsKhQd", b"AsKhQd"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(TypeError, "non-string iterable"):
                    normalise_flops(value)  # type: ignore[arg-type]

    def test_reports_the_invalid_item_index(self) -> None:
        with self.assertRaisesRegex(ValueError, r"flops\[1\]"):
            normalise_flops(["AsKhQd", "AsAsKh", "Ac8d3d"])

    def test_validates_options_for_empty_iterables(self) -> None:
        with self.assertRaisesRegex(TypeError, "with_spaces"):
            normalise_flops([], with_spaces="yes")  # type: ignore[arg-type]


class NormalFormCatalogueTests(unittest.TestCase):
    def test_catalogue_matches_exhaustive_normalisation(self) -> None:
        catalogue = all_flop_normal_forms()
        expected = {
            flop_normalise("".join(cards)) for cards in combinations(DECK, 3)
        }

        self.assertEqual(len(catalogue), 1755)
        self.assertEqual(len(set(catalogue)), 1755)
        self.assertEqual(set(catalogue), expected)

    def test_returns_a_fresh_deterministic_list(self) -> None:
        first = all_flop_normal_forms()
        second = all_flop_normal_forms()
        original_first_form = second[0]

        first.pop(0)
        self.assertEqual(len(second), 1755)
        self.assertEqual(all_flop_normal_forms()[0], original_first_form)

    def test_supports_spacing_and_custom_order(self) -> None:
        spaced = all_flop_normal_forms(with_spaces=True)
        custom = all_flop_normal_forms(
            suits_order="cdhs", rank_order="23456789TJQKA"
        )

        self.assertTrue(all(result.count(" ") == 2 for result in spaced))
        self.assertEqual(len(custom), 1755)
        self.assertEqual(custom[0], "2c2d2h")

    def test_rejects_ambiguous_spacing_values(self) -> None:
        with self.assertRaisesRegex(TypeError, "True or False"):
            all_flop_normal_forms(with_spaces=None)  # type: ignore[arg-type]


class PackageMetadataTests(unittest.TestCase):
    def test_exposes_stable_version_and_api(self) -> None:
        expected_names = {
            "__version__",
            "all_flop_normal_forms",
            "flop_isomorphism_class",
            "flop_isomorphisms",
            "flop_normalise",
            "flop_normalize",
            "flops_are_isomorphic",
            "normalise_flops",
            "normalize_flops",
        }

        self.assertEqual(__version__, "1.0.0")
        self.assertTrue(expected_names.issubset(poker_isomorphisms.__all__))

    def test_includes_typing_marker(self) -> None:
        package_directory = Path(poker_isomorphisms.__file__).parent

        self.assertTrue((package_directory / "py.typed").is_file())


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
