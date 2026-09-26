-- =========================================================================
-- Smart Blood Bank Management System
-- MySQL Database Setup Script
-- =========================================================================

CREATE DATABASE IF NOT EXISTS bloodbank;

USE bloodbank;


-- =========================================================================
-- TABLE: donors
-- =========================================================================

CREATE TABLE IF NOT EXISTS donors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    city VARCHAR(100) NOT NULL
);


-- =========================================================================
-- TABLE: blood_stock
-- =========================================================================

CREATE TABLE IF NOT EXISTS blood_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    blood_group VARCHAR(5) NOT NULL UNIQUE,
    units INT NOT NULL DEFAULT 0
);


-- =========================================================================
-- TABLE: blood_requests
-- =========================================================================

CREATE TABLE IF NOT EXISTS blood_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_name VARCHAR(150) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    units INT NOT NULL,
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Pending'
);


-- =========================================================================
-- TABLE: hospitals
-- =========================================================================

CREATE TABLE IF NOT EXISTS hospitals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_name VARCHAR(150) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);


-- =========================================================================
-- INSERT BLOOD GROUPS
-- =========================================================================

INSERT IGNORE INTO blood_stock (blood_group, units)
VALUES
('A+', 0),
('A-', 0),
('B+', 0),
('B-', 0),
('AB+', 0),
('AB-', 0),
('O+', 0),
('O-', 0);


-- =========================================================================
-- DATABASE SETUP COMPLETE
-- =========================================================================
