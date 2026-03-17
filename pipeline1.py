import pandas as pd
import sqlite3
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
    )

logging.info("Starting pipeline")


# Extract
df = pd.read_csv("bmw_global_sales_2018_2025.csv")
logging.info("Dataset loaded")

# Transform
df = df.dropna()
df = df.drop_duplicates()
df.columns = df.columns.str.lower()
df["revenue_millions"] = df["revenue_eur"] / 1_000_000
df["date"] = pd.to_datetime(df[["year", "month"]].assign(day=1))
df = df[df["year"] >= 2020]

logging.info("Data cleaned")

# Load
conn = sqlite3.connect("bmw_sales.db")
df.to_sql("bmw_sales", conn, if_exists="replace", index=False)
logging.info("Data loaded into database!")
logging.info("Pipeline completed")



# Analytics query
summary_query = """
SELECT 
    model,
    SUM(units_sold) AS total_units_solds,
    SUM(revenue_eur) AS total_revenue
From bmw_sales
Group BY model
Order BY total_units_solds DESC
"""
summary_df = pd.read_sql(summary_query, conn)
summary_df.to_sql("bmw_model_summary", conn, if_exists="replace", index=False)
logging.info("Summary table created")
print(summary_df.head())

query = "SELECT * FROM bmw_sales LIMIT 5"
result = pd.read_sql(query, conn)

print(result)

conn.close()