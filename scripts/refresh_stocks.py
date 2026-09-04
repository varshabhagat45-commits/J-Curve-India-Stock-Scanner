"""
Refresh data/stocks.json from Yahoo Finance, with hard fallbacks.

Behavior:
- Reads tickers + curated fields from data/tickers.json.
- Pulls last 4 quarters of revenue/EBITDA/PAT via yfinance.
  Falls back to a direct HTTP query against Yahoo's chart API
  (much more reliable from cloud IPs).
- Pulls current price; falls back to chart close.
- Never overwrites an existing non-null value with a null.
- Logs enough detail to diagnose any ticker failure in the run log.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
TICKERS_PATH = ROOT / "data" / "tickers.json"
STOCKS_PATH = ROOT / "data" / "stocks.json"


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: list[dict]) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def keep(existing, fresh):
    """Return fresh if it's not None, else existing. Used to never blank good data."""
    if fresh is None:
        return existing
    if isinstance(fresh, float) and math.isnan(fresh):
        return existing
    return fresh


def http_get_json(url: str, timeout: int = 15) -> dict | None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 j-curve-refresh/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        print(f"      http_get_json failed for {url}: {exc}")
        return None


def growth_series(series: list[float | None]) -> list[float | None]:
    out: list[float | None] = [None, None, None, None]
    if not series or any(v is None for v in series):
        return out
    for i in range(1, 4):
        prev, cur = series[i - 1], series[i]
        if prev is None or cur is None or prev <= 0:
            continue
        out[i] = round((cur / prev - 1.0) * 100.0, 1)
    return out


def fetch_via_yfinance(yf_symbol: str) -> dict:
    """Try yfinance Ticker; return whatever we get back."""
    tkr = yf.Ticker(yf_symbol)
    out: dict = {
        "rev_q": [None] * 4,
        "ebd_q": [None] * 4,
        "pat_q": [None] * 4,
        "margin": None,
        "price": None,
    }
    try:
        inc = tkr.quarterly_income_stmt
    except Exception as exc:
        print(f"      yfinance quarterly_income_stmt error: {exc}")
        inc = None
    if inc is not None and not inc.empty:
        cols = list(inc.columns[:4])[::-1]
        for key, row_name in [
            ("rev_q", "Total Revenue"),
            ("ebd_q", "EBITDA"),
            ("pat_q", "Net Income"),
        ]:
            if row_name in inc.index:
                vals: list[float | None] = []
                for c in cols:
                    try:
                        f = float(inc.loc[row_name, c])
                        vals.append(None if math.isnan(f) else f)
                    except Exception:
                        vals.append(None)
                while len(vals) < 4:
                    vals.insert(0, None)
                out[key] = vals[-4:]
        if "Operating Margin" in inc.index:
            try:
                f = float(inc["Operating Margin"].iloc[0])
                if not math.isnan(f):
                    out["margin"] = round(f * 100.0, 1)
            except Exception:
                pass
    try:
        fi = tkr.fast_info
        p = fi.get("last_price") or fi.get("regular_market_price")
        if p:
            out["price"] = round(float(p), 2)
    except Exception as exc:
        print(f"      yfinance fast_info error: {exc}")
    if out["price"] is None:
        try:
            hist = tkr.history(period="5d", auto_adjust=False)
            if not hist.empty:
                out["price"] = round(float(hist["Close"].dropna().iloc[-1]), 2)
        except Exception as exc:
            print(f"      yfinance history error: {exc}")
    return out


def _ymd_to_str(ts_ms) -> str:
    import datetime as _dt
    return _dt.datetime.utcfromtimestamp(ts_ms / 1000).strftime("%Y-%m-%d")


def fetch_via_http_v8(yf_symbol: str) -> dict:
    """Fallback using chart v8 with period1/period2 to get 1y price + fundamentals
    from the chart meta (only `regularMarketPrice` is reliably present)."""
    out: dict = {
        "rev_q": [None] * 4,
        "ebd_q": [None] * 4,
        "pat_q": [None] * 4,
        "margin": None,
        "price": None,
    }
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(yf_symbol)}"
        "?interval=1d&range=1y"
    )
    data = http_get_json(url)
    if data and data.get("chart", {}).get("result"):
        meta = (data["chart"]["result"][0] or {}).get("meta", {}) or {}
        p = meta.get("regularMarketPrice") or meta.get("previousClose")
        if p is not None:
            try:
                out["price"] = round(float(p), 2)
            except (TypeError, ValueError):
                pass
    return out


def fetch_via_http(yf_symbol: str) -> dict:
    """Direct HTTP fallback against Yahoo's chart API (more reliable from cloud IPs)."""
    out: dict = {
        "rev_q": [None] * 4,
        "ebd_q": [None] * 4,
        "pat_q": [None] * 4,
        "margin": None,
        "price": None,
    }
    # Price
    chart_url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(yf_symbol)}"
        "?interval=1d&range=5d"
    )
    data = http_get_json(chart_url)
    if data and data.get("chart", {}).get("result"):
        meta = data["chart"]["result"][0].get("meta", {}) or {}
        p = meta.get("regularMarketPrice") or meta.get("previousClose")
        if p is not None:
            try:
                out["price"] = round(float(p), 2)
            except (TypeError, ValueError):
                pass
    # Fundamentals: scraper endpoint (works from cloud IPs most of the time)
    fund_url = (
        f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{urllib.parse.quote(yf_symbol)}"
        "?modules=incomeStatementHistoryQuarterly"
    )
    data = http_get_json(fund_url)
    if data and data.get("quoteSummary", {}).get("result"):
        result = data["quoteSummary"]["result"][0]
        stmt = result.get("incomeStatementHistoryQuarterly", {}).get("incomeStatementHistory", [])
        # stmt is most-recent first
        stmt = list(stmt)[::-1][-4:]  # chronological, last 4
        for key, src_key in [
            ("rev_q", "totalRevenue"),
            ("ebd_q", "ebitda"),
            ("pat_q", "netIncome"),
        ]:
            vals: list[float | None] = []
            for q in stmt:
                v = q.get(src_key, {})
                if v and "raw" in v:
                    try:
                        f = float(v["raw"])
                        vals.append(None if math.isnan(f) else f)
                    except (TypeError, ValueError):
                        vals.append(None)
                else:
                    vals.append(None)
            while len(vals) < 4:
                vals.insert(0, None)
            out[key] = vals[-4:]
    return out


def refresh_one(entry: dict) -> dict:
    symbol = entry["symbol"]
    yf_symbol = entry.get("yf") or f"{symbol}.NS"
    print(f"  - {symbol} ({yf_symbol})")

    attempts = []
    for attempt_fn, name in [
        (lambda: fetch_via_yfinance(yf_symbol), "yfinance"),
        (lambda: fetch_via_http(yf_symbol), "http-summary"),
        (lambda: fetch_via_http_v8(yf_symbol), "http-v8"),
    ]:
        try:
            data = attempt_fn()
        except Exception as exc:
            print(f"      {name} threw: {exc}")
            data = None
        if data and any([
            data["rev_q"], data["ebd_q"], data["pat_q"],
            data["margin"] is not None, data["price"] is not None
        ]):
            attempts.append(data)
            non_null = sum(1 for v in [data["price"], data["margin"]] if v is not None)
            non_null += sum(1 for q in [data["rev_q"], data["ebd_q"], data["pat_q"]] for v in q if v is not None)
            if non_null >= 4:
                break
        time.sleep(0.3)

    if len(attempts) >= 2:
        merged = dict(attempts[0])
        for k in ["rev_q", "ebd_q", "pat_q", "margin", "price"]:
            v0, v1 = attempts[0].get(k), attempts[1].get(k)
            if k in ("rev_q", "ebd_q", "pat_q"):
                merged[k] = [a if a is not None else b for a, b in zip(v0 or [None]*4, v1 or [None]*4)]
            else:
                merged[k] = v0 if v0 is not None else v1
        if len(attempts) >= 3:
            v2 = attempts[2]
            for k in ["rev_q", "ebd_q", "pat_q", "margin", "price"]:
                v0 = merged.get(k)
                if k in ("rev_q", "ebd_q", "pat_q"):
                    merged[k] = [a if a is not None else b for a, b in zip(v0 or [None]*4, v2.get(k) or [None]*4)]
                else:
                    merged[k] = v0 if v0 is not None else v2.get(k)
        data = merged
    elif attempts:
        data = attempts[0]
    else:
        data = {"rev_q": [None]*4, "ebd_q": [None]*4, "pat_q": [None]*4, "margin": None, "price": None}

    rev_g = growth_series(data["rev_q"])
    ebd_g = growth_series(data["ebd_q"])
    pat_g = growth_series(data["pat_q"])

    margin = data["margin"]
    if margin is None and data["ebd_q"] and data["rev_q"]:
        if data["ebd_q"][-1] and data["rev_q"][-1] and data["rev_q"][-1] > 0:
            margin = round(data["ebd_q"][-1] / data["rev_q"][-1] * 100.0, 1)

    out = dict(entry)
    # Never overwrite existing non-null values with null
    out["rev"]    = keep(entry.get("rev"),    rev_g[-1])
    out["ebitda"] = keep(entry.get("ebitda"), ebd_g[-1])
    out["pat"]    = keep(entry.get("pat"),    pat_g[-1])
    out["margin"] = keep(entry.get("margin"), margin)
    out["price"]  = keep(entry.get("price"),  data["price"])
    out["series"] = {
        "rev":    [None if v is None else round(v, 1) for v in data["rev_q"]],
        "ebitda": [None if v is None else round(v, 1) for v in data["ebd_q"]],
        "pat":    [None if v is None else round(v, 1) for v in data["pat_q"]],
        "margin": [None] * 4 if margin is None else [None, None, None, margin],
    }
    print(
        f"      rev={out['rev']} ebitda={out['ebitda']} pat={out['pat']} "
        f"margin={out['margin']} price={out['price']}"
    )
    return out


def main() -> int:
    tickers = load(TICKERS_PATH)
    if STOCKS_PATH.exists():
        existing = {row["symbol"]: row for row in load(STOCKS_PATH)}
    else:
        save(STOCKS_PATH, tickers)
        existing = {row["symbol"]: row for row in tickers}

    refreshed: list[dict] = []
    failed: list[str] = []
    for entry in tickers:
        merged = {**existing.get(entry["symbol"], {}), **entry}
        try:
            row = refresh_one(merged)
        except Exception as exc:
            failed.append(entry["symbol"])
            print(f"    ! refresh failed for {entry['symbol']}: {exc}")
            row = merged
        row["refreshed_at"] = date.today().isoformat()
        refreshed.append(row)
        time.sleep(0.5)

    save(STOCKS_PATH, refreshed)
    print(f"Done. {len(refreshed) - len(failed)}/{len(refreshed)} tickers ok.")
    if failed:
        print(f"Failed tickers: {failed}")
    # Exit 0 even if some tickers failed; data is best-effort
    return 0


if __name__ == "__main__":
    sys.exit(main())