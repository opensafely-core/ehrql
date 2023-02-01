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
  SELECT anon_2.patient_id AS patient_id,
    anon_2.booked_date AS booked_date,
    anon_2.start_date AS start_date,
    anon_2.organisation_id AS organisation_id
  FROM (
    SELECT [Appointment].[Patient_ID] AS patient_id,
      [Appointment].BookedDate AS booked_date,
      [Appointment].StartDate AS start_date,
      [Appointment].Organisation_ID AS organisation_id,
      row_number() OVER (
        PARTITION BY [Appointment].[Patient_ID] ORDER BY [Appointment].BookedDate
        ) AS anon_3
    FROM [Appointment]
    WHERE [Appointment].BookedDate >= '20210601'
      AND [Appointment].BookedDate <= '20221231'
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
        anon_2.booked_date AS booked_date,
        anon_2.start_date AS start_date,
        anon_2.organisation_id AS organisation_id
      FROM (
        SELECT [Appointment].[Patient_ID] AS patient_id,
          [Appointment].BookedDate AS booked_date,
          [Appointment].StartDate AS start_date,
          [Appointment].Organisation_ID AS organisation_id,
          row_number() OVER (
            PARTITION BY [Appointment].[Patient_ID] ORDER BY [Appointment].BookedDate
            ) AS anon_3
        FROM [Appointment]
        LEFT OUTER JOIN [{prev_table}] ON [{prev_table}].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [{prev_table}].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_{table}_patient_id] ON [{table}] (patient_id);

    """
    )


print(
    """
SELECT * INTO [#results] FROM (
  SELECT Patient.Patient_ID AS patient_id,
"""
)

for n in range(events):
    comma = "," if n < events - 1 else ""
    print(
        f"""
    [#tmp_{n}].start_date AS start_date_{n},
    [#tmp_{n}].booked_date AS booked_date_{n},
    [#tmp_{n}].organisation_id AS organisation_id_{n}{comma}
    """
    )

print(
    """
  FROM Patient
"""
)

for n in range(events):
    print(f"  LEFT OUTER JOIN [#tmp_{n}] ON [#tmp_{n}].patient_id = Patient.Patient_ID")

print(
    """
) t;
"""
)
