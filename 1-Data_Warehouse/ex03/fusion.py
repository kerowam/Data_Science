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
			CREATE TABLE IF NOT EXISTS customers_cleaned AS
			SELECT * FROM customers;

			DROP TABLE IF EXISTS customers;

			CREATE TABLE customers AS
			SELECT
				c.*,
    			i.category_ids,
    			i.category_codes,
    			i.brands
			FROM customers_cleaned AS c
			LEFT JOIN (
				SELECT
					product_id,
					ARRAY_AGG(DISTINCT category_id)
						FILTER (WHERE category_id IS NOT NULL) AS category_ids,
					ARRAY_AGG(DISTINCT category_code)
						FILTER (WHERE category_code IS NOT NULL) AS category_codes,
					ARRAY_AGG(DISTINCT brand)
						FILTER (WHERE brand IS NOT NULL) AS brands
				FROM items
				GROUP BY product_id
			) AS i
				ON c.product_id = i.product_id;
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