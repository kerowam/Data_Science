#!/usr/bin/env python

import matplotlib.pyplot as plt
import pandas as pd
import psycopg2


def print_data(price):
	stats = price.describe()

	for label, value in stats.items():
		print(f"{label:<6} {value:>14.6f}")
	

def box_plot_price_items_purchased(price_df, showflier):
	fig, ax = plt.subplots(figsize=(12, 6), layout="constrained")

	ax.set_facecolor("#d8d5e8")
	ax.set_axisbelow(True)
	box = ax.boxplot(
			x=price_df,
			orientation="horizontal",
			widths=0.8,
			patch_artist=True,
			showfliers=showflier,
			autorange=True,
			#capwidths=0.5,
			flierprops=dict(
				marker="D",
				markersize=3,
				markerfacecolor="grey",
				markeredgewidth=0.5,
				alpha=0.5
			),
			medianprops=dict(
				color="black",
			)
		)
	for b in box["boxes"]:
		b.set(facecolor="#48A490", linewidth=1.5, alpha=0.7)
	ax.grid(True, axis='x', linestyle="--", linewidth=0.6, alpha=0.7, color="white")
	ax.set_xlabel("price")
	ax.set_yticks([])
	plt.show()
	

def plot_average_basket_price_per_user(cursor):
	try:
		cursor.execute(f"""
			WITH user_basket AS (
				SELECT SUM(price) AS total_basket_price, user_id, user_session
				FROM customers
				WHERE event_type = 'purchase'
				GROUP BY user_id, user_session
			),
			average_basket AS (
				SELECT user_id, AVG(total_basket_price) AS average_basket_price
				FROM user_basket
				GROUP BY user_id
			)
			SELECT user_id, average_basket_price
			FROM average_basket
			"""
		)

		data = cursor.fetchall()
		df = pd.DataFrame(data, columns=["user_id", "average_basket_price"])
		average_df = df["average_basket_price"].astype(float)

		plt.boxplot(
			x=average_df,
    	    orientation='horizontal',
    	    patch_artist=True,
    	    showfliers=True,
    	    autorange=True,
    	)
		#plt.xlim(0, 43)
		plt.yticks([])
		plt.show()

	except Exception as e:
		print(f"Error: {e}")


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
		cursor.execute(f"""
			SELECT price
			FROM customers
			WHERE event_type = 'purchase';
		""")

		data = cursor.fetchall()
		df = pd.DataFrame(data, columns=["price"])
		df["price"] = df["price"].astype(float)
		print_data(df["price"])
		box_plot_price_items_purchased(df["price"], True)
		box_plot_price_items_purchased(df["price"], False)
		plot_average_basket_price_per_user(cursor)
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