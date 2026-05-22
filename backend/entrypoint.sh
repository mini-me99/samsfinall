#!/bin/sh
set -e

if [ "$SKIP_DJANGO_STARTUP" != "1" ]; then
  echo "Waiting for database..."
  until python -c "import socket,os; s=socket.socket(); s.connect((os.environ['POSTGRES_HOST'], int(os.environ.get('POSTGRES_PORT','5432'))))" 2>/dev/null; do
    sleep 1
  done

  echo "Applying migrations..."
  python manage.py makemigrations --noinput
  python manage.py migrate --noinput

  echo "Collecting static..."
  python manage.py collectstatic --noinput

  if [ "$SEED_DEMO" = "1" ]; then
    echo "Seeding demo data..."
    python manage.py seed_demo
  fi
fi

echo "Starting: $@"
exec sh -c "$*"
