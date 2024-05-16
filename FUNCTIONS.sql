--update classfication
DELIMITER $$
DROP PROCEDURE IF EXISTS updateClassfication$$
CREATE PROCEDURE updateClassfication (newClassification CHAR(1), cl_ID INT)
BEGIN
	UPDATE Crimes
SET Classification =  newClassification
WHERE Criminal_ID = cl_ID;
END$$
DELIMITER ;

--update date charged and hearing date
DELIMITER $$
DROP PROCEDURE IF EXISTS updateDateCH$$
CREATE PROCEDURE updateDateCH (new_date_charged DATE, new_hearing_date DATE, cl_ID INT)
BEGIN
	UPDATE Crimes
	SET Date_charged =  new_date_charged, Hearing_date = new_hearing_date
	WHERE Criminal_ID = cl_ID;
END$$
DELIMITER ;

--update status
DELIMITER $$
DROP PROCEDURE IF EXISTS updateStatus$$
CREATE PROCEDURE updateStatus (new_status CHAR(2), cl_ID INT)
BEGIN
	UPDATE Crimes
SET status =  new_status
WHERE Criminal_ID = cl_ID;
END$$
DELIMITER ;

--update appeal cut date
DELIMITER $$
DROP PROCEDURE IF EXISTS updateAppealCutDate$$
CREATE PROCEDURE updateAppealCutDate(new_appeal_cut_date DATE, cl_ID INT)
BEGIN
	UPDATE Crimes
SET Appeal_cut_date=  new_appeal_cut_date
WHERE Criminal_ID = cl_ID;
END$$
DELIMITER ;

-- delete crime
DELIMITER $$
DROP PROCEDURE IF EXISTS deleteCrime$$
CREATE PROCEDURE deleteCrime(cr_ID INT)
BEGIN
	DELETE FROM Crimes WHERE Crime_ID = cr_ID;
END$$
DELIMITER ;

-- add crime
DELIMITER $$
DROP PROCEDURE IF EXISTS addCrime$$
CREATE PROCEDURE addCrime(cr_ID INT, cl_ID INT, newClassification CHAR(1), newDateCharged DATE, newStatus CHAR(2), newHearingDate DATE, newAppealCut DATE)
BEGIN
INSERT INTO Crimes VALUES(cr_ID, cl_ID, newClassification,  newDateCharged, newStatus, newHearingDate, newAppealCut);
END$$
DELIMITER ;

-- add criminal
DELIMITER $$
DROP PROCEDURE IF EXISTS addCriminal$$
CREATE PROCEDURE addCriminal(cr_ID INT, new_Last VARCHAR(15), new_First VARCHAR(10), new_Street VARCHAR(30), new_City VARCHAR(20), new_State CHAR(2), new_Zip CHAR(5), new_Phone CHAR(10), new_V_status CHAR(1), new_P_status CHAR(1))
BEGIN
INSERT INTO Criminals VALUES(cr_ID, new_Last, new_First, new_Street, new_City, new_State, new_Zip, new_Phone, new_V_status, new_P_status);
END$$
DELIMITER ;

--Search by criminal name (Procedure)
DELIMITER $$
DROP PROCEDURE IF EXISTS searchCriminal$$
CREATE PROCEDURE searchCriminal(key_word VARCHAR(15))
BEGIN
    DECLARE searchFor VARCHAR(30);
    SET searchFor =  CONCAT("%" , key_word , "%");
    SELECT *
    FROM Alias a, Criminals cl, Crimes cr, Sentences s, Crime_charges ch, Crime_codes cc
    WHERE a.Criminal_ID = cl.criminal_ID
    AND  cr.Criminal_ID = cl.Criminal_ID
    AND s.Criminal_ID = cl.Criminal_ID
    AND ch.Crime_ID = cr.Crime_ID
    AND ch.Crime_code = cc.Crime_code
    AND (cl.last LIKE searchFor OR cl.first LIKE searchFor OR a.Alias LIKE searchFor);
END$$
DELIMITER ;

--Search For Probation Officer name (Procedure)
DELIMITER $$
DROP PROCEDURE IF EXISTS searchProbationOfficer$$
CREATE PROCEDURE searchProbationOfficer(key_word VARCHAR(15))
BEGIN
    DECLARE searchFor VARCHAR(30);
    SET searchFor =  CONCAT("%" , key_word , "%");
        SELECT *
    FROM Sentences s, Prob_officer pbo
    WHERE (s.Prob_ID = pbo.Prob_ID
    AND (pbo.Last LIKE searchFor OR pbo.First LIKE searchFor));
END$$
DELIMITER ;


--Search For a Crime Officer’s Badge Number by their Name (Function)
DELIMITER $$
CREATE OR REPLACE FUNCTION searchCrimeOfficer(key_word VARCHAR(14)) RETURNS VARCHAR(14)
BEGIN
    DECLARE searchFor VARCHAR(14);
    DECLARE badge_Num VARCHAR(14);
    SET searchFor =  CONCAT("%" , key_word , "%");
    SELECT o.Badge INTO badge_Num
    FROM Crime_officers co, Officers o
    WHERE (co.Officer_ID = o.Officer_ID
    AND (o.Last LIKE searchFor OR o.First LIKE searchFor));
    RETURN badge_Num;
END$$
DELIMITER ;

-- Triggers
DELIMITER @@
CREATE OR REPLACE TRIGGER postDeleteCrime
AFTER DELETE ON Crimes
FOR EACH ROW
BEGIN
IF (SELECT COUNT(*) FROM Crimes WHERE OLD.Criminal_ID = Criminal_ID) = 0 THEN
DELETE FROM Criminals WHERE Criminal_ID = OLD.Criminal_ID;
END IF;
DELETE FROM Appeals WHERE Crime_ID = OLD.Crime_ID;
DELETE FROM Crime_officers WHERE Crime_ID = OLD.Crime_ID;
DELETE FROM Crime_charges WHERE Crime_ID = OLD.Crime_ID;
END @@
DELIMITER ;

DELIMITER @@
CREATE OR REPLACE TRIGGER postDeleteCriminal
AFTER DELETE ON Criminals
FOR EACH ROW
BEGIN
	DELETE FROM Alias WHERE Criminal_ID = OLD.Criminal_ID;
	DELETE FROM Sentences WHERE Criminal_ID = OLD.Criminal_ID;
END @@
DELIMITER ;
