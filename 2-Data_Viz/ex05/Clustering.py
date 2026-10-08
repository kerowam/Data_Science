#!/usr/bin/env python

import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
from sklearn import cluster
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def load_data(cursor):
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
	return pd.DataFrame(data, columns=['user_id', 'last_purchase', 'frequency', 'monetary'])


def prepare_features(df):
	df['last_purchase'] = pd.to_datetime(df['last_purchase'])
	reference_date = df['last_purchase'].max()
	df['recency'] = (reference_date - df['last_purchase']).dt.days

	features = df[['frequency', 'monetary', 'recency']].astype(float)
	
	scaler = StandardScaler()
	scaled_features = scaler.fit_transform(features)
	return scaled_features


def cluster_customers(df, scaled_features):
	model = KMeans(n_clusters=4, random_state=42, n_init=10)
	df['cluster'] = model.fit_predict(scaled_features)
	return df


def plot_clusters_frequency_monetary(df):
	plt.figure(figsize=(10, 6))
	
	for cluster in sorted(df['cluster'].unique()):
		cluster_data = df[df['cluster'] == cluster]
		plt.scatter(
			cluster_data['frequency'],
			cluster_data['monetary'],
			label=f'Cluster {cluster}',
			alpha=0.6
		)

	plt.xlabel('Frequency')
	plt.ylabel('Monetary Value')
	plt.title('Customer Segmentation based on RFM Analysis')
	plt.legend()
	plt.grid(alpha=0.3)
	plt.tight_layout()
	plt.show()



def plot_clusters_recency_monetary(df):
    plt.figure(figsize=(10, 6))

    for cluster in sorted(df["cluster"].unique()):
        group = df[df["cluster"] == cluster]

        plt.scatter(
            group["recency"],
            group["monetary"],
            label=f"Cluster {cluster}",
            alpha=0.6
        )

    plt.xlabel("days since last purchase")
    plt.ylabel("monetary value")
    plt.title("Recency and monetary value by cluster")
    plt.legend()
    plt.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.show()


def plot_cluster_sizes(df):
	sizes = df["cluster"].value_counts().sort_index()
     
	fig, ax = plt.subplots(figsize=(10, 6))
	bars = ax.barh(sizes.index.astype(str), sizes.values)

	ax.bar_label(bars, fmt='%d', padding=3)
	ax.set_xlabel("customers")
	ax.set_ylabel("cluster")
	ax.set_title("Customers per cluster")
	ax.grid(axis="x", alpha=0.4)
	ax.set_yticks(range(4), ["New customers", "Platinum customers", "Inactive", "Loyal customers"])
	fig.tight_layout()
	plt.show()


def main():
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
        df = load_data(cursor)
        scaled_features = prepare_features(df)
        df = cluster_customers(df, scaled_features)

        print(df.groupby("cluster")[["frequency", "monetary", "recency"]].mean())

        plot_clusters_frequency_monetary(df)
        plot_clusters_recency_monetary(df)
        plot_cluster_sizes(df)

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