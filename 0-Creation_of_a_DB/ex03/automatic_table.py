#!/usr/bin/env python

import os
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


def create_table_and_load_data(cursor, table_name, csv_path):
	try:
		cursor.execute(f"""
			CREATE TABLE IF NOT EXISTS {table_name} (
				event_time TIMESTAMP,
				event_type VARCHAR(50),
				product_id INTEGER,
				price DECIMAL(10, 2),
				user_id BIGINT,
				user_session UUID
			);
		""")
		print(f"Table '{table_name}' created successfully.")

		with open(csv_path, "r") as f:
			cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)
		print(f"Data loaded successfully into table '{table_name}' from '{csv_path}'.")
	except Exception as e:
		print(f"Error creating table or loading data: {e}")
		raise


def main():
	if len(sys.argv) != 1:
		print("Usage: python automatic_table.py")
		sys.exit(1)

	conn = None
	cursor = None

	try:
		directory_path = Path("../subject/customer/")

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

		for filename in os.listdir(directory_path):
			if filename.endswith(".csv"):
				csv_path = os.path.join(directory_path, filename)
				table_name = os.path.splitext(filename)[0]
				print(f"Processing file '{csv_path}' for table '{table_name}'")
				create_table_and_load_data(cursor, table_name, csv_path)

		conn.commit()

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