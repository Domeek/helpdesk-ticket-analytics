-- Question: how does the number of new tickets change from week to week?
-- Assumption: weeks start on Monday (%W). The first and last week are partial.
-- How to read: each "#" in the bar is 5 tickets.
SELECT
    strftime('%Y-W%W', created_at)                    AS week,
    COUNT(*)                                          AS tickets,
    replace(hex(zeroblob(COUNT(*) / 5)), '00', '#')   AS bar
FROM tickets
GROUP BY week
ORDER BY week;
