FROM mysql:8.0

# MySQL automatically runs any .sql file placed here, in filename order,
# the first time the container starts with an empty data directory.
COPY schema_complete.sql /docker-entrypoint-initdb.d/

EXPOSE 3306