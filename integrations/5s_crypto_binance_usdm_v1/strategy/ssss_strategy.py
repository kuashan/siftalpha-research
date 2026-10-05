from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import base64
from hashlib import sha256
import math
from pathlib import Path
import re
from threading import RLock
from typing import Any, Iterable

SSSS_SOURCE_PATH = Path(__file__).with_name("SSSS.ftindex")
SSSS_SOURCE_B64_PATH = Path(__file__).with_name("SSSS.ftindex.b64")
SSSS_SOURCE_SHA256 = "25f8c56075c0021dd2d0567401d37def25d6a9b895f139b3a8a9abc376fecaa7"
SSSS_CLOSED_BAR_LIMIT = 1000
_ANALYSIS_CACHE_MAX = 8



@dataclass(frozen=True)
class SSSSBar:
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    values: dict[str, float]
    buy_icon_9: bool
    exit_icon_15: bool


@dataclass(frozen=True)
class SSSSAnalysis:
    bars: tuple[SSSSBar, ...]

    @property
    def latest(self) -> SSSSBar | None:
        return self.bars[-1] if self.bars else None

    def overlay(self, *, display_limit: int = SSSS_CLOSED_BAR_LIMIT) -> list[dict[str, object]]:
        bars = self.bars
        if display_limit > 0:
            bars = bars[-int(display_limit):]
        out: list[dict[str, object]] = []
        for bar in bars:
            v = bar.values
            state = (
                "GRAY" if _truth(v["GZB14"])
                else "BLUE" if _truth(v["GZB12"])
                else "RED" if _truth(v["GZB13"])
                else "OTHER"
            )
            out.append({
                "open_time": bar.open_time, "state": state,
                "GZB3": _json_number(v["GZB3"]), "GZB4": _json_number(v["GZB4"]),
                "ZK1": _json_number(v["ZK1"]), "ZD1": _json_number(v["ZD1"]),
                "BS": _json_number(v["BS"]), "BD": _json_number(v["BD"]),
                "buy_icon_9": bar.buy_icon_9, "exit_icon_15": bar.exit_icon_15,
            })
        return out


_ANALYSIS_CACHE: "OrderedDict[str, SSSSAnalysis]" = OrderedDict()
_ANALYSIS_CACHE_LOCK = RLock()


class SSSSFormulaError(RuntimeError):
    pass


def _source_bytes(path: Path = SSSS_SOURCE_PATH) -> bytes:
    if path.exists():
        return path.read_bytes()
    if path == SSSS_SOURCE_PATH and SSSS_SOURCE_B64_PATH.exists():
        return base64.b64decode(SSSS_SOURCE_B64_PATH.read_text(encoding="ascii"))
    raise SSSSFormulaError(f"找不到 SSSS 原始指标文件: {path}")


def source_sha256(path: Path = SSSS_SOURCE_PATH) -> str:
    return sha256(_source_bytes(path)).hexdigest()


def load_formula_source(path: Path = SSSS_SOURCE_PATH) -> str:
    data = _source_bytes(path)
    digest = sha256(data).hexdigest()
    if path == SSSS_SOURCE_PATH and digest != SSSS_SOURCE_SHA256:
        raise SSSSFormulaError(
            f"SSSS.ftindex 原始文件校验失败: {digest} != {SSSS_SOURCE_SHA256}"
        )
    text = data.decode("utf-8", errors="ignore")
    start = text.find("{====================")
    last = text.rfind("DRAWICON(")
    if start < 0 or last < 0:
        raise SSSSFormulaError("无法从 SSSS.ftindex 提取指标公式")
    end = text.find(";", last)
    if end < 0:
        raise SSSSFormulaError("SSSS.ftindex 最后一个 DRAWICON 语句不完整")
    return text[start : end + 1]


def _strip_comments(source: str) -> str:
    return re.sub(r"\{.*?\}", "", source, flags=re.S)


def _split_top_level(text: str, delimiter: str = ",") -> list[str]:
    out: list[str] = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == delimiter and depth == 0:
            out.append(text[start:i].strip())
            start = i + 1
    out.append(text[start:].strip())
    return out


def _statements(source: str) -> list[str]:
    clean = _strip_comments(source)
    return [x.strip() for x in clean.split(";") if x.strip()]


_TOKEN_RE = re.compile(
    r"\s*(?:(\d+(?:\.\d+)?)|([A-Za-z_][A-Za-z0-9_]*)|(>=|<=|<>|:=|[()+\-*/=><,]))"
)


def _tokenize(expr: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    pos = 0
    while pos < len(expr):
        m = _TOKEN_RE.match(expr, pos)
        if not m:
            fragment = expr[pos : pos + 40]
            raise SSSSFormulaError(f"无法解析公式片段: {fragment!r}")
        number, ident, op = m.groups()
        if number is not None:
            tokens.append(("NUMBER", number))
        elif ident is not None:
            upper = ident.upper()
            if upper in {"AND", "OR"}:
                tokens.append((upper, upper))
            else:
                tokens.append(("IDENT", upper))
        else:
            tokens.append((op, op))
        pos = m.end()
    tokens.append(("EOF", ""))
    return tokens


class _Parser:
    def __init__(self, expr: str):
        self.tokens = _tokenize(expr)
        self.i = 0

    def _peek(self, kind: str | None = None) -> tuple[str, str] | bool:
        token = self.tokens[self.i]
        return token if kind is None else token[0] == kind

    def _take(self, kind: str | None = None) -> tuple[str, str]:
        token = self.tokens[self.i]
        if kind is not None and token[0] != kind:
            raise SSSSFormulaError(f"期望 {kind}，实际 {token[0]}:{token[1]}")
        self.i += 1
        return token

    def parse(self):
        node = self._parse_or()
        if not self._peek("EOF"):
            raise SSSSFormulaError(f"公式尾部存在未解析内容: {self._peek()}")
        return node

    def _parse_or(self):
        node = self._parse_and()
        while self._peek("OR"):
            self._take("OR")
            node = ("bin", "OR", node, self._parse_and())
        return node

    def _parse_and(self):
        node = self._parse_compare()
        while self._peek("AND"):
            self._take("AND")
            node = ("bin", "AND", node, self._parse_compare())
        return node

    def _parse_compare(self):
        node = self._parse_add()
        if self.tokens[self.i][0] in {">=", "<=", ">", "<", "=", "<>"}:
            op = self._take()[0]
            node = ("bin", op, node, self._parse_add())
        return node

    def _parse_add(self):
        node = self._parse_mul()
        while self.tokens[self.i][0] in {"+", "-"}:
            op = self._take()[0]
            node = ("bin", op, node, self._parse_mul())
        return node

    def _parse_mul(self):
        node = self._parse_unary()
        while self.tokens[self.i][0] in {"*", "/"}:
            op = self._take()[0]
            node = ("bin", op, node, self._parse_unary())
        return node

    def _parse_unary(self):
        if self.tokens[self.i][0] in {"+", "-"}:
            op = self._take()[0]
            return ("unary", op, self._parse_unary())
        return self._parse_primary()

    def _parse_primary(self):
        if self._peek("NUMBER"):
            return ("num", float(self._take("NUMBER")[1]))
        if self._peek("IDENT"):
            name = self._take("IDENT")[1]
            if self._peek("("):
                self._take("(")
                args = []
                if not self._peek(")"):
                    while True:
                        args.append(self._parse_or())
                        if self._peek(","):
                            self._take(",")
                            continue
                        break
                self._take(")")
                return ("call", name, tuple(args))
            return ("var", name)
        if self._peek("("):
            self._take("(")
            node = self._parse_or()
            self._take(")")
            return node
        raise SSSSFormulaError(f"无法解析表达式 token: {self._peek()}")


def _is_series(value: Any) -> bool:
    return isinstance(value, list)


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _series(value: Any, size: int) -> list[float]:
    if _is_series(value):
        if len(value) != size:
            raise SSSSFormulaError("公式序列长度不一致")
        return [float(x) for x in value]
    return [float(value)] * size


def _binary(left: Any, right: Any, op: str, size: int) -> list[float] | float:
    if not _is_series(left) and not _is_series(right):
        return _apply_scalar(float(left), float(right), op)
    xs, ys = _series(left, size), _series(right, size)
    return [_apply_scalar(a, b, op) for a, b in zip(xs, ys)]


def _truth(value: float) -> bool:
    return _finite(value) and abs(float(value)) > 1e-12


def _apply_scalar(a: float, b: float, op: str) -> float:
    if op == "+": return a + b
    if op == "-": return a - b
    if op == "*": return a * b
    if op == "/": return a / b if b != 0 else math.nan
    if op == ">=": return 1.0 if a >= b else 0.0
    if op == "<=": return 1.0 if a <= b else 0.0
    if op == ">": return 1.0 if a > b else 0.0
    if op == "<": return 1.0 if a < b else 0.0
    if op == "=": return 1.0 if a == b else 0.0
    if op == "<>": return 1.0 if a != b else 0.0
    if op == "AND": return 1.0 if _truth(a) and _truth(b) else 0.0
    if op == "OR": return 1.0 if _truth(a) or _truth(b) else 0.0
    raise SSSSFormulaError(f"不支持运算符: {op}")


def _period(value: Any, index: int = -1) -> int:
    raw = value[index] if _is_series(value) else value
    try:
        return max(1, int(round(float(raw))))
    except (TypeError, ValueError):
        return 1


def _ref(values: Any, periods: Any, size: int) -> list[float]:
    xs = _series(values, size)
    out: list[float] = []
    for i in range(size):
        j = i - _period(periods, i)
        out.append(xs[j] if j >= 0 else math.nan)
    return out


def _ema(values: Any, periods: Any, size: int) -> list[float]:
    xs = _series(values, size)
    out: list[float] = []
    current: float | None = None
    for i, value in enumerate(xs):
        if not _finite(value):
            out.append(math.nan)
            continue
        n = _period(periods, i)
        if current is None:
            current = float(value)
        else:
            alpha = 2.0 / (n + 1.0)
            current = alpha * float(value) + (1.0 - alpha) * current
        out.append(current)
    return out


def _xma(values: Any, periods: Any, size: int) -> list[float]:
    """Future-function XMA. Re-running with new bars can repaint history."""
    xs = _series(values, size)
    out: list[float] = []
    for i in range(size):
        n = _period(periods, i)
        left = (n - 1) // 2
        right = n - left - 1
        window = xs[max(0, i - left) : min(size, i + right + 1)]
        finite = [float(x) for x in window if _finite(x)]
        out.append(sum(finite) / len(finite) if finite else math.nan)
    return out


def _cross(left: Any, right: Any, size: int) -> list[float]:
    xs, ys = _series(left, size), _series(right, size)
    out = [0.0] * size
    for i in range(1, size):
        if not all(_finite(x) for x in (xs[i], ys[i], xs[i - 1], ys[i - 1])):
            continue
        if xs[i] > ys[i] and xs[i - 1] <= ys[i - 1]:
            out[i] = 1.0
    return out


def _eval(node: Any, env: dict[str, Any], size: int) -> Any:
    kind = node[0]
    if kind == "num":
        return node[1]
    if kind == "var":
        name = node[1]
        if name not in env:
            raise SSSSFormulaError(f"公式引用了未知变量: {name}")
        return env[name]
    if kind == "unary":
        value = _eval(node[2], env, size)
        return value if node[1] == "+" else _binary(0.0, value, "-", size)
    if kind == "bin":
        return _binary(_eval(node[2], env, size), _eval(node[3], env, size), node[1], size)
    if kind == "call":
        name = node[1]
        args = [_eval(x, env, size) for x in node[2]]
        if name == "REF" and len(args) == 2: return _ref(args[0], args[1], size)
        if name == "EMA" and len(args) == 2: return _ema(args[0], args[1], size)
        if name == "XMA" and len(args) == 2: return _xma(args[0], args[1], size)
        if name == "CROSS" and len(args) == 2: return _cross(args[0], args[1], size)
        raise SSSSFormulaError(f"SSSS 当前不支持函数 {name}/{len(args)}")
    raise SSSSFormulaError(f"未知 AST 节点: {node}")


def _assignment(statement: str) -> tuple[str, str] | None:
    if ":=" in statement:
        name, expr = statement.split(":=", 1)
        return name.strip().upper(), expr.strip()
    if ":" in statement and not statement.lstrip().upper().startswith(
        ("STICKLINE", "DRAWTEXT", "DRAWICON")
    ):
        name, rest = statement.split(":", 1)
        return name.strip().upper(), _split_top_level(rest, ",")[0]
    return None


def _drawicon(statement: str) -> tuple[str, int] | None:
    upper = statement.strip().upper()
    if not upper.startswith("DRAWICON(") or not upper.endswith(")"):
        return None
    parts = _split_top_level(statement[statement.find("(") + 1 : -1], ",")
    if len(parts) != 3:
        raise SSSSFormulaError(f"DRAWICON 参数异常: {statement}")
    return parts[0], int(round(float(parts[2])))


def _row_values(rows: Iterable[Any]) -> tuple[list[int], dict[str, list[float]]]:
    times: list[int] = []
    opens: list[float] = []
    highs: list[float] = []
    lows: list[float] = []
    closes: list[float] = []
    volumes: list[float] = []
    for row in rows:
        if isinstance(row, dict):
            times.append(int(row.get("open_time", row.get("openTime"))))
            opens.append(float(row["open"]))
            highs.append(float(row["high"]))
            lows.append(float(row["low"]))
            closes.append(float(row["close"]))
            volumes.append(float(row.get("volume", 0.0)))
        else:
            times.append(int(row[0]))
            opens.append(float(row[1]))
            highs.append(float(row[2]))
            lows.append(float(row[3]))
            closes.append(float(row[4]))
            volumes.append(float(row[5] if len(row) > 5 else 0.0))
    return times, {
        "O": opens, "OPEN": opens, "H": highs, "HIGH": highs,
        "L": lows, "LOW": lows, "C": closes, "CLOSE": closes,
        "V": volumes, "VOL": volumes, "VOLUME": volumes,
    }


def evaluate_ssss(rows: Iterable[Any], *, source_path: Path = SSSS_SOURCE_PATH) -> list[SSSSBar]:
    row_list = list(rows)
    if not row_list:
        return []
    times, env = _row_values(row_list)
    size = len(times)
    drawicons: list[tuple[Any, int]] = []

    for statement in _statements(load_formula_source(source_path)):
        assignment = _assignment(statement)
        if assignment is not None:
            name, expr = assignment
            env[name] = _eval(_Parser(expr).parse(), env, size)
            continue
        icon = _drawicon(statement)
        if icon is not None:
            condition, icon_id = icon
            drawicons.append((_eval(_Parser(condition).parse(), env, size), icon_id))

    critical = ["GZB3", "GZB4", "GZB10", "GZB11", "GZB12", "GZB13", "GZB14", "ZK1", "ZD1", "BS", "BD"]
    for name in critical:
        if name not in env:
            raise SSSSFormulaError(f"SSSS 原始公式缺少关键输出 {name}")

    out: list[SSSSBar] = []
    for i in range(size):
        buy = any(icon_id == 9 and _truth(_series(cond, size)[i]) for cond, icon_id in drawicons)
        exit_ = any(icon_id == 15 and _truth(_series(cond, size)[i]) for cond, icon_id in drawicons)
        values = {name: float(_series(env[name], size)[i]) for name in critical}
        out.append(SSSSBar(
            open_time=times[i], open=float(env["O"][i]), high=float(env["H"][i]),
            low=float(env["L"][i]), close=float(env["C"][i]), volume=float(env["V"][i]),
            values=values, buy_icon_9=buy, exit_icon_15=exit_,
        ))
    return out


def _json_number(value: float) -> float | None:
    return float(value) if _finite(value) else None


def closed_bar_window(
    rows: Iterable[Any],
    *,
    closed_limit: int = SSSS_CLOSED_BAR_LIMIT,
) -> list[Any]:
    """Return the exact closed-bar window shared by chart and automation.

    Binance kline endpoints include the current open candle as the last row.
    SSSS is therefore fed exactly the last 1000 *closed* candles.
    """
    row_list = list(rows)
    if len(row_list) < 2:
        return []
    closed = row_list[:-1]
    if closed_limit > 0:
        closed = closed[-int(closed_limit):]
    return closed


def _analysis_fingerprint(rows: list[Any]) -> str:
    digest = sha256()
    for row in rows:
        if isinstance(row, dict):
            values = (
                row.get("open_time", row.get("openTime")),
                row.get("open"),
                row.get("high"),
                row.get("low"),
                row.get("close"),
                row.get("volume", 0.0),
            )
        else:
            values = tuple(row[:6])
        digest.update(repr(values).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()


def clear_analysis_cache() -> None:
    with _ANALYSIS_CACHE_LOCK:
        _ANALYSIS_CACHE.clear()


def analyze_ssss(
    rows: Iterable[Any],
    *,
    source_path: Path = SSSS_SOURCE_PATH,
) -> SSSSAnalysis:
    """Single cached SSSS calculation entry used by chart and automation."""
    row_list = list(rows)
    # Alternate source files are test/research inputs and deliberately bypass
    # the runtime cache. Preserve the historical default-call signature so
    # existing evaluator test seams remain valid.
    if source_path != SSSS_SOURCE_PATH:
        return SSSSAnalysis(tuple(evaluate_ssss(row_list, source_path=source_path)))
    if not row_list:
        return SSSSAnalysis(tuple(evaluate_ssss(row_list)))

    key = _analysis_fingerprint(row_list)
    with _ANALYSIS_CACHE_LOCK:
        cached = _ANALYSIS_CACHE.get(key)
        if cached is not None:
            _ANALYSIS_CACHE.move_to_end(key)
            return cached

    analysis = SSSSAnalysis(tuple(evaluate_ssss(row_list)))
    with _ANALYSIS_CACHE_LOCK:
        _ANALYSIS_CACHE[key] = analysis
        _ANALYSIS_CACHE.move_to_end(key)
        while len(_ANALYSIS_CACHE) > _ANALYSIS_CACHE_MAX:
            _ANALYSIS_CACHE.popitem(last=False)
    return analysis


def chart_overlay(
    rows: Iterable[Any],
    *,
    display_limit: int = SSSS_CLOSED_BAR_LIMIT,
) -> list[dict[str, object]]:
    return analyze_ssss(rows).overlay(display_limit=display_limit)
