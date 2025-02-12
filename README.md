# Mine Clinic Database Architecture

This project I design a system that uses both Postgres SQL and Kafka to create a future-proof for Mine Cline system.

Reasons:
1. Security
   - Implement security in Postgres for patient data access control
   - Encrypt sensitive data using encryption functions
   - Use SSL for database connections
2. Utilize Kafka for real time features
    - Real-time notification
    - Analytics and reporting pipeline
3. Performance optimization
   - Design indexes on tables
   - Implement partitioning for large tables
   - Use views for reporting 