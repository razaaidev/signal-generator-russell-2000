# Agents

One markdown file per scheduled run. Each is a complete, standalone prompt — a
scheduler fires it into a fresh session with no memory of previous runs, so every
file restates what it needs.

| File | When (UK) | Emails? |
|---|---|---|
| `weekly-rank-part1.md` | Sat 09:00 | only on failure |
| `weekly-rank-part2.md` | Sun 09:00 | yes — the shortlist |
| `pre-open-screen.md` | weekdays 14:00 | yes — the picks |
| `midday-screen.md` | weekdays 17:30 | yes — changes and picks |
| `clock-change.md` | Mar/Oct windows | only when it changes something |

## The pattern

Every prompt does the same four things in the same order:

1. **Load the rulebook first**, and abort loudly if it cannot be read. An agent
   that screens from memory is worse than an agent that fails.
2. **Restate the non-negotiables** — the handful of mistakes that would be costly,
   repeated inline even though they are in the rulebook. Belt and braces.
3. **Do the work**, with explicit budget discipline and an instruction to mark
   anything unverifiable as UNVERIFIED rather than estimate it.
4. **Write state back** before finishing, so the next run has something to compare
   against.

## Why the rules live in one file

An earlier version of this system pasted the rulebook into each scheduled task.
Five copies drifted apart within a week, and editing the canonical file silently
changed nothing. Now each prompt reads `rulebook/signal-rulebook.md` and carries
only its own run-specific section.

## Why part 1 and part 2 are separate

Not a daily quota problem — a wall-clock one. 600 names at 8 requests/minute is 75
minutes, too long for one scheduled run. Two passes of ~300 come in around 38
minutes each. Both can run on the same day if the daily budget allows.
