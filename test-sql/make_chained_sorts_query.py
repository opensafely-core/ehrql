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
  SELECT anon_2.patient_id AS patient_id,
    anon_2.visit_num AS visit_num,
    anon_2.visit_date AS visit_date,
    anon_2.nhs_data_share AS nhs_data_share,
    anon_2.last_linkage_dt AS last_linkage_dt
  FROM (
    SELECT [ONS_CIS_New].[Patient_ID] AS patient_id,
      [ONS_CIS_New].visit_num AS visit_num,
      [ONS_CIS_New].visit_date AS visit_date,
      [ONS_CIS_New].nhs_data_share AS nhs_data_share,
      [ONS_CIS_New].last_linkage_dt AS last_linkage_dt,
      row_number() OVER (
        PARTITION BY [ONS_CIS_New].[Patient_ID] ORDER BY [ONS_CIS_New].visit_date
        ) AS anon_3
    FROM [ONS_CIS_New]
    WHERE [ONS_CIS_New].visit_date >= '20200124'
      AND [ONS_CIS_New].visit_date <= '20220331'
    ) AS anon_2
  WHERE anon_2.anon_3 = 1
  ) AS anon_1;

CREATE CLUSTERED INDEX [ix_#tmp_0_patient_id] ON [#tmp_0] (patient_id);

"""
)


for n in range(1, events):
    prev_table = f"#tmp_{n-1}"
    table = f"#tmp_{n}"
    print(
        f"""
    SELECT *
    INTO [{table}]
    FROM (
      SELECT anon_2.patient_id AS patient_id,
        anon_2.nhs_data_share AS nhs_data_share,
        anon_2.visit_num AS visit_num,
        anon_2.visit_date AS visit_date,
        anon_2.last_linkage_dt AS last_linkage_dt
      FROM (
        SELECT [ONS_CIS_New].[Patient_ID] AS patient_id,
          [ONS_CIS_New].nhs_data_share AS nhs_data_share,
          [ONS_CIS_New].visit_num AS visit_num,
          [ONS_CIS_New].visit_date AS visit_date,
          [ONS_CIS_New].last_linkage_dt AS last_linkage_dt,
          row_number() OVER (
            PARTITION BY [ONS_CIS_New].[Patient_ID] ORDER BY [ONS_CIS_New].visit_date
            ) AS anon_3
        FROM [ONS_CIS_New]
        LEFT OUTER JOIN [{prev_table}] ON [{prev_table}].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [{prev_table}].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_{table}_patient_id] ON [{table}] (patient_id);

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
    [#tmp_{n}].visit_date AS visit_date_{n},
    [#tmp_{n}].visit_num AS visit_num_{n},
    [#tmp_{n}].last_linkage_dt AS last_linkage_dt_{n},
    [#tmp_{n}].nhs_data_share AS is_opted_out_of_nhs_data_share_{n}{comma}
    """
    )

print(
    """
  FROM [#pop]
"""
)

for n in range(events):
    print(f"  LEFT OUTER JOIN [#tmp_{n}] ON [#tmp_{n}].patient_id = [#pop].patient_id")

print(
    """
  WHERE [#pop].patient_id IS NOT NULL
) t;
"""
)
