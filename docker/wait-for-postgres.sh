#!/bin/bash
# wait-for-postgres.sh

set -e

host="$1"
if [ -z "$host" ]; then
  echo "Usage: 0$ <db-host" >&2
  exit 1
fi 

echo "Testing Postgres connection with psql ..."
until PGPASSWORD="$DBPASSWORD" psql -h "$host" -U "$DBUSER" -d "$DBNAME" -c "\q" >/dev/null 2>&1; do
  >&2 echo -n .
  sleep 1
done

>&2 echo "Postgres is up"
