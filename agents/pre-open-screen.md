# Agent — pre-open screen (14:00 UK, weekdays)

Cron: `0 13 * * 1-5` while the UK is on BST · `0 14 * * 1-5` on GMT

---

Signal Generator — PRE-OPEN screen, 14:00 UK, 30 minutes before the US open.

## Load
Read `rulebook/signal-rulebook.md`. It is the single source of truth for gates,
ranking, sizing, alerts and email conventions. If unreadable, email
`{{YOUR_EMAIL}}` with subject "Signal Gen - RULEBOOK UNREADABLE" and stop.

From the desk (`{{DESK_URL}}`):
- `shortlist/current` — the ~40 names the weekly rank produced
- `desk/state` — cash, settings and open positions

If `shortlist/current` is missing or more than 9 days old, say so at the top of
the email and screen the open positions only. Do not improvise a universe.

## Non-negotiables
- LONG ONLY. No shorting inside an ISA. Never output a short.
- Shortlist names plus currently held positions only. Never query anything on the
  NOT TRADEABLE list in `universe/eligible-universe.md`.
- Report both the broker ticker to search and the symbol it currently displays.
- `stop% = 3.0 x the stock's 20-day daily sigma`. No fixed floor. No sigma, no pick.
- Never state a price target or an expected return.
- A name leaving the top 5 is NOT a sell signal. Holdings are governed by the stop
  and the 21-day cap only.

## Currency
Prices are USD; the account is sterling. Fetch GBP/USD once and store it. Size in £
first, then convert: a buy costs `(USD / rate) x 1.0015` because the broker charges
0.15% FX each way. Quote £ first, USD in brackets.

## Data
One daily OHLCV call per symbol, `outputsize 260`. ~40 shortlist names plus
positions ≈ 50 credits. No per-indicator endpoints. Anything unverifiable is
UNVERIFIED and fails its gate.

## Screen
Apply gates G1–G5 on the last completed close. Rank survivors by the Part C
composite. Take the TOP 5. For each compute stop price, position size in £ and the
resulting quantity from the account value on the desk.

## Position check
Per open position: current price, distance to stop, whether the close is below its
20-day SMA, trading days held against the 21-day cap, next earnings date.

No open positions? One line saying so, plus: "Nothing is being monitored — anything
you buy is invisible to this system until it is logged on the desk."

## Emails

**1. Always** — subject "Signal Generator - today's picks", under 400 words.

First line, before the header and before anything else (rulebook Part J):

```
ACTION: none required today.
```
or
```
ACTION: close <SYMBOL> today — <reason and the numbers>.
```

Rule-driven exits only: stop breached, 21-day cap reached, earnings inside 5
trading days. Several? Semicolons on the one line. Never a buy on the ACTION line;
a 20-day-SMA alert is not an ACTION.

Then: header (run time, today's US hours in UK time worked out from the date, any
holiday, the FX rate used) · regime (index ETF vs its 50-day, VIX) · the TOP 5, one
line each with composite score, the four z-scores, stop $ and %, size £ and max
hold date · the "log them on the desk" line · open positions · data gaps · the
Part J closing block.

Fewer than 5 pass every gate? List only those that do and say why the rest failed.
Never pad.

**2. Only when a position triggers an alert** (rulebook Part E) — a separate email,
subject "Signal Gen ALERT - <SYMBOL> <reason>". Two or three lines: what happened,
the numbers, what the rules say. One per alerting position. Note that the 20-day
rule is a heads-up, not an instruction to sell. Close with the same Part J block.

## Write back
- the refreshed FX rate
- `signals/latest` and `signals/<YYYY-MM-DD>-PRE`
- each position updated with lastPrice, lastAt, sigma, below20, nextEarnings —
  preserving every other field
- any alert appended to the `alerts` collection
