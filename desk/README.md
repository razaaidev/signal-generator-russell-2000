# Desk

A single self-contained HTML page: the position log the agents read from and write
to. No build step, no dependencies beyond a web font.

## What it does

- **Log positions** — symbol, broker ticker, entry price in USD, quantity, stop,
  and the actual £ cost from your contract note. The £ estimate updates live as you
  type and includes the FX fee.
- **Show open positions** in both currencies, with distance to stop, days held
  against the 21-day cap, and whether the close is below its 20-day average.
- **Display the latest picks and alerts** written by the scheduled runs.
- **Close positions**, with £ proceeds auto-calculated net of the FX fee.

## Currency handling

Prices are USD; the account is sterling. The broker charges 0.15% FX **each way**,
so the direction matters:

```
buying  costs  (USD / rate) x 1.0015
selling nets   (USD / rate) x 0.9985
```

Open positions are marked at the **sell** rate, so the account value never
overstates itself by a fee you have not yet paid.

## Persistence

The page expects a small JSON document store exposed to the browser, with these
documents:

| Path | Written by | Holds |
|---|---|---|
| `desk/state` | page + agents | cash, settings, open positions, closed trades |
| `desk/fx` | agents | the current GBP/USD rate and its timestamp |
| `signals/latest` | agents | the most recent top 5 |
| `shortlist/current` | weekly rank | the ~40-name shortlist |
| `alerts` | agents | a collection of alert records |

It falls back to `localStorage` when no store is available, so it is usable
standalone — you just lose the agent integration.

Swap the persistence block at the bottom of `index.html` for whatever backend you
have.
