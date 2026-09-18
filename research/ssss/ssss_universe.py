"""SSSS research universe and historical sample splits.

This file is data/config only. It does not implement trading logic.

Rules:
- OFFICIAL_BASELINE_45 is the exact equity universe behind the corrected
  59.2% / +8.84% baseline.
- Historical cohorts must not be silently promoted into the official baseline.
- A cohort may overlap another cohort because many experiments intentionally
  reused previously known stocks.
"""

from __future__ import annotations

OFFICIAL_BASELINE_COHORTS = {
    "A": ["AAPL", "MSFT", "NVDA", "JPM", "XOM"],
    "B": ["ADBE", "WFC", "MRK", "FDX", "NEE"],
    "C": ["ORCL", "WMT", "GS", "TMO", "RTX"],
    "O1": ["AVGO", "PEP", "C", "MDT", "UNP"],
    "O2": ["IBM", "CVX", "HD", "AMGN", "MCD"],
    "O3": ["LLY", "GE", "V", "TGT", "COP"],
    "O4": ["QCOM", "NKE", "SCHW", "GILD", "CSX"],
    "N1": ["META", "AMD", "CRM", "TXN", "AMZN"],
    "OOS": ["COST", "DE", "SPGI", "CI", "DUK"],
}

OFFICIAL_BASELINE_45 = [
    ticker
    for cohort in OFFICIAL_BASELINE_COHORTS.values()
    for ticker in cohort
]

assert len(OFFICIAL_BASELINE_45) == 45
assert len(set(OFFICIAL_BASELINE_45)) == 45

HISTORICAL_SPLITS = {
    "pricenear_frozen_oos6": ["QCOM", "MCD", "TMO", "RTX", "SCHW"],
    "pricenear_frozen_oos7": ["CRM", "PM", "CVS", "UPS", "DUK"],
    "grb_third_oos": ["TMO", "RTX", "LMT", "C", "XLP"],

    "mtf_discovery": ["ADBE", "WFC", "MRK", "FDX", "NEE"],
    "mtf_oos1": ["AVGO", "PEP", "C", "MDT", "UNP"],
    "mtf_frozen_oos2": ["TSLA", "KO", "BK", "CAT", "CVS"],

    "broad50_tech_consumer": ["META", "AMD", "CRM", "TXN", "AMZN"],
    "broad50_financial": ["BAC", "MS", "BLK", "CME", "USB"],
    "broad50_health": ["JNJ", "ABBV", "PFE", "UNH", "ISRG"],

    "failure_sell_frozen_oos": ["COST", "DE", "SPGI", "CI", "DUK"],
    "mature_sell_frozen_oos2": ["NFLX", "AXP", "ABT", "HON", "SO"],
    "rte_frozen_oos3": ["GOOG", "MU", "DIS", "MA", "BMY"],

    # Defined/planned cohort; do not treat as a completed final-result cohort.
    "rte_planned_frozen_oos4": ["UPS", "LIN", "T", "SBUX", "PLD"],

    "crypto_frozen_validation": ["BTC", "ETH", "SOL", "BNB"],
}

# Exact membership not safely recoverable from the retained research context.
KNOWN_MISSING_HISTORICAL_MEMBERSHIP = {
    "early_grb_discovery12": 12,
    "early_grb_validation5": 5,
}


def validate() -> None:
    assert len(OFFICIAL_BASELINE_45) == 45
    assert len(set(OFFICIAL_BASELINE_45)) == 45

    for name, tickers in OFFICIAL_BASELINE_COHORTS.items():
        assert len(tickers) == 5, (name, tickers)

    for name, tickers in HISTORICAL_SPLITS.items():
        assert len(tickers) > 0, name


if __name__ == "__main__":
    validate()
    print("Official SSSS baseline universe:", len(OFFICIAL_BASELINE_45))
    print(", ".join(OFFICIAL_BASELINE_45))
