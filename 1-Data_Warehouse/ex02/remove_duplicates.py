#!/usr/bin/env python

from psycopg2 import connect
import sys
import time

def load_env(path="../ex00/.env"):
	env = {}

	with open(path, "r") as f:
		print(f"Loading environment variables from {path}")
		for line in f:
			line = line.strip()
			if line and not line.startswith("#") and "=" in line:
				key, value = line.split("=", 1)
				env[key.strip()] = value.strip()
	return env

def main():
	if len(sys.argv) != 1:
		print("Usage: ./remove_duplicates.py")
		sys.exit(1)

	try:
		conn = None
		cursor = None
		env = load_env()
		login = env.get("STUDENT_LOGIN")
		password = env.get("POSTGRES_PASSWORD")

		conn = connect(
			host="localhost",
			port=5432,
			dbname="piscineds",
			user=login,
			password=password,
		)
		print(f"Connected to PostgreSQL as {login}")
		cursor = conn.cursor()

		start = time.perf_counter()
		cursor.execute(f"""
			DO $$
			BEGIN
				IF NOT EXISTS (
					SELECT 1 
					FROM information_schema.tables
					WHERE table_name = 'customers_raw'
				) THEN
					ALTER TABLE customers RENAME TO customers_raw;
				END IF;
			END
			$$;

			DROP TABLE IF EXISTS customers;
			CREATE TABLE customers AS
			WITH ordered_rows AS (
				SELECT
					ctid,
					event_time,
					event_type,
					product_id,
					price,
					user_id,
					user_session,
					LAG(event_time) OVER (
						PARTITION BY event_type, product_id, price, user_id, user_session
						ORDER BY event_time, ctid
					) AS prev_event_time
				FROM customers_raw
			)
			SELECT
    			event_time,
    			event_type,
    			product_id,
    			price,
    			user_id,
    			user_session
			FROM ordered_rows
			WHERE prev_event_time IS NULL
			  OR event_time - prev_event_time > INTERVAL '1 second'
			ORDER BY event_time;
		""")

		print(f"Rows deleted: {cursor.rowcount}")		
		conn.commit()
		elapsed = time.perf_counter() - start
		print(f"Duplicates removed in {elapsed:.2f} seconds.")

	except Exception as e:
		print(f"Error: {e}")
		if conn is not None:
			conn.rollback()

	finally:
		if cursor is not None:
			cursor.close()
		if conn is not None:
			conn.close()
		print("Database connection closed.")

if __name__ == "__main__":
	main()