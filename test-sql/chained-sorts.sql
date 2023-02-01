
SET STATISTICS TIME ON;



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



    SELECT *
    INTO [#tmp_1]
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
        LEFT OUTER JOIN [#tmp_0] ON [#tmp_0].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_0].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_1_patient_id] ON [#tmp_1] (patient_id);

    

    SELECT *
    INTO [#tmp_2]
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
        LEFT OUTER JOIN [#tmp_1] ON [#tmp_1].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_1].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_2_patient_id] ON [#tmp_2] (patient_id);

    

    SELECT *
    INTO [#tmp_3]
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
        LEFT OUTER JOIN [#tmp_2] ON [#tmp_2].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_2].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_3_patient_id] ON [#tmp_3] (patient_id);

    

    SELECT *
    INTO [#tmp_4]
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
        LEFT OUTER JOIN [#tmp_3] ON [#tmp_3].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_3].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_4_patient_id] ON [#tmp_4] (patient_id);

    

    SELECT *
    INTO [#tmp_5]
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
        LEFT OUTER JOIN [#tmp_4] ON [#tmp_4].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_4].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_5_patient_id] ON [#tmp_5] (patient_id);

    

    SELECT *
    INTO [#tmp_6]
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
        LEFT OUTER JOIN [#tmp_5] ON [#tmp_5].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_5].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_6_patient_id] ON [#tmp_6] (patient_id);

    

    SELECT *
    INTO [#tmp_7]
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
        LEFT OUTER JOIN [#tmp_6] ON [#tmp_6].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_6].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_7_patient_id] ON [#tmp_7] (patient_id);

    

    SELECT *
    INTO [#tmp_8]
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
        LEFT OUTER JOIN [#tmp_7] ON [#tmp_7].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_7].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_8_patient_id] ON [#tmp_8] (patient_id);

    

    SELECT *
    INTO [#tmp_9]
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
        LEFT OUTER JOIN [#tmp_8] ON [#tmp_8].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_8].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_9_patient_id] ON [#tmp_9] (patient_id);

    

    SELECT *
    INTO [#tmp_10]
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
        LEFT OUTER JOIN [#tmp_9] ON [#tmp_9].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_9].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_10_patient_id] ON [#tmp_10] (patient_id);

    

    SELECT *
    INTO [#tmp_11]
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
        LEFT OUTER JOIN [#tmp_10] ON [#tmp_10].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_10].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_11_patient_id] ON [#tmp_11] (patient_id);

    

    SELECT *
    INTO [#tmp_12]
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
        LEFT OUTER JOIN [#tmp_11] ON [#tmp_11].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_11].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_12_patient_id] ON [#tmp_12] (patient_id);

    

    SELECT *
    INTO [#tmp_13]
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
        LEFT OUTER JOIN [#tmp_12] ON [#tmp_12].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_12].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_13_patient_id] ON [#tmp_13] (patient_id);

    

    SELECT *
    INTO [#tmp_14]
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
        LEFT OUTER JOIN [#tmp_13] ON [#tmp_13].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_13].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_14_patient_id] ON [#tmp_14] (patient_id);

    

    SELECT *
    INTO [#tmp_15]
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
        LEFT OUTER JOIN [#tmp_14] ON [#tmp_14].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_14].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_15_patient_id] ON [#tmp_15] (patient_id);

    

    SELECT *
    INTO [#tmp_16]
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
        LEFT OUTER JOIN [#tmp_15] ON [#tmp_15].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_15].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_16_patient_id] ON [#tmp_16] (patient_id);

    

    SELECT *
    INTO [#tmp_17]
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
        LEFT OUTER JOIN [#tmp_16] ON [#tmp_16].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_16].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_17_patient_id] ON [#tmp_17] (patient_id);

    

    SELECT *
    INTO [#tmp_18]
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
        LEFT OUTER JOIN [#tmp_17] ON [#tmp_17].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_17].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_18_patient_id] ON [#tmp_18] (patient_id);

    

    SELECT *
    INTO [#tmp_19]
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
        LEFT OUTER JOIN [#tmp_18] ON [#tmp_18].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_18].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_19_patient_id] ON [#tmp_19] (patient_id);

    

    SELECT *
    INTO [#tmp_20]
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
        LEFT OUTER JOIN [#tmp_19] ON [#tmp_19].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_19].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_20_patient_id] ON [#tmp_20] (patient_id);

    

    SELECT *
    INTO [#tmp_21]
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
        LEFT OUTER JOIN [#tmp_20] ON [#tmp_20].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_20].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_21_patient_id] ON [#tmp_21] (patient_id);

    

    SELECT *
    INTO [#tmp_22]
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
        LEFT OUTER JOIN [#tmp_21] ON [#tmp_21].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_21].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_22_patient_id] ON [#tmp_22] (patient_id);

    

    SELECT *
    INTO [#tmp_23]
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
        LEFT OUTER JOIN [#tmp_22] ON [#tmp_22].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_22].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_23_patient_id] ON [#tmp_23] (patient_id);

    

    SELECT *
    INTO [#tmp_24]
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
        LEFT OUTER JOIN [#tmp_23] ON [#tmp_23].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_23].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_24_patient_id] ON [#tmp_24] (patient_id);

    

    SELECT *
    INTO [#tmp_25]
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
        LEFT OUTER JOIN [#tmp_24] ON [#tmp_24].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_24].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_25_patient_id] ON [#tmp_25] (patient_id);

    

    SELECT *
    INTO [#tmp_26]
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
        LEFT OUTER JOIN [#tmp_25] ON [#tmp_25].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_25].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_26_patient_id] ON [#tmp_26] (patient_id);

    

    SELECT *
    INTO [#tmp_27]
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
        LEFT OUTER JOIN [#tmp_26] ON [#tmp_26].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_26].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_27_patient_id] ON [#tmp_27] (patient_id);

    

    SELECT *
    INTO [#tmp_28]
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
        LEFT OUTER JOIN [#tmp_27] ON [#tmp_27].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_27].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_28_patient_id] ON [#tmp_28] (patient_id);

    

    SELECT *
    INTO [#tmp_29]
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
        LEFT OUTER JOIN [#tmp_28] ON [#tmp_28].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_28].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_29_patient_id] ON [#tmp_29] (patient_id);

    

    SELECT *
    INTO [#tmp_30]
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
        LEFT OUTER JOIN [#tmp_29] ON [#tmp_29].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_29].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_30_patient_id] ON [#tmp_30] (patient_id);

    

    SELECT *
    INTO [#tmp_31]
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
        LEFT OUTER JOIN [#tmp_30] ON [#tmp_30].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_30].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_31_patient_id] ON [#tmp_31] (patient_id);

    

    SELECT *
    INTO [#tmp_32]
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
        LEFT OUTER JOIN [#tmp_31] ON [#tmp_31].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_31].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_32_patient_id] ON [#tmp_32] (patient_id);

    

    SELECT *
    INTO [#tmp_33]
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
        LEFT OUTER JOIN [#tmp_32] ON [#tmp_32].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_32].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_33_patient_id] ON [#tmp_33] (patient_id);

    

    SELECT *
    INTO [#tmp_34]
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
        LEFT OUTER JOIN [#tmp_33] ON [#tmp_33].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_33].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_34_patient_id] ON [#tmp_34] (patient_id);

    

    SELECT *
    INTO [#tmp_35]
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
        LEFT OUTER JOIN [#tmp_34] ON [#tmp_34].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_34].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_35_patient_id] ON [#tmp_35] (patient_id);

    

    SELECT *
    INTO [#tmp_36]
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
        LEFT OUTER JOIN [#tmp_35] ON [#tmp_35].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_35].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_36_patient_id] ON [#tmp_36] (patient_id);

    

    SELECT *
    INTO [#tmp_37]
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
        LEFT OUTER JOIN [#tmp_36] ON [#tmp_36].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_36].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_37_patient_id] ON [#tmp_37] (patient_id);

    

    SELECT *
    INTO [#tmp_38]
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
        LEFT OUTER JOIN [#tmp_37] ON [#tmp_37].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_37].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_38_patient_id] ON [#tmp_38] (patient_id);

    

    SELECT *
    INTO [#tmp_39]
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
        LEFT OUTER JOIN [#tmp_38] ON [#tmp_38].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_38].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_39_patient_id] ON [#tmp_39] (patient_id);

    

    SELECT *
    INTO [#tmp_40]
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
        LEFT OUTER JOIN [#tmp_39] ON [#tmp_39].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_39].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_40_patient_id] ON [#tmp_40] (patient_id);

    

    SELECT *
    INTO [#tmp_41]
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
        LEFT OUTER JOIN [#tmp_40] ON [#tmp_40].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_40].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_41_patient_id] ON [#tmp_41] (patient_id);

    

    SELECT *
    INTO [#tmp_42]
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
        LEFT OUTER JOIN [#tmp_41] ON [#tmp_41].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_41].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_42_patient_id] ON [#tmp_42] (patient_id);

    

    SELECT *
    INTO [#tmp_43]
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
        LEFT OUTER JOIN [#tmp_42] ON [#tmp_42].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_42].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_43_patient_id] ON [#tmp_43] (patient_id);

    

    SELECT *
    INTO [#tmp_44]
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
        LEFT OUTER JOIN [#tmp_43] ON [#tmp_43].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_43].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_44_patient_id] ON [#tmp_44] (patient_id);

    

    SELECT *
    INTO [#tmp_45]
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
        LEFT OUTER JOIN [#tmp_44] ON [#tmp_44].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_44].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_45_patient_id] ON [#tmp_45] (patient_id);

    

    SELECT *
    INTO [#tmp_46]
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
        LEFT OUTER JOIN [#tmp_45] ON [#tmp_45].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_45].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_46_patient_id] ON [#tmp_46] (patient_id);

    

    SELECT *
    INTO [#tmp_47]
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
        LEFT OUTER JOIN [#tmp_46] ON [#tmp_46].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_46].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_47_patient_id] ON [#tmp_47] (patient_id);

    

    SELECT *
    INTO [#tmp_48]
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
        LEFT OUTER JOIN [#tmp_47] ON [#tmp_47].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_47].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_48_patient_id] ON [#tmp_48] (patient_id);

    

    SELECT *
    INTO [#tmp_49]
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
        LEFT OUTER JOIN [#tmp_48] ON [#tmp_48].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_48].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_49_patient_id] ON [#tmp_49] (patient_id);

    

    SELECT *
    INTO [#tmp_50]
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
        LEFT OUTER JOIN [#tmp_49] ON [#tmp_49].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_49].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_50_patient_id] ON [#tmp_50] (patient_id);

    

    SELECT *
    INTO [#tmp_51]
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
        LEFT OUTER JOIN [#tmp_50] ON [#tmp_50].patient_id = [Appointment].[Patient_ID]
        WHERE [Appointment].BookedDate > [#tmp_50].booked_date
          AND [Appointment].BookedDate <= '20221231'
        ) AS anon_2
          WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_51_patient_id] ON [#tmp_51] (patient_id);

    

SELECT * INTO [#results] FROM (
  SELECT Patient.Patient_ID AS patient_id,


    [#tmp_0].start_date AS start_date_0,
    [#tmp_0].booked_date AS booked_date_0,
    [#tmp_0].organisation_id AS organisation_id_0,
    

    [#tmp_1].start_date AS start_date_1,
    [#tmp_1].booked_date AS booked_date_1,
    [#tmp_1].organisation_id AS organisation_id_1,
    

    [#tmp_2].start_date AS start_date_2,
    [#tmp_2].booked_date AS booked_date_2,
    [#tmp_2].organisation_id AS organisation_id_2,
    

    [#tmp_3].start_date AS start_date_3,
    [#tmp_3].booked_date AS booked_date_3,
    [#tmp_3].organisation_id AS organisation_id_3,
    

    [#tmp_4].start_date AS start_date_4,
    [#tmp_4].booked_date AS booked_date_4,
    [#tmp_4].organisation_id AS organisation_id_4,
    

    [#tmp_5].start_date AS start_date_5,
    [#tmp_5].booked_date AS booked_date_5,
    [#tmp_5].organisation_id AS organisation_id_5,
    

    [#tmp_6].start_date AS start_date_6,
    [#tmp_6].booked_date AS booked_date_6,
    [#tmp_6].organisation_id AS organisation_id_6,
    

    [#tmp_7].start_date AS start_date_7,
    [#tmp_7].booked_date AS booked_date_7,
    [#tmp_7].organisation_id AS organisation_id_7,
    

    [#tmp_8].start_date AS start_date_8,
    [#tmp_8].booked_date AS booked_date_8,
    [#tmp_8].organisation_id AS organisation_id_8,
    

    [#tmp_9].start_date AS start_date_9,
    [#tmp_9].booked_date AS booked_date_9,
    [#tmp_9].organisation_id AS organisation_id_9,
    

    [#tmp_10].start_date AS start_date_10,
    [#tmp_10].booked_date AS booked_date_10,
    [#tmp_10].organisation_id AS organisation_id_10,
    

    [#tmp_11].start_date AS start_date_11,
    [#tmp_11].booked_date AS booked_date_11,
    [#tmp_11].organisation_id AS organisation_id_11,
    

    [#tmp_12].start_date AS start_date_12,
    [#tmp_12].booked_date AS booked_date_12,
    [#tmp_12].organisation_id AS organisation_id_12,
    

    [#tmp_13].start_date AS start_date_13,
    [#tmp_13].booked_date AS booked_date_13,
    [#tmp_13].organisation_id AS organisation_id_13,
    

    [#tmp_14].start_date AS start_date_14,
    [#tmp_14].booked_date AS booked_date_14,
    [#tmp_14].organisation_id AS organisation_id_14,
    

    [#tmp_15].start_date AS start_date_15,
    [#tmp_15].booked_date AS booked_date_15,
    [#tmp_15].organisation_id AS organisation_id_15,
    

    [#tmp_16].start_date AS start_date_16,
    [#tmp_16].booked_date AS booked_date_16,
    [#tmp_16].organisation_id AS organisation_id_16,
    

    [#tmp_17].start_date AS start_date_17,
    [#tmp_17].booked_date AS booked_date_17,
    [#tmp_17].organisation_id AS organisation_id_17,
    

    [#tmp_18].start_date AS start_date_18,
    [#tmp_18].booked_date AS booked_date_18,
    [#tmp_18].organisation_id AS organisation_id_18,
    

    [#tmp_19].start_date AS start_date_19,
    [#tmp_19].booked_date AS booked_date_19,
    [#tmp_19].organisation_id AS organisation_id_19,
    

    [#tmp_20].start_date AS start_date_20,
    [#tmp_20].booked_date AS booked_date_20,
    [#tmp_20].organisation_id AS organisation_id_20,
    

    [#tmp_21].start_date AS start_date_21,
    [#tmp_21].booked_date AS booked_date_21,
    [#tmp_21].organisation_id AS organisation_id_21,
    

    [#tmp_22].start_date AS start_date_22,
    [#tmp_22].booked_date AS booked_date_22,
    [#tmp_22].organisation_id AS organisation_id_22,
    

    [#tmp_23].start_date AS start_date_23,
    [#tmp_23].booked_date AS booked_date_23,
    [#tmp_23].organisation_id AS organisation_id_23,
    

    [#tmp_24].start_date AS start_date_24,
    [#tmp_24].booked_date AS booked_date_24,
    [#tmp_24].organisation_id AS organisation_id_24,
    

    [#tmp_25].start_date AS start_date_25,
    [#tmp_25].booked_date AS booked_date_25,
    [#tmp_25].organisation_id AS organisation_id_25,
    

    [#tmp_26].start_date AS start_date_26,
    [#tmp_26].booked_date AS booked_date_26,
    [#tmp_26].organisation_id AS organisation_id_26,
    

    [#tmp_27].start_date AS start_date_27,
    [#tmp_27].booked_date AS booked_date_27,
    [#tmp_27].organisation_id AS organisation_id_27,
    

    [#tmp_28].start_date AS start_date_28,
    [#tmp_28].booked_date AS booked_date_28,
    [#tmp_28].organisation_id AS organisation_id_28,
    

    [#tmp_29].start_date AS start_date_29,
    [#tmp_29].booked_date AS booked_date_29,
    [#tmp_29].organisation_id AS organisation_id_29,
    

    [#tmp_30].start_date AS start_date_30,
    [#tmp_30].booked_date AS booked_date_30,
    [#tmp_30].organisation_id AS organisation_id_30,
    

    [#tmp_31].start_date AS start_date_31,
    [#tmp_31].booked_date AS booked_date_31,
    [#tmp_31].organisation_id AS organisation_id_31,
    

    [#tmp_32].start_date AS start_date_32,
    [#tmp_32].booked_date AS booked_date_32,
    [#tmp_32].organisation_id AS organisation_id_32,
    

    [#tmp_33].start_date AS start_date_33,
    [#tmp_33].booked_date AS booked_date_33,
    [#tmp_33].organisation_id AS organisation_id_33,
    

    [#tmp_34].start_date AS start_date_34,
    [#tmp_34].booked_date AS booked_date_34,
    [#tmp_34].organisation_id AS organisation_id_34,
    

    [#tmp_35].start_date AS start_date_35,
    [#tmp_35].booked_date AS booked_date_35,
    [#tmp_35].organisation_id AS organisation_id_35,
    

    [#tmp_36].start_date AS start_date_36,
    [#tmp_36].booked_date AS booked_date_36,
    [#tmp_36].organisation_id AS organisation_id_36,
    

    [#tmp_37].start_date AS start_date_37,
    [#tmp_37].booked_date AS booked_date_37,
    [#tmp_37].organisation_id AS organisation_id_37,
    

    [#tmp_38].start_date AS start_date_38,
    [#tmp_38].booked_date AS booked_date_38,
    [#tmp_38].organisation_id AS organisation_id_38,
    

    [#tmp_39].start_date AS start_date_39,
    [#tmp_39].booked_date AS booked_date_39,
    [#tmp_39].organisation_id AS organisation_id_39,
    

    [#tmp_40].start_date AS start_date_40,
    [#tmp_40].booked_date AS booked_date_40,
    [#tmp_40].organisation_id AS organisation_id_40,
    

    [#tmp_41].start_date AS start_date_41,
    [#tmp_41].booked_date AS booked_date_41,
    [#tmp_41].organisation_id AS organisation_id_41,
    

    [#tmp_42].start_date AS start_date_42,
    [#tmp_42].booked_date AS booked_date_42,
    [#tmp_42].organisation_id AS organisation_id_42,
    

    [#tmp_43].start_date AS start_date_43,
    [#tmp_43].booked_date AS booked_date_43,
    [#tmp_43].organisation_id AS organisation_id_43,
    

    [#tmp_44].start_date AS start_date_44,
    [#tmp_44].booked_date AS booked_date_44,
    [#tmp_44].organisation_id AS organisation_id_44,
    

    [#tmp_45].start_date AS start_date_45,
    [#tmp_45].booked_date AS booked_date_45,
    [#tmp_45].organisation_id AS organisation_id_45,
    

    [#tmp_46].start_date AS start_date_46,
    [#tmp_46].booked_date AS booked_date_46,
    [#tmp_46].organisation_id AS organisation_id_46,
    

    [#tmp_47].start_date AS start_date_47,
    [#tmp_47].booked_date AS booked_date_47,
    [#tmp_47].organisation_id AS organisation_id_47,
    

    [#tmp_48].start_date AS start_date_48,
    [#tmp_48].booked_date AS booked_date_48,
    [#tmp_48].organisation_id AS organisation_id_48,
    

    [#tmp_49].start_date AS start_date_49,
    [#tmp_49].booked_date AS booked_date_49,
    [#tmp_49].organisation_id AS organisation_id_49,
    

    [#tmp_50].start_date AS start_date_50,
    [#tmp_50].booked_date AS booked_date_50,
    [#tmp_50].organisation_id AS organisation_id_50,
    

    [#tmp_51].start_date AS start_date_51,
    [#tmp_51].booked_date AS booked_date_51,
    [#tmp_51].organisation_id AS organisation_id_51
    

  FROM Patient

  LEFT OUTER JOIN [#tmp_0] ON [#tmp_0].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_1] ON [#tmp_1].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_2] ON [#tmp_2].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_3] ON [#tmp_3].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_4] ON [#tmp_4].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_5] ON [#tmp_5].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_6] ON [#tmp_6].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_7] ON [#tmp_7].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_8] ON [#tmp_8].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_9] ON [#tmp_9].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_10] ON [#tmp_10].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_11] ON [#tmp_11].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_12] ON [#tmp_12].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_13] ON [#tmp_13].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_14] ON [#tmp_14].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_15] ON [#tmp_15].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_16] ON [#tmp_16].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_17] ON [#tmp_17].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_18] ON [#tmp_18].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_19] ON [#tmp_19].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_20] ON [#tmp_20].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_21] ON [#tmp_21].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_22] ON [#tmp_22].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_23] ON [#tmp_23].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_24] ON [#tmp_24].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_25] ON [#tmp_25].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_26] ON [#tmp_26].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_27] ON [#tmp_27].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_28] ON [#tmp_28].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_29] ON [#tmp_29].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_30] ON [#tmp_30].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_31] ON [#tmp_31].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_32] ON [#tmp_32].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_33] ON [#tmp_33].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_34] ON [#tmp_34].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_35] ON [#tmp_35].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_36] ON [#tmp_36].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_37] ON [#tmp_37].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_38] ON [#tmp_38].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_39] ON [#tmp_39].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_40] ON [#tmp_40].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_41] ON [#tmp_41].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_42] ON [#tmp_42].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_43] ON [#tmp_43].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_44] ON [#tmp_44].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_45] ON [#tmp_45].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_46] ON [#tmp_46].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_47] ON [#tmp_47].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_48] ON [#tmp_48].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_49] ON [#tmp_49].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_50] ON [#tmp_50].patient_id = Patient.Patient_ID
  LEFT OUTER JOIN [#tmp_51] ON [#tmp_51].patient_id = Patient.Patient_ID

) t;

