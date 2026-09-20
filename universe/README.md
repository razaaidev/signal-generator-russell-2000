# Universe

`eligible-universe.md` is the list of Russell 2000 constituents that can actually
be bought in the target brokerage account, ranked by index weight, with the untradeable tail
listed at the end so a screener can exclude it without querying it.

Current snapshot: **1,652 of 1,769 constituents tradeable (93.4%)**, covering 94.9%
of index weight. 117 are not offered.

## Rebuild it

```bash
python3 build_universe.py broker_instruments.json index_holdings.json eligible-universe.md
```

Inputs are not committed — see the root README for how to fetch them.

## The ticker trap

Brokers commonly use an internal instrument ID that preserves the ticker from the
day the instrument was listed, and never revise it after a rename or a SPAC
merger. Real examples from the reference broker:

| Index says | Broker ID | Currently displays as |
|---|---|---|
| IONQ | `DMYI_US_EQ` | IONQ |
| ASGN | `ASGN_US_EQ` | EFOR |
| SATS | `SATS_US_EQ` | ECHO |
| ACHR | `ACIC_US_EQ` | ACHR |

Matching Russell symbols against the ticker **prefix** alone misclassified 233
names — excluding some that are perfectly available, and matching others to
entirely different companies. The builder matches on `shortName` (the current
symbol) first, prefix second, and records which route each name took.

Anything that consumes this file should display **both** the broker ticker to
search and the symbol it currently shows.

## Refresh cadence

Quarterly. Russell reconstitutes each June, and brokers add and drop instruments
continuously. Rebuild sooner if a pick cannot be found in the app.
