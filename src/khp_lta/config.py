"""Paths, wave map and variable definitions for the KHP unmet-need LTA study.

Every path is derived from PROJECT_ROOT so that the same code runs unchanged on a
local machine, in Google Colab and inside a GitHub Actions runner.  The only
machine-specific setting is KHP_RAW_DIR, the directory that holds the restricted
Korea Health Panel (KHP) annual SPSS files; it is read from the environment so
that no local path is baked into the repository.
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

# --------------------------------------------------------------------------- #
# Console encoding: Korean/Chinese variable labels must survive a cp949 console.
# --------------------------------------------------------------------------- #
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace", line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8",
                                  errors="replace", line_buffering=True)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_DIR = PROJECT_ROOT / "input"
DERIVED_DIR = INPUT_DIR / "derived"
SYNTHETIC_DIR = INPUT_DIR / "synthetic"
DICTIONARY_DIR = INPUT_DIR / "dictionary"

OUTPUT_DIR = PROJECT_ROOT / "output"
TABLES_DIR = OUTPUT_DIR / "tables"
FIGURES_DIR = OUTPUT_DIR / "figures"
LOGS_DIR = OUTPUT_DIR / "logs"

for _d in (DERIVED_DIR, SYNTHETIC_DIR, DICTIONARY_DIR, TABLES_DIR, FIGURES_DIR, LOGS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

PANEL_CSV = DERIVED_DIR / "khp_unmet_panel_2020_2023.csv"
SYNTHETIC_CSV = SYNTHETIC_DIR / "synthetic_unmet_panel.csv"
NUMBERS_JSON = LOGS_DIR / "numbers.json"

RANDOM_SEED = 20260720

# --------------------------------------------------------------------------- #
# Restricted source microdata
# --------------------------------------------------------------------------- #
DEFAULT_RAW_DIR = Path(
    r"G:\我的云端硬盘\2026_fall semester\Dataset\medical_pannel"
)


def raw_dir() -> Path:
    """Directory holding the KHP ``KHP+<year>_spss`` subfolders."""
    return Path(os.environ.get("KHP_RAW_DIR", str(DEFAULT_RAW_DIR)))


# wave label -> (year, subfolder, individual-level file)
WAVES: dict[int, tuple[int, str, str]] = {
    1: (2020, "KHP+2020_spss", "b_ind.sav"),
    2: (2021, "KHP+2021_spss", "c_ind.sav"),
    3: (2022, "KHP+2022_spss", "d_ind.sav"),
    4: (2023, "KHP+2023_spss", "e_ind.sav"),
}
YEARS = [y for y, _, _ in WAVES.values()]
N_WAVES = len(WAVES)

# --------------------------------------------------------------------------- #
# Unmet-need measurement model
# --------------------------------------------------------------------------- #
# AH1 = unmet need for physician/hospital care, AH2 = unmet need for dental care.
# 1 = "yes, in the end I could not go", 2 = "no", 3 = "no care was needed",
# -9 = don't know/refused.  Responses 2 and 3 are both coded 0: collapsing them
# makes the indicator invariant to the 2020-2023 drift in how often option 3 was
# selected (444 -> 34 for AH1), which is a questionnaire-administration artefact.
UNMET_STEMS = {"phy": "AH1", "den": "AH2"}

# Reason dummies (asked only of respondents with AH*=1).
COST_REASONS = [1, 2]           # medical/transport cost; forgone earnings
NONCOST_REASONS = [3, 4, 5, 6, 7, 8]  # time, opening hours/appointment, did not
                                      # know where to go, transport/distance,
                                      # mobility or health, complicated booking
# Reason 9 (care refused: 0-4 cases per year) and 10 ("other", affected by a
# 2021 coding change) are not used to define the indicators.

INDICATORS = ["phy_cost", "phy_noncost", "den_cost", "den_noncost"]
INDICATOR_LABELS = {
    "phy_cost": "Physician care forgone - cost barrier",
    "phy_noncost": "Physician care forgone - non-financial barrier",
    "den_cost": "Dental care forgone - cost barrier",
    "den_noncost": "Dental care forgone - non-financial barrier",
}

# --------------------------------------------------------------------------- #
# Covariates
# --------------------------------------------------------------------------- #
ID_VARS = ["PIDWON", "HHID"]
WEIGHT_VARS = ["I_WGL", "I_WGC"]
COVARIATE_SOURCE_VARS = [
    "SEX", "BIRTH_Y", "EDU", "MARR", "ECO1", "REGION1", "HEALTH_INS",
    "H_INC_TOT", "CD", "DISA_YN", "HS_SRH", "USC1_YN", "I_PHI1_YN",
]
RAW_COLUMNS = (
    ID_VARS
    + WEIGHT_VARS
    + COVARIATE_SOURCE_VARS
    + list(UNMET_STEMS.values())
    + [f"{stem}_{i}_D" for stem in UNMET_STEMS.values() for i in range(1, 11)]
)

CAPITAL_AREA = {11, 28, 41}                 # Seoul, Incheon, Gyeonggi
METRO_CITIES = {26, 27, 29, 30, 31, 36}     # Busan, Daegu, Gwangju, Daejeon,
                                            # Ulsan, Sejong

MISSING_CODES = (-9, -1)

# --------------------------------------------------------------------------- #
# Model fitting
# --------------------------------------------------------------------------- #
K_RANGE = (1, 2, 3, 4, 5, 6)
K_SELECTED = 4          # confirmed against BIC in output/tables/tableA1_*.csv

# Two-stage random starts: SCREEN_* short runs to find the global basin,
# N_POLISH_* of them iterated to convergence.
N_STARTS = 60           # final model
N_POLISH = 4
SCREEN_ITER = 300
MAX_ITER = 20000
TOL = 1e-7

N_STARTS_SELECT = 16    # model-selection sweep over K
N_POLISH_SELECT = 2
MAX_ITER_SELECT = 6000
TOL_SELECT = 1e-5

N_BOOTSTRAP = 400
BOOT_MAX_ITER = 1200
BOOT_TOL = 1e-5
