import os
import sklearn
import numpy as np
import pandas as pd
from datetime import datetime
from pandas.tseries.offsets import DateOffset

def random_day_offset(ts: pd._libs.tslibs.timestamps.Timestamp, max_days=60):
    """
    Given a pandas Timestamp, return a new timestep offset to an earlier date by
    a random number of days between 0 and max_days.
    """
    return ts - DateOffset(np.random.randint(0, max_days))


def get_active_feature_names(
    column_transformer,
):
    """Inspect the transformer steps in a given sklearn.ColumnTransformer to collect and
    return the names of all features that are not dropped as part of the pipeline."""

    active_steps = [
        k for k, v in column_transformer.named_transformers_.items() if v != "drop"
    ]

    return np.concatenate(
        [column_transformer.named_transformers_[step].feature_names_in_ for step in active_steps]
    ).tolist()

def get_latest_deployment_details(client, model_name):
    """
    Given a APIv2 client object and Model Name, use APIv2 to retrieve details about the latest/current deployment.

    This function only works for models deployed within the current project.
    """

    project_id = os.environ["CDSW_PROJECT_ID"]

    # gather model details
    models = client.list_models(project_id=project_id, async_req=True).get().to_dict()
    model_info = [model for model in models["models"] if model["name"] == model_name][0]

    model_id = model_info["id"]
    model_crn = model_info["crn"]
    model_access_key = model_info["access_key"]

    # gather latest build details
    builds = (
        client.list_model_builds(
            project_id=project_id, model_id=model_id, async_req=True
        )
        .get()
        .to_dict()
    )
    build_info = builds["model_builds"][-1]  # most recent build

    build_id = build_info["id"]

    # gather latest deployment details
    deployments = (
        client.list_model_deployments(
            project_id=project_id, model_id=model_id, build_id=build_id, async_req=True
        )
        .get()
        .to_dict()
    )
    deployment_info = deployments["model_deployments"][-1]  # most recent deployment

    model_deployment_crn = deployment_info["crn"]

    return {
        "model_name": model_name,
        "model_id": model_id,
        "model_crn": model_crn,
        "model_access_key": model_access_key,
        "latest_build_id": build_id,
        "latest_deployment_crn": model_deployment_crn,
    }