import os
import numpy as np
import pandas as pd

from utils.utils import random_day_offset, outlier_removal

# Load raw data
df = pd.read_csv("data/raw/kc_house_data.csv")

# Drop duplicates
df = df.drop_duplicates(subset=["id"], keep="first")

# Create an artificial "listed" date to help mimic production scenario
np.random.seed(42)
df["date_sold"] = pd.to_datetime(df.date, infer_datetime_format=True)
df["date_listed"] = df.date_sold.apply(lambda x: random_day_offset(x))
df = df.drop(columns=["date"])
df.sort_values(by="date_listed", inplace=True)
df.reset_index(drop=True, inplace=True)

# remove price outliers for simplicity
df = outlier_removal(X=df, multiple=3, cols=["price"])

# Split out first 6 months of data for training, remaining for simulating a "production" scenario
min_sold_date = df.date_sold.min()
max_sold_date = df.date_sold.max()

train_df = df[
    df.date_sold.between(min_sold_date, "2014-10-31", inclusive="both")
].sort_values("date_sold")

prod_df = df[
    df.date_sold.between("2014-10-31", max_sold_date, inclusive="right")
].sort_values("date_sold")

# Save off these dataframes
working_dir = "data/working"
os.makedirs(working_dir, exist_ok=True)
dfs = [("train", train_df), ("prod", prod_df)]
for name, dataframe in dfs:
    path = os.path.join(working_dir, f"{name}_df.pkl")
    dataframe.to_pickle(path)
