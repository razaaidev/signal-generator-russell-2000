# Agent — weekly rank, part 1 of 2 (Saturday)

Cron: `0 8 * * 6` · silent on success

---

Weekly universe rank, PART 1 of 2. No email unless it fails.

## Load
`rulebook/signal-rulebook.md` (the rules) and `universe/eligible-universe.md` (the
universe). If either is unreadable, email `{{YOUR_EMAIL}}` with subject
"Signal Gen - RULEBOOK UNREADABLE", say which, and stop.

## Scope
The **top 300 by index weight** (ranks 1–300). These and only these. Never query a
symbol from the NOT TRADEABLE list at the foot of the universe file.

## Data discipline
One daily OHLCV call per symbol, `interval 1day`, `outputsize 260` — one call gives
everything needed. No per-indicator endpoints. The per-minute rate limit is the
binding constraint, so expect roughly 40 minutes and pace accordingly. Out of
budget? Stop, record what completed, and say so.

Pull the index ETF's 260-day series once, for the relative-strength factor.

## Compute locally, per symbol
close · 20-day SMA · 50-day SMA · sigma (20-day standard deviation of daily
returns) · 20-day average dollar volume · momentum (126-day return excluding the
most recent 21 days) · relative strength (63-day return minus the index ETF's) ·
risk-adjusted momentum (momentum ÷ annualised volatility) · proximity to the
52-week high.

Apply gates G1, G2, G4, G5. Record gate results per name.

## Write
Store the raw metrics for all 300 to `rankwork/part1`:

```json
{"rankedAt": "<ISO>", "part": 1, "count": 300, "indexRs63": 0.0,
 "rows": [{"symbol","t212","close","sma20","sma50","sigma","dollarVol",
           "mom126_21","rs63","riskAdjMom","pctOf52wHigh","g1","g2","g4","g5"}]}
```

Do not compute z-scores yet — part 2 does that across both halves together.
