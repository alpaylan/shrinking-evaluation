# etna-haskell-fsub

System F-sub workload for [Etna](https://github.com/alpaylan/etna-cli),
implemented in Haskell.

**Status:** The `steps.json` and `marauder.toml` were seeded from
`etna-haskell-bst` to match the current Haskell workload contract. The
executable layout (single `etna-workload` binary, no sampler) still needs
to be aligned with the `./bin/$workload` / `./bin/$workload-sampler`
pattern before `etna experiment run` can drive it.

## Usage

```bash
etna workload add https://github.com/alpaylan/etna-haskell-fsub
```

The shared `etna-lib` support library is included as a git submodule at
`./etna-lib`. When cloning outside the `etna` CLI, remember to
`git clone --recurse-submodules`.
