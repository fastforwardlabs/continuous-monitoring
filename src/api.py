import os
import json
import string
import cmlapi
import random
import logging
from packaging import version

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

log_file = "logs/simulation.log"
os.makedirs(os.path.dirname(log_file), exist_ok=True)
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)


class ApiUtility:
    """A utility class for working with CML API_v2

    This class contains methods that wrap API_v2 to achieve specific
    needs that facilitate the simulation.

    Attributes:
        client (cmlapi.api.cml_service_api.CMLServiceApi)

    """

    def __init__(self):
        self.client = cmlapi.default_client()

    def get_latest_deployment_details(self, model_name):
        """
        Given a APIv2 client object and Model Name, use APIv2 to retrieve details about the latest/current deployment.

        This function only works for models deployed within the current project.
        """

        project_id = os.environ["CDSW_PROJECT_ID"]

        # gather model details
        models = (
            self.client.list_models(project_id=project_id, async_req=True)
            .get()
            .to_dict()
        )
        model_info = [
            model for model in models["models"] if model["name"] == model_name
        ][0]

        model_id = model_info["id"]
        model_crn = model_info["crn"]
        model_access_key = model_info["access_key"]

        # gather latest build details
        builds = (
            self.client.list_model_builds(
                project_id=project_id, model_id=model_id, async_req=True
            )
            .get()
            .to_dict()
        )
        build_info = builds["model_builds"][-1]  # most recent build

        build_id = build_info["id"]

        # gather latest deployment details
        deployments = (
            self.client.list_model_deployments(
                project_id=project_id,
                model_id=model_id,
                build_id=build_id,
                async_req=True,
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

    def get_latest_standard_runtime(self):
        """
        Use CML APIv2 to identify and return the latest version of a Python 3.6,
        Standard, Workbench Runtime
        """

        try:
            runtime_criteria = {
                "kernel": "Python 3.6",
                "edition": "Standard",
                "editor": "Workbench",
            }
            runtimes = self.client.list_runtimes(
                search_filter=json.dumps(runtime_criteria)
            ).to_dict()["runtimes"]

            versions = {
                version.parse(rt["full_version"]): i for i, rt in enumerate(runtimes)
            }
            latest = versions[max(versions.keys())]

            return runtimes[latest]["image_identifier"]

        except:
            logger.info("No matching runtime available.")
            return None

    def deploy_monitoring_application(self, application_name):
        """
        Use CML APIv2 to create and deploy an application to serve the Evidently
        monitoring reports via a Flask application.

        Utilize a runtime if available, else use legacy Python3 engine.

        """

        ipt = {
            "name": application_name,
            "description": "An Evidently.ai dashboard for monitoring data drift, target drift, and regression performance.",
            "project_id": os.environ["CDSW_PROJECT_ID"],
            "subdomain": "".join(
                [random.choice(string.ascii_lowercase) for _ in range(6)]
            ),
            "script": "apps/app.py",
            "cpu": 1,
            "memory": 2,
        }

        # configure runtime if available
        runtime = self.get_latest_standard_runtime()
        if runtime:
            ipt["runtime_identifier"] = runtime
        else:
            ipt["kernel"] = "python3"

        application_request = cmlapi.CreateApplicationRequest(**ipt)

        self.client.create_application(
            project_id=os.environ["CDSW_PROJECT_ID"], body=application_request
        )
        logger.info(f"Created and deployed new application: {application_name}")

    def restart_running_application(self, application_name):
        """
        Use CML APIv2 to restart a running application provided the application name.

        """

        search_criteria = {"name": application_name}

        app = self.client.list_applications(
            project_id=os.environ["CDSW_PROJECT_ID"],
            search_filter=json.dumps(search_criteria),
        ).to_dict()["applications"][0]

        self.client.restart_application(
            project_id=os.environ["CDSW_PROJECT_ID"], application_id=app["id"]
        )

        logger.info(f"Restarted existing application: {application_name}")
