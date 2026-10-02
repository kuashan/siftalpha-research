# siftalpha-research

Private research and strategy-integration repository for SiftAlpha.

## Current canonical strategy state

The repository currently contains three formal strategy definitions:

1. **5s crypto v1** — `FROZEN_BASELINE`
2. **5s stocks v1** — `FROZEN_BASELINE`
3. **SLTD V6** — `OFFICIAL`

The canonical registry is:

`research/ssss/STRATEGY_FAMILY_REGISTRY_v1.md`

Do not use older branch descriptions or historical SSSS state files as the
current strategy-status source when they conflict with this registry and the
strategy-specific frozen / official records below.

## Strategy references

### 5s crypto v1

Frozen research baseline:

`research/ssss/5S_CRYPTO_V1_BASELINE.md`

Current Binance USDⓈ-M Demo integration:

`integrations/5s_crypto_binance_usdm_v1/`

Integration milestone status:

`integrations/5s_crypto_binance_usdm_v1/MILESTONES.md`

### 5s stocks v1

Frozen research baseline:

`research/ssss/5S_STOCKS_V1_BASELINE.md`

The strategy definition is frozen, but a stock trading runtime equivalent to
the current 5s-crypto Binance integration is not yet present.

### SLTD V6

Official naming record:

`research/ssss_reboot_v1/phase6/SLTD_V6_OFFICIAL_NAMING.md`

Formal 15-rule BUY / HOLD / WAIT / SELL taxonomy:

`research/ssss_reboot_v1/phase6/SSSS_FORMAL_15_ACTION_TAXONOMY_v1.md`

Independent V6 validation result:

`research/ssss_reboot_v1/phase6/SSSS_V6_FIVE_V5_DISCOVERY_INDEPENDENT_RESULT.md`

SLTD V6 is an official research strategy rule set.
It does not yet have the same completed Trading Console execution integration
as 5s crypto v1.

## Repository layout

- `research/ssss/` — frozen 5s baselines, registry, shared research material and source-XMA work.
- `research/ssss_reboot_v1/` — reboot research lineage leading to SLTD V6.
- `research/ssss/source_xma/experiments/` — supporting 5s / XMA experiments and audits.
- `integrations/5s_crypto_binance_usdm_v1/` — current 5s-crypto Binance Demo runtime integration.
- `.github/workflows/` — research and integration CI / workflow definitions.

## Governance

- Never modify a frozen baseline in place.
- Any strategy change must receive a new version / experiment identity.
- Preserve frozen / official strategy records as controls.
- Keep research validation status separate from runtime-integration status.
- Do not call a strategy production-ready solely because its research rules are frozen or official.
- Historical branches are retained for provenance; the consolidated `main` branch is the repository baseline after this consolidation is merged.

## Current consolidation note

The 2026-10-02 repository consolidation combines:
- the latest `research/ssss-reboot-v1` research state;
- the `feature/5s-crypto-binance-usdm-v1` runtime integration;
- synchronized strategy registry and integration documentation.

This consolidation does **not** change any frozen 5s strategy rule or any
official SLTD V6 rule.
