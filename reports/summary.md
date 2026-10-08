# Helpdesk ticket analysis: summary

Data: 1000 synthetic tickets, January to June 2026, 5 agents, 5 categories (plus 4 tickets with an unknown category).
All numbers come from the queries in `sql/queries/` and the charts from `src/make_charts.py`.

## 1. Mondays are the busiest day, and software and account issues are over half of all tickets

- Monday has 291 of 1000 tickets (29%). Tuesday to Friday have 155 to 200 each. Saturday and Sunday together have 24.
- Software (299) and account (248) tickets make up 547 tickets, or 55%.
- Software also has the most critical tickets: 25 of the 59 critical tickets (42%).

Suggestion: put the most agents on Monday and train the team first on software and account problems.

## 2. Critical tickets miss their SLA most often, although their average time is under the limit

- Critical tickets take 3.5 h on average, which is under the 4 h SLA. But 25 of 55 resolved critical tickets (45.5%) took longer than 4 h.
- Overall 29.7% of the 910 resolved tickets missed their SLA.
- Medium tickets do best (23.0% breached). Low tickets breach 31.6% of the time, although their limit is the loosest (48 h).

Suggestion: track the share of breached tickets per priority, not just the average resolution time.

## 3. Tomasz B. is the slowest agent overall, but monthly rankings are too noisy to trust

- Average resolution time: Marta S. 17.0 h, Anna K. 18.0 h, Piotr W. 20.7 h, Ola N. 21.8 h, Tomasz B. 25.3 h.
- The gap between the fastest and the slowest agent is 8.3 h.
- The monthly winner changes: Anna (January, April), Marta (February, May, June), Piotr (March). Each agent resolves 21 to 42 tickets per month, too few for one month to settle anything.

Suggestion: compare agents over the full period, and only after checking that they get a similar mix of categories and priorities.

## Limitations

- The data is synthetic. It was made by `src/generate_data.py` with a fixed seed, so the patterns above reflect the generator's settings (for example the Monday weight and the resolution time ranges), not a real company.
- The SLA limits (critical 4 h, high 8 h, medium 24 h, low 48 h) are my assumption.
- 90 tickets are not resolved yet and have no resolution time. They are left out of every average.
- The CSV contained 5 duplicate rows and 16 rows with formatting problems. `src/load_data.py` removes or fixes them before loading.
- The comparison of agents does not account for the ticket mix. A slower average can mean harder tickets.
