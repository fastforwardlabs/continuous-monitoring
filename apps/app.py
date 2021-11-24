import os
from flask import Flask

app = Flask(__name__, static_folder='reports', static_url_path='')
  
@app.route('/data-drift')
def report():
    return app.send_static_file('iris_data_and_target_drift.html')

# @app.route('/regression')
# def regression():
#     return app.send_static_file('bike_sharing_demand_model_perfomance.html')
  
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=os.environ.get('CDSW_READONLY_PORT'))