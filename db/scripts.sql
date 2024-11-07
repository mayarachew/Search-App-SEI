CREATE DATABASE sei;

USE sei;

CREATE TABLE acts (
    document_id INT NOT NULL,
    person_signing VARCHAR(255),
    person_name VARCHAR(255),
    person_id VARCHAR(255),
    contract_id VARCHAR(255),
    organization VARCHAR(255),
    raw_text TEXT,
    id INT AUTO_INCREMENT PRIMARY KEY
);

CREATE TABLE announcements (
    document_id INT NOT NULL,
    person_signing VARCHAR(255),
    person_name VARCHAR(255),
    organization VARCHAR(255),
    subject VARCHAR(255),
    raw_text TEXT,
    id INT AUTO_INCREMENT PRIMARY KEY
);

-- Data import was done in MySQL Workbench -> Import Data from Wizard