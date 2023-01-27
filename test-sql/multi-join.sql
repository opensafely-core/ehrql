
SET STATISTICS TIME ON;



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
  WHERE t.row_num <= 26
) AS anon_1;

CREATE CLUSTERED INDEX [ix_#tmp_0_patient_id] ON [#tmp_0] (row_num, patient_id);



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


    anon_0.visit_date AS visit_date_0,
    anon_0.visit_num AS visit_num_0,
    anon_0.last_linkage_dt AS last_linkage_dt_0,
    anon_0.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_0,


    anon_1.visit_date AS visit_date_1,
    anon_1.visit_num AS visit_num_1,
    anon_1.last_linkage_dt AS last_linkage_dt_1,
    anon_1.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_1,


    anon_2.visit_date AS visit_date_2,
    anon_2.visit_num AS visit_num_2,
    anon_2.last_linkage_dt AS last_linkage_dt_2,
    anon_2.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_2,


    anon_3.visit_date AS visit_date_3,
    anon_3.visit_num AS visit_num_3,
    anon_3.last_linkage_dt AS last_linkage_dt_3,
    anon_3.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_3,


    anon_4.visit_date AS visit_date_4,
    anon_4.visit_num AS visit_num_4,
    anon_4.last_linkage_dt AS last_linkage_dt_4,
    anon_4.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_4,


    anon_5.visit_date AS visit_date_5,
    anon_5.visit_num AS visit_num_5,
    anon_5.last_linkage_dt AS last_linkage_dt_5,
    anon_5.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_5,


    anon_6.visit_date AS visit_date_6,
    anon_6.visit_num AS visit_num_6,
    anon_6.last_linkage_dt AS last_linkage_dt_6,
    anon_6.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_6,


    anon_7.visit_date AS visit_date_7,
    anon_7.visit_num AS visit_num_7,
    anon_7.last_linkage_dt AS last_linkage_dt_7,
    anon_7.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_7,


    anon_8.visit_date AS visit_date_8,
    anon_8.visit_num AS visit_num_8,
    anon_8.last_linkage_dt AS last_linkage_dt_8,
    anon_8.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_8,


    anon_9.visit_date AS visit_date_9,
    anon_9.visit_num AS visit_num_9,
    anon_9.last_linkage_dt AS last_linkage_dt_9,
    anon_9.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_9,


    anon_10.visit_date AS visit_date_10,
    anon_10.visit_num AS visit_num_10,
    anon_10.last_linkage_dt AS last_linkage_dt_10,
    anon_10.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_10,


    anon_11.visit_date AS visit_date_11,
    anon_11.visit_num AS visit_num_11,
    anon_11.last_linkage_dt AS last_linkage_dt_11,
    anon_11.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_11,


    anon_12.visit_date AS visit_date_12,
    anon_12.visit_num AS visit_num_12,
    anon_12.last_linkage_dt AS last_linkage_dt_12,
    anon_12.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_12,


    anon_13.visit_date AS visit_date_13,
    anon_13.visit_num AS visit_num_13,
    anon_13.last_linkage_dt AS last_linkage_dt_13,
    anon_13.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_13,


    anon_14.visit_date AS visit_date_14,
    anon_14.visit_num AS visit_num_14,
    anon_14.last_linkage_dt AS last_linkage_dt_14,
    anon_14.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_14,


    anon_15.visit_date AS visit_date_15,
    anon_15.visit_num AS visit_num_15,
    anon_15.last_linkage_dt AS last_linkage_dt_15,
    anon_15.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_15,


    anon_16.visit_date AS visit_date_16,
    anon_16.visit_num AS visit_num_16,
    anon_16.last_linkage_dt AS last_linkage_dt_16,
    anon_16.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_16,


    anon_17.visit_date AS visit_date_17,
    anon_17.visit_num AS visit_num_17,
    anon_17.last_linkage_dt AS last_linkage_dt_17,
    anon_17.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_17,


    anon_18.visit_date AS visit_date_18,
    anon_18.visit_num AS visit_num_18,
    anon_18.last_linkage_dt AS last_linkage_dt_18,
    anon_18.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_18,


    anon_19.visit_date AS visit_date_19,
    anon_19.visit_num AS visit_num_19,
    anon_19.last_linkage_dt AS last_linkage_dt_19,
    anon_19.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_19,


    anon_20.visit_date AS visit_date_20,
    anon_20.visit_num AS visit_num_20,
    anon_20.last_linkage_dt AS last_linkage_dt_20,
    anon_20.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_20,


    anon_21.visit_date AS visit_date_21,
    anon_21.visit_num AS visit_num_21,
    anon_21.last_linkage_dt AS last_linkage_dt_21,
    anon_21.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_21,


    anon_22.visit_date AS visit_date_22,
    anon_22.visit_num AS visit_num_22,
    anon_22.last_linkage_dt AS last_linkage_dt_22,
    anon_22.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_22,


    anon_23.visit_date AS visit_date_23,
    anon_23.visit_num AS visit_num_23,
    anon_23.last_linkage_dt AS last_linkage_dt_23,
    anon_23.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_23,


    anon_24.visit_date AS visit_date_24,
    anon_24.visit_num AS visit_num_24,
    anon_24.last_linkage_dt AS last_linkage_dt_24,
    anon_24.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_24,


    anon_25.visit_date AS visit_date_25,
    anon_25.visit_num AS visit_num_25,
    anon_25.last_linkage_dt AS last_linkage_dt_25,
    anon_25.is_opted_out_of_nhs_data_share AS is_opted_out_of_nhs_data_share_25


  FROM [#pop]

  LEFT OUTER JOIN [#tmp_0] AS anon_0 ON anon_0.row_num = 1 AND anon_0.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_1 ON anon_1.row_num = 2 AND anon_1.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_2 ON anon_2.row_num = 3 AND anon_2.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_3 ON anon_3.row_num = 4 AND anon_3.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_4 ON anon_4.row_num = 5 AND anon_4.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_5 ON anon_5.row_num = 6 AND anon_5.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_6 ON anon_6.row_num = 7 AND anon_6.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_7 ON anon_7.row_num = 8 AND anon_7.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_8 ON anon_8.row_num = 9 AND anon_8.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_9 ON anon_9.row_num = 10 AND anon_9.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_10 ON anon_10.row_num = 11 AND anon_10.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_11 ON anon_11.row_num = 12 AND anon_11.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_12 ON anon_12.row_num = 13 AND anon_12.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_13 ON anon_13.row_num = 14 AND anon_13.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_14 ON anon_14.row_num = 15 AND anon_14.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_15 ON anon_15.row_num = 16 AND anon_15.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_16 ON anon_16.row_num = 17 AND anon_16.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_17 ON anon_17.row_num = 18 AND anon_17.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_18 ON anon_18.row_num = 19 AND anon_18.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_19 ON anon_19.row_num = 20 AND anon_19.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_20 ON anon_20.row_num = 21 AND anon_20.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_21 ON anon_21.row_num = 22 AND anon_21.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_22 ON anon_22.row_num = 23 AND anon_22.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_23 ON anon_23.row_num = 24 AND anon_23.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_24 ON anon_24.row_num = 25 AND anon_24.patient_id = [#pop].patient_id
  LEFT OUTER JOIN [#tmp_0] AS anon_25 ON anon_25.row_num = 26 AND anon_25.patient_id = [#pop].patient_id

  WHERE [#pop].patient_id IS NOT NULL
) t;
