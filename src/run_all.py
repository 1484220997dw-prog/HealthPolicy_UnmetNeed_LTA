"""Run the whole analysis in order and keep a log of the run.

  python run_all.py                 full run on the restricted KHP files
  python run_all.py --synthetic     same pipeline on input/synthetic/
  python run_all.py --quick         40 bootstrap replications instead of 400
"""
from __future__ import annotations

import argparse
import os
import runpy
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from khp_lta import config as cfg

STEPS = [
    ("00_check_environment.py", "check environment and data paths"),
    ("01_build_panel.py", "build the person-wave panel from the KHP files"),
    ("02_fit_lta.py", "select the number of statuses, fit the LTA, bootstrap"),
    ("03_covariates.py", "three-step covariate models"),
    ("04_tables_figures.py", "tables, figure and numbers.json"),
    ("05_make_synthetic.py", "write the synthetic replica of the panel"),
    ("06_sensitivity_k5.py", "the five-status solution, as a sensitivity analysis"),
    ("07_check_manuscript.py", "word counts and audit of the numbers in the text"),
]


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              cwd=cfg.PROJECT_ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:                              # noqa: BLE001
        return "not a git checkout"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true",
                    help="analyse input/synthetic/ instead of the KHP files")
    ap.add_argument("--quick", action="store_true",
                    help="40 bootstrap replications, for a smoke test")
    ap.add_argument("--reuse", action="store_true",
                    help="let step 02 reuse the stored point estimate and "
                         "bootstrap draws instead of refitting them")
    args = ap.parse_args()

    if args.reuse:
        sys.argv = [sys.argv[0], "--reuse-fit", "--reuse-bootstrap"]
    else:
        sys.argv = [sys.argv[0]]

    if args.quick:
        os.environ["KHP_LTA_QUICK"] = "1"
        cfg.N_BOOTSTRAP = 40
        cfg.N_STARTS = 20
        cfg.N_STARTS_SELECT = 8

    steps = list(STEPS)
    if args.synthetic:
        if not cfg.SYNTHETIC_CSV.exists():
            print("input/synthetic/synthetic_unmet_panel.csv is missing; it is "
                  "produced by step 05 from the real data.")
            return 1
        # Read the synthetic panel where it lies and send every output to its own
        # folder. A synthetic run must never be able to overwrite the panel built
        # from the real data, or the tables and figures reported in the paper.
        cfg.PANEL_CSV = cfg.SYNTHETIC_CSV
        cfg.DERIVED_DIR = cfg.SYNTHETIC_DIR
        base = cfg.OUTPUT_DIR / "synthetic"
        cfg.TABLES_DIR = base / "tables"
        cfg.FIGURES_DIR = base / "figures"
        cfg.LOGS_DIR = base / "logs"
        for _d in (cfg.TABLES_DIR, cfg.FIGURES_DIR, cfg.LOGS_DIR):
            _d.mkdir(parents=True, exist_ok=True)
        cfg.NUMBERS_JSON = cfg.LOGS_DIR / "numbers.json"
        print(f"synthetic mode: reading {cfg.SYNTHETIC_CSV.name}; "
              f"all results go to {base}")
        # Step 01 needs the restricted files; step 05 produces the synthetic panel
        # from them; step 07 audits the manuscript, whose numbers come from the
        # real data and would all appear to mismatch.
        steps = [s for s in steps if s[0] not in ("01_build_panel.py",
                                                  "05_make_synthetic.py",
                                                  "07_check_manuscript.py")]
        # step 04 reads the prevalence log that step 01 normally writes
        import pandas as pd
        panel = pd.read_csv(cfg.PANEL_CSV)
        sub = panel[panel.module_asked == 1]
        (100 * sub.groupby("year")[cfg.INDICATORS + ["phy_any", "den_any"]].mean()
         ).round(2).to_csv(cfg.LOGS_DIR / "indicator_prevalence_by_year.csv")

    log = cfg.LOGS_DIR / "run_log.txt"
    started = datetime.now(timezone.utc)
    lines = [f"run started {started.isoformat(timespec='seconds')}",
             f"python {sys.version.split()[0]}",
             f"git commit {git_commit()}",
             f"mode {'synthetic' if args.synthetic else 'KHP microdata'}"
             f"{' (quick)' if args.quick else ''}",
             f"KHP_RAW_DIR {cfg.raw_dir()}", ""]

    for script, what in steps:
        print(f"\n{'=' * 72}\n{script}  -  {what}\n{'=' * 72}", flush=True)
        t0 = time.time()
        try:
            runpy.run_path(str(HERE / script), run_name="__main__")
        except SystemExit as exc:
            if exc.code:
                lines.append(f"{script}: FAILED (exit {exc.code})")
                log.write_text("\n".join(lines), encoding="utf-8")
                return int(exc.code)
        dt = time.time() - t0
        lines.append(f"{script}: ok in {dt:,.1f}s")
        print(f"\n{script} finished in {dt:,.1f}s", flush=True)

    lines.append("")
    lines.append(f"run finished {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    log.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nwrote {log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
