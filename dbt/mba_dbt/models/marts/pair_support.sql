-- Tính support cho từng cặp item (A, B)
-- Support(A,B) = Số giao dịch chứa cả A và B / Tổng số giao dịch

WITH txn_items AS (
  SELECT DISTINCT txn_id, item_name
  FROM {{ ref('stg_transaction_items') }}
),
item_pairs AS (
  SELECT 
    a.txn_id,
    a.item_name AS a_name,
    b.item_name AS b_name
  FROM txn_items a
  INNER JOIN txn_items b
    ON a.txn_id = b.txn_id 
    AND a.item_name < b.item_name  -- Tránh trùng lặp: chỉ lấy A < B
),
total_txns AS (
  SELECT COUNT(DISTINCT txn_id) AS total_txn
  FROM {{ ref('stg_transaction_items') }}
)
SELECT
  a_name,
  b_name,
  COUNT(DISTINCT txn_id) AS txn_count,
  ROUND(
    COUNT(DISTINCT txn_id)::NUMERIC / NULLIF((SELECT total_txn FROM total_txns), 0),
    4
  ) AS support_pair
FROM item_pairs
GROUP BY a_name, b_name
HAVING COUNT(DISTINCT txn_id) >= 2  -- Lọc các cặp xuất hiện ít nhất 2 lần
ORDER BY support_pair DESC