#!/usr/bin/env python

import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def elbow_method(df):
	features = df[['frequency', 'monetary', 'recency']].astype(float)

	scaler = StandardScaler()
	scaled_features = scaler.fit_transform(features)

	inertias = []
	k_values = range(1, 11)

	for k in k_values:
		model = KMeans(n_clusters=k, random_state=42, n_init=10)
		model.fit(scaled_features)
		inertias.append(model.inertia_)

	plt.plot(k_values, inertias, marker='o')
	plt.xlabel('Number of clusters')
	plt.title('The Elbow Method')
	plt.xticks(k_values)
	plt.grid(True, linestyle="--", linewidth=0.6, alpha=0.7, color="grey")
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

		cursor.execute(f"""
			SELECT
				user_id,
				MAX(event_time) AS last_purchase,
				COUNT(DISTINCT user_session) AS frequency,
				SUM(price) AS monetary
			FROM customers
			WHERE event_type = 'purchase'
			GROUP BY user_id
		""")

		data = cursor.fetchall()
		df = pd.DataFrame(data, columns=['user_id', 'last_purchase', 'frequency', 'monetary'])
		df['last_purchase'] = pd.to_datetime(df['last_purchase'])
		reference_date = df['last_purchase'].max()
		df['recency'] = (reference_date - df['last_purchase']).dt.days
		elbow_method(df)

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