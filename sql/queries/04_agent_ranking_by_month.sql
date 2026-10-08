-- Question: how do agents rank each month by average resolution time?
-- Assumption: a ticket belongs to the month it was created in; only resolved
-- tickets count. Rank 1 is the fastest agent of that month.
-- How to read: rank restarts at 1 in every month.
WITH monthly AS (
    SELECT
        strftime('%Y-%m', t.created_at)   AS month,
        a.name                            AS agent,
        COUNT(*)                          AS resolved_tickets,
        ROUND(AVG(t.resolution_hours), 1) AS avg_hours
    FROM tickets AS t
    JOIN agents AS a ON a.agent_id = t.agent_id
    WHERE t.status = 'resolved'
    GROUP BY month, a.name
)
SELECT
    month,
    RANK() OVER (PARTITION BY month ORDER BY avg_hours) AS place,
    agent,
    resolved_tickets,
    avg_hours
FROM monthly
ORDER BY month, place;
