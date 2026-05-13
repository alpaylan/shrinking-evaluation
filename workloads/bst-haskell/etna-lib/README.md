# etna-haskell-lib

Shared Haskell support library for [Etna](https://github.com/alpaylan/etna-cli)
workloads. Wraps QuickCheck, SmallCheck, and LeanCheck behind Etna's common
runner and sampler interfaces.

## Usage

This repo is consumed as a git submodule by Haskell Etna workload repos
(e.g. `etna-haskell-bst`, `etna-haskell-rbt`). Each workload's `stack.yaml`
lists `./etna-lib` as a local package.

It is not a standalone workload — it has no `etna.toml` and cannot be
registered via `etna workload add`.
