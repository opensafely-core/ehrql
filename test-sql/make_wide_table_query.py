#!/usr/bin/env python
events = 26


print(
    """
SET STATISTICS TIME ON;

"""
)

print(
    """
SELECT *
INTO [#tmp_0]
FROM (
  SELECT
    anon_2.patient_id AS patient_id,
"""
)


for n in range(events):
    comma = "," if n < events - 1 else ""
    row_n = n + 1
    print(
        f"""
    MAX(CASE WHEN anon_2.row_num = {row_n} THEN anon_2.visit_num END) AS visit_num_{n},
    MAX(CASE WHEN anon_2.row_num = {row_n} THEN anon_2.visit_date END) AS visit_date_{n},
    MAX(CASE WHEN anon_2.row_num = {row_n} THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_{n},
    MAX(CASE WHEN anon_2.row_num = {row_n} THEN anon_2.last_linkage_dt END) AS last_linkage_dt_{n}{comma}
    """
    )

print(
    f"""
  FROM (
    SELECT [ONS_CIS_New].[Patient_ID] AS patient_id,
      [ONS_CIS_New].visit_num AS visit_num,
      [ONS_CIS_New].visit_date AS visit_date,
      [ONS_CIS_New].nhs_data_share AS nhs_data_share,
      [ONS_CIS_New].last_linkage_dt AS last_linkage_dt,
      row_number() OVER (
        PARTITION BY [ONS_CIS_New].[Patient_ID] ORDER BY [ONS_CIS_New].visit_date
        ) AS row_num
    FROM [ONS_CIS_New]
    WHERE [ONS_CIS_New].visit_date >= '20200124'
      AND [ONS_CIS_New].visit_date <= '20220331'
    ) AS anon_2
  WHERE anon_2.row_num <= {events}
  GROUP BY anon_2.patient_id
  ) AS anon_1;

CREATE CLUSTERED INDEX [ix_#tmp_0_patient_id] ON [#tmp_0] (patient_id);

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
    [#tmp_0].visit_date_{n},
    [#tmp_0].visit_num_{n},
    [#tmp_0].last_linkage_dt_{n},
    [#tmp_0].is_opted_out_of_nhs_data_share_{n}{comma}
    """
    )

print(
    """
  FROM [#pop]
  LEFT OUTER JOIN [#tmp_0] ON [#tmp_0].patient_id = [#pop].patient_id
  WHERE [#pop].patient_id IS NOT NULL
) t;
"""
)
