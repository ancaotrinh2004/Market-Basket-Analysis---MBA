-- Tính support cho từng item đơn lẻ
-- Support = Số giao dịch chứa item / Tổng số giao dịch

WITH txn_items AS (
  SELECT DISTINCT txn_id, item_name
  FROM {{ ref('stg_transaction_items') }}
),
total_txns AS (
  SELECT COUNT(DISTINCT txn_id) AS total_txn
  FROM {{ ref('stg_transaction_items') }}
)
SELECT
  item_name,
  COUNT(DISTINCT txn_id) AS txn_count,
  ROUND(
    COUNT(DISTINCT txn_id)::NUMERIC / NULLIF((SELECT total_txn FROM total_txns), 0),
    4
  ) AS support_item
FROM txn_items
GROUP BY item_name
ORDER BY support_item DESC