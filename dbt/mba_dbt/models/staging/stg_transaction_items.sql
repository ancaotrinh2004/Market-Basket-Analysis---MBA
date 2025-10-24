-- Unpivot các cột sản phẩm thành từng dòng (txn_id, item_name)
{% set rel = ref('basket_analysis') %}
{% set cols = adapter.get_columns_in_relation(rel) %}

WITH base AS (
  SELECT row_number() OVER () AS txn_id, *
  FROM {{ rel }}
),
pairs AS (
  SELECT
    b.txn_id,
    v.item_name,
    v.bought
  FROM base b
  CROSS JOIN LATERAL (
    VALUES
    {%- for c in cols if c.name|lower != 'unnamed: 0' %}
      ('{{ c.name }}',
       CASE
         WHEN lower(b."{{ c.name }}"::text) IN ('t','true','1') THEN true
         ELSE false
       END)
      {%- if not loop.last -%},{%- endif %}
    {%- endfor %}
  ) AS v(item_name, bought)
)
SELECT txn_id, item_name
FROM pairs
WHERE bought = true