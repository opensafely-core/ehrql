
SET STATISTICS TIME ON;



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
  WHERE t.row_num <= 52
) AS anon_1;

CREATE CLUSTERED INDEX [ix_#tmp_0_patient_id] ON [#tmp_0] (row_num, patient_id);



SELECT * INTO [#results] FROM (
  SELECT [Patient].Patient_ID AS patient_id,


    anon_0.booked_date AS booked_date_0,
    anon_0.start_date AS start_date_0,
    anon_0.organisation_id AS organisation_id_0,


    anon_1.booked_date AS booked_date_1,
    anon_1.start_date AS start_date_1,
    anon_1.organisation_id AS organisation_id_1,


    anon_2.booked_date AS booked_date_2,
    anon_2.start_date AS start_date_2,
    anon_2.organisation_id AS organisation_id_2,


    anon_3.booked_date AS booked_date_3,
    anon_3.start_date AS start_date_3,
    anon_3.organisation_id AS organisation_id_3,


    anon_4.booked_date AS booked_date_4,
    anon_4.start_date AS start_date_4,
    anon_4.organisation_id AS organisation_id_4,


    anon_5.booked_date AS booked_date_5,
    anon_5.start_date AS start_date_5,
    anon_5.organisation_id AS organisation_id_5,


    anon_6.booked_date AS booked_date_6,
    anon_6.start_date AS start_date_6,
    anon_6.organisation_id AS organisation_id_6,


    anon_7.booked_date AS booked_date_7,
    anon_7.start_date AS start_date_7,
    anon_7.organisation_id AS organisation_id_7,


    anon_8.booked_date AS booked_date_8,
    anon_8.start_date AS start_date_8,
    anon_8.organisation_id AS organisation_id_8,


    anon_9.booked_date AS booked_date_9,
    anon_9.start_date AS start_date_9,
    anon_9.organisation_id AS organisation_id_9,


    anon_10.booked_date AS booked_date_10,
    anon_10.start_date AS start_date_10,
    anon_10.organisation_id AS organisation_id_10,


    anon_11.booked_date AS booked_date_11,
    anon_11.start_date AS start_date_11,
    anon_11.organisation_id AS organisation_id_11,


    anon_12.booked_date AS booked_date_12,
    anon_12.start_date AS start_date_12,
    anon_12.organisation_id AS organisation_id_12,


    anon_13.booked_date AS booked_date_13,
    anon_13.start_date AS start_date_13,
    anon_13.organisation_id AS organisation_id_13,


    anon_14.booked_date AS booked_date_14,
    anon_14.start_date AS start_date_14,
    anon_14.organisation_id AS organisation_id_14,


    anon_15.booked_date AS booked_date_15,
    anon_15.start_date AS start_date_15,
    anon_15.organisation_id AS organisation_id_15,


    anon_16.booked_date AS booked_date_16,
    anon_16.start_date AS start_date_16,
    anon_16.organisation_id AS organisation_id_16,


    anon_17.booked_date AS booked_date_17,
    anon_17.start_date AS start_date_17,
    anon_17.organisation_id AS organisation_id_17,


    anon_18.booked_date AS booked_date_18,
    anon_18.start_date AS start_date_18,
    anon_18.organisation_id AS organisation_id_18,


    anon_19.booked_date AS booked_date_19,
    anon_19.start_date AS start_date_19,
    anon_19.organisation_id AS organisation_id_19,


    anon_20.booked_date AS booked_date_20,
    anon_20.start_date AS start_date_20,
    anon_20.organisation_id AS organisation_id_20,


    anon_21.booked_date AS booked_date_21,
    anon_21.start_date AS start_date_21,
    anon_21.organisation_id AS organisation_id_21,


    anon_22.booked_date AS booked_date_22,
    anon_22.start_date AS start_date_22,
    anon_22.organisation_id AS organisation_id_22,


    anon_23.booked_date AS booked_date_23,
    anon_23.start_date AS start_date_23,
    anon_23.organisation_id AS organisation_id_23,


    anon_24.booked_date AS booked_date_24,
    anon_24.start_date AS start_date_24,
    anon_24.organisation_id AS organisation_id_24,


    anon_25.booked_date AS booked_date_25,
    anon_25.start_date AS start_date_25,
    anon_25.organisation_id AS organisation_id_25,


    anon_26.booked_date AS booked_date_26,
    anon_26.start_date AS start_date_26,
    anon_26.organisation_id AS organisation_id_26,


    anon_27.booked_date AS booked_date_27,
    anon_27.start_date AS start_date_27,
    anon_27.organisation_id AS organisation_id_27,


    anon_28.booked_date AS booked_date_28,
    anon_28.start_date AS start_date_28,
    anon_28.organisation_id AS organisation_id_28,


    anon_29.booked_date AS booked_date_29,
    anon_29.start_date AS start_date_29,
    anon_29.organisation_id AS organisation_id_29,


    anon_30.booked_date AS booked_date_30,
    anon_30.start_date AS start_date_30,
    anon_30.organisation_id AS organisation_id_30,


    anon_31.booked_date AS booked_date_31,
    anon_31.start_date AS start_date_31,
    anon_31.organisation_id AS organisation_id_31,


    anon_32.booked_date AS booked_date_32,
    anon_32.start_date AS start_date_32,
    anon_32.organisation_id AS organisation_id_32,


    anon_33.booked_date AS booked_date_33,
    anon_33.start_date AS start_date_33,
    anon_33.organisation_id AS organisation_id_33,


    anon_34.booked_date AS booked_date_34,
    anon_34.start_date AS start_date_34,
    anon_34.organisation_id AS organisation_id_34,


    anon_35.booked_date AS booked_date_35,
    anon_35.start_date AS start_date_35,
    anon_35.organisation_id AS organisation_id_35,


    anon_36.booked_date AS booked_date_36,
    anon_36.start_date AS start_date_36,
    anon_36.organisation_id AS organisation_id_36,


    anon_37.booked_date AS booked_date_37,
    anon_37.start_date AS start_date_37,
    anon_37.organisation_id AS organisation_id_37,


    anon_38.booked_date AS booked_date_38,
    anon_38.start_date AS start_date_38,
    anon_38.organisation_id AS organisation_id_38,


    anon_39.booked_date AS booked_date_39,
    anon_39.start_date AS start_date_39,
    anon_39.organisation_id AS organisation_id_39,


    anon_40.booked_date AS booked_date_40,
    anon_40.start_date AS start_date_40,
    anon_40.organisation_id AS organisation_id_40,


    anon_41.booked_date AS booked_date_41,
    anon_41.start_date AS start_date_41,
    anon_41.organisation_id AS organisation_id_41,


    anon_42.booked_date AS booked_date_42,
    anon_42.start_date AS start_date_42,
    anon_42.organisation_id AS organisation_id_42,


    anon_43.booked_date AS booked_date_43,
    anon_43.start_date AS start_date_43,
    anon_43.organisation_id AS organisation_id_43,


    anon_44.booked_date AS booked_date_44,
    anon_44.start_date AS start_date_44,
    anon_44.organisation_id AS organisation_id_44,


    anon_45.booked_date AS booked_date_45,
    anon_45.start_date AS start_date_45,
    anon_45.organisation_id AS organisation_id_45,


    anon_46.booked_date AS booked_date_46,
    anon_46.start_date AS start_date_46,
    anon_46.organisation_id AS organisation_id_46,


    anon_47.booked_date AS booked_date_47,
    anon_47.start_date AS start_date_47,
    anon_47.organisation_id AS organisation_id_47,


    anon_48.booked_date AS booked_date_48,
    anon_48.start_date AS start_date_48,
    anon_48.organisation_id AS organisation_id_48,


    anon_49.booked_date AS booked_date_49,
    anon_49.start_date AS start_date_49,
    anon_49.organisation_id AS organisation_id_49,


    anon_50.booked_date AS booked_date_50,
    anon_50.start_date AS start_date_50,
    anon_50.organisation_id AS organisation_id_50,


    anon_51.booked_date AS booked_date_51,
    anon_51.start_date AS start_date_51,
    anon_51.organisation_id AS organisation_id_51


  FROM [Patient]

  LEFT OUTER JOIN [#tmp_0] AS anon_0 ON anon_0.row_num = 1 AND anon_0.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_1 ON anon_1.row_num = 2 AND anon_1.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_2 ON anon_2.row_num = 3 AND anon_2.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_3 ON anon_3.row_num = 4 AND anon_3.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_4 ON anon_4.row_num = 5 AND anon_4.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_5 ON anon_5.row_num = 6 AND anon_5.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_6 ON anon_6.row_num = 7 AND anon_6.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_7 ON anon_7.row_num = 8 AND anon_7.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_8 ON anon_8.row_num = 9 AND anon_8.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_9 ON anon_9.row_num = 10 AND anon_9.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_10 ON anon_10.row_num = 11 AND anon_10.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_11 ON anon_11.row_num = 12 AND anon_11.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_12 ON anon_12.row_num = 13 AND anon_12.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_13 ON anon_13.row_num = 14 AND anon_13.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_14 ON anon_14.row_num = 15 AND anon_14.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_15 ON anon_15.row_num = 16 AND anon_15.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_16 ON anon_16.row_num = 17 AND anon_16.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_17 ON anon_17.row_num = 18 AND anon_17.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_18 ON anon_18.row_num = 19 AND anon_18.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_19 ON anon_19.row_num = 20 AND anon_19.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_20 ON anon_20.row_num = 21 AND anon_20.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_21 ON anon_21.row_num = 22 AND anon_21.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_22 ON anon_22.row_num = 23 AND anon_22.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_23 ON anon_23.row_num = 24 AND anon_23.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_24 ON anon_24.row_num = 25 AND anon_24.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_25 ON anon_25.row_num = 26 AND anon_25.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_26 ON anon_26.row_num = 27 AND anon_26.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_27 ON anon_27.row_num = 28 AND anon_27.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_28 ON anon_28.row_num = 29 AND anon_28.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_29 ON anon_29.row_num = 30 AND anon_29.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_30 ON anon_30.row_num = 31 AND anon_30.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_31 ON anon_31.row_num = 32 AND anon_31.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_32 ON anon_32.row_num = 33 AND anon_32.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_33 ON anon_33.row_num = 34 AND anon_33.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_34 ON anon_34.row_num = 35 AND anon_34.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_35 ON anon_35.row_num = 36 AND anon_35.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_36 ON anon_36.row_num = 37 AND anon_36.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_37 ON anon_37.row_num = 38 AND anon_37.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_38 ON anon_38.row_num = 39 AND anon_38.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_39 ON anon_39.row_num = 40 AND anon_39.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_40 ON anon_40.row_num = 41 AND anon_40.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_41 ON anon_41.row_num = 42 AND anon_41.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_42 ON anon_42.row_num = 43 AND anon_42.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_43 ON anon_43.row_num = 44 AND anon_43.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_44 ON anon_44.row_num = 45 AND anon_44.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_45 ON anon_45.row_num = 46 AND anon_45.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_46 ON anon_46.row_num = 47 AND anon_46.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_47 ON anon_47.row_num = 48 AND anon_47.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_48 ON anon_48.row_num = 49 AND anon_48.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_49 ON anon_49.row_num = 50 AND anon_49.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_50 ON anon_50.row_num = 51 AND anon_50.patient_id = [Patient].Patient_ID
  LEFT OUTER JOIN [#tmp_0] AS anon_51 ON anon_51.row_num = 52 AND anon_51.patient_id = [Patient].Patient_ID

) t;
