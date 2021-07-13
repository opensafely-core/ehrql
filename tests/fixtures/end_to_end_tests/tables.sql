DROP TABLE IF EXISTS CodedEvent, RegistrationHistory;
CREATE TABLE CodedEvent (Patient_ID int, ConsultationDate datetime, CTV3Code varchar(255));
INSERT INTO CodedEvent (Patient_ID, ConsultationDate, CTV3Code) VALUES (1, '2021-01-01', 'xyz');
CREATE TABLE RegistrationHistory (Patient_ID int);
INSERT INTO RegistrationHistory (Patient_ID) VALUES (1);
