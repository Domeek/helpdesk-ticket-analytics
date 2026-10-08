-- Question: how many resolved tickets missed their SLA, per priority?
-- Assumption: SLA targets are critical 4 h, high 8 h, medium 24 h, low 48 h.
-- Open and in-progress tickets have no resolution time yet, so they are left out.
-- How to read: breached_pct is the share of resolved tickets over the SLA.
WITH resolved AS (
    SELECT
        priority,
        resolution_hours,
        CASE priority
            WHEN 'critical' THEN 4
            WHEN 'high'     THEN 8
            WHEN 'medium'   THEN 24
            ELSE 48
        END AS sla_hours
    FROM tickets
    WHERE status = 'resolved'
)
SELECT
    priority,
    sla_hours,
    COUNT(*) AS resolved_tickets,
    SUM(CASE WHEN resolution_hours > sla_hours THEN 1 ELSE 0 END) AS breached,
    ROUND(100.0 * SUM(CASE WHEN resolution_hours > sla_hours THEN 1 ELSE 0 END) / COUNT(*), 1) AS breached_pct
FROM resolved
GROUP BY priority, sla_hours
ORDER BY sla_hours;
