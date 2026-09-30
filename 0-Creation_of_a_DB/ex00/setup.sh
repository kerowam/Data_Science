#!/usr/bin/env bash

set -eu

if [ "$#" -ne 1 ]; then
  echo "Usage: ./setup.sh <student_login>"
  exit 1
fi

LOGIN="$1"

cat > .env <<EOF
STUDENT_LOGIN=${LOGIN}
POSTGRES_PASSWORD=mysecretpassword
EOF

docker compose up -d --build

echo "PostgreSQL is starting with user: ${LOGIN}, database: piscineds"
echo "Connect using: psql -U ${LOGIN} -d piscineds -h localhost -W"