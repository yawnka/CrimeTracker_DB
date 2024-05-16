CREATE TABLE Crimes (Crime_ID INT, Criminal_ID INT REFERENCES Criminal (Criminal_ID), Classification CHAR(1) DEFAULT "U", Date_charged DATE, Status CHAR(2) NOT NULL, Hearing_date DATE CHECK (Hearing_date > Date_charged), Appeal_cut_date DATE, PRIMARY KEY (Crime_ID));

CREATE TABLE Criminals (Criminal_ID INT, Last VARCHAR(15), First VARCHAR(10), Street VARCHAR(30), City VARCHAR(20), State CHAR(2), Zip CHAR(5), Phone CHAR(10), V_status CHAR(1) DEFAULT "N", P_status CHAR(1) DEFAULT "N", PRIMARY KEY (Criminal_ID));

CREATE TABLE Alias (Criminal_ID INT REFERENCES Criminals(Criminal_ID) , Alias_ID INT, Alias VARCHAR(20), PRIMARY KEY (Alias_ID));

CREATE TABLE Sentences (Criminal_ID INT REFERENCES Criminals(Criminal_ID), Sentence_ID INT, Start_date DATE, End_date DATE CHECK (End_date > Start_date), Violations INT NOT NULL, Type CHAR(1), Prob_ID INT REFERENCES Prob_officer(Prob_ID), PRIMARY KEY(Sentence_ID));

CREATE TABLE Prob_officer(Prob_ID INT, Last VARCHAR(15), First VARCHAR(10), Street VARCHAR(30), City VARCHAR(20), State CHAR(2), Zip CHAR(5), Phone CHAR(10), Email VARCHAR(30), Status CHAR(1) NOT NULL, PRIMARY KEY(Prob_ID));

CREATE TABLE Crime_charges(Charge_ID INT, Crime_ID INT REFERENCES Crimes(Crime_ID), Crime_code INT REFERENCES Crime_codes(Crime_code), Charge_status CHAR(2), Fine_amount INT, Court_fee INT, Amount_paid INT CHECK (Amount_Paid <= (Fine_amount + Court_fee)), Pay_due_date DATE, PRIMARY KEY(Charge_ID));

CREATE TABLE Crime_officers(Officer_ID INT REFERENCES Officers(Officer_ID), Crime_ID INT REFERENCES Crimes(Crime_ID), PRIMARY KEY (Officer_ID, Crime_ID));

CREATE TABLE Officers(Officer_ID INT, Last VARCHAR(15), First VARCHAR(10), Precinct CHAR(4) NOT NULL, Badge VARCHAR(14) UNIQUE, Phone CHAR(10), Status CHAR(1) DEFAULT "A", PRIMARY KEY(Officer_ID));

CREATE TABLE Appeals(Appeal_ID INT, Crime_ID INT REFERENCES Crimes(Crime_ID), Filing_date DATE, Hearing_date DATE, Status CHAR(1) DEFAULT "P", PRIMARY KEY(Appeal_ID));

CREATE TABLE Crime_codes(Crime_code INT NOT NULL, Code_description VARCHAR(30) UNIQUE NOT NULL, PRIMARY KEY(Crime_code));

CREATE TABLE OfficerUsers(Username VARCHAR(15) UNIQUE, Password VARCHAR(255), First VARCHAR(10), Last VARCHAR(15), Badge VARCHAR(14) NOT NULL UNIQUE REFERENCES Officers(BADGE), PRIMARY KEY(Username));

CREATE TABLE CommonUsers(Username VARCHAR(15) UNIQUE, Password VARCHAR(255), First VARCHAR(10), Last VARCHAR(15), PRIMARY KEY(Username));
