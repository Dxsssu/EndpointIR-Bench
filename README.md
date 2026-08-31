# EndpointIR-Bench

This repository uses Git submodules for both Atomic Red Team and CALDERA. Clone it recursively so both projects and CALDERA's nested plugin submodules are populated:

```bash
git clone --recurse-submodules https://github.com/Dxsssu/EndpointIR-Bench.git
cd EndpointIR-Bench
git submodule status --recursive
```

If the main repository was already cloned without submodules, initialize it with:

```bash
git pull
git submodule sync --recursive
git submodule update --init --recursive
```

A plain `git clone` checks out only the main repository and leaves submodule directories uninitialized. The recursive commands above fetch the exact Atomic Red Team and CALDERA commits pinned by this repository.
