#!/usr/bin/env python
events = 26


print(
    """
SET STATISTICS TIME ON;

"""
)

print(
    f"""
SELECT *
INTO [#tmp_0]
FROM (
  SELECT * FROM (
    SELECT [ONS_CIS_New].[Patient_ID] AS patient_id,
      [ONS_CIS_New].visit_num AS visit_num,
      [ONS_CIS_New].visit_date AS visit_date,
      [ONS_CIS_New].nhs_data_share AS is_opted_out_of_nhs_data_share,
      [ONS_CIS_New].last_linkage_dt AS last_linkage_dt,
      row_number() OVER (
        PARTITION BY [ONS_CIS_New].[Patient_ID] ORDER BY [ONS_CIS_New].visit_date
        ) AS row_num
    FROM [ONS_CIS_New]
    WHERE [ONS_CIS_New].visit_date >= '20200124'
      AND [ONS_CIS_New].visit_date <= '20220331'
  ) t
  WHERE t.row_num <= {events}
) AS anon_1;

CREATE CLUSTERED INDEX [ix_#tmp_0_patient_id] ON [#tmp_0] (row_num, patient_id);

"""
)

print(
    """
SELECT *
INTO [#pop]
FROM (
  SELECT DISTINCT [ONS_CIS_New].[Patient_ID] AS patient_id
  FROM [ONS_CIS_New]
  WHERE [ONS_CIS_New].visit_date >= '20200124'
    AND [ONS_CIS_New].visit_date <= '20220331'
  ) AS anon_1;

"""
)

print(
    """
SELECT * INTO [#results] FROM (
  SELECT [#pop].patient_id AS patient_id,
"""
)

for n in range(events):
    comma = "," if n < events - 1 else ""
    print(
        f"""
    anon_{n}.visit_date AS visit_date_{n},
    anon_{n}.visit_num AS visit_num_{n},
    anon_{n}.last_linkage_dt AS last_linkage_dt_{n},
    anon_{n}.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_{n}{comma}
    """
    )

print(
    """
  FROM [#pop]
"""
)

for n in range(events):
    print(
        f"  LEFT OUTER JOIN [#tmp_0] AS anon_{n} ON"
        f" anon_{n}.row_num = {n+1} AND anon_{n}.patient_id = [#pop].patient_id"
    )

print(
    """
  WHERE [#pop].patient_id IS NOT NULL
) t;
"""
)
