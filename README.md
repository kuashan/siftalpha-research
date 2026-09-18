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
