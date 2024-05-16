CREATE ROLE Common_user;
CREATE ROLE Officer_user;
GRANT SELECT ON crime_tracker.* TO Common_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON crime_tracker.* TO Officer_user;
CREATE ROLE developer;
GRANT ALL PRIVILEGES ON crime_tracker.* TO developer;
