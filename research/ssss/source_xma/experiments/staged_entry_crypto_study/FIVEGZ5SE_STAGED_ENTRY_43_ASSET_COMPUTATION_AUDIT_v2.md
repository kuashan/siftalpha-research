# FIVEGZ5SE staged-entry 43-asset computation audit v2

Status: **COMPUTED_PENDING_INTERPRETATION**

Date: 2026-09-30

Universe is exactly 39 U.S. stocks plus BTC, ETH, BNB and SOL (43 assets). Each asset contains all 16 pre-registered configurations: W3/W5 × BASE/50/60/70 × FULL_FIRST/SELECTIVE.

Immutable source Git blobs:
- stock_batch1_v1.json: 8104e8e4c6cd3673b70d70a5b9b4c756670d5146
- stock_batch2_v1.json: f545a7cb5d7b0cc8b74a632c5aa7afbfb8d0865f
- stock_batch3_v1.json: 1e1fcb969674a8cbfd04c90c65fef954a68f153d
- crypto_batch_v1.json: 9fa75d1a0f6a2cbb379e3ca4268c8ee1f66bcbc7

The crypto scope amendment is user-directed and was frozen before this computation. No signal rule, slippage rule, position size, confirmation window, or exit rule was changed.

Generated tables:
- all 43 assets × all 16 configs;
- grouped stock/crypto/combined summary containing FULL_FIRST and SELECTIVE;
- confirmation event table and confirmation accuracy;
- asset-level bootstrap 95% intervals for return/MDD/P5/CVaR deltas;
- SELECTIVE-vs-FULL_FIRST synergy table.

Bootstrap: deterministic asset-level resampling, n=5000, seed=20260930.

The failed GitHub Actions run #36657310048 did not compute or commit results; final tables were computed directly from the immutable repository blobs and committed through the Git data API.

No operating-policy conclusion is encoded here. Final interpretation is recorded separately after reviewing these tables.
