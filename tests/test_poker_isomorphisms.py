"""Tests for the public poker-isomorphisms API."""

import unittest
from hashlib import sha256
from inspect import Parameter, signature
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


def reference_normal_form(flop: str) -> str:
    """Select a normal form without using the package normaliser."""
    return min(
        reference_physical_flops(flop),
        key=lambda board: tuple(
            CARD_POSITIONS[board[index : index + 2]]
            for index in range(0, 6, 2)
        ),
    )


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
    def test_matches_reference_order_and_suit_permutations(self) -> None:
        # Digests capture the complete 0.5 result order at commit 935a769.
        legacy_results = {
            "AsKsQs": (
                24,
                "b74541ad01289c228ed2c71051183b111d906ddd618923c55d437d8203724c33",
            ),
            "AsKhQh": (
                72,
                "6eba3ed6908e0934db89ae24c9adbdf43b736a0e31efceba05c1ff84536e5e23",
            ),
            "AsKhQd": (
                144,
                "672ae6d9cc01998a50948e2a9d3127ea576dbb8bfbaddb55c99e3d081726a1cf",
            ),
            "AsAhKs": (
                72,
                "caa4acab12ce7e38ae461dfabae561d5729efbe5945ed2e1629c623d5ea86ca0",
            ),
            "AsAhKd": (
                72,
                "76adfe2a2fec566e0af5e649e055eed4c3f002795c8ff0ba14bf29c89a30fff7",
            ),
            "AsAhAd": (
                24,
                "8112af450540c1d32896e1685b05e8ea506c7379d1cb1ab58898e19b221ce507",
            ),
        }

        for flop, (expected_length, expected_digest) in legacy_results.items():
            with self.subTest(flop=flop):
                actual = flop_isomorphisms(flop)
                self.assertEqual(set(actual), reference_isomorphisms(flop))
                self.assertEqual(len(actual), expected_length)
                actual_digest = sha256(
                    "\n".join(actual).encode("ascii")
                ).hexdigest()
                self.assertEqual(actual_digest, expected_digest)

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
    def test_catalogue_matches_independent_exhaustive_reference(self) -> None:
        catalogue = all_flop_normal_forms()
        expected = sorted(
            {
                reference_normal_form("".join(cards))
                for cards in combinations(DECK, 3)
            },
            key=lambda flop: tuple(
                CARD_POSITIONS[flop[index : index + 2]]
                for index in range(0, 6, 2)
            ),
        )

        self.assertEqual(len(catalogue), 1755)
        self.assertEqual(len(set(catalogue)), 1755)
        self.assertEqual(catalogue, expected)

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

    def test_preserves_stable_public_signatures(self) -> None:
        positional = Parameter.POSITIONAL_OR_KEYWORD
        keyword_only = Parameter.KEYWORD_ONLY
        required = Parameter.empty
        flop_parameters = (
            ("flop", positional, required),
            ("with_spaces", positional, None),
            ("suits_order", positional, SUITS),
            ("rank_order", positional, RANKS),
        )
        expected_parameters = {
            "flop_normalise": flop_parameters,
            "flop_normalize": flop_parameters,
            "flop_isomorphisms": flop_parameters,
            "flop_isomorphism_class": flop_parameters,
            "flops_are_isomorphic": (
                ("flop_a", positional, required),
                ("flop_b", positional, required),
                ("suits_order", keyword_only, SUITS),
                ("rank_order", keyword_only, RANKS),
            ),
            "normalise_flops": (
                ("flops", positional, required),
                ("with_spaces", keyword_only, False),
                ("suits_order", keyword_only, SUITS),
                ("rank_order", keyword_only, RANKS),
            ),
            "normalize_flops": (
                ("flops", positional, required),
                ("with_spaces", keyword_only, False),
                ("suits_order", keyword_only, SUITS),
                ("rank_order", keyword_only, RANKS),
            ),
            "all_flop_normal_forms": (
                ("with_spaces", keyword_only, False),
                ("suits_order", keyword_only, SUITS),
                ("rank_order", keyword_only, RANKS),
            ),
        }

        for name, expected in expected_parameters.items():
            with self.subTest(name=name):
                parameters = tuple(
                    (parameter.name, parameter.kind, parameter.default)
                    for parameter in signature(
                        getattr(poker_isomorphisms, name)
                    ).parameters.values()
                )
                self.assertEqual(parameters, expected)

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

        for function in (
            flop_normalise,
            flop_isomorphisms,
            flop_isomorphism_class,
        ):
            for flop in invalid_flops:
                with self.subTest(function=function.__name__, flop=flop):
                    with self.assertRaises(ValueError):
                        function(flop)

    def test_rejects_non_string_flops(self) -> None:
        for function in (
            flop_normalise,
            flop_isomorphisms,
            flop_isomorphism_class,
        ):
            with self.subTest(function=function.__name__):
                with self.assertRaisesRegex(TypeError, "flop must be a string"):
                    function(None)  # type: ignore[arg-type]

    def test_rejects_invalid_with_spaces_values(self) -> None:
        for value in (0, 1, "yes"):
            for function in (
                flop_normalise,
                flop_isomorphisms,
                flop_isomorphism_class,
            ):
                with self.subTest(function=function.__name__, value=value):
                    with self.assertRaisesRegex(TypeError, "with_spaces"):
                        function(
                            "AsKhQd",
                            with_spaces=value,  # type: ignore[arg-type]
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
