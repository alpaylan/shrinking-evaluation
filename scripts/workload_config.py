"""Per-workload configuration for the bucket/ECDF chart scripts.

Holds the store filenames, strategy variants per framework, and the
GROUPS x-axis layout for each workload. Single source of truth so
`bucket_charts.py` and `shrink_distribution_plots.py` agree on naming.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

QUICK_COLOR    = "#1b7837"
HEDGEHOG_COLOR = "#2166ac"
FALSIFY_COLOR  = "#b35806"
COLORS = {
    "Quick": QUICK_COLOR, "QuickCBC": QUICK_COLOR, "QuickGbE": QUICK_COLOR,
    "Correct": QUICK_COLOR,
    "Hedgehog": HEDGEHOG_COLOR, "HedgehogCBC": HEDGEHOG_COLOR,
    "HedgehogCBC2": HEDGEHOG_COLOR, "HedgehogGbE": HEDGEHOG_COLOR,
    "Falsify": FALSIFY_COLOR, "FalsifyCBC": FALSIFY_COLOR,
    "FalsifyCBC2": FALSIFY_COLOR, "FalsifyGbE": FALSIFY_COLOR,
}
HATCHED = {"HedgehogCBC2", "FalsifyCBC2"}

# Display labels for charts. The store data keeps the raw strategy name
# ("HedgehogCBC2"); charts show the friendlier "Idiomatic" naming.
DISPLAY_NAMES = {
    "Correct": "QuickCBC",
    "HedgehogCBC2": "HedgehogIdiomatic",
    "FalsifyCBC2":  "FalsifyIdiomatic",
}


def display_name(strategy: str) -> str:
    return DISPLAY_NAMES.get(strategy, strategy)


# Line style per generator type, so combined charts stay legible when
# same-framework variants share a color.
LINESTYLES = {
    "vanilla":   "-",    # solid
    "cbc":       "--",   # dashed
    "idiomatic": "-.",   # dash-dot
    "qbe":       ":",    # dotted
}


def generator_type(strategy: str) -> str:
    """Classify a strategy into a generator family for styling."""
    if strategy in HATCHED:
        return "idiomatic"
    if strategy.endswith("GbE"):
        return "qbe"
    if strategy.endswith("CBC") or strategy == "Correct":
        return "cbc"
    return "vanilla"


def linestyle(strategy: str) -> str:
    return LINESTYLES[generator_type(strategy)]


def _store(wl: str, fw: str, mode: str) -> str:
    """Map (workload, framework, mode) -> store filename."""
    suffix = {"none": "shrink-0", "fixed-100": "shrink-100", "default": "shrink-default"}[mode]
    fw_low = fw.lower()
    return f"store.{wl}.{fw_low}.{suffix}.jsonl"


WORKLOADS = {
    "bst": {
        "long_name": "bst-haskell",
        "modes": ["none", "fixed-100", "default"],
        "variants": {
            "Quick":    ["Quick", "QuickCBC",                    "QuickGbE"],
            "Hedgehog": ["Hedgehog", "HedgehogCBC", "HedgehogCBC2", "HedgehogGbE"],
            "Falsify":  ["Falsify",  "FalsifyCBC",  "FalsifyCBC2",  "FalsifyGbE"],
        },
        "groups": [
            ("vanilla", [
                ("Quick",    "Quick",    "Quick"),
                ("Hedgehog", "Hedgehog", "Hedgehog"),
                ("Falsify",  "Falsify",  "Falsify"),
            ]),
            ("CBC", [
                ("Quick",    "QuickCBC",     "Quick"),
                ("Hedgehog", "HedgehogCBC",  "Hedgehog"),
                ("Hedgehog", "HedgehogCBC2", "Hedgehog\nIdiomatic"),
                ("Falsify",  "FalsifyCBC",   "Falsify"),
                ("Falsify",  "FalsifyCBC2",  "Falsify\nIdiomatic"),
            ]),
            ("GbE", [
                ("Quick",    "QuickGbE",    "Quick"),
                ("Hedgehog", "HedgehogGbE", "Hedgehog"),
                ("Falsify",  "FalsifyGbE",  "Falsify"),
            ]),
        ],
        "families": {
            "vanilla": ["Quick", "Hedgehog", "Falsify"],
            "cbc":     ["QuickCBC", "HedgehogCBC", "HedgehogCBC2", "FalsifyCBC", "FalsifyCBC2"],
            "qbe":     ["QuickGbE", "HedgehogGbE", "FalsifyGbE"],
        },
    },
    "rbt": {
        "long_name": "rbt-haskell",
        "modes": ["none", "default"],
        # Idiomatic (CBC2) variants are intentionally excluded from rbt
        # charts — they showed no benefit there (only HedgehogCBC2 on bst
        # did). The store data still contains the CBC2 rows.
        "variants": {
            "Quick":    ["Quick", "QuickCBC",                "QuickGbE"],
            "Hedgehog": ["Hedgehog", "HedgehogCBC",          "HedgehogGbE"],
            "Falsify":  ["Falsify",  "FalsifyCBC",           "FalsifyGbE"],
        },
        "groups": [
            ("vanilla", [
                ("Quick",    "Quick",    "Quick"),
                ("Hedgehog", "Hedgehog", "Hedgehog"),
                ("Falsify",  "Falsify",  "Falsify"),
            ]),
            ("CBC", [
                ("Quick",    "QuickCBC",     "Quick"),
                ("Hedgehog", "HedgehogCBC",  "Hedgehog"),
                ("Falsify",  "FalsifyCBC",   "Falsify"),
            ]),
            ("GbE", [
                ("Quick",    "QuickGbE",    "Quick"),
                ("Hedgehog", "HedgehogGbE", "Hedgehog"),
                ("Falsify",  "FalsifyGbE",  "Falsify"),
            ]),
        ],
        "families": {
            "vanilla": ["Quick", "Hedgehog", "Falsify"],
            "cbc":     ["QuickCBC", "HedgehogCBC", "FalsifyCBC"],
            "qbe":     ["QuickGbE", "HedgehogGbE", "FalsifyGbE"],
        },
    },
    "stlc": {
        "long_name": "stlc-haskell",
        "modes": ["none", "default"],
        "variants": {
            "Quick":    ["Quick", "Correct"],
            "Hedgehog": ["Hedgehog", "HedgehogCBC"],
            "Falsify":  ["Falsify",  "FalsifyCBC"],
        },
        "groups": [
            ("vanilla", [
                ("Quick",    "Quick",    "Quick"),
                ("Hedgehog", "Hedgehog", "Hedgehog"),
                ("Falsify",  "Falsify",  "Falsify"),
            ]),
            ("CBC", [
                ("Quick",    "Correct",     "Quick"),
                ("Hedgehog", "HedgehogCBC", "Hedgehog"),
                ("Falsify",  "FalsifyCBC",  "Falsify"),
            ]),
        ],
        "families": {
            "vanilla": ["Quick", "Hedgehog", "Falsify"],
            "cbc":     ["Correct", "HedgehogCBC", "FalsifyCBC"],
        },
        "groundtruth_store": "store.stlc.det.jsonl",
    },
    "fsub": {
        "long_name": "fsub-haskell",
        "modes": ["default"],
        "variants": {
            "Quick":    ["Quick", "Correct"],
            "Hedgehog": ["Hedgehog", "HedgehogCBC"],
            "Falsify":  ["Falsify",  "FalsifyCBC"],
        },
        "groups": [
            ("vanilla", [
                ("Quick",    "Quick",    "Quick"),
                ("Hedgehog", "Hedgehog", "Hedgehog"),
                ("Falsify",  "Falsify",  "Falsify"),
            ]),
            ("CBC", [
                ("Quick",    "Correct",     "Quick"),
                ("Hedgehog", "HedgehogCBC", "Hedgehog"),
                ("Falsify",  "FalsifyCBC",  "Falsify"),
            ]),
        ],
        "families": {
            "vanilla": ["Quick", "Hedgehog", "Falsify"],
            "cbc":     ["Correct", "HedgehogCBC", "FalsifyCBC"],
        },
        "groundtruth_store": "store.fsub.det.jsonl",
    },
}


def get_config(workload: str) -> dict:
    if workload not in WORKLOADS:
        raise SystemExit(f"unknown workload {workload!r}; pick one of {list(WORKLOADS)}")
    cfg = dict(WORKLOADS[workload])
    cfg["name"] = workload
    # Build stores map only for the modes / frameworks that the workload has.
    stores = {}
    for fw in cfg["variants"]:
        for m in cfg["modes"]:
            stores[(fw, m)] = _store(workload, fw, m)
    cfg["stores"] = stores
    return cfg
