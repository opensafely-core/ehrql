
SET STATISTICS TIME ON;



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



    SELECT *
    INTO [#tmp_1]
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
        LEFT OUTER JOIN [#tmp_0] ON [#tmp_0].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_0].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_1_patient_id] ON [#tmp_1] (patient_id);



    SELECT *
    INTO [#tmp_2]
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
        LEFT OUTER JOIN [#tmp_1] ON [#tmp_1].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_1].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_2_patient_id] ON [#tmp_2] (patient_id);



    SELECT *
    INTO [#tmp_3]
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
        LEFT OUTER JOIN [#tmp_2] ON [#tmp_2].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_2].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_3_patient_id] ON [#tmp_3] (patient_id);



    SELECT *
    INTO [#tmp_4]
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
        LEFT OUTER JOIN [#tmp_3] ON [#tmp_3].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_3].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_4_patient_id] ON [#tmp_4] (patient_id);



    SELECT *
    INTO [#tmp_5]
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
        LEFT OUTER JOIN [#tmp_4] ON [#tmp_4].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_4].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_5_patient_id] ON [#tmp_5] (patient_id);



    SELECT *
    INTO [#tmp_6]
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
        LEFT OUTER JOIN [#tmp_5] ON [#tmp_5].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_5].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_6_patient_id] ON [#tmp_6] (patient_id);



    SELECT *
    INTO [#tmp_7]
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
        LEFT OUTER JOIN [#tmp_6] ON [#tmp_6].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_6].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_7_patient_id] ON [#tmp_7] (patient_id);



    SELECT *
    INTO [#tmp_8]
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
        LEFT OUTER JOIN [#tmp_7] ON [#tmp_7].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_7].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_8_patient_id] ON [#tmp_8] (patient_id);



    SELECT *
    INTO [#tmp_9]
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
        LEFT OUTER JOIN [#tmp_8] ON [#tmp_8].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_8].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_9_patient_id] ON [#tmp_9] (patient_id);



    SELECT *
    INTO [#tmp_10]
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
        LEFT OUTER JOIN [#tmp_9] ON [#tmp_9].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_9].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_10_patient_id] ON [#tmp_10] (patient_id);



    SELECT *
    INTO [#tmp_11]
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
        LEFT OUTER JOIN [#tmp_10] ON [#tmp_10].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_10].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_11_patient_id] ON [#tmp_11] (patient_id);



    SELECT *
    INTO [#tmp_12]
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
        LEFT OUTER JOIN [#tmp_11] ON [#tmp_11].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_11].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_12_patient_id] ON [#tmp_12] (patient_id);



    SELECT *
    INTO [#tmp_13]
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
        LEFT OUTER JOIN [#tmp_12] ON [#tmp_12].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_12].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_13_patient_id] ON [#tmp_13] (patient_id);



    SELECT *
    INTO [#tmp_14]
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
        LEFT OUTER JOIN [#tmp_13] ON [#tmp_13].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_13].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_14_patient_id] ON [#tmp_14] (patient_id);



    SELECT *
    INTO [#tmp_15]
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
        LEFT OUTER JOIN [#tmp_14] ON [#tmp_14].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_14].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_15_patient_id] ON [#tmp_15] (patient_id);



    SELECT *
    INTO [#tmp_16]
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
        LEFT OUTER JOIN [#tmp_15] ON [#tmp_15].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_15].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_16_patient_id] ON [#tmp_16] (patient_id);



    SELECT *
    INTO [#tmp_17]
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
        LEFT OUTER JOIN [#tmp_16] ON [#tmp_16].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_16].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_17_patient_id] ON [#tmp_17] (patient_id);



    SELECT *
    INTO [#tmp_18]
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
        LEFT OUTER JOIN [#tmp_17] ON [#tmp_17].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_17].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_18_patient_id] ON [#tmp_18] (patient_id);



    SELECT *
    INTO [#tmp_19]
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
        LEFT OUTER JOIN [#tmp_18] ON [#tmp_18].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_18].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_19_patient_id] ON [#tmp_19] (patient_id);



    SELECT *
    INTO [#tmp_20]
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
        LEFT OUTER JOIN [#tmp_19] ON [#tmp_19].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_19].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_20_patient_id] ON [#tmp_20] (patient_id);



    SELECT *
    INTO [#tmp_21]
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
        LEFT OUTER JOIN [#tmp_20] ON [#tmp_20].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_20].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_21_patient_id] ON [#tmp_21] (patient_id);



    SELECT *
    INTO [#tmp_22]
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
        LEFT OUTER JOIN [#tmp_21] ON [#tmp_21].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_21].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_22_patient_id] ON [#tmp_22] (patient_id);



    SELECT *
    INTO [#tmp_23]
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
        LEFT OUTER JOIN [#tmp_22] ON [#tmp_22].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_22].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_23_patient_id] ON [#tmp_23] (patient_id);



    SELECT *
    INTO [#tmp_24]
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
        LEFT OUTER JOIN [#tmp_23] ON [#tmp_23].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_23].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_24_patient_id] ON [#tmp_24] (patient_id);



    SELECT *
    INTO [#tmp_25]
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
        LEFT OUTER JOIN [#tmp_24] ON [#tmp_24].patient_id = [ONS_CIS_New].[Patient_ID]
        WHERE [ONS_CIS_New].visit_date > [#tmp_24].visit_date
        ) AS anon_2
      WHERE anon_2.anon_3 = 1
      ) AS anon_1;

    CREATE CLUSTERED INDEX [ix_#tmp_25_patient_id] ON [#tmp_25] (patient_id);



SELECT *
INTO [#pop]
FROM (
  SELECT DISTINCT [ONS_CIS_New].[Patient_ID] AS patient_id
  FROM [ONS_CIS_New]
  WHERE [ONS_CIS_New].visit_date >= '20200124'
    AND [ONS_CIS_New].visit_date <= '20220331'
  ) AS anon_1;



SELECT * INTO [#results] FROM (
  SELECT [#pop].patient_id AS patient_id,


    [#tmp_0].visit_date AS visit_date_0,
    [#tmp_0].visit_num AS visit_num_0,
    [#tmp_0].last_linkage_dt AS last_linkage_dt_0,
    [#tmp_0].nhs_data_share AS is_opted_out_of_nhs_data_share_0,


    [#tmp_1].visit_date AS visit_date_1,
    [#tmp_1].visit_num AS visit_num_1,
    [#tmp_1].last_linkage_dt AS last_linkage_dt_1,
    [#tmp_1].nhs_data_share AS is_opted_out_of_nhs_data_share_1,


    [#tmp_2].visit_date AS visit_date_2,
    [#tmp_2].visit_num AS visit_num_2,
    [#tmp_2].last_linkage_dt AS last_linkage_dt_2,
    [#tmp_2].nhs_data_share AS is_opted_out_of_nhs_data_share_2,


    [#tmp_3].visit_date AS visit_date_3,
    [#tmp_3].visit_num AS visit_num_3,
    [#tmp_3].last_linkage_dt AS last_linkage_dt_3,
    [#tmp_3].nhs_data_share AS is_opted_out_of_nhs_data_share_3,


    [#tmp_4].visit_date AS visit_date_4,
    [#tmp_4].visit_num AS visit_num_4,
    [#tmp_4].last_linkage_dt AS last_linkage_dt_4,
    [#tmp_4].nhs_data_share AS is_opted_out_of_nhs_data_share_4,


    [#tmp_5].visit_date AS visit_date_5,
    [#tmp_5].visit_num AS visit_num_5,
    [#tmp_5].last_linkage_dt AS last_linkage_dt_5,
    [#tmp_5].nhs_data_share AS is_opted_out_of_nhs_data_share_5,


    [#tmp_6].visit_date AS visit_date_6,
    [#tmp_6].visit_num AS visit_num_6,
    [#tmp_6].last_linkage_dt AS last_linkage_dt_6,
    [#tmp_6].nhs_data_share AS is_opted_out_of_nhs_data_share_6,


    [#tmp_7].visit_date AS visit_date_7,
    [#tmp_7].visit_num AS visit_num_7,
    [#tmp_7].last_linkage_dt AS last_linkage_dt_7,
    [#tmp_7].nhs_data_share AS is_opted_out_of_nhs_data_share_7,


    [#tmp_8].visit_date AS visit_date_8,
    [#tmp_8].visit_num AS visit_num_8,
    [#tmp_8].last_linkage_dt AS last_linkage_dt_8,
    [#tmp_8].nhs_data_share AS is_opted_out_of_nhs_data_share_8,


    [#tmp_9].visit_date AS visit_date_9,
    [#tmp_9].visit_num AS visit_num_9,
    [#tmp_9].last_linkage_dt AS last_linkage_dt_9,
    [#tmp_9].nhs_data_share AS is_opted_out_of_nhs_data_share_9,


    [#tmp_10].visit_date AS visit_date_10,
    [#tmp_10].visit_num AS visit_num_10,
    [#tmp_10].last_linkage_dt AS last_linkage_dt_10,
    [#tmp_10].nhs_data_share AS is_opted_out_of_nhs_data_share_10,


    [#tmp_11].visit_date AS visit_date_11,
    [#tmp_11].visit_num AS visit_num_11,
    [#tmp_11].last_linkage_dt AS last_linkage_dt_11,
    [#tmp_11].nhs_data_share AS is_opted_out_of_nhs_data_share_11,


    [#tmp_12].visit_date AS visit_date_12,
    [#tmp_12].visit_num AS visit_num_12,
    [#tmp_12].last_linkage_dt AS last_linkage_dt_12,
    [#tmp_12].nhs_data_share AS is_opted_out_of_nhs_data_share_12,


    [#tmp_13].visit_date AS visit_date_13,
    [#tmp_13].visit_num AS visit_num_13,
    [#tmp_13].last_linkage_dt AS last_linkage_dt_13,
    [#tmp_13].nhs_data_share AS is_opted_out_of_nhs_data_share_13,


    [#tmp_14].visit_date AS visit_date_14,
    [#tmp_14].visit_num AS visit_num_14,
    [#tmp_14].last_linkage_dt AS last_linkage_dt_14,
    [#tmp_14].nhs_data_share AS is_opted_out_of_nhs_data_share_14,


    [#tmp_15].visit_date AS visit_date_15,
    [#tmp_15].visit_num AS visit_num_15,
    [#tmp_15].last_linkage_dt AS last_linkage_dt_15,
    [#tmp_15].nhs_data_share AS is_opted_out_of_nhs_data_share_15,


    [#tmp_16].visit_date AS visit_date_16,
    [#tmp_16].visit_num AS visit_num_16,
    [#tmp_16].last_linkage_dt AS last_linkage_dt_16,
    [#tmp_16].nhs_data_share AS is_opted_out_of_nhs_data_share_16,


    [#tmp_17].visit_date AS visit_date_17,
    [#tmp_17].visit_num AS visit_num_17,
    [#tmp_17].last_linkage_dt AS last_linkage_dt_17,
    [#tmp_17].nhs_data_share AS is_opted_out_of_nhs_data_share_17,


    [#tmp_18].visit_date AS visit_date_18,
    [#tmp_18].visit_num AS visit_num_18,
    [#tmp_18].last_linkage_dt AS last_linkage_dt_18,
    [#tmp_18].nhs_data_share AS is_opted_out_of_nhs_data_share_18,


    [#tmp_19].visit_date AS visit_date_19,
    [#tmp_19].visit_num AS visit_num_19,
    [#tmp_19].last_linkage_dt AS last_linkage_dt_19,
    [#tmp_19].nhs_data_share AS is_opted_out_of_nhs_data_share_19,


    [#tmp_20].visit_date AS visit_date_20,
    [#tmp_20].visit_num AS visit_num_20,
    [#tmp_20].last_linkage_dt AS last_linkage_dt_20,
    [#tmp_20].nhs_data_share AS is_opted_out_of_nhs_data_share_20,


    [#tmp_21].visit_date AS visit_date_21,
    [#tmp_21].visit_num AS visit_num_21,
    [#tmp_21].last_linkage_dt AS last_linkage_dt_21,
    [#tmp_21].nhs_data_share AS is_opted_out_of_nhs_data_share_21,


    [#tmp_22].visit_date AS visit_date_22,
    [#tmp_22].visit_num AS visit_num_22,
    [#tmp_22].last_linkage_dt AS last_linkage_dt_22,
    [#tmp_22].nhs_data_share AS is_opted_out_of_nhs_data_share_22,


    [#tmp_23].visit_date AS visit_date_23,
    [#tmp_23].visit_num AS visit_num_23,
    [#tmp_23].last_linkage_dt AS last_linkage_dt_23,
    [#tmp_23].nhs_data_share AS is_opted_out_of_nhs_data_share_23,


    [#tmp_24].visit_date AS visit_date_24,
    [#tmp_24].visit_num AS visit_num_24,
    [#tmp_24].last_linkage_dt AS last_linkage_dt_24,
    [#tmp_24].nhs_data_share AS is_opted_out_of_nhs_data_share_24,


    [#tmp_25].visit_date AS visit_date_25,
    [#tmp_25].visit_num AS visit_num_25,
    [#tmp_25].last_linkage_dt AS last_linkage_dt_25,
    [#tmp_25].nhs_data_share AS is_opted_out_of_nhs_data_share_25


  FROM [#pop]

  LEFT OUTER JOIN [#tmp_0] ON [#tmp_0].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_1] ON [#tmp_1].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_2] ON [#tmp_2].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_3] ON [#tmp_3].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_4] ON [#tmp_4].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_5] ON [#tmp_5].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_6] ON [#tmp_6].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_7] ON [#tmp_7].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_8] ON [#tmp_8].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_9] ON [#tmp_9].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_10] ON [#tmp_10].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_11] ON [#tmp_11].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_12] ON [#tmp_12].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_13] ON [#tmp_13].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_14] ON [#tmp_14].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_15] ON [#tmp_15].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_16] ON [#tmp_16].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_17] ON [#tmp_17].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_18] ON [#tmp_18].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_19] ON [#tmp_19].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_20] ON [#tmp_20].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_21] ON [#tmp_21].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_22] ON [#tmp_22].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_23] ON [#tmp_23].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_24] ON [#tmp_24].patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_25] ON [#tmp_25].patient_id = [#pop].patient_id

  WHERE [#pop].patient_id IS NOT NULL
) t;
