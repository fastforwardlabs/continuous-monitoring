# Read the fitted model (scripts/train.py) from the file model.pkl
# and define a function that uses the model to make inference

# This version of the predict function is wrapped with the
# model_metrics decorator, enabling it to call .track_metrics()
# to store mathematical metrics associated with each prediction

import cdsw
import pickle
import pandas as pd

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# The model_metrics decorator equips the predict function to
# call .track_metrics(). It also changes the return type. If the
# raw predict function returns a value "result", the wrapped
# function will return eg
# {
#   "uuid": "612a0f17-33ad-4c41-8944-df15183ac5bd",
#   "prediction": "result"
# }

# The UUID can be used to query the stored metrics for this
# prediction later.


@cdsw.model_metrics
def predict(data_input):

    # Convert dict representation back to dataframe for inference
    df = pd.DataFrame.from_records([data_input["record"]])

    df = df[col_order].drop("price", axis=1)

    # Log raw input values of features used in inference pipeline
    # active_features = get_active_feature_names(model.named_steps["preprocess"]) # feature not compatible with Python 3.6
    active_features = [
        "bedrooms",
        "bathrooms",
        "sqft_living",
        "sqft_lot",
        "sqft_above",
        "waterfront",
        "zipcode",
        "condition",
        "view",
    ]
    cdsw.track_metric(
        "input_features", df[active_features].to_dict(orient="records")[0]
    )

    # Use pipeline to make inference on request
    result = model.predict(df).item()

    # Log the prediction
    cdsw.track_metric("predicted_result", result)

    return result
