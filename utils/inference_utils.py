import time
import cdsw
import json
import requests
import concurrent
import threading
import numpy as np

def cast_date_as_str_for_json(df):
    """Given a dataframe, return the same dataframe with non-numeric columns cast as string"""

    for column, dt in zip(df.columns, df.dtypes):
        if dt.type not in [np.int64, np.float64]:
            df.loc[:, column] = df.loc[:, column].astype(str)
    return df


class ThreadedModelRequest:
    """
    Utilize multi-threading to achieve concurrency and speed up I/O bottleneck associated
    with making a large number of synchronous API calls to the model endpoint.

    Note - this function can also be implemented with cdsw.call_model()

    """

    def __init__(self, deployment_details, n_threads=2):
        self.n_threads = n_threads
        self.deployment_details = deployment_details
        self.model_service_url = cdsw._get_model_call_endpoint()
        self.thread_local = threading.local()

    def get_session(self):
        if not hasattr(self.thread_local, "session"):
            self.thread_local.session = requests.Session()
        return self.thread_local.session

    def call_model(self, record):

        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "accessKey": self.deployment_details["model_access_key"],
            "request": {"record": record},
        }

        session = self.get_session()
        response = session.post(
            url=self.model_service_url,
            headers=headers,
            data=json.dumps(data),
        ).json()

        return record["id"], response["response"]["uuid"]

    def call_model_cdsw(self, record):
        """
        Not Implemented - currently performs 42% slower than call_model.
        Threading cant be properly implemented
        """

        response = cdsw.call_model(
            model_access_key=self.deployment_details["model_access_key"],
            ipt={"record": record},
        )

        return record["id"], response["response"]["uuid"]

    def threaded_call(self, records):

        start_timestamp_ms = int(round(time.time() * 1000))

        results = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.n_threads
        ) as executor:
            completed = executor.map(self.call_model, records)

        results.extend(completed)

        end_timestamp_ms = int(round(time.time() * 1000))

        return {
            "start_timestamp_ms": start_timestamp_ms,
            "end_timestamp_ms": end_timestamp_ms,
            "id_uuid_mapping": dict(results),
        }