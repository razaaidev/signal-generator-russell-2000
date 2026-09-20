#!/usr/bin/env python3
"""
Build the eligible universe: Russell 2000 constituents that are actually
tradeable in a Trading 212 Stocks & Shares ISA.

Inputs
------
  t212_instruments.json : the array returned by
      GET https://live.trading212.com/api/v0/equity/metadata/instruments
      (HTTP Basic auth: API_KEY:API_SECRET -- see README)
  iwm_holdings.json     : an object with a "holdings" array of
      {"symbol", "description", "weight"} -- e.g. Alpha Vantage ETF_PROFILE
      for IWM, or any source giving Russell 2000 constituents and weights.

Output
------
  eligible-universe.md  : ranked, human-readable, with the untradeable tail
                          listed at the end so a screener can exclude it.

Why the matching is fiddly
--------------------------
Trading 212's `ticker` field preserves the symbol from the day the instrument
was added and goes stale after a rename or a SPAC merger. IonQ trades as
`DMYI_US_EQ`; ASGN now displays as `EFOR`; EchoStar sits under `SATS_US_EQ`.
Matching Russell symbols against the ticker PREFIX alone misclassified 233
names when this was first built -- in both directions, excluding names that
are available and matching others to entirely different companies.

So: match on `shortName` (the current symbol) first, ticker prefix second,
and record which route was used.
"""
import json, re, sys, collections
from pathlib import Path


def load_t212(path):
    """US common stock, USD, excluding warrants."""
    raw = json.loads(Path(path).read_text())
    by_short, by_prefix = {}, {}
    for x in raw:
        if x.get("type") != "STOCK" or x.get("currencyCode") != "USD":
            continue
        t = x.get("ticker", "")
        if not t.endswith("_US_EQ") or "WAR" in t:
            continue
        rec = {
            "t212Ticker": t,
            "prefix": t.split("_US_EQ")[0],
            "short": (x.get("shortName") or "").strip().upper(),
            "isin": x.get("isin"),
            "name": x.get("name"),
            "maxQty": x.get("maxOpenQuantity"),
            "extendedHours": x.get("extendedHours"),
            "addedOn": (x.get("addedOn") or "")[:10],
        }
        if rec["short"]:
            by_short.setdefault(rec["short"], rec)
        by_prefix.setdefault(rec["prefix"], rec)
    return by_short, by_prefix


def load_constituents(path):
    """Valid equity tickers and index weights from an ETF holdings dump."""
    data = json.loads(Path(path).read_text())
    out = {}
    for h in data.get("holdings", []):
        s = (h.get("symbol") or "").strip().upper()
        # drop cash lines, futures and anything that isn't a plain ticker
        if not s or s == "N/A" or not re.fullmatch(r"[A-Z][A-Z0-9.]{0,6}", s):
            continue
        out[s] = {
            "symbol": s,
            "name": h.get("description"),
            "weight": float(h.get("weight") or 0),
        }
    return out


def build(t212_path, holdings_path):
    by_short, by_prefix = load_t212(t212_path)
    cons = load_constituents(holdings_path)

    universe, missing = {}, []
    how = collections.Counter()
    for sym, v in cons.items():
        if sym in by_short:
            rec, via = by_short[sym], "shortName"
        elif sym in by_prefix:
            rec, via = by_prefix[sym], "legacyTicker"
        else:
            missing.append(sym)
            how["absent"] += 1
            continue
        how[via] += 1
        universe[sym] = {**v, **rec, "matchedBy": via,
                         "symbolAgrees": rec["short"] == sym}
    return universe, sorted(missing), how, len(cons)


def write_markdown(universe, missing, how, n_cons, out_path):
    rows = sorted(universe.values(), key=lambda x: -x["weight"])
    total_w = sum(v["weight"] for v in universe.values()) or 1
    cons_w = total_w + 0  # weights of matched names only; see note below

    L = [
        "# ELIGIBLE UNIVERSE - Russell 2000 tradeable in a Trading 212 ISA",
        "#",
        f"# {n_cons} valid constituents -> {len(universe)} tradeable "
        f"({len(universe)/n_cons:.1%}).",
        f"# {len(missing)} not offered by Trading 212; listed at the end and never queried.",
        f"# Matched via current symbol: {how['shortName']}; "
        f"via stale ticker prefix: {how['legacyTicker']}.",
        "#",
        "# `t212Ticker` is what you search in the app. `current` is the symbol it",
        "# displays now - these differ after a rename, so always show both.",
        "#",
        "# rank | symbol | t212Ticker | current | idxWeight% | matchedBy | name",
    ]
    for i, x in enumerate(rows, 1):
        L.append(f"{i} | {x['symbol']} | {x['t212Ticker']} | {x['short']} | "
                 f"{x['weight']*100:.4f} | {x['matchedBy']} | {x['name']}")
    L += ["", f"## NOT TRADEABLE - never query these ({len(missing)})", ", ".join(missing), ""]
    Path(out_path).write_text("\n".join(L))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__ + "\nusage: build_universe.py <t212_instruments.json> "
                           "<iwm_holdings.json> [out.md]")
    out = sys.argv[3] if len(sys.argv) > 3 else "eligible-universe.md"
    universe, missing, how, n = build(sys.argv[1], sys.argv[2])
    write_markdown(universe, missing, how, n, out)
    print(f"{len(universe)} tradeable of {n} constituents "
          f"({len(missing)} absent) -> {out}")
    print("matched:", dict(how))
    stale = [s for s, v in universe.items() if not v["symbolAgrees"]]
    if stale:
        print(f"note: {len(stale)} names whose T212 ticker ID is a dead symbol, e.g. "
              + ", ".join(f"{s}->{universe[s]['short']}" for s in stale[:5]))


if __name__ == "__main__":
    main()
