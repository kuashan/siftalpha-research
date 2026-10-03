from __future__ import annotations

import csv
import gzip
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PROJECT = REPO / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(PROJECT))

import chan_strategy as cs  # noqa: E402

DATA_ROOT = REPO / "research" / "ssss_reboot_v1" / "phase7" / "data_snapshot"
HORIZONS = (5, 10, 20, 40)


def load(path: Path) -> list[dict]:
    out: list[dict] = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.append(
                {
                    "date": r["Date"][:10],
                    "open": float(r["Open"]),
                    "high": float(r["High"]),
                    "low": float(r["Low"]),
                    "close": float(r["Close"]),
                    "volume": float(r.get("Volume") or 0.0),
                }
            )
    return out


def classify_b1_family(
    bars: list[cs.RawBar],
    snapshot: dict,
    *,
    canonical: bool,
) -> list[dict]:
    """Return standard B1/S1 and theory-review B1P/S1P candidates.

    B1P/S1P are diagnostic only. They must satisfy the same local
    departure/new-extreme/weaker-force predicates as current standard B1/S1,
    but are separated by same-level Zhongshu relationship:
      FIRST_CENTER: no incoming same-level link (link=None)
      OVERLAP_CENTER: incoming same-level relationship overlaps
      STANDARD: incoming link matches the expected trend direction
      OPPOSITE_LINK: recorded only as a rejected context
    """
    macd = cs.compute_macd([x.close for x in bars])
    dif, hist = macd["dif"], macd["hist"]
    rows: list[dict] = []

    for info in snapshot["levels"]:
        if bool(info.get("canonical", False)) != canonical:
            continue

        level = int(info["level"])
        units = info["units"]
        zss = info["zss"]
        links = info["links"]

        for zi, zs in enumerate(zss):
            if zs.pending:
                continue

            enter = units[zs.start_sub - 1] if zs.start_sub > 0 else None
            leave = units[zs.end_sub + 1] if zs.end_sub + 1 < len(units) else None
            if enter is None or leave is None or leave.pending:
                continue
            if enter.direction != leave.direction:
                continue

            down = enter.direction == "down"
            sign = -1 if down else 1
            outside_center = leave.low < zs.zd if down else leave.high > zs.zg
            if not outside_center:
                continue

            new_extreme = (
                leave.low < min(enter.low, zs.dd)
                if down
                else leave.high > max(enter.high, zs.gg)
            )
            if not new_extreme:
                continue

            enter_dif = cs._dif_extreme(enter, dif, sign)
            weaker = (
                cs._movement_force(leave, hist, sign)
                < cs._movement_force(enter, hist, sign)
                or abs(cs._dif_extreme(leave, dif, sign))
                < abs(enter_dif)
            )
            if not weaker:
                continue

            expected = "down" if down else "up"
            actual = links[zi] if zi < len(links) else None
            if actual == expected:
                subtype = "STANDARD"
            elif actual is None:
                subtype = "FIRST_CENTER"
            elif actual == "overlap":
                subtype = "OVERLAP_CENTER"
            else:
                subtype = "OPPOSITE_LINK"

            base_kind = "B1" if down else "S1"
            kind = base_kind if subtype == "STANDARD" else f"{base_kind}P"
            rows.append(
                {
                    "level": level,
                    "kind": kind,
                    "base_kind": base_kind,
                    "subtype": subtype,
                    "anchor_index": int(leave.to_index),
                    "source_confirm_index": int(
                        leave.confirm_index
                        if leave.confirm_index is not None
                        else leave.end_index
                    ),
                    "anchor_price": float(leave.to_price),
                    "leave_low": float(leave.low),
                    "leave_high": float(leave.high),
                    "ZG": float(zs.zg),
                    "ZD": float(zs.zd),
                    "zs_start_index": int(zs.start_index),
                    "zs_end_index": int(zs.end_index),
                }
            )

    # Final structure can expose the same endpoint through overlapping
    # diagnostic contexts; keep one deterministic row per class/level/anchor.
    unique: dict[tuple, dict] = {}
    priority = {
        "STANDARD": 0,
        "FIRST_CENTER": 1,
        "OVERLAP_CENTER": 2,
        "OPPOSITE_LINK": 3,
    }
    for row in rows:
        key = (row["level"], row["base_kind"], row["anchor_index"])
        prev = unique.get(key)
        if prev is None or priority[row["subtype"]] < priority[prev["subtype"]]:
            unique[key] = row
    return list(unique.values())


def first_observed_index(
    bars: list[cs.RawBar],
    target: dict,
) -> int | None:
    """Find first prefix where this final B1P/S1P candidate is observable."""
    start = max(cs.CHAN_MIN_BARS - 1, int(target["source_confirm_index"]))
    for end in range(start, len(bars)):
        snap = cs.build_structure_snapshot(bars[: end + 1])
        for row in classify_b1_family(
            bars[: end + 1],
            snap,
            canonical=True,
        ):
            if row["subtype"] not in {"FIRST_CENTER", "OVERLAP_CENTER"}:
                continue
            if (
                row["level"] == target["level"]
                and row["base_kind"] == target["base_kind"]
                and row["anchor_index"] == target["anchor_index"]
                and row["subtype"] == target["subtype"]
            ):
                return end
    return None


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def round_or_none(value: float | None, digits: int = 6):
    return None if value is None else round(float(value), digits)


def evaluate_event(
    bars: list[cs.RawBar],
    row: dict,
    confirm_index: int,
    final_snapshot: dict,
) -> dict:
    out = dict(row)
    out["first_observed_index"] = int(confirm_index)
    out["first_observed_date"] = bars[confirm_index].date
    out["source_confirm_date"] = bars[row["source_confirm_index"]].date
    out["anchor_date"] = bars[row["anchor_index"]].date
    out["observation_delay_bars"] = int(confirm_index - row["source_confirm_index"])

    entry_index = confirm_index + 1
    out["entry_index"] = entry_index if entry_index < len(bars) else None
    if entry_index >= len(bars):
        out["entry_date"] = None
        return out

    entry = float(bars[entry_index].open)
    out["entry_date"] = bars[entry_index].date
    out["entry_price"] = entry
    is_buy = row["base_kind"] == "B1"

    for horizon in HORIZONS:
        target_index = entry_index + horizon - 1
        if target_index >= len(bars):
            continue
        window = bars[entry_index : target_index + 1]
        close_ret = float(bars[target_index].close) / entry - 1.0
        signed_ret = close_ret if is_buy else -close_ret

        if is_buy:
            mfe = max(float(x.high) / entry - 1.0 for x in window)
            mae = min(float(x.low) / entry - 1.0 for x in window)
        else:
            mfe = max(1.0 - float(x.low) / entry for x in window)
            mae = min(1.0 - float(x.high) / entry for x in window)

        out[f"ret_{horizon}"] = signed_ret
        out[f"mfe_{horizon}"] = mfe
        out[f"mae_{horizon}"] = mae

    # Structural outcomes over the next 40 bars.
    max_end = min(len(bars) - 1, entry_index + 39)
    center_idx = None
    extreme_idx = None
    for i in range(entry_index, max_end + 1):
        bar = bars[i]
        if center_idx is None:
            if is_buy and float(bar.high) >= row["ZD"]:
                center_idx = i
            elif (not is_buy) and float(bar.low) <= row["ZG"]:
                center_idx = i
        if extreme_idx is None:
            if is_buy and float(bar.low) < row["leave_low"]:
                extreme_idx = i
            elif (not is_buy) and float(bar.high) > row["leave_high"]:
                extreme_idx = i

    out["center_return_40"] = center_idx is not None
    out["new_extreme_40"] = extreme_idx is not None
    if center_idx is None and extreme_idx is None:
        out["path_40"] = "NEITHER"
    elif center_idx is None:
        out["path_40"] = "EXTREME_ONLY"
    elif extreme_idx is None:
        out["path_40"] = "CENTER_ONLY"
    elif center_idx < extreme_idx:
        out["path_40"] = "CENTER_FIRST"
    elif extreme_idx < center_idx:
        out["path_40"] = "EXTREME_FIRST"
    else:
        out["path_40"] = "SAME_BAR"

    follow_kind = "B2" if is_buy else "S2"
    follow = False
    for signal in final_snapshot["signals"]:
        if (
            int(signal["level"]) == int(row["level"])
            and signal["kind"] == follow_kind
            and entry_index <= int(signal["anchor_index"]) <= max_end
        ):
            follow = True
            break
    out["same_level_b2s2_follow_40"] = follow
    return out


def summarize(rows: list[dict]) -> dict:
    result: dict = {
        "count": len(rows),
        "symbols": len({x["symbol"] for x in rows}),
        "kinds": dict(Counter(x["kind"] for x in rows)),
        "subtypes": dict(Counter(x["subtype"] for x in rows)),
    }
    if not rows:
        return result

    delays = [float(x["observation_delay_bars"]) for x in rows if "observation_delay_bars" in x]
    if delays:
        result["observation_delay_bars"] = {
            "mean": round_or_none(statistics.fmean(delays)),
            "median": round_or_none(statistics.median(delays)),
            "p75": round_or_none(percentile(delays, 0.75)),
            "max": round_or_none(max(delays)),
        }

    for horizon in HORIZONS:
        rr = [float(x[f"ret_{horizon}"]) for x in rows if f"ret_{horizon}" in x]
        mfe = [float(x[f"mfe_{horizon}"]) for x in rows if f"mfe_{horizon}" in x]
        mae = [float(x[f"mae_{horizon}"]) for x in rows if f"mae_{horizon}" in x]
        if rr:
            result[f"h{horizon}"] = {
                "n": len(rr),
                "win_rate": round_or_none(sum(x > 0 for x in rr) / len(rr)),
                "mean_return": round_or_none(statistics.fmean(rr)),
                "median_return": round_or_none(statistics.median(rr)),
                "p25_return": round_or_none(percentile(rr, 0.25)),
                "p75_return": round_or_none(percentile(rr, 0.75)),
                "mean_mfe": round_or_none(statistics.fmean(mfe)),
                "median_mfe": round_or_none(statistics.median(mfe)),
                "mean_mae": round_or_none(statistics.fmean(mae)),
                "median_mae": round_or_none(statistics.median(mae)),
            }

    structural = [x for x in rows if "center_return_40" in x]
    if structural:
        n = len(structural)
        result["structural_40"] = {
            "center_return_rate": round_or_none(sum(x["center_return_40"] for x in structural) / n),
            "new_extreme_rate": round_or_none(sum(x["new_extreme_40"] for x in structural) / n),
            "same_level_b2s2_follow_rate": round_or_none(
                sum(x["same_level_b2s2_follow_40"] for x in structural) / n
            ),
            "paths": dict(Counter(x["path_40"] for x in structural)),
        }
    return result


def static_evaluate(
    bars: list[cs.RawBar],
    row: dict,
    snapshot: dict,
) -> dict | None:
    # Comparator only: use the structure's own source confirmation, not a
    # prefix-replay first observation. This is intentionally labeled STATIC.
    confirm = int(row["source_confirm_index"])
    evaluated = evaluate_event(bars, row, confirm, snapshot)
    evaluated["observation_delay_bars"] = 0
    evaluated["causality_mode"] = "STATIC_SOURCE_CONFIRM"
    return evaluated


def main() -> None:
    b1p_rows: list[dict] = []
    standard_l1_rows: list[dict] = []
    standard_l0_rows: list[dict] = []
    rejected_opposite = Counter()
    symbols = 0

    for path in sorted(DATA_ROOT.glob("batch_*_stocks/*.csv.gz")):
        symbol = path.stem.replace(".csv", "")
        candles = load(path)
        bars = cs._validate_candles(candles)
        bars, _ = cs._slice_analysis_window(bars)
        snap = cs.build_structure_snapshot(bars)
        symbols += 1

        l1 = classify_b1_family(bars, snap, canonical=True)
        l0 = classify_b1_family(bars, snap, canonical=False)

        for row in l1:
            row = dict(row)
            row["symbol"] = symbol
            if row["subtype"] in {"FIRST_CENTER", "OVERLAP_CENTER"}:
                first = first_observed_index(bars, row)
                if first is None:
                    raise AssertionError(("candidate_not_observed", symbol, row))
                evaluated = evaluate_event(bars, row, first, snap)
                evaluated["symbol"] = symbol
                evaluated["causality_mode"] = "PREFIX_FIRST_OBSERVED"
                b1p_rows.append(evaluated)
            elif row["subtype"] == "STANDARD":
                evaluated = static_evaluate(bars, row, snap)
                if evaluated is not None:
                    evaluated["symbol"] = symbol
                    standard_l1_rows.append(evaluated)
            else:
                rejected_opposite[row["base_kind"]] += 1

        for row in l0:
            if row["subtype"] != "STANDARD":
                continue
            row = dict(row)
            row["symbol"] = symbol
            evaluated = static_evaluate(bars, row, snap)
            if evaluated is not None:
                evaluated["symbol"] = symbol
                standard_l0_rows.append(evaluated)

    print("CHAN_B1P_STUDY_SYMBOLS", symbols)
    print("CHAN_B1P_CANDIDATE_ROWS", len(b1p_rows))
    print("CHAN_B1P_OPPOSITE_LINK_REJECTED", dict(rejected_opposite))
    print("CHAN_B1P_SUMMARY", json.dumps(summarize(b1p_rows), sort_keys=True))
    print(
        "CHAN_B1P_FIRST_CENTER_SUMMARY",
        json.dumps(
            summarize([x for x in b1p_rows if x["subtype"] == "FIRST_CENTER"]),
            sort_keys=True,
        ),
    )
    print(
        "CHAN_B1P_OVERLAP_CENTER_SUMMARY",
        json.dumps(
            summarize([x for x in b1p_rows if x["subtype"] == "OVERLAP_CENTER"]),
            sort_keys=True,
        ),
    )
    print(
        "CHAN_STANDARD_L1_B1S1_STATIC_COMPARATOR",
        json.dumps(summarize(standard_l1_rows), sort_keys=True),
    )
    print(
        "CHAN_STANDARD_L0_B1S1_STATIC_COMPARATOR",
        json.dumps(summarize(standard_l0_rows), sort_keys=True),
    )
    print(
        "CHAN_B1P_EVENTS",
        json.dumps(
            [
                {
                    k: row.get(k)
                    for k in (
                        "symbol",
                        "kind",
                        "subtype",
                        "level",
                        "anchor_date",
                        "source_confirm_date",
                        "first_observed_date",
                        "entry_date",
                        "observation_delay_bars",
                        "ret_5",
                        "ret_10",
                        "ret_20",
                        "ret_40",
                        "mfe_20",
                        "mae_20",
                        "center_return_40",
                        "new_extreme_40",
                        "same_level_b2s2_follow_40",
                        "path_40",
                    )
                }
                for row in b1p_rows
            ],
            sort_keys=True,
        ),
    )


if __name__ == "__main__":
    main()
