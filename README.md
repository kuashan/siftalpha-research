# siftalpha-research

Private research repository for SiftAlpha quantitative trading research.

## Current primary project

SSSS causal trading model and position-state-machine research.

## Repository structure

- `models/ssss_core_v0_1.py` — executable reference implementation of the current frozen core model
- `research/ssss/SSSS_CURRENT_STATE.md` — current source of truth
- `research/ssss/SSSS_STATE_MACHINE.md` — OPEN / ADD / REDUCE / RE-ADD / HOLD / CLOSE architecture
- `research/ssss/SSSS_RESEARCH_LOG.md` — accepted and rejected research history
- `research/ssss/SSSS_EXPERIMENTS.csv` — machine-readable experiment ledger
- `research/ssss/checkpoints/` — dated research checkpoints

## Important

Research results currently rely mainly on approximately two years of available market history. They are not claims of long-run or live performance.

The executable Python model contains only the rules currently accepted as the core research model. Candidate position-management logic remains explicitly marked as research until validated.


## Universe and sample-split audit

- `research/ssss/SSSS_UNIVERSE_45.md` — exact 45-stock universe behind the corrected official baseline
- `research/ssss/SSSS_SAMPLE_SPLITS.md` — human-readable Discovery / OOS / Frozen OOS split history
- `research/ssss/SSSS_SAMPLE_SPLITS.csv` — machine-readable sample-split ledger
- `research/ssss/ssss_universe.py` — executable ticker/cohort configuration with integrity checks

Important: historical research cohorts must not be silently mixed into the official 45-stock baseline.


## Research governance

- `research/ssss/SSSS_RESEARCH_PROTOCOL.md` — mandatory pre-registration protocol for every new research round

Every new round must commit its Discovery / OOS / Frozen OOS membership to `main` before any corresponding results are computed or inspected.


## SSSS data-source resilience

- `research/ssss/SSSS_DATA_SOURCE_POLICY.md` — provider-switching and parity-audit rules
- `research/ssss/data_sources/yfinance_daily.py` — research fallback downloader
- `research/ssss/data_sources/requirements.txt` — isolated fallback-data dependencies

Do not silently mix market-data providers inside one official research stage.
