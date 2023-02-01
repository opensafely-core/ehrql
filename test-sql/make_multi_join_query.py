#!/usr/bin/env python
events = 52


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
  ) t
  WHERE t.row_num <= {events}
) AS anon_1;

CREATE CLUSTERED INDEX [ix_#tmp_0_patient_id] ON [#tmp_0] (row_num, patient_id);

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
    anon_{n}.booked_date AS booked_date_{n},
    anon_{n}.start_date AS start_date_{n},
    anon_{n}.organisation_id AS organisation_id_{n}{comma}
    """
    )

print(
    """
  FROM [Patient]
"""
)

for n in range(events):
    print(
        f"  LEFT OUTER JOIN [#tmp_0] AS anon_{n} ON"
        f" anon_{n}.row_num = {n+1} AND anon_{n}.patient_id = [Patient].Patient_ID"
    )

print(
    """
) t;
"""
)
