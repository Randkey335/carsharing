#!/bin/sh
echo "Waiting for postgres..."
python wait_for_db.py
echo "PostgreSQL started"

python -m flask run --host=0.0.0.0