USE helpdesk_lite_db;

ALTER TABLE users
ADD COLUMN password_hash VARCHAR(255) NOT NULL AFTER email;


