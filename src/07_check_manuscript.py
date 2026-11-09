"""Step 07 - count the manuscript words and audit the numbers quoted in the text.

The journal counts the manuscript text and boxes, excluding the abstract, the
references, the tables and the figures, against a 4,000-word limit for
full-length articles. This script reports that count and then checks each
quantity listed in CLAIMS against output/logs/numbers.json and the generated
tables, so a transcription error in the prose is caught before submission
rather than by a reviewer.

Writes output/logs/word_count.txt and output/logs/manuscript_audit.txt.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

from khp_lta import config as cfg

MANUSCRIPT = cfg.PROJECT_ROOT / "manuscript" / "05_manuscript.md"


def read_manuscript() -> str:
    """The manuscript text with Markdown escaping removed.

    Editors and Markdown formatters legitimately escape characters that could be
    read as markup, turning "1. Background" into "1\\. Background" and "[21,22]"
    into "\\[21,22\\]". Undoing that here keeps the heading and citation matching
    below from breaking the first time the file is opened in another tool.
    """
    raw = MANUSCRIPT.read_text(encoding="utf-8")
    return re.sub(r"\\([.\[\]|*_<>~`#+=-])", r"\1", raw)

# Sections counted towards the journal's limit, by their heading text.
COUNTED = ("Research in context", "1. Background", "2. Methods", "3. Results",
           "4. Discussion", "5. Conclusion")

# (what the prose says, where the value comes from)
CLAIMS: list[tuple[str, str]] = [
    ("10,508 adults", "numbers.n_baseline_cohort"),
    ("38,548 person-wave", "numbers.n_person_waves_module_answered"),
    ("7,905 adults", "numbers.n_answered_all_four_waves"),
    ("21.8% ... 14.9%", "numbers.any_unmet_2020 / any_unmet_2023"),
    ("78.2% / 85.1% no unmet need", "numbers.prevalence_2020[0] / prevalence_2023[0]"),
    ("8.0% / 4.6% cost barrier", "numbers.prevalence_2020[1] / prevalence_2023[1]"),
    ("13.2% / 9.9% time and availability", "numbers.prevalence_2020[2] / prevalence_2023[2]"),
    ("0.6% / 0.5% compound", "numbers.prevalence_2020[3] / prevalence_2023[3]"),
    ("92.9% stay with no unmet need", "numbers.stay_prob_mean"),
    ("60.6% stay in the cost barrier status", "numbers.stay_prob_mean"),
    ("50.3% stay in time and availability", "numbers.stay_prob_mean"),
    ("22.1% stay in compound", "numbers.stay_prob_mean"),
    ("7.1% annual entry rate", "numbers.entry_from_no_unmet_mean"),
    ("34.0% exit cost barrier to no unmet need", "numbers.exit_to_no_unmet_mean"),
    ("47.0% exit time and availability", "numbers.exit_to_no_unmet_mean"),
    ("68.5 / 16.3 / 15.2 / 7.8 / 3.4%", "numbers.share_* over four waves"),
    ("50.9% conditional persistence", "numbers.model_b_persist_rate"),
    ("entropy 0.814", "numbers.entropy_R2"),
    ("BIC 58,143", "numbers.bic_selected"),
    ("400 bootstrap replications", "numbers.n_bootstrap"),
]


def _words(body: str) -> int:
    body = re.sub(r"`[^`]*`", " ", body)                  # code spans
    body = re.sub(r"\[[0-9,–\- ]+\]", " ", body)     # citation markers
    body = re.sub(r"\*[^*\n]*\bSource:[^*\n]*\*", " ", body)
    body = re.sub(r"[*_>|#]", " ", body)
    return len([w for w in re.split(r"\s+", body) if re.search(r"[A-Za-z0-9]", w)])


def word_count() -> dict[str, int]:
    """Count the sections the journal counts: the box plus Background to Conclusion.

    Headings are not counted, and nor is anything after the Conclusion (tables,
    figure captions and references are excluded from the limit).
    """
    text = read_manuscript()
    heads = [(m.start(), m.end(), m.group(1).strip())
             for m in re.finditer(r"^#+\s+(.*)$", text, flags=re.M)]
    counts, total = {}, 0
    for i, (_, end, head) in enumerate(heads):
        if not any(head.startswith(c) for c in COUNTED):
            continue
        stop = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        n = _words(text[end:stop])
        # a counted section's subsections belong to it
        j = i + 1
        while j < len(heads) and not any(heads[j][2].startswith(c) for c in COUNTED) \
                and not heads[j][2].startswith(("Tables and figure", "References",
                                                "Abstract",
                                                "Declaration of generative AI")):
            nxt = heads[j + 1][0] if j + 1 < len(heads) else len(text)
            n += _words(text[heads[j][1]:nxt])
            j += 1
        counts[head] = n
        total += n
    counts["TOTAL (limit 4,000)"] = total
    return counts


def audit() -> list[str]:
    nums = json.loads(cfg.NUMBERS_JSON.read_text(encoding="utf-8"))
    text = read_manuscript()
    out = []

    def check(label: str, value, scale: float = 1.0, decimals: int = 1,
              integer: bool = False) -> None:
        """Look for the value in the prose, allowing either rounding of the last digit.

        Patterns are built from the value itself rather than typed in, so this
        cannot drift away from the analysis output the way a hand-written
        expectation would.
        """
        if integer:
            cands = [f"{int(value):,}", f"{int(value)}"]
        else:
            v = float(value) * scale
            q = 10 ** decimals
            import math
            cands = sorted({f"{math.floor(v * q) / q:.{decimals}f}",
                            f"{math.ceil(v * q) / q:.{decimals}f}",
                            f"{v:.{decimals}f}"})
        found = any(re.search(re.escape(c), text) for c in cands)
        shown = " or ".join(cands)
        out.append(f"{'ok  ' if found else 'MISS'} {label:<52} = {shown}")

    check("baseline cohort", nums["n_baseline_cohort"], integer=True)
    check("person-waves with the module answered",
          nums["n_person_waves_module_answered"], integer=True)
    check("answered all four waves", nums["n_answered_all_four_waves"], integer=True)
    check("any unmet need 2020 (%)", nums["any_unmet_2020"])
    check("any unmet need 2023 (%)", nums["any_unmet_2023"])
    for i, lab in enumerate(nums["status_names"]):
        for year, key in ((2020, "prevalence_2020"), (2023, "prevalence_2023")):
            check(f"{lab} prevalence {year} (%)", nums[key][i])
    for lab, v in nums["stay_prob_mean"].items():
        check(f"mean probability of staying, {lab}", v, scale=100)
    for lab, v in nums["exit_to_no_unmet_mean"].items():
        check(f"mean exit to no unmet need, {lab}", v, scale=100)
    check("annual entry rate (%)", nums["entry_from_no_unmet_mean"], scale=100)
    for key in ("share_never_unmet_4w", "share_once_unmet_4w",
                "share_two_or_more_4w", "share_three_or_more_4w",
                "share_all_four_4w"):
        check(key, nums[key])
    check("conditional persistence (%)", nums["model_b_persist_rate"])
    check("entropy R2", nums["entropy_R2"], decimals=3)
    check("BIC of the selected model", nums["bic_selected"], integer=True)
    check("bootstrap replications", nums["n_bootstrap"], integer=True)
    check("largest shift, complete-case (pp)", nums["max_abs_shift_complete_case_pp"])

    # headline indicator prevalences quoted in section 3.1
    ind = nums["indicator_prevalence_by_year"]
    for name in ("phy_any", "den_any", "phy_cost", "phy_noncost",
                 "den_cost", "den_noncost"):
        for year in ("2020", "2023"):
            check(f"{name} {year} (%)", ind[name][year])

    # Model A and Model B estimates quoted in section 3.4. Each quoted figure is
    # searched for in the prose, so a change in the estimates shows up here
    # instead of leaving a stale number in the text.
    ta = pd.read_csv(cfg.TABLES_DIR / "tableA3_model_a_baseline_status.csv")
    tb = pd.read_csv(cfg.TABLES_DIR / "tableA4_model_b_persistence.csv")
    quoted_a = {
        ("Cost barrier", "income_q5_c: Q1 (lowest)"): "full",
        ("Cost barrier", "income_q5_c: Q2"): "point",
        ("Cost barrier", "income_q5_c: Q3"): "point",
        ("Cost barrier", "income_q5_c: Q4"): "point",
        ("Cost barrier", "insurance3: Medical Aid"): "full",
        ("Time and availability barrier", "income_q5_c: Q1 (lowest)"): "full",
        ("Time and availability barrier", "employed"): "full",
        ("Time and availability barrier", "disability"): "full",
        ("Time and availability barrier", "age_group: 65+"): "full",
    }
    quoted_b = {
        "status_t: Compound barrier": "full",
        "status_t: Time and availability barrier": "full",
        "employed": "full",
        "poor_srh": "full",
        "interval: 2021-2022": "full",
        "interval: 2022-2023": "full",
    }
    for _, r in ta.iterrows():
        how = quoted_a.get((r.outcome, r.term))
        if how:
            check(f"Model A, {r.outcome}, {r.term}", r.RRR, decimals=2)
            if how == "full":
                check(f"   ... lower bound", r.ci_low, decimals=2)
                check(f"   ... upper bound", r.ci_high, decimals=2)
    for _, r in tb.iterrows():
        how = quoted_b.get(r.term)
        if how:
            check(f"Model B, {r.term}", r.OR, decimals=2)
            check(f"   ... lower bound", r.ci_low, decimals=2)
            check(f"   ... upper bound", r.ci_high, decimals=2)
    return out


def limits() -> list[str]:
    """The journal's other hard limits: abstract, box, title, highlights."""
    text = read_manuscript()
    out = []

    ab = text[text.index("## Abstract"):text.index("**Keywords:**")]
    n = _words(ab.split("\n", 1)[1])
    out.append(f"{'ok  ' if n <= 250 else 'OVER'} abstract{'':<22} {n:>4} / 250 words")

    box = text[text.index("## Research in context"):text.index("## 1. Background")]
    n = _words(box.split("\n", 1)[1])
    out.append(f"{'ok  ' if n <= 200 else 'OVER'} research in context box{'':<7} "
               f"{n:>4} / 200 words")

    title = re.search(r"^# (.+)$", text, flags=re.M).group(1)
    n = len(title.replace("—", " ").split())
    out.append(f"{'ok  ' if n <= 20 else 'OVER'} title{'':<25} {n:>4} / 20 words")

    hl_raw = (cfg.PROJECT_ROOT / "manuscript" / "04_highlights.md").read_text(
        encoding="utf-8")
    hl = re.sub(r"\\(.)", r"\1", hl_raw)
    bullets = [l[2:].strip() for l in hl.splitlines() if l.startswith("- ")]
    worst = max((len(b) for b in bullets), default=0)
    out.append(f"{'ok  ' if len(bullets) <= 5 and worst <= 85 else 'OVER'} "
               f"highlights{'':<19} {len(bullets)} bullets, longest {worst} / 85 chars")

    n_main = len(re.findall(r"^\*\*Table [0-9]", text, flags=re.M)) + \
        len(re.findall(r"^\*\*Figure [0-9]", text, flags=re.M))
    out.append(f"{'ok  ' if n_main <= 4 else 'OVER'} tables plus figures{'':<11} "
               f"{n_main} / 4")

    eqs = len(re.findall(r"^> ", text, flags=re.M))
    out.append(f"{'ok  ' if eqs <= 3 else 'OVER'} displayed equations{'':<11} {eqs} / 3")
    return out


def main() -> None:
    print(f"writing results to {cfg.TABLES_DIR.parent}")
    counts = word_count()
    lines = [f"{k:<34} {v:>6,}" for k, v in counts.items()]
    lim = limits()
    (cfg.LOGS_DIR / "word_count.txt").write_text(
        "\n".join(lines + [""] + lim), encoding="utf-8")
    print("Word count (journal limit 4,000 for a full-length article)")
    print("\n".join(lines))
    if counts["TOTAL (limit 4,000)"] > 4000:
        print(f"\nOVER THE LIMIT by {counts['TOTAL (limit 4,000)'] - 4000} words")
    print("\nOther journal limits")
    print("\n".join(lim))

    rows = audit()
    (cfg.LOGS_DIR / "manuscript_audit.txt").write_text("\n".join(rows), encoding="utf-8")
    print("\nNumbers quoted in the manuscript, checked against the analysis output")
    print("\n".join(rows))
    missing = [r for r in rows if r.startswith("MISS")]
    if missing:
        print(f"\n{len(missing)} value(s) in the analysis output could not be found in "
              f"the manuscript text; check whether the prose is out of date.")


if __name__ == "__main__":
    main()
