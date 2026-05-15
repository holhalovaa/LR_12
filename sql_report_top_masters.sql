-- =====================================================
-- Отчёт: Топ-3 мастера по количеству выполненных заказов
-- за последние 30 дней
-- База данных: PostgreSQL
-- Предметная область: Автосервис (вариант 28)
-- =====================================================

SELECT 
    m.name AS master_name,
    m.specialization,
    COUNT(o.id) AS orders_completed,
    COALESCE(SUM(o.total_price), 0) AS total_revenue
FROM masters m
INNER JOIN orders o ON m.id = o.master_id
WHERE o.status = 'COMPLETED'                    -- статус "выдан" (COMPLETED)
    AND o.created_at >= NOW() - INTERVAL '30 days'
GROUP BY m.id, m.name, m.specialization
ORDER BY orders_completed DESC
LIMIT 3;
