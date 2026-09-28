"""Deterministic negative-control generators for XMA Falsification v2."""
from __future__ import annotations

import numpy as np
import pandas as pd

SEEDS = {
    "G-F1": 2026092801,
    "G-F2": 2026092802,
    "G-F3": 2026092803,
    "G-F4": 2026092804,
    "G-F5": 2026092805,
}


def _permute_within_groups(
    frame: pd.DataFrame,
    value_col: str,
    group_cols: list[str],
    seed: int,
) -> pd.Series:
    rng = np.random.default_rng(seed)
    out = pd.Series(index=frame.index, dtype=object)
    # group order is deterministic.
    grouped = frame.groupby(group_cols, sort=True, dropna=False)
    for _, idx in grouped.groups.items():
        idx = list(idx)
        vals = frame.loc[idx, value_col].to_numpy(copy=True)
        perm = rng.permutation(len(vals))
        out.loc[idx] = vals[perm]
    return out


def guard_f1_state_labels(frame: pd.DataFrame) -> pd.Series:
    """Permute UP/DOWN labels within symbol x calendar-quarter."""
    x = frame.copy()
    x["quarter"] = pd.to_datetime(x["date"]).dt.to_period("Q").astype(str)
    return _permute_within_groups(
        x, "state", ["symbol", "quarter"], SEEDS["G-F1"]
    )


def guard_f2_distance(frame: pd.DataFrame) -> pd.Series:
    """Permute distance-to-mid values within symbol x calendar-quarter."""
    x = frame.copy()
    x["quarter"] = pd.to_datetime(x["date"]).dt.to_period("Q").astype(str)
    return _permute_within_groups(
        x, "distance_to_mid", ["symbol", "quarter"], SEEDS["G-F2"]
    ).astype(float)


def guard_f3_sector_rs(frame: pd.DataFrame) -> pd.Series:
    """Permute Sector-RS values within date x XMA-state cross-section."""
    return _permute_within_groups(
        frame, "sector_rs", ["date", "xma_state"], SEEDS["G-F3"]
    ).astype(float)


def guard_f4_condition_labels(frame: pd.DataFrame) -> pd.Series:
    """Permute external z>1 labels within symbol x state x quarter."""
    x = frame.copy()
    x["quarter"] = pd.to_datetime(x["date"]).dt.to_period("Q").astype(str)
    return _permute_within_groups(
        x, "condition_true", ["symbol", "xma_state", "quarter"], SEEDS["G-F4"]
    ).astype(bool)


def guard_f5_riskoff_dates(frame: pd.DataFrame) -> pd.Series:
    """Permute Risk-Off labels at date level within quarter, then broadcast.

    Input may have multiple symbols per date. Each unique date must have one
    consistent risk_off label before permutation.
    """
    x = frame[["date", "risk_off"]].copy()
    consistency = x.groupby("date")["risk_off"].nunique(dropna=False)
    if (consistency > 1).any():
        raise ValueError("risk_off must be market-wide and consistent per date")

    dates = x.drop_duplicates("date").copy()
    dates["quarter"] = pd.to_datetime(dates["date"]).dt.to_period("Q").astype(str)
    perm = _permute_within_groups(
        dates, "risk_off", ["quarter"], SEEDS["G-F5"]
    )
    mapping = dict(zip(dates["date"], perm.astype(bool)))
    return frame["date"].map(mapping).astype(bool)
