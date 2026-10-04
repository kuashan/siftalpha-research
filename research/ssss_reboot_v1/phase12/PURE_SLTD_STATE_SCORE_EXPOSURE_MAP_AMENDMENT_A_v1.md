# Pure SLTD State Score Exposure Map v1 — Amendment A

Status: **PRE-RESULT DATA-AVAILABILITY AMENDMENT**

The first CI attempt (Run 37178472616) stopped before result generation because Yahoo Finance returned no daily price history for `EA` over the frozen study range and reported the symbol as possibly delisted.

No Fresh24 result, portfolio metric, score-bucket metric, or admission decision was produced.

To preserve a 24-stock untouched universe without changing any model parameter, score definition, exposure mapping, threshold, evaluation window, or admission gate:

- remove unavailable `EA`;
- replace it with `CHTR` in the Communication sector.

`CHTR` is not present in:
- the original 79-stock universe,
- Phase11 OOS10,
- R2 Fresh20,
- R3 Fresh20.

All other protocol terms remain unchanged.

`PURE_SLTD_STATE_SCORE_EXPOSURE_MAP_V1_AMENDMENT_A = FROZEN_BEFORE_RESULT`
