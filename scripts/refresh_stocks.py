"""
Refresh data/stocks.json from Yahoo Finance.

Behavior:
- Reads tickers + curated fields from data/tickers.json (sector, stage, score,
  trigger, evidence, invalidation, capacity, redFlags).
- Pulls last 4 quarters of revenue/EBITDA/PAT from yfinance income_stmt.
- Pulls current price from yfinance fast_info.
- Computes growth rates (rev/ebitda/pat, accel) and writes back into
  data/stocks.json alongside the curated fields the app already renders.
- On any ticker failure, keeps the existing values from data/stocks.json
  so a transient API hiccup never blanks out your dashboard.
"""

from __future__ import annotations

import json
import math
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
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


def growth_series(series: list[float | None]) -> list[float | None]:
    """Per-quarter YoY growth (%) of a 4-quarter series."""
    out: list[float | None] = [None, None, None, None]
    if not series or any(v is None for v in series):
        return out
    for i in range(1, 4):
        prev, cur = series[i - 1], series[i]
        if prev is None or cur is None or prev <= 0:
            continue
        out[i] = round((cur / prev - 1.0) * 100.0, 1)
    return out


def last4_quarterly(tkr: yf.Ticker) -> dict[str, list[float | None]]:
    """Return last 4 quarters of revenue, EBITDA, PAT, operating-margin series."""
    fields = {
        "rev": "Total Revenue",
        "ebitda": "EBITDA",
        "pat": "Net Income",
    }
    out = {k: [None] * 4 for k in fields}
    try:
        inc = tkr.quarterly_income_stmt
    except Exception:
        inc = None
    if inc is None or inc.empty:
        return out

    cols = list(inc.columns[:4])  # yfinance returns most-recent first
    cols = cols[::-1]              # chronological order
    for key, row_name in fields.items():
        if row_name not in inc.index:
            continue
        vals: list[float | None] = []
        for c in cols:
            v = inc.loc[row_name, c]
            try:
                f = float(v)
                if math.isnan(f):
                    vals.append(None)
                else:
                    vals.append(f)
            except (TypeError, ValueError):
                vals.append(None)
        while len(vals) < 4:
            vals.insert(0, None)
        out[key] = vals[-4:]
    return out


def latest_margin_pct(tkr: yf.Ticker, rev_q: list[float | None], ebd_q: list[float | None]) -> float | None:
    # Prefer yfinance-reported operating margin; otherwise derive EBITDA margin.
    try:
        inc = tkr.quarterly_income_stmt
        if inc is not None and not inc.empty and "Operating Margin" in inc.index:
            v = inc["Operating Margin"].iloc[0]
            f = float(v)
            if not math.isnan(f):
                return round(f * 100.0, 1)
    except Exception:
        pass
    if rev_q and ebd_q and rev_q[-1] and ebd_q[-1] and rev_q[-1] > 0:
        return round(ebd_q[-1] / rev_q[-1] * 100.0, 1)
    return None


def current_price(tkr: yf.Ticker) -> float | None:
    try:
        fi = tkr.fast_info
        p = fi.get("last_price") or fi.get("regular_market_price")
        if p:
            return round(float(p), 2)
    except Exception:
        pass
    try:
        hist = tkr.history(period="5d", auto_adjust=False)
        if not hist.empty:
            return round(float(hist["Close"].dropna().iloc[-1]), 2)
    except Exception:
        pass
    return None


def refresh_one(entry: dict) -> dict:
    symbol = entry["symbol"]
    yf_symbol = entry.get("yf") or f"{symbol}.NS"
    print(f"  - {symbol} ({yf_symbol})")
    tkr = yf.Ticker(yf_symbol)

    q = last4_quarterly(tkr)
    rev_g = growth_series(q["rev"])
    ebd_g = growth_series(q["ebitda"])
    pat_g = growth_series(q["pat"])
    margin = latest_margin_pct(tkr, q["rev"], q["ebitda"])
    price = current_price(tkr)

    latest_rev = next((v for v in reversed(q["rev"]) if v is not None), None)
    latest_ebd = next((v for v in reversed(q["ebitda"]) if v is not None), None)
    latest_pat = next((v for v in reversed(q["pat"]) if v is not None), None)

    out = dict(entry)
    out["rev"] = rev_g[-1] if rev_g[-1] is not None else entry.get("rev")
    out["ebitda"] = ebd_g[-1] if ebd_g[-1] is not None else entry.get("ebitda")
    out["pat"] = pat_g[-1] if pat_g[-1] is not None else entry.get("pat")
    out["margin"] = margin if margin is not None else entry.get("margin")
    out["price"] = price if price is not None else entry.get("price")
    out["series"] = {
        "rev": [None if v is None else round(v, 1) for v in q["rev"]],
        "ebitda": [None if v is None else round(v, 1) for v in q["ebitda"]],
        "pat": [None if v is None else round(v, 1) for v in q["pat"]],
        "margin": [None] * 4 if margin is None else [
            None, None, None, margin
        ],
    }
    return out


def main() -> int:
    tickers = load(TICKERS_PATH)
    if STOCKS_PATH.exists():
        existing = {row["symbol"]: row for row in load(STOCKS_PATH)}
    else:
        # First run: seed stocks.json from the tickers list so the app
        # has something to render before yfinance returns.
        save(STOCKS_PATH, tickers)
        existing = {row["symbol"]: row for row in tickers}
    refreshed: list[dict] = []
    failures = 0
    for entry in tickers:
        # Carry forward any curated field the refresh script doesn't touch.
        merged = {**existing.get(entry["symbol"], {}), **entry}
        try:
            row = refresh_one(merged)
        except Exception as exc:
            failures += 1
            print(f"    ! refresh failed for {entry['symbol']}: {exc}")
            row = merged
        row["refreshed_at"] = date.today().isoformat()
        refreshed.append(row)
        time.sleep(0.2)  # be polite to Yahoo
    save(STOCKS_PATH, refreshed)
    print(f"Done. {len(refreshed) - failures}/{len(refreshed)} tickers refreshed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())