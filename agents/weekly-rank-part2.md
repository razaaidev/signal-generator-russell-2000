# Agent — weekly rank, part 2 of 2, and shortlist (Sunday)

Cron: `0 8 * * 0` · emails on success

---

Weekly universe rank, PART 2 of 2, then build the shortlist.

## Load
`rulebook/signal-rulebook.md` and `universe/eligible-universe.md`. If either is
unreadable, email `{{YOUR_EMAIL}}` with subject "Signal Gen - RULEBOOK UNREADABLE"
and stop.

## Scope
**Ranks 301–600 by index weight.** Never query anything on the NOT TRADEABLE list.

## Data discipline
As part 1: one daily OHLCV call per symbol, `outputsize 260`, no per-indicator
endpoints. The per-minute limit is what makes this slow — expect ~40 minutes. Stop
and report if the daily budget runs out.

## Compute
The same metrics and gates as part 1.

## Merge and rank
Read `rankwork/part1`. Missing or older than 8 days? Say so in the email and rank
on part 2 alone rather than silently ranking half a universe.

Combine both halves. Drop every name failing any gate. Across the survivors compute
z-scores for the four Part C factors, equal-weight them into a composite, and
subtract 0.5 for each gate WARNING.

Write the top 40 to `shortlist/current`, and the same object to
`shortlist/<YYYY-MM-DD>` so history accumulates:

```json
{"rankedAt","universeSize","gatesFailed",
 "names":[{"symbol","broker","score","z":{"mom","rs","riskAdj","high52"},
           "sigma","dollarVol","close","sma20","sma50","nextEarnings"}]}
```

Refresh GBP/USD once and store it for the desk.

## Email
Subject "Signal Gen - weekly shortlist", under 250 words: how many names were
scored and how many each gate dropped · the top 10 with symbol, broker ticker,
composite score and strongest factor · anything UNVERIFIED and whether the credit
budget held · one line if open positions carry into the new week · the Part J
closing block.
