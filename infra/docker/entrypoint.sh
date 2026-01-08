#!/bin/sh
set -e

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

echo "Waiting for Postgres..."
python - <<'PY'
import os, time
import psycopg

dbname = os.getenv("DB_NAME", "crud_perfis")
user = os.getenv("DB_USER", "crud_perfis")
password = os.getenv("DB_PASSWORD", "crud_perfis")
host = os.getenv("DB_HOST", "db")
port = os.getenv("DB_PORT", "5432")

for _ in range(30):
    try:
        conn = psycopg.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        conn.close()
        print("Postgres is ready!")
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Postgres not ready after 30s")
PY

python manage.py migrate
exec python manage.py runserver 0.0.0.0:8000
