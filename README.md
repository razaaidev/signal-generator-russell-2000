# Signal Generator

A rules-based screening system for US small-cap equities, run by scheduled LLM
agents. It narrows the Russell 2000 to five daily candidates, sizes them, and
monitors open positions — and it is deliberately built so that **it never tells you
what to buy**.

It screens. You decide.

---

## What it does

Three stages on three clocks:

| Stage | When | Work |
|---|---|---|
| **Universe build** | quarterly | Russell 2000 ∩ broker-tradeable ∩ top 600 by index weight |
| **Weekly rank** | weekend, 2 passes | gate and score all 600 → a 40-name shortlist |
| **Daily screen** | 14:00 and 17:30 UK | re-gate the shortlist + your holdings → top 5, plus alerts |

Each daily run emails a ranked five with the evidence behind each name, the stop
price, the position size in sterling, and the status of everything you already
hold. A separate alert email fires when a position breaches its stop, drops below
its 20-day average, approaches its hold limit, or runs into earnings.

See [`docs/how-picks-are-made.html`](docs/how-picks-are-made.html) for the flow
charts, and [`rulebook/signal-rulebook.md`](rulebook/signal-rulebook.md) for the
rules the agents actually follow.

---

## Read this before anything else

The system was calibrated on 40,000 simulated months, block-bootstrapped from real
daily returns of a 41%-annualised-volatility cohort, with realistic costs. Results
for a £100 stake:

| Directional hit rate | Median month | Break even | ≥ £110 | ≤ £90 |
|---|---|---|---|---|
| 50% (no skill) | £100.55 | 53.2% | 9.0% | 6.8% |
| 55% (good) | £101.19 | 57.4% | 9.8% | 5.7% |
| 60% (very good) | £101.90 | 61.7% | 11.2% | 5.0% |
| 65% (exceptional) | £102.46 | 65.8% | 12.3% | 4.1% |

**The gap between no skill and exceptional skill is about 2% a month.** Most of the
median outcome is market drift, not selection. The screen's realistic contribution
is a few tenths of a percent plus a meaningful reduction in bad months.

Two caveats that cut against those numbers: the sample period (2013–18) was a bull
market, so a long-only baseline is flattered; and the hit rate is an **input** to
the simulation, not something this screen has been shown to achieve.

If you are looking for a system that turns a small stake into a large one, this is
not it, and the arithmetic in [`research/FINDINGS.md`](research/FINDINGS.md)
explains why no system of this shape is.

---

## Design decisions worth knowing

**Gates are absolute, the score is relative.** Five pass/fail checks run first — no
composite score rescues a failed gate. Survivors are then z-scored *against each
other*, so a high score means "best of what passed today", not a fixed quality bar.

**The stop is calibrated, not chosen.** `stop = 3.0 × the stock's 20-day daily
sigma`. That multiple is volatility-invariant: it is touched in ~33% of 21-day
holds on both a 25%-vol and a 41%-vol cohort. A fixed percentage stop is the
classic mistake — it is simultaneously too tight for volatile names and too loose
for calm ones.

**The 20-day moving average is an alert, not an exit.** Tested as an exit rule it
cut the median month from £101.10 to £99.07, dropped break-even odds from 57% to
45%, and quadrupled the number of round trips. It fires on 84% of positions within
a month. Useful as a prompt to look; destructive as a trigger to sell.

**Buying is optional, selling is not.** Entries are your judgement call from a
ranked screen. Exits are mechanical — a stop level or a day count — so every email
opens with a single ACTION line stating what the rules require, or that they
require nothing.

**Broker tickers go stale.** Trading 212's instrument IDs preserve the symbol from
the day the instrument was added. IonQ trades as `DMYI_US_EQ`; ASGN displays as
`EFOR`. Matching on the ticker prefix alone misclassified 233 names — in both
directions. The universe builder matches on the current symbol first and records
which route it used.

---

## Layout

```
rulebook/    the rules every agent reads first — the single source of truth
universe/    builder script + the generated eligible universe
agents/      one markdown file per scheduled run, ready to paste into a scheduler
research/    the calibration: data cleaning, Monte Carlo, verification
desk/        a single-page position log the agents read from and write to
docs/        flow charts explaining how the five picks are selected
```

---

## Setup

### 1. Fill in the placeholders

Two tokens appear across the agent prompts and the desk page:

| Placeholder | Replace with |
|---|---|
| `{{YOUR_EMAIL}}` | the address the agents email |
| `{{DESK_URL}}` | wherever you host `desk/index.html` |

```bash
grep -rl '{{YOUR_EMAIL}}\|{{DESK_URL}}' . 
```

### 2. Build the universe

You need two inputs:

- **Broker instruments.** For Trading 212, generate a read-only API key
  (Settings → API), then:

  ```bash
  curl -sS -u "API_KEY:API_SECRET" \
    "https://live.trading212.com/api/v0/equity/metadata/instruments" \
    -o t212_instruments.json -w "status=%{http_code}\n"
  ```

  Note the endpoint is rate-limited to one request per 50 seconds, and the API
  covers Invest and Stocks ISA accounts only.

- **Index constituents.** Any source giving Russell 2000 symbols and weights — an
  IWM holdings dump works (Alpha Vantage's `ETF_PROFILE` returns ~1,795 rows).

Then:

```bash
python3 universe/build_universe.py t212_instruments.json iwm_holdings.json \
        universe/eligible-universe.md
```

Neither input is committed here: the broker dump comes from your own authenticated
call, and holdings data is licensed by its provider.

### 3. Wire up the agents

Each file in `agents/` is a self-contained prompt for one scheduled run. Point your
scheduler at them with the cron expressions in each header, and give the runs
access to a market-data provider and an email sender.

Cron is evaluated in UTC while the run times are UK local, so
`agents/clock-change.md` shifts the expressions automatically at each UK clock
change. Set that one up too, or accept that your runs drift by an hour twice a year.

### 4. Host the desk

`desk/index.html` is a single self-contained page. It stores positions, shows the
latest picks and alerts, and converts USD prices to sterling including the broker's
0.15% FX fee in the correct direction on each side. It expects a small JSON
document store; adapt the persistence layer at the bottom of the file to whatever
you have.

**Monitoring only sees what is logged.** A position bought and not recorded gets no
stop check, no alert and no hold-period countdown.

---

## Reproducing the calibration

```bash
pip install numpy pandas
cd research
python3 0_explore.py      # fetch and inspect the daily return dataset
python3 1_clean_splits.py # detect and back-adjust unadjusted stock splits
python3 2_calibrate.py    # sweep stop width, hold period, sizing, exit rules
python3 3_verify.py       # controls, scaling checks, alert frequency
```

`1_clean_splits.py` matters more than it sounds: the source data uses unadjusted
closes, so four stock splits were inflating measured kurtosis from 13 to 119 and
producing entirely fictional tail risk until they were corrected.

---

## Disclaimer

This is a personal research project published for reference. It is **not financial
advice**, not a recommendation to buy or sell anything, and not a product. Nothing
here has been tested with real money at any meaningful scale.

Leveraged and small-capitalisation equities can lose value rapidly and permanently.
The simulation results describe one historical sample under a set of stated
assumptions; live results will differ, and a falling market shifts every figure
down. If you run this, run it with money you can afford to lose entirely, and place
real stop orders with your broker rather than relying on an email.

The author is not a licensed financial adviser.

---

## Licence

MIT — see [`LICENSE`](LICENSE).
