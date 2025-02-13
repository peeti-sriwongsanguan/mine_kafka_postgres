!/bin/bash
# init-db.sh

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE healthcare_db;
    GRANT ALL PRIVILEGES ON DATABASE healthcare_db TO postgres;
EOSQL