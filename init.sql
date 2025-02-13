-- Only create database if it doesn't exist
CREATE DATABASE healthcare_db;
\c healthcare_db;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Add any initial schema or data here
-- For example:
-- CREATE TABLE example (
--     id SERIAL PRIMARY KEY,
--     name VARCHAR(100)
-- );
