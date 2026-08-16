# Repository guidance

## Project purpose

This package normalises three-card poker flops under global suit permutations.
It also enumerates every equivalent card-string representation.

## Model and delegation routing

Use only `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna`. Always set
reasoning effort to `xhigh`. Never select another reasoning effort.

The primary agent uses Sol and remains responsible for integration, validation,
and the final answer. Unnamed subagents use Terra. Use
`implementation_worker` for routine, scoped implementation or testing after the
design and security boundaries are settled.

Use Sol liberally for ambiguous or open-ended work, architecture, security,
trust boundaries, native Windows APIs, ABI, process containment, filesystem
identity, concurrency, interop, and difficult diagnosis. Use Sol after the first
straightforward attempt fails, for high-risk or high-value implementation, and
for review of every material implementation slice. Use `sol_specialist` for
complex work and `sol_reviewer` for read-only review of a coherent frozen slice
or final integration.

Use `mechanical_worker` only for deterministic, judgement-light work with an
exact result, such as formatting, inventories, repetitive transformations,
link checks, lint cleanup, or mechanical test expansion. Never assign Luna
security analysis, architecture, native or ABI decisions, difficult debugging,
HRC interaction, or final review.

Allow at most one active subagent. Do not run a reviewer beside an active
writer. Freeze the implementation slice before starting `sol_reviewer`.

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
