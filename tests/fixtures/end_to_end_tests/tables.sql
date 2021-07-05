DROP TABLE IF EXISTS events, practice_registrations;
CREATE TABLE events (PatientId int, Date varchar(255), EventCode varchar(255));
INSERT INTO events (PatientId, Date, EventCode) VALUES (1, '2021-01-01', 'xyz');
CREATE TABLE practice_registrations (PatientId int);
INSERT INTO practice_registrations (PatientId) VALUES (1);
