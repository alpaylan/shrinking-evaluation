# Shrinking configuration & counters

The Haskell workloads (bst-haskell, rbt-haskell, …) expose a single env var,
`ETNA_SHRINKS`, that selects how QuickCheck, Hedgehog, and Falsify cap their
shrink budget. They also emit per-trial counters describing what happened
during the shrinking phase.

## Modes

| `ETNA_SHRINKS`              | mode      | effect |
| --------------------------- | --------- | ------ |
| unset / empty / `default`   | default   | no override; each framework uses its own built-in cap |
| `none`                      | none      | cap at 0 (no shrinking) |
| numeric `N` (e.g. `50`)     | fixed     | override the cap to N |

Framework defaults when in `default` mode:

| Framework  | Default cap | What the cap counts |
| ---------- | ----------- | ------------------- |
| QuickCheck | `maxBound :: Int` (effectively unlimited) | every shrink attempt: accepted + rejected + discarded |
| Hedgehog   | `1000` | accepted shrinks only |
| Falsify    | none (`Nothing`) | depth of the accepted-shrink chain only |

So the same nominal "budget" means three different things. At `ETNA_SHRINKS=50`,
QuickCheck stops after 50 total attempts, Hedgehog after 50 accepted shrinks,
and Falsify after 50 accepted shrinks worth of chain depth (with no bound on
the rejected attempts explored along the way).

In practice, for our BST/RBT-style workloads the shrinkers terminate
*structurally* — they reach a local minimum where no smaller candidate fails —
well before any of these caps fire. The cap is a safety net, not the normal
termination condition.

## Counters in `store.jsonl`

Each trial emits these new fields alongside the existing `tests` / `discards`:

| Field                 | Type     | Meaning |
| --------------------- | -------- | ------- |
| `shrink_mode`         | `String` | `"default"`, `"none"`, or `"fixed"` |
| `shrinks`             | `Int`    | the numeric cap (0 for default/none, N for fixed) |
| `shrinking_passed`    | `Int?`   | property body evaluations during shrinking where the postcondition held |
| `shrinking_failed`    | `Int?`   | …where the postcondition failed (= accepted shrinks) |
| `shrinking_discarded` | `Int?`   | …where the precondition rejected the input |

`null` (`Nothing`) on these means the trial timed out before the framework
returned a result. For Lean / Small / Size strategies (no shrinking phase)
they are `0`.

## Caveats

- **Falsify's `none` leaks ~7 evaluations.** Tasty's IsTest instance for Falsify
  calls `renderTestResult` internally, which forces the first node of the lazy
  `ShrinkExplanation` tree. That forcing requires running the property on
  candidates regardless of `maxShrinks=0`. To get a true zero you'd have to
  bypass Tasty and call `falsify` directly.

- **QC's `tests` excludes shrink attempts; Hedgehog's and Falsify's `tests`
  include them.** This was already true before the new counters; the new
  `shrinking_*` fields let you compute "pre-shrinking tests" for HH/Falsify
  as `tests - shrinking_passed - shrinking_failed`.

## Running

Default mode (no env var set):
```sh
stack exec bst -- '{"workload":"bst-haskell","strategy":"Quick","property":"prop_InsertPost","timeout":10}'
```

No shrinking:
```sh
ETNA_SHRINKS=none stack exec bst -- '{"workload":"bst-haskell","strategy":"Hedgehog","property":"prop_InsertPost","timeout":10}'
```

Fixed budget:
```sh
ETNA_SHRINKS=200 stack exec bst -- '{"workload":"bst-haskell","strategy":"Falsify","property":"prop_InsertPost","timeout":10}'
```

Switch mutation first if you want a failing trial:
```sh
cd workloads/bst-haskell && marauders set --variant insert_1 && stack build
```

Note: direct `stack exec` invocations need the `prop_` prefix on the property
name (`prop_InsertPost`, not `InsertPost`). The standard etna harness adds the
prefix internally, so test JSON files and `store.jsonl` use the bare name.
