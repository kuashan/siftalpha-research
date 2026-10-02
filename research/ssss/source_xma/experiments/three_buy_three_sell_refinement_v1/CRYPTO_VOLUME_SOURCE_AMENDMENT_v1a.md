# Crypto Volume Data-Source Amendment v1a

Status: **PRE_REGISTERED_BEFORE_EXTENDED_CRYPTO_COMPUTATION**

Date: 2026-10-01

The main protocol requested Twelve Data daily OHLCV. Verification before computation showed that Twelve Data's BTC/USD, ETH/USD, BNB/USD and SOL/USD daily series expose OHLC but not historical Volume in this connector.

Because FIVEGZ5SE Capital and Anomaly states require Volume, missing volume MUST NOT be filled with zero, forward-filled, synthesized from price, or silently omitted.

Therefore for the crypto extension:

1. The frozen signal equations and execution rules do not change.
2. Crypto input must contain real historical daily OHLCV.
3. Prefer exchange-native spot OHLCV in UTC daily bars for BTC, ETH, BNB and SOL.
4. Previous 2021-2024 crypto results remain archived and are not overwritten.
5. If an extended OHLCV source cannot be obtained for a coin with a documented provenance and reproducible date range, that coin is marked BLOCKED_BY_DATA for the extended-horizon portion rather than computed with fake volume.
6. No result from the extended crypto study has been inspected before this amendment.

The stock data source remains Twelve Data daily OHLCV.
