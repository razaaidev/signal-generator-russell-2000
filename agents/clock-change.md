# Agent — clock-change re-anchor (twice yearly, silent)

Cron: `0 5 24-31 3,10 *` — daily through the two UK clock-change windows

---

Maintenance task. Keep the daily schedules anchored to UK local time.

Cron is evaluated in UTC but the run times are UK local, so the expressions must
shift by an hour at each UK clock change. This task runs daily during the two
change windows (24–31 March and 24–31 October) and corrects them the same day.

## Step 1 — current UK offset
Work out whether Europe/London is on BST (UTC+1) or GMT (UTC+0) right now. UK
clocks go forward on the last Sunday of March and back on the last Sunday of
October, at 01:00 UTC. On the changeover day itself use the offset in effect **now**,
not earlier today.

## Step 2 — the correct expressions

| Task | UK time | BST (UTC+1) | GMT (UTC+0) |
|---|---|---|---|
| Pre-open screen | 14:00 | `0 13 * * 1-5` | `0 14 * * 1-5` |
| Midday screen | 17:30 | `30 16 * * 1-5` | `30 17 * * 1-5` |

The weekend rank jobs are deliberately absent — an hour either way is immaterial
for batch work. Leave them alone.

The midday run tracks the US session midpoint. For the few weeks each spring and
autumn when the UK and US changes are out of step, the UK-time target stays 17:30
and only the UTC expression moves; do not re-derive it from New York time.

## Step 3 — compare and correct
Read those two cron expressions. For any that does not match the column for the
current offset, update **only** the cron expression — never pass a prompt, so
nothing else is disturbed.

## Step 4 — report only if something changed
Changed nothing? Do nothing further and send no email. This task is silent on quiet
days.

Changed something? Email `{{YOUR_EMAIL}}`, subject
"Signal Gen schedules re-anchored - [GMT/BST]": which offset the UK is now on and
from what date · a line per task with name, old cron, new cron and resulting UK
time · anything that could not be updated and why · "No action needed from you.
Next check: [date of the next window]."

Do not change any task's prompt, name or enabled state. Do not create or delete
tasks. Do not touch the rulebook or the desk.
