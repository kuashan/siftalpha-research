"""SSSS crypto research universe.

Data/config only.  This does not implement trading logic.

Important:
- Core assets were already seen in earlier SSSS crypto work.
- OOS and Frozen OOS assets below were not found in the retained repository
  at the time this file was created.
- Venue / quote pair must be frozen separately before an empirical experiment.
"""

from __future__ import annotations

CRYPTO_CORE_DISCOVERY = [
    "BTC",
    "ETH",
    "SOL",
    "BNB",
]

CRYPTO_OOS_CANDIDATES = [
    "XRP",
    "ADA",
    "DOGE",
    "TRX",
]

CRYPTO_FROZEN_OOS_CANDIDATES = [
    "LINK",
    "AVAX",
    "LTC",
    "BCH",
]

CRYPTO_RESEARCH_12 = (
    CRYPTO_CORE_DISCOVERY
    + CRYPTO_OOS_CANDIDATES
    + CRYPTO_FROZEN_OOS_CANDIDATES
)


def validate() -> None:
    assert len(CRYPTO_CORE_DISCOVERY) == 4
    assert len(CRYPTO_OOS_CANDIDATES) == 4
    assert len(CRYPTO_FROZEN_OOS_CANDIDATES) == 4
    assert len(CRYPTO_RESEARCH_12) == 12
    assert len(set(CRYPTO_RESEARCH_12)) == 12

    assert not (
        set(CRYPTO_CORE_DISCOVERY)
        & set(CRYPTO_OOS_CANDIDATES)
    )
    assert not (
        set(CRYPTO_CORE_DISCOVERY)
        & set(CRYPTO_FROZEN_OOS_CANDIDATES)
    )
    assert not (
        set(CRYPTO_OOS_CANDIDATES)
        & set(CRYPTO_FROZEN_OOS_CANDIDATES)
    )


if __name__ == "__main__":
    validate()
    print("SSSS crypto research assets:", ", ".join(CRYPTO_RESEARCH_12))
