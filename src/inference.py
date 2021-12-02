import time
import cdsw
import json
import requests
import concurrent
import threading


class ThreadedModelRequest:
    """A utility for making concurrent model API calls

    Utilize multi-threading to achieve concurrency and speed up I/O bottleneck associated
    with making a large number of synchronous API calls to the model endpoint.

    Attributes:
        n_threads (int)
        deployment_details (dict): config info about deployed model
        model_service_url (str): deployed models API endpoint URL
        thread_local (_thread._local): A class that represents thread-local data

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
        """'
        Use a self created payload object and the requests library to call the
        deployed model.

        Configuring the requests session manually allows for multithreading to
        work.

        """

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
        """

        response = cdsw.call_model(
            model_access_key=self.deployment_details["model_access_key"],
            ipt={"record": record},
        )

        return record["id"], response["response"]["uuid"]

    def threaded_call(self, records):
        """
        Utilize the call_model() method to make API calls to the deployed model
        for a batch of input records using multithreading for efficiency.

        """

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
