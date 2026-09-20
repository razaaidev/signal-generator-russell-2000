# Agent — midday screen (17:30 UK, weekdays)

Cron: `30 16 * * 1-5` while the UK is on BST · `30 17 * * 1-5` on GMT

---

Signal Generator — MIDDAY screen, 17:30 UK (12:30 New York), the midpoint of the
US session.

## Load
Read `rulebook/signal-rulebook.md` — the single source of truth, including Part J
on email conventions. If unreadable, email `{{YOUR_EMAIL}}` with subject
"Signal Gen - RULEBOOK UNREADABLE" and stop.

From the desk (`{{DESK_URL}}`): `shortlist/current`, `desk/state`, and
`signals/latest` (this morning's pre-open run, for comparison).

Confirm the market is open, working today's US hours in UK time out from the date.
Holiday or an early close already passed? Send nothing and stop.

## Why midday
The opening half-hour is the noisiest window of the day. By now three hours of
trading have set a more representative price, so a stop distance or a 20-day break
read here is likelier to be real than one read shortly after the open. Treat these
readings as the day's meaningful check.

## Non-negotiables
Same as the pre-open run. Long only; shortlist plus holdings; both tickers;
`stop% = 3.0 x sigma`; no targets or expected returns; leaving the top 5 is not a
sell signal.

## Data
One daily OHLCV call per symbol, `outputsize 260`, ~50 credits. Use live intraday
prices for the current quote; compute sigma and the moving averages from
**completed sessions only** — never let a partial day contaminate them.

## Email
Subject "Signal Generator - today's picks", under 400 words.

Open with the ACTION line exactly as in the pre-open run.

This run is otherwise about **change since the pre-open**: names that entered or
left the top 5, any gate that flipped, and in particular where a morning reading
has reversed by midday — that is the point of this slot. Nothing changed? Say "No
change since the pre-open run" in one line and keep the rest brief.

Then the TOP 5 as now, the "log them on the desk" line, open positions, data gaps,
and the Part J closing block.

Send separate alert emails on the same conditions as the pre-open run. Do not
repeat an alert already sent for the same position and reason today — check the
`alerts` collection first.

## Write back
As the pre-open run, with `signals/<YYYY-MM-DD>-MID` and `"slot":"MID"`.
