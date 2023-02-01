
SET STATISTICS TIME ON;



SELECT *
INTO [#tmp_0]
FROM (
  SELECT
    anon_2.patient_id AS patient_id,


    MAX(CASE WHEN anon_2.row_num = 1 THEN anon_2.booked_date END) AS booked_date_0,
    MAX(CASE WHEN anon_2.row_num = 1 THEN anon_2.start_date END) AS start_date_0,
    MAX(CASE WHEN anon_2.row_num = 1 THEN anon_2.organisation_id END) AS organisation_id_0,
    

    MAX(CASE WHEN anon_2.row_num = 2 THEN anon_2.booked_date END) AS booked_date_1,
    MAX(CASE WHEN anon_2.row_num = 2 THEN anon_2.start_date END) AS start_date_1,
    MAX(CASE WHEN anon_2.row_num = 2 THEN anon_2.organisation_id END) AS organisation_id_1,
    

    MAX(CASE WHEN anon_2.row_num = 3 THEN anon_2.booked_date END) AS booked_date_2,
    MAX(CASE WHEN anon_2.row_num = 3 THEN anon_2.start_date END) AS start_date_2,
    MAX(CASE WHEN anon_2.row_num = 3 THEN anon_2.organisation_id END) AS organisation_id_2,
    

    MAX(CASE WHEN anon_2.row_num = 4 THEN anon_2.booked_date END) AS booked_date_3,
    MAX(CASE WHEN anon_2.row_num = 4 THEN anon_2.start_date END) AS start_date_3,
    MAX(CASE WHEN anon_2.row_num = 4 THEN anon_2.organisation_id END) AS organisation_id_3,
    

    MAX(CASE WHEN anon_2.row_num = 5 THEN anon_2.booked_date END) AS booked_date_4,
    MAX(CASE WHEN anon_2.row_num = 5 THEN anon_2.start_date END) AS start_date_4,
    MAX(CASE WHEN anon_2.row_num = 5 THEN anon_2.organisation_id END) AS organisation_id_4,
    

    MAX(CASE WHEN anon_2.row_num = 6 THEN anon_2.booked_date END) AS booked_date_5,
    MAX(CASE WHEN anon_2.row_num = 6 THEN anon_2.start_date END) AS start_date_5,
    MAX(CASE WHEN anon_2.row_num = 6 THEN anon_2.organisation_id END) AS organisation_id_5,
    

    MAX(CASE WHEN anon_2.row_num = 7 THEN anon_2.booked_date END) AS booked_date_6,
    MAX(CASE WHEN anon_2.row_num = 7 THEN anon_2.start_date END) AS start_date_6,
    MAX(CASE WHEN anon_2.row_num = 7 THEN anon_2.organisation_id END) AS organisation_id_6,
    

    MAX(CASE WHEN anon_2.row_num = 8 THEN anon_2.booked_date END) AS booked_date_7,
    MAX(CASE WHEN anon_2.row_num = 8 THEN anon_2.start_date END) AS start_date_7,
    MAX(CASE WHEN anon_2.row_num = 8 THEN anon_2.organisation_id END) AS organisation_id_7,
    

    MAX(CASE WHEN anon_2.row_num = 9 THEN anon_2.booked_date END) AS booked_date_8,
    MAX(CASE WHEN anon_2.row_num = 9 THEN anon_2.start_date END) AS start_date_8,
    MAX(CASE WHEN anon_2.row_num = 9 THEN anon_2.organisation_id END) AS organisation_id_8,
    

    MAX(CASE WHEN anon_2.row_num = 10 THEN anon_2.booked_date END) AS booked_date_9,
    MAX(CASE WHEN anon_2.row_num = 10 THEN anon_2.start_date END) AS start_date_9,
    MAX(CASE WHEN anon_2.row_num = 10 THEN anon_2.organisation_id END) AS organisation_id_9,
    

    MAX(CASE WHEN anon_2.row_num = 11 THEN anon_2.booked_date END) AS booked_date_10,
    MAX(CASE WHEN anon_2.row_num = 11 THEN anon_2.start_date END) AS start_date_10,
    MAX(CASE WHEN anon_2.row_num = 11 THEN anon_2.organisation_id END) AS organisation_id_10,
    

    MAX(CASE WHEN anon_2.row_num = 12 THEN anon_2.booked_date END) AS booked_date_11,
    MAX(CASE WHEN anon_2.row_num = 12 THEN anon_2.start_date END) AS start_date_11,
    MAX(CASE WHEN anon_2.row_num = 12 THEN anon_2.organisation_id END) AS organisation_id_11,
    

    MAX(CASE WHEN anon_2.row_num = 13 THEN anon_2.booked_date END) AS booked_date_12,
    MAX(CASE WHEN anon_2.row_num = 13 THEN anon_2.start_date END) AS start_date_12,
    MAX(CASE WHEN anon_2.row_num = 13 THEN anon_2.organisation_id END) AS organisation_id_12,
    

    MAX(CASE WHEN anon_2.row_num = 14 THEN anon_2.booked_date END) AS booked_date_13,
    MAX(CASE WHEN anon_2.row_num = 14 THEN anon_2.start_date END) AS start_date_13,
    MAX(CASE WHEN anon_2.row_num = 14 THEN anon_2.organisation_id END) AS organisation_id_13,
    

    MAX(CASE WHEN anon_2.row_num = 15 THEN anon_2.booked_date END) AS booked_date_14,
    MAX(CASE WHEN anon_2.row_num = 15 THEN anon_2.start_date END) AS start_date_14,
    MAX(CASE WHEN anon_2.row_num = 15 THEN anon_2.organisation_id END) AS organisation_id_14,
    

    MAX(CASE WHEN anon_2.row_num = 16 THEN anon_2.booked_date END) AS booked_date_15,
    MAX(CASE WHEN anon_2.row_num = 16 THEN anon_2.start_date END) AS start_date_15,
    MAX(CASE WHEN anon_2.row_num = 16 THEN anon_2.organisation_id END) AS organisation_id_15,
    

    MAX(CASE WHEN anon_2.row_num = 17 THEN anon_2.booked_date END) AS booked_date_16,
    MAX(CASE WHEN anon_2.row_num = 17 THEN anon_2.start_date END) AS start_date_16,
    MAX(CASE WHEN anon_2.row_num = 17 THEN anon_2.organisation_id END) AS organisation_id_16,
    

    MAX(CASE WHEN anon_2.row_num = 18 THEN anon_2.booked_date END) AS booked_date_17,
    MAX(CASE WHEN anon_2.row_num = 18 THEN anon_2.start_date END) AS start_date_17,
    MAX(CASE WHEN anon_2.row_num = 18 THEN anon_2.organisation_id END) AS organisation_id_17,
    

    MAX(CASE WHEN anon_2.row_num = 19 THEN anon_2.booked_date END) AS booked_date_18,
    MAX(CASE WHEN anon_2.row_num = 19 THEN anon_2.start_date END) AS start_date_18,
    MAX(CASE WHEN anon_2.row_num = 19 THEN anon_2.organisation_id END) AS organisation_id_18,
    

    MAX(CASE WHEN anon_2.row_num = 20 THEN anon_2.booked_date END) AS booked_date_19,
    MAX(CASE WHEN anon_2.row_num = 20 THEN anon_2.start_date END) AS start_date_19,
    MAX(CASE WHEN anon_2.row_num = 20 THEN anon_2.organisation_id END) AS organisation_id_19,
    

    MAX(CASE WHEN anon_2.row_num = 21 THEN anon_2.booked_date END) AS booked_date_20,
    MAX(CASE WHEN anon_2.row_num = 21 THEN anon_2.start_date END) AS start_date_20,
    MAX(CASE WHEN anon_2.row_num = 21 THEN anon_2.organisation_id END) AS organisation_id_20,
    

    MAX(CASE WHEN anon_2.row_num = 22 THEN anon_2.booked_date END) AS booked_date_21,
    MAX(CASE WHEN anon_2.row_num = 22 THEN anon_2.start_date END) AS start_date_21,
    MAX(CASE WHEN anon_2.row_num = 22 THEN anon_2.organisation_id END) AS organisation_id_21,
    

    MAX(CASE WHEN anon_2.row_num = 23 THEN anon_2.booked_date END) AS booked_date_22,
    MAX(CASE WHEN anon_2.row_num = 23 THEN anon_2.start_date END) AS start_date_22,
    MAX(CASE WHEN anon_2.row_num = 23 THEN anon_2.organisation_id END) AS organisation_id_22,
    

    MAX(CASE WHEN anon_2.row_num = 24 THEN anon_2.booked_date END) AS booked_date_23,
    MAX(CASE WHEN anon_2.row_num = 24 THEN anon_2.start_date END) AS start_date_23,
    MAX(CASE WHEN anon_2.row_num = 24 THEN anon_2.organisation_id END) AS organisation_id_23,
    

    MAX(CASE WHEN anon_2.row_num = 25 THEN anon_2.booked_date END) AS booked_date_24,
    MAX(CASE WHEN anon_2.row_num = 25 THEN anon_2.start_date END) AS start_date_24,
    MAX(CASE WHEN anon_2.row_num = 25 THEN anon_2.organisation_id END) AS organisation_id_24,
    

    MAX(CASE WHEN anon_2.row_num = 26 THEN anon_2.booked_date END) AS booked_date_25,
    MAX(CASE WHEN anon_2.row_num = 26 THEN anon_2.start_date END) AS start_date_25,
    MAX(CASE WHEN anon_2.row_num = 26 THEN anon_2.organisation_id END) AS organisation_id_25,
    

    MAX(CASE WHEN anon_2.row_num = 27 THEN anon_2.booked_date END) AS booked_date_26,
    MAX(CASE WHEN anon_2.row_num = 27 THEN anon_2.start_date END) AS start_date_26,
    MAX(CASE WHEN anon_2.row_num = 27 THEN anon_2.organisation_id END) AS organisation_id_26,
    

    MAX(CASE WHEN anon_2.row_num = 28 THEN anon_2.booked_date END) AS booked_date_27,
    MAX(CASE WHEN anon_2.row_num = 28 THEN anon_2.start_date END) AS start_date_27,
    MAX(CASE WHEN anon_2.row_num = 28 THEN anon_2.organisation_id END) AS organisation_id_27,
    

    MAX(CASE WHEN anon_2.row_num = 29 THEN anon_2.booked_date END) AS booked_date_28,
    MAX(CASE WHEN anon_2.row_num = 29 THEN anon_2.start_date END) AS start_date_28,
    MAX(CASE WHEN anon_2.row_num = 29 THEN anon_2.organisation_id END) AS organisation_id_28,
    

    MAX(CASE WHEN anon_2.row_num = 30 THEN anon_2.booked_date END) AS booked_date_29,
    MAX(CASE WHEN anon_2.row_num = 30 THEN anon_2.start_date END) AS start_date_29,
    MAX(CASE WHEN anon_2.row_num = 30 THEN anon_2.organisation_id END) AS organisation_id_29,
    

    MAX(CASE WHEN anon_2.row_num = 31 THEN anon_2.booked_date END) AS booked_date_30,
    MAX(CASE WHEN anon_2.row_num = 31 THEN anon_2.start_date END) AS start_date_30,
    MAX(CASE WHEN anon_2.row_num = 31 THEN anon_2.organisation_id END) AS organisation_id_30,
    

    MAX(CASE WHEN anon_2.row_num = 32 THEN anon_2.booked_date END) AS booked_date_31,
    MAX(CASE WHEN anon_2.row_num = 32 THEN anon_2.start_date END) AS start_date_31,
    MAX(CASE WHEN anon_2.row_num = 32 THEN anon_2.organisation_id END) AS organisation_id_31,
    

    MAX(CASE WHEN anon_2.row_num = 33 THEN anon_2.booked_date END) AS booked_date_32,
    MAX(CASE WHEN anon_2.row_num = 33 THEN anon_2.start_date END) AS start_date_32,
    MAX(CASE WHEN anon_2.row_num = 33 THEN anon_2.organisation_id END) AS organisation_id_32,
    

    MAX(CASE WHEN anon_2.row_num = 34 THEN anon_2.booked_date END) AS booked_date_33,
    MAX(CASE WHEN anon_2.row_num = 34 THEN anon_2.start_date END) AS start_date_33,
    MAX(CASE WHEN anon_2.row_num = 34 THEN anon_2.organisation_id END) AS organisation_id_33,
    

    MAX(CASE WHEN anon_2.row_num = 35 THEN anon_2.booked_date END) AS booked_date_34,
    MAX(CASE WHEN anon_2.row_num = 35 THEN anon_2.start_date END) AS start_date_34,
    MAX(CASE WHEN anon_2.row_num = 35 THEN anon_2.organisation_id END) AS organisation_id_34,
    

    MAX(CASE WHEN anon_2.row_num = 36 THEN anon_2.booked_date END) AS booked_date_35,
    MAX(CASE WHEN anon_2.row_num = 36 THEN anon_2.start_date END) AS start_date_35,
    MAX(CASE WHEN anon_2.row_num = 36 THEN anon_2.organisation_id END) AS organisation_id_35,
    

    MAX(CASE WHEN anon_2.row_num = 37 THEN anon_2.booked_date END) AS booked_date_36,
    MAX(CASE WHEN anon_2.row_num = 37 THEN anon_2.start_date END) AS start_date_36,
    MAX(CASE WHEN anon_2.row_num = 37 THEN anon_2.organisation_id END) AS organisation_id_36,
    

    MAX(CASE WHEN anon_2.row_num = 38 THEN anon_2.booked_date END) AS booked_date_37,
    MAX(CASE WHEN anon_2.row_num = 38 THEN anon_2.start_date END) AS start_date_37,
    MAX(CASE WHEN anon_2.row_num = 38 THEN anon_2.organisation_id END) AS organisation_id_37,
    

    MAX(CASE WHEN anon_2.row_num = 39 THEN anon_2.booked_date END) AS booked_date_38,
    MAX(CASE WHEN anon_2.row_num = 39 THEN anon_2.start_date END) AS start_date_38,
    MAX(CASE WHEN anon_2.row_num = 39 THEN anon_2.organisation_id END) AS organisation_id_38,
    

    MAX(CASE WHEN anon_2.row_num = 40 THEN anon_2.booked_date END) AS booked_date_39,
    MAX(CASE WHEN anon_2.row_num = 40 THEN anon_2.start_date END) AS start_date_39,
    MAX(CASE WHEN anon_2.row_num = 40 THEN anon_2.organisation_id END) AS organisation_id_39,
    

    MAX(CASE WHEN anon_2.row_num = 41 THEN anon_2.booked_date END) AS booked_date_40,
    MAX(CASE WHEN anon_2.row_num = 41 THEN anon_2.start_date END) AS start_date_40,
    MAX(CASE WHEN anon_2.row_num = 41 THEN anon_2.organisation_id END) AS organisation_id_40,
    

    MAX(CASE WHEN anon_2.row_num = 42 THEN anon_2.booked_date END) AS booked_date_41,
    MAX(CASE WHEN anon_2.row_num = 42 THEN anon_2.start_date END) AS start_date_41,
    MAX(CASE WHEN anon_2.row_num = 42 THEN anon_2.organisation_id END) AS organisation_id_41,
    

    MAX(CASE WHEN anon_2.row_num = 43 THEN anon_2.booked_date END) AS booked_date_42,
    MAX(CASE WHEN anon_2.row_num = 43 THEN anon_2.start_date END) AS start_date_42,
    MAX(CASE WHEN anon_2.row_num = 43 THEN anon_2.organisation_id END) AS organisation_id_42,
    

    MAX(CASE WHEN anon_2.row_num = 44 THEN anon_2.booked_date END) AS booked_date_43,
    MAX(CASE WHEN anon_2.row_num = 44 THEN anon_2.start_date END) AS start_date_43,
    MAX(CASE WHEN anon_2.row_num = 44 THEN anon_2.organisation_id END) AS organisation_id_43,
    

    MAX(CASE WHEN anon_2.row_num = 45 THEN anon_2.booked_date END) AS booked_date_44,
    MAX(CASE WHEN anon_2.row_num = 45 THEN anon_2.start_date END) AS start_date_44,
    MAX(CASE WHEN anon_2.row_num = 45 THEN anon_2.organisation_id END) AS organisation_id_44,
    

    MAX(CASE WHEN anon_2.row_num = 46 THEN anon_2.booked_date END) AS booked_date_45,
    MAX(CASE WHEN anon_2.row_num = 46 THEN anon_2.start_date END) AS start_date_45,
    MAX(CASE WHEN anon_2.row_num = 46 THEN anon_2.organisation_id END) AS organisation_id_45,
    

    MAX(CASE WHEN anon_2.row_num = 47 THEN anon_2.booked_date END) AS booked_date_46,
    MAX(CASE WHEN anon_2.row_num = 47 THEN anon_2.start_date END) AS start_date_46,
    MAX(CASE WHEN anon_2.row_num = 47 THEN anon_2.organisation_id END) AS organisation_id_46,
    

    MAX(CASE WHEN anon_2.row_num = 48 THEN anon_2.booked_date END) AS booked_date_47,
    MAX(CASE WHEN anon_2.row_num = 48 THEN anon_2.start_date END) AS start_date_47,
    MAX(CASE WHEN anon_2.row_num = 48 THEN anon_2.organisation_id END) AS organisation_id_47,
    

    MAX(CASE WHEN anon_2.row_num = 49 THEN anon_2.booked_date END) AS booked_date_48,
    MAX(CASE WHEN anon_2.row_num = 49 THEN anon_2.start_date END) AS start_date_48,
    MAX(CASE WHEN anon_2.row_num = 49 THEN anon_2.organisation_id END) AS organisation_id_48,
    

    MAX(CASE WHEN anon_2.row_num = 50 THEN anon_2.booked_date END) AS booked_date_49,
    MAX(CASE WHEN anon_2.row_num = 50 THEN anon_2.start_date END) AS start_date_49,
    MAX(CASE WHEN anon_2.row_num = 50 THEN anon_2.organisation_id END) AS organisation_id_49,
    

    MAX(CASE WHEN anon_2.row_num = 51 THEN anon_2.booked_date END) AS booked_date_50,
    MAX(CASE WHEN anon_2.row_num = 51 THEN anon_2.start_date END) AS start_date_50,
    MAX(CASE WHEN anon_2.row_num = 51 THEN anon_2.organisation_id END) AS organisation_id_50,
    

    MAX(CASE WHEN anon_2.row_num = 52 THEN anon_2.booked_date END) AS booked_date_51,
    MAX(CASE WHEN anon_2.row_num = 52 THEN anon_2.start_date END) AS start_date_51,
    MAX(CASE WHEN anon_2.row_num = 52 THEN anon_2.organisation_id END) AS organisation_id_51
    

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
  WHERE anon_2.row_num <= 52
  GROUP BY anon_2.patient_id
  ) AS anon_1;

CREATE CLUSTERED INDEX [ix_#tmp_0_patient_id] ON [#tmp_0] (patient_id);



SELECT * INTO [#results] FROM (
  SELECT [Patient].Patient_ID AS patient_id,


    [#tmp_0].booked_date_0,
    [#tmp_0].start_date_0,
    [#tmp_0].organisation_id_0,
    

    [#tmp_0].booked_date_1,
    [#tmp_0].start_date_1,
    [#tmp_0].organisation_id_1,
    

    [#tmp_0].booked_date_2,
    [#tmp_0].start_date_2,
    [#tmp_0].organisation_id_2,
    

    [#tmp_0].booked_date_3,
    [#tmp_0].start_date_3,
    [#tmp_0].organisation_id_3,
    

    [#tmp_0].booked_date_4,
    [#tmp_0].start_date_4,
    [#tmp_0].organisation_id_4,
    

    [#tmp_0].booked_date_5,
    [#tmp_0].start_date_5,
    [#tmp_0].organisation_id_5,
    

    [#tmp_0].booked_date_6,
    [#tmp_0].start_date_6,
    [#tmp_0].organisation_id_6,
    

    [#tmp_0].booked_date_7,
    [#tmp_0].start_date_7,
    [#tmp_0].organisation_id_7,
    

    [#tmp_0].booked_date_8,
    [#tmp_0].start_date_8,
    [#tmp_0].organisation_id_8,
    

    [#tmp_0].booked_date_9,
    [#tmp_0].start_date_9,
    [#tmp_0].organisation_id_9,
    

    [#tmp_0].booked_date_10,
    [#tmp_0].start_date_10,
    [#tmp_0].organisation_id_10,
    

    [#tmp_0].booked_date_11,
    [#tmp_0].start_date_11,
    [#tmp_0].organisation_id_11,
    

    [#tmp_0].booked_date_12,
    [#tmp_0].start_date_12,
    [#tmp_0].organisation_id_12,
    

    [#tmp_0].booked_date_13,
    [#tmp_0].start_date_13,
    [#tmp_0].organisation_id_13,
    

    [#tmp_0].booked_date_14,
    [#tmp_0].start_date_14,
    [#tmp_0].organisation_id_14,
    

    [#tmp_0].booked_date_15,
    [#tmp_0].start_date_15,
    [#tmp_0].organisation_id_15,
    

    [#tmp_0].booked_date_16,
    [#tmp_0].start_date_16,
    [#tmp_0].organisation_id_16,
    

    [#tmp_0].booked_date_17,
    [#tmp_0].start_date_17,
    [#tmp_0].organisation_id_17,
    

    [#tmp_0].booked_date_18,
    [#tmp_0].start_date_18,
    [#tmp_0].organisation_id_18,
    

    [#tmp_0].booked_date_19,
    [#tmp_0].start_date_19,
    [#tmp_0].organisation_id_19,
    

    [#tmp_0].booked_date_20,
    [#tmp_0].start_date_20,
    [#tmp_0].organisation_id_20,
    

    [#tmp_0].booked_date_21,
    [#tmp_0].start_date_21,
    [#tmp_0].organisation_id_21,
    

    [#tmp_0].booked_date_22,
    [#tmp_0].start_date_22,
    [#tmp_0].organisation_id_22,
    

    [#tmp_0].booked_date_23,
    [#tmp_0].start_date_23,
    [#tmp_0].organisation_id_23,
    

    [#tmp_0].booked_date_24,
    [#tmp_0].start_date_24,
    [#tmp_0].organisation_id_24,
    

    [#tmp_0].booked_date_25,
    [#tmp_0].start_date_25,
    [#tmp_0].organisation_id_25,
    

    [#tmp_0].booked_date_26,
    [#tmp_0].start_date_26,
    [#tmp_0].organisation_id_26,
    

    [#tmp_0].booked_date_27,
    [#tmp_0].start_date_27,
    [#tmp_0].organisation_id_27,
    

    [#tmp_0].booked_date_28,
    [#tmp_0].start_date_28,
    [#tmp_0].organisation_id_28,
    

    [#tmp_0].booked_date_29,
    [#tmp_0].start_date_29,
    [#tmp_0].organisation_id_29,
    

    [#tmp_0].booked_date_30,
    [#tmp_0].start_date_30,
    [#tmp_0].organisation_id_30,
    

    [#tmp_0].booked_date_31,
    [#tmp_0].start_date_31,
    [#tmp_0].organisation_id_31,
    

    [#tmp_0].booked_date_32,
    [#tmp_0].start_date_32,
    [#tmp_0].organisation_id_32,
    

    [#tmp_0].booked_date_33,
    [#tmp_0].start_date_33,
    [#tmp_0].organisation_id_33,
    

    [#tmp_0].booked_date_34,
    [#tmp_0].start_date_34,
    [#tmp_0].organisation_id_34,
    

    [#tmp_0].booked_date_35,
    [#tmp_0].start_date_35,
    [#tmp_0].organisation_id_35,
    

    [#tmp_0].booked_date_36,
    [#tmp_0].start_date_36,
    [#tmp_0].organisation_id_36,
    

    [#tmp_0].booked_date_37,
    [#tmp_0].start_date_37,
    [#tmp_0].organisation_id_37,
    

    [#tmp_0].booked_date_38,
    [#tmp_0].start_date_38,
    [#tmp_0].organisation_id_38,
    

    [#tmp_0].booked_date_39,
    [#tmp_0].start_date_39,
    [#tmp_0].organisation_id_39,
    

    [#tmp_0].booked_date_40,
    [#tmp_0].start_date_40,
    [#tmp_0].organisation_id_40,
    

    [#tmp_0].booked_date_41,
    [#tmp_0].start_date_41,
    [#tmp_0].organisation_id_41,
    

    [#tmp_0].booked_date_42,
    [#tmp_0].start_date_42,
    [#tmp_0].organisation_id_42,
    

    [#tmp_0].booked_date_43,
    [#tmp_0].start_date_43,
    [#tmp_0].organisation_id_43,
    

    [#tmp_0].booked_date_44,
    [#tmp_0].start_date_44,
    [#tmp_0].organisation_id_44,
    

    [#tmp_0].booked_date_45,
    [#tmp_0].start_date_45,
    [#tmp_0].organisation_id_45,
    

    [#tmp_0].booked_date_46,
    [#tmp_0].start_date_46,
    [#tmp_0].organisation_id_46,
    

    [#tmp_0].booked_date_47,
    [#tmp_0].start_date_47,
    [#tmp_0].organisation_id_47,
    

    [#tmp_0].booked_date_48,
    [#tmp_0].start_date_48,
    [#tmp_0].organisation_id_48,
    

    [#tmp_0].booked_date_49,
    [#tmp_0].start_date_49,
    [#tmp_0].organisation_id_49,
    

    [#tmp_0].booked_date_50,
    [#tmp_0].start_date_50,
    [#tmp_0].organisation_id_50,
    

    [#tmp_0].booked_date_51,
    [#tmp_0].start_date_51,
    [#tmp_0].organisation_id_51
    

  FROM [Patient]
  LEFT OUTER JOIN [#tmp_0] ON [#tmp_0].patient_id = [Patient].Patient_ID
) t;

