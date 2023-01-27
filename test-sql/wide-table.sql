
SET STATISTICS TIME ON;



SELECT *
INTO [#tmp_0]
FROM (
  SELECT
    anon_2.patient_id AS patient_id,


    MAX(CASE WHEN anon_2.row_num = 1 THEN anon_2.visit_num END) AS visit_num_0,
    MAX(CASE WHEN anon_2.row_num = 1 THEN anon_2.visit_date END) AS visit_date_0,
    MAX(CASE WHEN anon_2.row_num = 1 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_0,
    MAX(CASE WHEN anon_2.row_num = 1 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_0,


    MAX(CASE WHEN anon_2.row_num = 2 THEN anon_2.visit_num END) AS visit_num_1,
    MAX(CASE WHEN anon_2.row_num = 2 THEN anon_2.visit_date END) AS visit_date_1,
    MAX(CASE WHEN anon_2.row_num = 2 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_1,
    MAX(CASE WHEN anon_2.row_num = 2 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_1,


    MAX(CASE WHEN anon_2.row_num = 3 THEN anon_2.visit_num END) AS visit_num_2,
    MAX(CASE WHEN anon_2.row_num = 3 THEN anon_2.visit_date END) AS visit_date_2,
    MAX(CASE WHEN anon_2.row_num = 3 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_2,
    MAX(CASE WHEN anon_2.row_num = 3 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_2,


    MAX(CASE WHEN anon_2.row_num = 4 THEN anon_2.visit_num END) AS visit_num_3,
    MAX(CASE WHEN anon_2.row_num = 4 THEN anon_2.visit_date END) AS visit_date_3,
    MAX(CASE WHEN anon_2.row_num = 4 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_3,
    MAX(CASE WHEN anon_2.row_num = 4 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_3,


    MAX(CASE WHEN anon_2.row_num = 5 THEN anon_2.visit_num END) AS visit_num_4,
    MAX(CASE WHEN anon_2.row_num = 5 THEN anon_2.visit_date END) AS visit_date_4,
    MAX(CASE WHEN anon_2.row_num = 5 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_4,
    MAX(CASE WHEN anon_2.row_num = 5 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_4,


    MAX(CASE WHEN anon_2.row_num = 6 THEN anon_2.visit_num END) AS visit_num_5,
    MAX(CASE WHEN anon_2.row_num = 6 THEN anon_2.visit_date END) AS visit_date_5,
    MAX(CASE WHEN anon_2.row_num = 6 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_5,
    MAX(CASE WHEN anon_2.row_num = 6 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_5,


    MAX(CASE WHEN anon_2.row_num = 7 THEN anon_2.visit_num END) AS visit_num_6,
    MAX(CASE WHEN anon_2.row_num = 7 THEN anon_2.visit_date END) AS visit_date_6,
    MAX(CASE WHEN anon_2.row_num = 7 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_6,
    MAX(CASE WHEN anon_2.row_num = 7 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_6,


    MAX(CASE WHEN anon_2.row_num = 8 THEN anon_2.visit_num END) AS visit_num_7,
    MAX(CASE WHEN anon_2.row_num = 8 THEN anon_2.visit_date END) AS visit_date_7,
    MAX(CASE WHEN anon_2.row_num = 8 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_7,
    MAX(CASE WHEN anon_2.row_num = 8 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_7,


    MAX(CASE WHEN anon_2.row_num = 9 THEN anon_2.visit_num END) AS visit_num_8,
    MAX(CASE WHEN anon_2.row_num = 9 THEN anon_2.visit_date END) AS visit_date_8,
    MAX(CASE WHEN anon_2.row_num = 9 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_8,
    MAX(CASE WHEN anon_2.row_num = 9 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_8,


    MAX(CASE WHEN anon_2.row_num = 10 THEN anon_2.visit_num END) AS visit_num_9,
    MAX(CASE WHEN anon_2.row_num = 10 THEN anon_2.visit_date END) AS visit_date_9,
    MAX(CASE WHEN anon_2.row_num = 10 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_9,
    MAX(CASE WHEN anon_2.row_num = 10 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_9,


    MAX(CASE WHEN anon_2.row_num = 11 THEN anon_2.visit_num END) AS visit_num_10,
    MAX(CASE WHEN anon_2.row_num = 11 THEN anon_2.visit_date END) AS visit_date_10,
    MAX(CASE WHEN anon_2.row_num = 11 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_10,
    MAX(CASE WHEN anon_2.row_num = 11 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_10,


    MAX(CASE WHEN anon_2.row_num = 12 THEN anon_2.visit_num END) AS visit_num_11,
    MAX(CASE WHEN anon_2.row_num = 12 THEN anon_2.visit_date END) AS visit_date_11,
    MAX(CASE WHEN anon_2.row_num = 12 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_11,
    MAX(CASE WHEN anon_2.row_num = 12 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_11,


    MAX(CASE WHEN anon_2.row_num = 13 THEN anon_2.visit_num END) AS visit_num_12,
    MAX(CASE WHEN anon_2.row_num = 13 THEN anon_2.visit_date END) AS visit_date_12,
    MAX(CASE WHEN anon_2.row_num = 13 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_12,
    MAX(CASE WHEN anon_2.row_num = 13 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_12,


    MAX(CASE WHEN anon_2.row_num = 14 THEN anon_2.visit_num END) AS visit_num_13,
    MAX(CASE WHEN anon_2.row_num = 14 THEN anon_2.visit_date END) AS visit_date_13,
    MAX(CASE WHEN anon_2.row_num = 14 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_13,
    MAX(CASE WHEN anon_2.row_num = 14 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_13,


    MAX(CASE WHEN anon_2.row_num = 15 THEN anon_2.visit_num END) AS visit_num_14,
    MAX(CASE WHEN anon_2.row_num = 15 THEN anon_2.visit_date END) AS visit_date_14,
    MAX(CASE WHEN anon_2.row_num = 15 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_14,
    MAX(CASE WHEN anon_2.row_num = 15 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_14,


    MAX(CASE WHEN anon_2.row_num = 16 THEN anon_2.visit_num END) AS visit_num_15,
    MAX(CASE WHEN anon_2.row_num = 16 THEN anon_2.visit_date END) AS visit_date_15,
    MAX(CASE WHEN anon_2.row_num = 16 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_15,
    MAX(CASE WHEN anon_2.row_num = 16 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_15,


    MAX(CASE WHEN anon_2.row_num = 17 THEN anon_2.visit_num END) AS visit_num_16,
    MAX(CASE WHEN anon_2.row_num = 17 THEN anon_2.visit_date END) AS visit_date_16,
    MAX(CASE WHEN anon_2.row_num = 17 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_16,
    MAX(CASE WHEN anon_2.row_num = 17 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_16,


    MAX(CASE WHEN anon_2.row_num = 18 THEN anon_2.visit_num END) AS visit_num_17,
    MAX(CASE WHEN anon_2.row_num = 18 THEN anon_2.visit_date END) AS visit_date_17,
    MAX(CASE WHEN anon_2.row_num = 18 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_17,
    MAX(CASE WHEN anon_2.row_num = 18 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_17,


    MAX(CASE WHEN anon_2.row_num = 19 THEN anon_2.visit_num END) AS visit_num_18,
    MAX(CASE WHEN anon_2.row_num = 19 THEN anon_2.visit_date END) AS visit_date_18,
    MAX(CASE WHEN anon_2.row_num = 19 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_18,
    MAX(CASE WHEN anon_2.row_num = 19 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_18,


    MAX(CASE WHEN anon_2.row_num = 20 THEN anon_2.visit_num END) AS visit_num_19,
    MAX(CASE WHEN anon_2.row_num = 20 THEN anon_2.visit_date END) AS visit_date_19,
    MAX(CASE WHEN anon_2.row_num = 20 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_19,
    MAX(CASE WHEN anon_2.row_num = 20 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_19,


    MAX(CASE WHEN anon_2.row_num = 21 THEN anon_2.visit_num END) AS visit_num_20,
    MAX(CASE WHEN anon_2.row_num = 21 THEN anon_2.visit_date END) AS visit_date_20,
    MAX(CASE WHEN anon_2.row_num = 21 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_20,
    MAX(CASE WHEN anon_2.row_num = 21 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_20,


    MAX(CASE WHEN anon_2.row_num = 22 THEN anon_2.visit_num END) AS visit_num_21,
    MAX(CASE WHEN anon_2.row_num = 22 THEN anon_2.visit_date END) AS visit_date_21,
    MAX(CASE WHEN anon_2.row_num = 22 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_21,
    MAX(CASE WHEN anon_2.row_num = 22 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_21,


    MAX(CASE WHEN anon_2.row_num = 23 THEN anon_2.visit_num END) AS visit_num_22,
    MAX(CASE WHEN anon_2.row_num = 23 THEN anon_2.visit_date END) AS visit_date_22,
    MAX(CASE WHEN anon_2.row_num = 23 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_22,
    MAX(CASE WHEN anon_2.row_num = 23 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_22,


    MAX(CASE WHEN anon_2.row_num = 24 THEN anon_2.visit_num END) AS visit_num_23,
    MAX(CASE WHEN anon_2.row_num = 24 THEN anon_2.visit_date END) AS visit_date_23,
    MAX(CASE WHEN anon_2.row_num = 24 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_23,
    MAX(CASE WHEN anon_2.row_num = 24 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_23,


    MAX(CASE WHEN anon_2.row_num = 25 THEN anon_2.visit_num END) AS visit_num_24,
    MAX(CASE WHEN anon_2.row_num = 25 THEN anon_2.visit_date END) AS visit_date_24,
    MAX(CASE WHEN anon_2.row_num = 25 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_24,
    MAX(CASE WHEN anon_2.row_num = 25 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_24,


    MAX(CASE WHEN anon_2.row_num = 26 THEN anon_2.visit_num END) AS visit_num_25,
    MAX(CASE WHEN anon_2.row_num = 26 THEN anon_2.visit_date END) AS visit_date_25,
    MAX(CASE WHEN anon_2.row_num = 26 THEN anon_2.nhs_data_share END) AS is_opted_out_of_nhs_data_share_25,
    MAX(CASE WHEN anon_2.row_num = 26 THEN anon_2.last_linkage_dt END) AS last_linkage_dt_25


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
  WHERE anon_2.row_num <= 26
  GROUP BY anon_2.patient_id
  ) AS anon_1;

CREATE CLUSTERED INDEX [ix_#tmp_0_patient_id] ON [#tmp_0] (patient_id);



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


    [#tmp_0].visit_date_0,
    [#tmp_0].visit_num_0,
    [#tmp_0].last_linkage_dt_0,
    [#tmp_0].is_opted_out_of_nhs_data_share_0,


    [#tmp_0].visit_date_1,
    [#tmp_0].visit_num_1,
    [#tmp_0].last_linkage_dt_1,
    [#tmp_0].is_opted_out_of_nhs_data_share_1,


    [#tmp_0].visit_date_2,
    [#tmp_0].visit_num_2,
    [#tmp_0].last_linkage_dt_2,
    [#tmp_0].is_opted_out_of_nhs_data_share_2,


    [#tmp_0].visit_date_3,
    [#tmp_0].visit_num_3,
    [#tmp_0].last_linkage_dt_3,
    [#tmp_0].is_opted_out_of_nhs_data_share_3,


    [#tmp_0].visit_date_4,
    [#tmp_0].visit_num_4,
    [#tmp_0].last_linkage_dt_4,
    [#tmp_0].is_opted_out_of_nhs_data_share_4,


    [#tmp_0].visit_date_5,
    [#tmp_0].visit_num_5,
    [#tmp_0].last_linkage_dt_5,
    [#tmp_0].is_opted_out_of_nhs_data_share_5,


    [#tmp_0].visit_date_6,
    [#tmp_0].visit_num_6,
    [#tmp_0].last_linkage_dt_6,
    [#tmp_0].is_opted_out_of_nhs_data_share_6,


    [#tmp_0].visit_date_7,
    [#tmp_0].visit_num_7,
    [#tmp_0].last_linkage_dt_7,
    [#tmp_0].is_opted_out_of_nhs_data_share_7,


    [#tmp_0].visit_date_8,
    [#tmp_0].visit_num_8,
    [#tmp_0].last_linkage_dt_8,
    [#tmp_0].is_opted_out_of_nhs_data_share_8,


    [#tmp_0].visit_date_9,
    [#tmp_0].visit_num_9,
    [#tmp_0].last_linkage_dt_9,
    [#tmp_0].is_opted_out_of_nhs_data_share_9,


    [#tmp_0].visit_date_10,
    [#tmp_0].visit_num_10,
    [#tmp_0].last_linkage_dt_10,
    [#tmp_0].is_opted_out_of_nhs_data_share_10,


    [#tmp_0].visit_date_11,
    [#tmp_0].visit_num_11,
    [#tmp_0].last_linkage_dt_11,
    [#tmp_0].is_opted_out_of_nhs_data_share_11,


    [#tmp_0].visit_date_12,
    [#tmp_0].visit_num_12,
    [#tmp_0].last_linkage_dt_12,
    [#tmp_0].is_opted_out_of_nhs_data_share_12,


    [#tmp_0].visit_date_13,
    [#tmp_0].visit_num_13,
    [#tmp_0].last_linkage_dt_13,
    [#tmp_0].is_opted_out_of_nhs_data_share_13,


    [#tmp_0].visit_date_14,
    [#tmp_0].visit_num_14,
    [#tmp_0].last_linkage_dt_14,
    [#tmp_0].is_opted_out_of_nhs_data_share_14,


    [#tmp_0].visit_date_15,
    [#tmp_0].visit_num_15,
    [#tmp_0].last_linkage_dt_15,
    [#tmp_0].is_opted_out_of_nhs_data_share_15,


    [#tmp_0].visit_date_16,
    [#tmp_0].visit_num_16,
    [#tmp_0].last_linkage_dt_16,
    [#tmp_0].is_opted_out_of_nhs_data_share_16,


    [#tmp_0].visit_date_17,
    [#tmp_0].visit_num_17,
    [#tmp_0].last_linkage_dt_17,
    [#tmp_0].is_opted_out_of_nhs_data_share_17,


    [#tmp_0].visit_date_18,
    [#tmp_0].visit_num_18,
    [#tmp_0].last_linkage_dt_18,
    [#tmp_0].is_opted_out_of_nhs_data_share_18,


    [#tmp_0].visit_date_19,
    [#tmp_0].visit_num_19,
    [#tmp_0].last_linkage_dt_19,
    [#tmp_0].is_opted_out_of_nhs_data_share_19,


    [#tmp_0].visit_date_20,
    [#tmp_0].visit_num_20,
    [#tmp_0].last_linkage_dt_20,
    [#tmp_0].is_opted_out_of_nhs_data_share_20,


    [#tmp_0].visit_date_21,
    [#tmp_0].visit_num_21,
    [#tmp_0].last_linkage_dt_21,
    [#tmp_0].is_opted_out_of_nhs_data_share_21,


    [#tmp_0].visit_date_22,
    [#tmp_0].visit_num_22,
    [#tmp_0].last_linkage_dt_22,
    [#tmp_0].is_opted_out_of_nhs_data_share_22,


    [#tmp_0].visit_date_23,
    [#tmp_0].visit_num_23,
    [#tmp_0].last_linkage_dt_23,
    [#tmp_0].is_opted_out_of_nhs_data_share_23,


    [#tmp_0].visit_date_24,
    [#tmp_0].visit_num_24,
    [#tmp_0].last_linkage_dt_24,
    [#tmp_0].is_opted_out_of_nhs_data_share_24,


    [#tmp_0].visit_date_25,
    [#tmp_0].visit_num_25,
    [#tmp_0].last_linkage_dt_25,
    [#tmp_0].is_opted_out_of_nhs_data_share_25


  FROM [#pop]
  LEFT OUTER JOIN [#tmp_0] ON [#tmp_0].patient_id = [#pop].patient_id
  WHERE [#pop].patient_id IS NOT NULL
) t;
