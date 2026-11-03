"""Step 00 - check that the environment and the data are where the pipeline expects.

Run this first. It fails loudly and specifically rather than part-way through a
40-minute model fit.
"""
from __future__ import annotations

import importlib
import platform
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from khp_lta import config as cfg

REQUIRED = {"numpy": "2.0", "pandas": "2.0", "scipy": "1.11",
            "matplotlib": "3.8", "pyreadstat": "1.2"}


def main() -> int:
    print(f"python   {platform.python_version()}  ({platform.system()} "
          f"{platform.release()})")
    problems: list[str] = []

    for mod, minimum in REQUIRED.items():
        try:
            m = importlib.import_module(mod)
            print(f"{mod:<13} {m.__version__}")
        except ImportError:
            problems.append(f"missing package: {mod} (>= {minimum}); "
                            f"run  pip install -r requirements.txt")

    print(f"\nproject root  {cfg.PROJECT_ROOT}")
    print(f"KHP_RAW_DIR   {cfg.raw_dir()}")

    missing_waves = []
    for wave, (year, folder, fname) in cfg.WAVES.items():
        path = cfg.raw_dir() / folder / fname
        mark = "found" if path.exists() else "MISSING"
        print(f"  wave {wave} ({year}): {mark:>7}  {path.name}")
        if not path.exists():
            missing_waves.append(f"{folder}/{fname}")

    if missing_waves:
        print("\nThe restricted KHP files are not visible at that path.")
        print("Either set KHP_RAW_DIR to the folder holding the KHP+<year>_spss")
        print("directories, or run the pipeline on the synthetic panel:")
        print("  python src/run_all.py --synthetic")
        if cfg.SYNTHETIC_CSV.exists():
            print(f"\nsynthetic panel present: {cfg.SYNTHETIC_CSV}")
        else:
            problems.append("neither the KHP files nor a synthetic panel is available")

    if cfg.PANEL_CSV.exists():
        print(f"\nderived panel present: {cfg.PANEL_CSV}")

    if problems:
        print("\nProblems found:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nEnvironment looks usable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
