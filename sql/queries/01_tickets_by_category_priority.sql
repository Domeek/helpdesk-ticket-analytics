-- Question: how many tickets does each category get, split by priority?
-- Assumption: every ticket counts, including open and in-progress ones.
-- How to read: one row per category and priority; "tickets" is the count.
SELECT
    c.name       AS category,
    t.priority   AS priority,
    COUNT(*)     AS tickets
FROM tickets AS t
JOIN categories AS c ON c.category_id = t.category_id
GROUP BY c.name, t.priority
ORDER BY
    c.name,
    CASE t.priority
        WHEN 'critical' THEN 1
        WHEN 'high'     THEN 2
        WHEN 'medium'   THEN 3
        ELSE 4
    END;
