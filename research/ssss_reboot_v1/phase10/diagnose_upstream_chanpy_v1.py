from __future__ import annotations

import csv
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DATA_ROOT = REPO / "research" / "ssss_reboot_v1" / "phase7" / "data_snapshot"
UPSTREAM = Path("/tmp/chanpy")
sys.path.insert(0, str(UPSTREAM))

from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_FIELD, KL_TYPE
from Common.CTime import CTime
from KLine.KLine_Unit import CKLine_Unit


def load(path: Path) -> list[dict]:
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.append({
                "date": r["Date"][:10],
                "open": float(r["Open"]),
                "high": float(r["High"]),
                "low": float(r["Low"]),
                "close": float(r["Close"]),
                "volume": float(r.get("Volume") or 0.0),
            })
    return out


def klu(row: dict) -> CKLine_Unit:
    y, m, d = [int(x) for x in row["date"].split("-")]
    return CKLine_Unit({
        DATA_FIELD.FIELD_TIME: CTime(y, m, d, 0, 0, auto=False),
        DATA_FIELD.FIELD_OPEN: row["open"],
        DATA_FIELD.FIELD_HIGH: row["high"],
        DATA_FIELD.FIELD_LOW: row["low"],
        DATA_FIELD.FIELD_CLOSE: row["close"],
        DATA_FIELD.FIELD_VOLUME: row["volume"],
    })


def main() -> None:
    total = Counter()
    per_symbol = []
    all_bsp_types = Counter()
    all_seg_bsp_types = Counter()

    for path in sorted(DATA_ROOT.glob("batch_*_stocks/*.csv.gz")):
        symbol = path.stem.replace(".csv", "")
        rows = load(path)

        config = CChanConfig({
            "trigger_step": True,
        })
        chan = CChan(
            code=symbol,
            lv_list=[KL_TYPE.K_DAY],
            config=config,
            autype=AUTYPE.NONE,
        )

        # Strictly incremental: feed one bar at a time.
        for row in rows:
            chan.trigger_load({KL_TYPE.K_DAY: [klu(row)]})

        kl = chan[0]
        bis = len(kl.bi_list)
        segs = len(kl.seg_list)
        zss = len(kl.zs_list)

        bsps = kl.bs_point_lst.getSortedBspList()
        bsp_types = Counter()
        buy_count = 0
        sell_count = 0
        sure_bi = sum(1 for x in kl.bi_list if x.is_sure)
        sure_seg = sum(1 for x in kl.seg_list if x.is_sure)
        virtual_seg = segs - sure_seg

        for p in bsps:
            buy_count += int(bool(p.is_buy))
            sell_count += int(not bool(p.is_buy))
            for t in p.type:
                bsp_types[t.value] += 1
                all_bsp_types[t.value] += 1

        seg_bsps = kl.seg_bs_point_lst.getSortedBspList()
        seg_bsp_types = Counter()
        for p in seg_bsps:
            for t in p.type:
                seg_bsp_types[t.value] += 1
                all_seg_bsp_types[t.value] += 1

        total["symbols"] += 1
        total["bars"] += len(rows)
        total["bis"] += bis
        total["sure_bis"] += sure_bi
        total["segments"] += segs
        total["sure_segments"] += sure_seg
        total["virtual_segments"] += virtual_seg
        total["zss"] += zss
        total["bsps"] += len(bsps)
        total["seg_bsps"] += len(seg_bsps)
        total["symbols_with_bsp"] += int(bool(bsps))
        total["symbols_with_seg_bsp"] += int(bool(seg_bsps))

        per_symbol.append({
            "symbol": symbol,
            "bars": len(rows),
            "bis": bis,
            "sure_bis": sure_bi,
            "segments": segs,
            "sure_segments": sure_seg,
            "virtual_segments": virtual_seg,
            "zss": zss,
            "bsp_count": len(bsps),
            "bsp_types": dict(sorted(bsp_types.items())),
            "seg_bsp_count": len(seg_bsps),
            "seg_bsp_types": dict(sorted(seg_bsp_types.items())),
            "buy_count": buy_count,
            "sell_count": sell_count,
        })

    print("CHANPY_UPSTREAM_SHA", "429d6ed3043e27c93a003ba2b10e70a05575e1f5")
    print("CHANPY_TOTAL", json.dumps(dict(total), sort_keys=True))
    print("CHANPY_BSP_TYPES", json.dumps(dict(sorted(all_bsp_types.items())), sort_keys=True))
    print("CHANPY_SEG_BSP_TYPES", json.dumps(dict(sorted(all_seg_bsp_types.items())), sort_keys=True))
    print("CHANPY_PER_SYMBOL", json.dumps(per_symbol, sort_keys=True))


if __name__ == "__main__":
    main()
