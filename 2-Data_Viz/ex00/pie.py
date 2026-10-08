#!/usr/bin/env python

import matplotlib.pyplot as plt
import pandas as pd
import psycopg2


def	main():

	try:
		conn = psycopg2.connect(
			dbname="piscineds",
			user="gfredes-",
			host="localhost",
			port=5432,
			password="mysecretpassword"
		)

		print("Connected to PostgreSQL database")
		cursor = conn.cursor()
		cursor.execute(f"""
			SELECT event_type, COUNT(*)
			FROM customers
			GROUP BY event_type;
		""")

		data = cursor.fetchall()
		cursor.close()
		conn.commit()
		conn.close()

		df = pd.DataFrame(data, columns=["event_type", "count"])
		plt.pie(df["count"], labels=df["event_type"], autopct="%1.1f%%")
		plt.axis("equal")
		plt.show()

	except Exception as e:
		print(f"Error: {e}")
		if conn is not None:
			conn.rollback()

if __name__ == "__main__":
	main()