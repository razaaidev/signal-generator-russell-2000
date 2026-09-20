# Findings

Every number the rulebook asserts, and where it came from. 40,000 simulated months
per configuration unless stated, block-bootstrapped from 1,255 real trading days
(Feb 2013 – Feb 2018) of US equity daily returns, with 0.6% round-trip costs.

---

## 0. The data was wrong before it was right

The source dataset uses **unadjusted** closes. Four stock splits inside the sample
read as one-day crashes of up to −86%.

| | Before correction | After |
|---|---|---|
| Median excess kurtosis | — | 5.7 |
| High-vol cohort excess kurtosis | **119** | 13.3 |

Measured tail risk was almost entirely fictional, and three names only appeared in
the "high volatility" cohort because of split artefacts. Everything below was
recomputed after `1_clean_splits.py`.

The lesson generalises: check for corporate actions before trusting any volatility
estimate from raw price data.

---

## 1. Stop width — why 3.0 sigma

A stop placed *k* standard deviations below entry gets touched by noise alone at a
rate that depends only on *k* and the holding period — not on the volatility level.
Measured, direction ignored:

| Stop | 5 days | 10 days | 21 days |
|---|---|---|---|
| 1.5σ | 25.3% | 40.2% | 55.7% |
| 2.0σ | 17.7% | 30.8% | 46.1% |
| 2.5σ | 12.1% | 22.9% | 39.3% |
| **3.0σ** | **8.6%** | **17.9%** | **32.9%** |
| 4.0σ | 4.0% | 10.7% | 22.6% |

**Scaling check.** The same 3.0σ stop is touched in 32.8% of 21-day holds on a
41%-vol cohort and 33.5% on a 25%-vol cohort. The formula travels; a fixed
percentage stop does not.

This is why a fixed-percentage stop is the classic error. A 10% stop is roughly
1.3σ on a volatile name — stopped out by noise a third of the time in a week — and
several sigma on a calm one, where it stops protecting anything.

---

## 2. Hold period — longer is better, to a point

At a 55% hit rate, 3.0σ stop:

| Hold cap | Median | Break even | ≥ £110 | Stop-outs | Trades/month |
|---|---|---|---|---|---|
| 5 days | £99.67 | 48.0% | 7.5% | 7.7% | 17.6 |
| 10 days | £100.68 | 54.0% | 9.2% | 16.1% | 9.6 |
| **21 days** | **£101.24** | **57.5%** | **9.9%** | 27.6% | **5.5** |

Short holds lose to friction. Twenty-one trading days — roughly a calendar month —
was the best of those tested.

---

## 3. Position sizing saturates

At a 3.0σ stop the 25%-of-account cap binds at every risk-per-trade level from 2%
to 8%, so the risk parameter is inert:

| Risk/trade | Effective size | Median | ≥ £110 | ≤ £90 |
|---|---|---|---|---|
| 2% | 25% | £101.16 | 9.9% | 5.6% |
| 5% | 25% | £101.28 | 9.8% | 5.6% |
| 8% | 25% | £101.25 | 10.1% | 5.8% |

Four positions at 25% is a fully-invested book. Risk-per-trade only becomes the
binding term when the stop exceeds 20% — i.e. on genuinely wild names.

---

## 4. The 20-day moving average is a bad exit

Tested directly, at 5% risk and 4 positions, 55% hit rate:

| Exit rule | Median | Break even | ≥ £110 | ≤ £90 | Trades/month |
|---|---|---|---|---|---|
| **3.0σ stop + 21-day cap** | **£101.10** | **56.8%** | **9.6%** | **5.9%** | **5.5** |
| 3.0σ stop + close below 20-day | £99.07 | 44.6% | 7.2% | 10.4% | 20.0 |
| 2.5σ stop + close below 20-day | £98.81 | 43.4% | 6.5% | 10.6% | 20.2 |
| close below 20-day only | £98.89 | 43.7% | 6.7% | 10.1% | 20.0 |

Adding the moving-average exit costs £2 of median outcome, twelve points of
break-even probability, and nearly doubles the chance of a bad month — while
quadrupling the number of round trips. The friction alone eats 2–3% of the account.

**Why:** on a 41%-vol cohort, 84% of positions entered above their 20-day close
below it within 21 trading days. The signal fires constantly without the trend
actually breaking.

Kept as an **alert** — about 3.4 a month across 4 positions, a readable cadence.
Never as an exit.

---

## 5. The ceiling: skill is worth about 2% a month

Chosen configuration (3.0σ stop, 21-day cap, 4 positions at 25%), across skill:

| Hit rate | Median | Break even | ≥ £110 | ≥ £120 | ≤ £90 | ≤ £75 |
|---|---|---|---|---|---|---|
| 50% | £100.55 | 53.2% | 9.0% | 1.3% | 6.8% | 0.2% |
| 55% | £101.19 | 57.4% | 9.8% | 1.2% | 5.7% | 0.2% |
| 60% | £101.90 | 61.7% | 11.2% | 1.4% | 5.0% | 0.1% |
| 65% | £102.46 | 65.8% | 12.3% | 1.5% | 4.1% | 0.1% |

Going from a coin flip to an exceptional 65% directional record moves the median
month by **£1.91**. Most of what the median shows is market drift.

Where skill does earn its keep is the left tail: P(≤£90) falls from 6.8% to 4.1%.
Better selection mostly means fewer bad months, not better good ones.

**Caveats.** 2013–18 was a bull market, which flatters any long-only baseline. And
the hit rate is an input to the simulation — nothing here demonstrates that the
four-factor composite achieves 55%. That is the thing live running is meant to
measure.

---

## Appendix — why leverage was abandoned

An earlier version of this system traded 3x leveraged ETPs. The same machinery was
used to test whether a small stake could be multiplied quickly. It cannot:

- **Daily-reset drag** at 3x on a 46%-vol underlying runs ≈ **−75% annualised**,
  matching the closed form `−½·L(L−1)·σ²` minus costs to within 2.5 points. About
  −6% a month before being wrong about anything.
- A **−3x product is wiped out entirely** by a +33.3% single-day move in its
  underlying. That occurred 5 times in 18,825 stock-days in the sample.
- **Ceiling test.** Given *perfect foresight* — every direction call correct,
  all-in, compounded daily for a month — the median month ends at £246 and only
  **1.5%** of months reach 10x. The binding constraint is how far these instruments
  travel in 21 days, not skill. No amount of signal quality changes it.

Removing leverage removed the decay, the ruin risk, and a class of instrument
identity hazards, at the cost of a lower ceiling that was never reachable anyway.
