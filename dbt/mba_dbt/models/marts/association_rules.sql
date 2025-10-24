-- Tính các association rules với Confidence và Lift
-- Confidence(A→B) = Support(A,B) / Support(A)
-- Lift(A→B) = Confidence(A→B) / Support(B)

WITH item_sup AS (
  SELECT * FROM {{ ref('item_support') }}
),
pair_sup AS (
  SELECT * FROM {{ ref('pair_support') }}
),
rules AS (
  -- Rule A → B
  SELECT
    p.a_name AS antecedent,
    p.b_name AS consequent,
    p.support_pair,
    p.txn_count AS pair_count,
    ia.support_item AS antecedent_support,
    ic.support_item AS consequent_support,
    ROUND(
      p.support_pair / NULLIF(ia.support_item, 0),
      4
    ) AS confidence,
    ROUND(
      (p.support_pair / NULLIF(ia.support_item, 0)) / NULLIF(ic.support_item, 0),
      4
    ) AS lift
  FROM pair_sup p
  INNER JOIN item_sup ia ON ia.item_name = p.a_name
  INNER JOIN item_sup ic ON ic.item_name = p.b_name
  
  UNION ALL
  
  -- Rule B → A (đảo ngược)
  SELECT
    p.b_name AS antecedent,
    p.a_name AS consequent,
    p.support_pair,
    p.txn_count AS pair_count,
    ib.support_item AS antecedent_support,
    ia.support_item AS consequent_support,
    ROUND(
      p.support_pair / NULLIF(ib.support_item, 0),
      4
    ) AS confidence,
    ROUND(
      (p.support_pair / NULLIF(ib.support_item, 0)) / NULLIF(ia.support_item, 0),
      4
    ) AS lift
  FROM pair_sup p
  INNER JOIN item_sup ia ON ia.item_name = p.a_name
  INNER JOIN item_sup ib ON ib.item_name = p.b_name
)
SELECT
  antecedent,
  consequent,
  support_pair AS support,
  confidence,
  lift,
  pair_count,
  antecedent_support,
  consequent_support
FROM rules
WHERE confidence >= 0.1  -- Chỉ lấy rules có confidence >= 10%
  AND lift > 1.0         -- Chỉ lấy rules có lift > 1 (tương quan dương)
ORDER BY lift DESC, confidence DESC