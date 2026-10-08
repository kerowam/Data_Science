#!/usr/bin/env python

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import psycopg2
from matplotlib.ticker import MultipleLocator
from collections import defaultdict
from decimal import Decimal


def plot_nbr_of_customers_timeline(data):

	df = pd.DataFrame(data, columns=["event_time", "user_id", "price"])
	df["event_time"] = pd.to_datetime(df["event_time"])
	df["day"] = df["event_time"].dt.normalize()
	customers_per_day = df.groupby("day")["user_id"].nunique().reset_index(name="customer_count")

	plt.figure(figsize=(12, 6))
	plt.plot(customers_per_day["day"], customers_per_day["customer_count"])
	ax = plt.gca()
	ax.set_axisbelow(True)
	ax.margins(x=0)
	ax.xaxis.set_major_locator(mdates.MonthLocator())
	ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
	ax.set_facecolor("#d8d5e8")
	ax.grid(
	    True,
	    linestyle="--",
	    linewidth=0.6,
	    alpha=0.7,
	    color="white"
	)
	plt.ylabel("Number of Customers")
	plt.tight_layout()
	plt.show()


def plot_total_sales_per_month(data):

	sales_by_month = defaultdict(Decimal)
	months = []
	total_sales_list = []

	for event_time, _, price in data:
		year, month = event_time.year, event_time.month
		sales_by_month[(year, month)] += Decimal(str(price))

	for (year, month), total_sales in sales_by_month.items():
		months.append(pd.Timestamp(year=year, month=month, day=1))
		total_sales_list.append(float(total_sales))

	plt.figure(figsize=(12, 6))
	plt.bar(months, total_sales_list, width=20, alpha=1, color="#95A2AB")
	ax = plt.gca()
	ax.set_xlabel("month")
	ax.xaxis.set_major_locator(mdates.MonthLocator())
	ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
	ax.set_facecolor("#d8d5e8")
	ax.set_axisbelow(True)
	ax.spines['top'].set_visible(False)
	ax.spines['right'].set_visible(False)
	ax.spines['left'].set_visible(False)
	ax.spines['bottom'].set_visible(False)
	ax.tick_params(axis='both', which='both', length=0)
	ax.yaxis.get_offset_text().set_visible(False)
	ax.grid(
	    True,
		axis="y",
	    linestyle="--",
	    linewidth=0.6,
	    alpha=0.7,
	    color="white"
	)
	plt.ylabel("total sales in million of Altarians")
	plt.xlabel("month")
	plt.tight_layout()
	plt.show()


def plot_average_spend_customers_timeline(data):
	
	nbr_of_customers_per_day = defaultdict(set)
	total_spend_per_day = defaultdict(Decimal)

	for event_time, user_id, price in data:
		year, month, day = event_time.year, event_time.month, event_time.day
		date = pd.Timestamp(year=year, month=month, day=day)
		nbr_of_customers_per_day[date].add(user_id)
		total_spend_per_day[date] += Decimal(str(price))

	
	average_spend_per_day = {date: float(total_spend) / len(customers) if len(customers) > 0 else 0 for date, customers in nbr_of_customers_per_day.items() for total_spend in [total_spend_per_day[date]]}
	date = average_spend_per_day.keys()
	average_spend = average_spend_per_day.values()

	plt.figure(figsize=(12, 6))
	plt.fill_between(date, average_spend)
	ax = plt.gca()
	ax.margins(x=0)
	ax.yaxis.set_major_locator(MultipleLocator(5))
	ax.xaxis.set_major_locator(mdates.MonthLocator())
	ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
	ax.set_facecolor("#d8d5e8")
	ax.set_axisbelow(True)
	ax.grid(
	    True,
	    linestyle="--",
	    linewidth=0.6,
	    alpha=0.7,
	    color="white"
	)
	plt.ylabel("average spend/customers in Altarians")
	plt.ylim(bottom=0)
	plt.tight_layout()
	plt.show()


def	main():
	conn = None

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
			SELECT DISTINCT
				event_time,
				user_id,
				price
			FROM customers
			WHERE event_type = 'purchase'
			ORDER BY event_time ASC;
		""")

		data = cursor.fetchall()
		cursor.close()
		conn.commit()

		plot_nbr_of_customers_timeline(data)
		plot_total_sales_per_month(data)
		plot_average_spend_customers_timeline(data)

	except Exception as e:
		print(f"Error: {e}")
		if conn is not None:
			try:
				conn.rollback()
			except Exception:
				print("Error rolling back transaction")
	finally:
		if conn is not None:
			conn.close()

if __name__ == "__main__":
	main()