#!/usr/bin/env python

from psycopg2 import connect, sql
import sys

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
		print("Usage: python customers_table.py")
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

		cursor.execute(f"""
			SELECT table_name
			FROM information_schema.tables
			WHERE table_schema = 'public' AND table_name LIKE 'data_202%_%'
		""")

		table_names = [row[0] for row in cursor.fetchall()]
		if not table_names:
			raise Exception("No tables found matching the pattern 'data_202%_%' in the public schema.")

		print(f"Found tables: {table_names}")

		selects = [
			sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
			for table_name in table_names
		]

		query = sql.SQL("""
			CREATE TABLE IF NOT EXISTS customers AS
			{}
		""").format(sql.SQL(" UNION ALL ").join(selects))
		cursor.execute(f"DROP TABLE IF EXISTS customers;")
		cursor.execute(query)
		print("Table 'customers' created successfully")
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