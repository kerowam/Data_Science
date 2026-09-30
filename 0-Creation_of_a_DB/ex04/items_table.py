#!/usr/bin/env python

import psycopg2
import sys
from pathlib import Path

def load_env(path="../ex01/.env"):
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
		print("Usage: python items_table.py")
		sys.exit(1)

	try:
		csv_path = Path("../subject/item/item.csv")
		table_name = "items"
		conn = None
		cursor = None
		env = load_env()
		login = env.get("STUDENT_LOGIN")
		password = env.get("POSTGRES_PASSWORD")

		conn = psycopg2.connect(
			host="localhost",
			port=5432,
			dbname="piscineds",
			user=login,
			password=password,
		)
		print(f"Connected to PostgreSQL as {login}")
		cursor = conn.cursor()
		print(f"Creating table '{table_name}' and loading data from '{csv_path}'")

		cursor.execute(f"""
			CREATE TABLE IF NOT EXISTS {table_name} (
				product_id INTEGER,
				category_id BIGINT,
				category_code VARCHAR(50),
				brand VARCHAR(50)
			);
		""")
		
		print(f"Table '{table_name}' created successfully.")

		with open(csv_path, "r") as f:
			cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)
		print(f"Data loaded successfully into table '{table_name}' from '{csv_path}'.")
		conn.commit()
		print(f"Table '{table_name}' created and data loaded successfully from '{csv_path}'.")

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