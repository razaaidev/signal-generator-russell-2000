# Research

The calibration behind every number in the rulebook. Run in order.

```bash
pip install numpy pandas
python3 0_explore.py       # fetch the daily return dataset, inspect volatility
python3 1_clean_splits.py  # detect and back-adjust unadjusted splits
python3 2_calibrate.py     # sweep stop width, hold period, sizing, exit rules
python3 3_verify.py        # controls, scaling checks, alert frequency
```

## Method

Block bootstrap: draw 21 contiguous trading days from real daily returns, so
volatility clustering and fat tails survive rather than being assumed away. 40,000
simulated months per configuration. Costs are modelled explicitly — 0.6% round trip
covering spread plus 0.15% FX each way.

Positions within a simulated month draw the **same date window** across different
tickers, which preserves cross-sectional correlation. Drawing independently would
have quietly manufactured diversification that does not exist.

## Clean the data first

`1_clean_splits.py` is not boilerplate. The source dataset uses unadjusted closes,
so a 7:1 split reads as a −86% day. Four such splits inflated measured excess
kurtosis from **13 to 119** and produced entirely fictional tail risk. Every
conclusion drawn before that correction was wrong.

The detector looks for one-day ratios close to a small-integer split factor and
back-adjusts the earlier series.

## What came out

See [`FINDINGS.md`](FINDINGS.md).
