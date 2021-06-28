CREATE TABLE clinical_events (patient_id int, date varchar(255), code varchar(255), test_value int);
INSERT INTO clinical_events (patient_id, date, code, test_value) VALUES (1, '2021-01-01', 'xyz', 1);
INSERT INTO clinical_events (patient_id, date, code, test_value) VALUES (1, '2021-01-02', 'xyz', 2);
INSERT INTO clinical_events (patient_id, date, code, test_value) VALUES (1, '2021-01-03', 'abc', 3);
INSERT INTO clinical_events (patient_id, date, code, test_value) VALUES (1, '2021-01-04', 'abc', 4);
GO
