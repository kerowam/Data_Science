#!/usr/bin/env python

import matplotlib.pyplot as plt
import pandas as pd
import psycopg2


def plot_orders_by_frequency(cursor):
	cursor.execute(f"""
		SELECT user_id, COUNT(*) AS order_count
		FROM customers
		WHERE event_type = 'purchase'
		GROUP BY user_id
		HAVING COUNT(*) < 40
		ORDER BY COUNT(*) ASC;
	""")
	data = cursor.fetchall()
	df = pd.DataFrame(data, columns=["user_id", "order_count"])

	plt.hist(df["order_count"], bins=5, edgecolor='black')
	plt.xlabel("frequency")
	plt.ylabel("customers")
	plt.grid(alpha=0.5)
	plt.yticks(range(0, 70000, 10000))
	plt.xticks(range(0, 39, 10))
	plt.show()


def plot_spent_by_customers(cursor):
	cursor.execute(f"""
		SELECT user_id, SUM(price) AS total_spent
		FROM customers
		WHERE event_type = 'purchase'
		GROUP BY user_id
		HAVING SUM(price) < 225
		ORDER BY SUM(price) ASC;
	""")
	data = cursor.fetchall()
	df = pd.DataFrame(data, columns=["user_id", "total_spent"])
	df["total_spent"] = df["total_spent"].astype(float)

	plt.hist(df["total_spent"], bins=5, edgecolor='black')
	plt.xlabel("monetary value in Altarians")
	plt.ylabel("customers")
	plt.grid(alpha=0.25)
	plt.tight_layout()
	plt.show()


def	main():
	conn = None
	cursor = None

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
		plot_orders_by_frequency(cursor)
		plot_spent_by_customers(cursor)
		
		conn.commit()	


	except Exception as e:
		print(f"Error: {e}")
		if conn is not None and not conn.closed:
			try:
				conn.rollback()
			except Exception:
				print("Error rolling back transaction")
	finally:
		if cursor is not None:
			cursor.close()
		if conn is not None:
			conn.close()

if __name__ == "__main__":
	main()