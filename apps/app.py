import os
from flask import Flask

from utils.utils import find_latest_report

app = Flask(__name__, static_folder="apps/reports", static_url_path="")


@app.route("/")
def report():
    latest_report = find_latest_report(report_dir="apps/reports/")
    return app.send_static_file(latest_report)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=os.environ.get("CDSW_READONLY_PORT"))
