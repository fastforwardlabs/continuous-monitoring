import os
import pandas as pd

from src.simulation import Simulation

train_path = "data/working/train_df.pkl"
prod_path = "data/working/prod_df.pkl"

train_df = pd.read_pickle(train_path)
prod_df = pd.read_pickle(prod_path)

sim = Simulation(model_name="Price Regressor")
sim.run_simulation(train_df, prod_df)
