"""
1. Score Train Data - this provides evaluation data in Evidently.ai
2. Run simulation - for every N=2 months that pass (starting with data split date):
    - Query prod_df for new listings (date_listed) and score it using deployed model
    - Query prod_df for newly sold properties (date_sold) and use cdsw.track_metric() to assign ground truth to stored prediction
    - Query CML Metric Store for those newly sold properties, generate dataframe, and then a new evidently report
    - Deploy updated Evidently dashboards (data drift & regression metrics) for newly sold properties
    - Wait a bit, maybe...
"""
import os
import pandas as pd

from utils.simulation_utils import Simulation

train_path = "../data/working/train_df.pkl"
prod_path = "../data/working/prod_df.pkl"

train_df = pd.read_pickle(train_path)
prod_df = pd.read_pickle(prod_path)

if os.environ["DEV_MODE"] == True:
    train_df = train_df.sample(frac=0.05, random_state=42)
    prod_df = prod_df.sample(frac=0.05, random_state=42)

sim = Simulation(model_name="Price Regressor")
sim.run_simulation(train_df, prod_df)
