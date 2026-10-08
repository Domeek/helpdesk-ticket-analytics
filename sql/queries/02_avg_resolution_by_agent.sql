-- Question: which agent resolves tickets the fastest on average?
-- Assumption: only resolved tickets have a resolution time, so open and
-- in-progress tickets (NULL) are left out of the average.
-- How to read: lower avg_hours is faster. Compare agents only if their
-- mix of priorities is similar, otherwise the comparison is unfair.
SELECT
    a.name                            AS agent,
    COUNT(*)                          AS resolved_tickets,
    ROUND(AVG(t.resolution_hours), 1) AS avg_hours
FROM tickets AS t
JOIN agents AS a ON a.agent_id = t.agent_id
WHERE t.status = 'resolved'
GROUP BY a.name
ORDER BY avg_hours;
