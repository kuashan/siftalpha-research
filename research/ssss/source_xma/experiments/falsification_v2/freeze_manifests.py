#!/usr/bin/env python3
"""Generate deterministic v2 freeze manifests from already-persisted artifacts.

No data download and no hypothesis computation occurs here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest_for_files(files: Iterable[Path], root: Path) -> list[dict]:
    out = []
    for p in sorted(files, key=lambda x: str(x)):
        if not p.exists() or not p.is_file():
            raise FileNotFoundError(p)
        out.append({
            "path": str(p.relative_to(root)),
            "bytes": p.stat().st_size,
            "sha256": sha256(p),
        })
    return out


def write_manifest(kind: str, root: Path, files: list[Path], output: Path, metadata: dict) -> None:
    payload = {
        "schema": 1,
        "kind": kind,
        "metadata": metadata,
        "files": manifest_for_files(files, root),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--kind", required=True, choices=["data", "code"])
    p.add_argument("--root", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--file", action="append", dest="files", required=True)
    p.add_argument("--metadata-json", default="{}")
    return p.parse_args()


def main() -> None:
    a = parse_args()
    root = Path(a.root).resolve()
    files = [(root / x).resolve() for x in a.files]
    for f in files:
        if root not in f.parents and f != root:
            raise SystemExit(f"file outside root: {f}")
    metadata = json.loads(a.metadata_json)
    write_manifest(a.kind, root, files, Path(a.output), metadata)


if __name__ == "__main__":
    main()
