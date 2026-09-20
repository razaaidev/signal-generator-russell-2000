# SIGNAL GENERATOR RULEBOOK — US small-cap equities

The single source of truth. Every scheduled agent reads this file first and
follows it exactly; the prompts in `../agents/` carry only their own run-specific
instructions. Edit here, not there.

Universe file: `../universe/eligible-universe.md`
Desk: `{{DESK_URL}}`

---

## Purpose and limits

This agent **screens**. It ranks candidates on a disclosed factor composite and
reports the evidence. It does not forecast returns, does not express conviction,
and never says "buy".

Forbidden output: price targets, expected returns, "this will/should",
"strong buy", any ranking by expected profit, any claim of an edge.

**Buying is optional; selling is not.** Entries are the operator's judgement call
from a ranked screen. Exits are mechanical — a stop level or a day count — so the
agent states them as instructions, not information. Part J puts that distinction
at the top of every email.

---

## PART A — UNIVERSE

**U1 — Long only.** The reference account type (a UK Stocks & Shares ISA) does not
permit short positions, so every candidate is a long. In a downtrend the correct
output is fewer picks or none — never a short. Check your own account before
relaxing this.

**U2 — The eligible list.** Candidates come only from `eligible-universe.md`:
Russell 2000 constituents intersected with the instruments the broker actually
offers. Names absent from the broker are listed at the foot of that file and must
never be queried.

**U3 — Working depth: top 600 by index weight.** An API-budget decision, not a
judgement about the excluded names — see Part G. Raise the depth when the data
plan allows; the file is ranked, so this is one number.

**U4 — Identity.** A broker's internal instrument ID often preserves the ticker
from the day the instrument was listed and is never revised after a rename or a
SPAC merger. The ID still points at the right company; it just spells a symbol
that no longer exists publicly. Match on the broker's **current** display symbol
first, the legacy ID prefix second — matching on the prefix alone misclassified
233 names when this was built, in both directions. Every email line carries the
**broker ticker to search** and the **symbol it currently displays**.

**U5 — Re-verify quarterly.** Russell reconstitutes each June; brokers add and
drop instruments continuously. Rebuild the intersection every quarter, or sooner
if a pick cannot be found in the app.

---

## PART B — GATES

Each returns OK, WARNING or FAIL with one line of evidence. Any FAIL removes the
candidate.

**G1 — Trend.** Close above BOTH the 50-day and 20-day SMA.
- above both, ≥ 2% clear of the 50-day → OK
- above both but within 2% of the 50-day → WARNING
- below either → FAIL

**G2 — Liquidity.** 20-day average dollar volume.
- ≥ $5m/day → OK · $2–5m → WARNING · < $2m → FAIL

At a ~£25 position this is never about capacity; it is about the spread you pay.

**G3 — Event clearance.** No earnings inside the next 10 trading days.
- clear 10 days → OK · day 6–10 → WARNING · day 1–5 → FAIL

Report the actual next earnings date, or mark UNVERIFIED.

**G4 — Volatility and stop.**

```
sigma  = 20-day standard deviation of daily returns
stop%  = 3.0 x sigma
```

- sigma from ≥ 20 sessions → OK · 10–19 → WARNING · unavailable → FAIL

The 3.0 multiple is calibrated, not chosen for neatness: it is
volatility-invariant, touching ~33% of 21-day holds on both a 25%-vol and a
41%-vol cohort. Tighter multiples stop you out on noise without improving
returns. See `../research/FINDINGS.md`.

**G5 — Data freshness.** Every price used must be from the last completed
session. Anything stale or unavailable is UNVERIFIED and fails the gate it feeds.

---

## PART C — RANKING

Candidates passing every gate are scored on an equal-weight composite of four
z-scores, computed across the surviving set:

1. **Momentum** — 126-day return excluding the most recent 21 days.
2. **Relative strength** — 63-day return minus the index ETF's 63-day return.
3. **Risk-adjusted momentum** — factor 1 divided by annualised 20-day volatility.
4. **Proximity to the 52-week high** — current close ÷ 52-week high.

Report each name's four z-scores alongside its total. A WARNING on any gate
subtracts 0.5 from the composite. Present the **top 5**.

This is a screen. The composite says "these score highest on these four stated
measures today". It is not a forecast, and the factors are noisy — Part F
quantifies how noisy.

**A name leaving the top 5 is not a sell signal.** The ranking concerns
candidates, not holdings. Once a position exists it is governed by Part D's exits
and nothing else.

---

## PART D — SIZING, CURRENCY AND EXITS

```
sigma    = 20-day daily standard deviation
stop%    = 3.0 x sigma
size £   = min( 5% of account / stop% , 25% of account , available cash )
quantity = (size £ x rate / 1.0015) / price        (fractional shares assumed)
max loss = size x stop%
```

**Currency.** Prices are USD, the account is sterling. `rate` is GBP/USD (USD per
GBP), refreshed every run. The reference broker charges **0.15% FX each way** —
substitute your own rate:

- a buy costs `(USD amount / rate) x 1.0015`
- a sale nets `(USD amount / rate) x 0.9985`

Size in sterling first, then convert. Quote £ first with USD in brackets. Mark
open positions at the sell rate, so the account value never overstates itself by
the fee.

Maximum **4 concurrent positions**. On typical small-cap volatility the 25% cap
binds, so four positions is a fully-invested book. Risk-per-trade only becomes the
binding term when stop% exceeds 20%.

**Exit rules, in order:**

1. Stop hit — exit.
2. 21 trading days elapsed — exit.
3. Nothing else. No profit target, no trailing stop.

**The stop belongs with the broker, not in an email.** Place it as a real stop
order at entry. The emails report status twice a day; they are not a safety net
and cannot act between runs. A position whose stop exists only as a number in an
inbox is unprotected overnight and through every gap.

**The 20-day SMA is an alert, not an exit.** See Part E.

---

## PART E — POSITION MONITORING

Every run checks each open position and emails a **separate** alert — subject
distinct from the daily screen — when:

- the close is below its 20-day SMA (trend-change warning), or
- the stop has been breached (ACTION), or
- earnings now falls inside the next 5 trading days (ACTION), or
- the position reaches day 19 of 21 (exit due).

**Why the 20-day close is an alert and not an exit.** Tested directly: using it as
an exit rule cut the median month from £101.10 to £99.07, dropped break-even odds
from 57% to 45%, nearly doubled the chance of finishing below £90, and pushed
trading from 5.5 to 20 round trips a month — the friction alone costs 2–3% of the
account. On 40%-vol small caps a name closes below its 20-day constantly without
the trend actually breaking; it fires on 84% of positions within a month. As a
heads-up that is about 3.4 alerts a month across 4 positions, a reasonable cadence
to read. As an exit it is a shredder.

So the alert tells you to look. The stop and the 21-day cap decide.

---

## PART F — WHAT TO EXPECT

40,000 simulated months, block-bootstrapped from real daily returns of a
41%-annualised-volatility cohort, 0.6% round-trip costs, at the configuration
above. Figures are for a £100 starting stake — scale as you like, the
probabilities do not change.

| Directional hit rate | Median month | Break even | ≥ £110 | ≥ £120 | ≤ £90 | ≤ £75 |
|---|---|---|---|---|---|---|
| 50% (no skill) | £100.55 | 53.2% | 9.0% | 1.3% | 6.8% | 0.2% |
| 55% (good) | £101.19 | 57.4% | 9.8% | 1.2% | 5.7% | 0.2% |
| 60% (very good) | £101.90 | 61.7% | 11.2% | 1.4% | 5.0% | 0.1% |
| 65% (exceptional) | £102.46 | 65.8% | 12.3% | 1.5% | 4.1% | 0.1% |

**The honest reading: the gap between no skill and exceptional skill is about 2% a
month.** Most of the median outcome is market drift, not selection. The screen's
realistic contribution is a few tenths of a percent a month plus a meaningful
reduction in bad months — P(≤£90) falls from 6.8% to 4.1% across that skill range.

Two cautions. The sample period is 2013–18, a bull market, so the long-only
baseline is flattered; a flat or falling market shifts every row down. And the hit
rate is an **input**, not something the screen has been shown to achieve — treat
55% as an aspiration to be measured, not a property of the system.

The purpose of running this small is to find out whether the process is followed
and whether the hit rate is real. Judge it on adherence and on measured hit rate,
and revisit funding only after both look solid over several months.

---

## PART G — DATA BUDGET

Reference figures are for the Twelve Data free tier: **8 credits per minute, 800
per day, one credit per symbol.** Adjust for your own provider.

Two separate limits, and it is the **per-minute** one that shapes the design:

- 600 names = 600 credits — comfortably inside the 800/day cap
- but at 8/minute that is 75 minutes of wall clock, too long for one scheduled run

So the weekly rank is split into two passes of ~300 (≈38 minutes each) because of
run **duration**, not because 300 is a daily ceiling. Both passes can run on the
same day when the daily budget allows.

- Weekly rank, 600 names = 600 credits across 2 runs
- Daily screen, ~40 shortlist + open positions ≈ 50 credits per run
- Two daily runs ≈ 100 credits, leaving ample headroom

Pull raw daily OHLCV once per symbol and compute SMA, sigma, momentum and dollar
volume locally. Never call per-indicator endpoints — that multiplies credits for
no extra information. Batching symbols per call saves round trips, not credits or
rate-limit time.

If a run exhausts its budget, stop, report what was completed, and say so in the
email. Never fill gaps with estimates.

---

## PART H — RUN SCHEDULE

- **Weekly rank** (weekend, 2 parts): score the top 600, store the ~40-name shortlist.
- **Pre-open screen, 14:00 UK:** 30 minutes before the US open. Last completed
  close; the day's plan. Email the top 5 plus any position alerts.
- **Midday screen, 17:30 UK** (12:30 New York, the midpoint of the session):
  re-rank on live prices, email changes against the 14:00 list, re-check every
  position.

Why midday rather than shortly after the open: the first half-hour is the noisiest
window of the day — overnight imbalances clearing, gap fills, the opening auction
unwinding. A stop distance or a 20-day break measured at 15:00 is often an artefact
that has reversed by lunchtime. By 17:30 three hours of trading have set a more
representative price, so alerts are likelier to be real and entries face tighter
spreads. It also lands nearer the end of the UK working day, when acting on it is
practical.

This choice is only safe because the stop lives with the broker as a real order
(Part D). Protection is the broker's job and runs continuously; the email's job is
information, and information is better when the price it rests on is not noise.

All times UK local. Cron is evaluated in UTC, so the expressions shift by an hour
at each UK clock change — `../agents/clock-change.md` handles that automatically.

---

## PART I — REVIEW TRIGGERS

Revisit this rulebook when any of these is true:

- realised stop-out rate exceeds 45% over 20 trades (calibrated expectation ~33%)
- realised hit rate is below 45% over 30 trades — the composite is not working
- cohort volatility moves outside 25–55% annualised
- a quarterly universe rebuild changes the tradeable count by more than 10%

---

## PART J — EMAIL CONVENTIONS

### The ACTION line comes first

**Every picks email opens with a single line, before the header, before anything.**
It states what the rules require today, or that they require nothing. Exits are
mechanical, so this line is an instruction, not a summary.

When nothing is due:

```
ACTION: none required today.
```

When something is:

```
ACTION: close CRDO today — stop breached at $168.40 (stop $171.20).
```

Two or more? List them on that one line, separated by semicolons. Keep it to
rule-driven exits only: stop breached, 21-day cap reached, or earnings inside 5
trading days. **Never put a buy on the ACTION line** — buying is the operator's
call and belongs with the top 5 further down. A 20-day-SMA alert is not an ACTION
either; it is a prompt to look.

### The closing block

**Every email this system sends — picks, alert, weekly shortlist, failure notice —
ends with the desk link.** No exceptions:

```
Log what you buy or sell: {{DESK_URL}}
Screen, not advice. Ranked on four stated factors, not expected return.
```

On a picks email, one line directly under the top 5 as well:

```
Bought any of these? Log them on the desk so tomorrow's run can monitor them.
```

Monitoring only works on positions recorded on the desk. A position bought and not
logged is invisible: no stop check, no 20-day alert, no hold-period countdown. Say
so whenever the desk shows no open positions and picks are being issued.
