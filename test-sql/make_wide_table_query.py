#!/usr/bin/env python
events = 52


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
    MAX(CASE WHEN anon_2.row_num = {row_n} THEN anon_2.booked_date END) AS booked_date_{n},
    MAX(CASE WHEN anon_2.row_num = {row_n} THEN anon_2.start_date END) AS start_date_{n},
    MAX(CASE WHEN anon_2.row_num = {row_n} THEN anon_2.organisation_id END) AS organisation_id_{n}{comma}
    """
    )

print(
    f"""
  FROM (
    SELECT [Appointment].[Patient_ID] AS patient_id,
      [Appointment].BookedDate AS booked_date,
      [Appointment].StartDate AS start_date,
      [Appointment].Organisation_ID AS organisation_id,
      row_number() OVER (
        PARTITION BY [Appointment].[Patient_ID] ORDER BY [Appointment].BookedDate
        ) AS row_num
    FROM [Appointment]
    WHERE [Appointment].BookedDate >= '20210601'
      AND [Appointment].BookedDate <= '20221231'
    ) AS anon_2
  WHERE anon_2.row_num <= {events}
  GROUP BY anon_2.patient_id
  ) AS anon_1;

CREATE CLUSTERED INDEX [ix_#tmp_0_patient_id] ON [#tmp_0] (patient_id);

"""
)

print(
    """
SELECT * INTO [#results] FROM (
  SELECT [Patient].Patient_ID AS patient_id,
"""
)

for n in range(events):
    comma = "," if n < events - 1 else ""
    print(
        f"""
    [#tmp_0].booked_date_{n},
    [#tmp_0].start_date_{n},
    [#tmp_0].organisation_id_{n}{comma}
    """
    )

print(
    """
  FROM [Patient]
  LEFT OUTER JOIN [#tmp_0] ON [#tmp_0].patient_id = [Patient].Patient_ID
) t;
"""
)
