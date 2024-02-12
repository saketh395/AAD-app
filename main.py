from flask import Flask, request, render_template, jsonify, url_for
import json
import urllib.request
import urllib.error
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.form.to_dict()
    try:
        credential = DefaultAzureCredential()
        # Check if given credential can get token successfully.
        access_token = credential.get_token("https://ml.azure.com/.default")
    except Exception as ex:
        # Fall back to InteractiveBrowserCredential in case DefaultAzureCredential not work
        # This will open a browser page for
        credential = InteractiveBrowserCredential()

    data = {
        "Inputs": {
            "data": [
                {
                    "day": int(data['day']),
                    "mnth": int(data['month']),
                    "year": int(data['year']),
                    "season": int(data['season']),
                    "holiday": int(data['holiday']),
                    "weekday": int(data['week_day']),
                    "workingday": int(data['working_day']),
                    "weathersit": int(data['weather_quality']),
                    "temp": float(data['min_temperature']) / 100,
                    "atemp": float(data['max_temperature']) / 100,
                    "hum": float(data['Humidity']) / 100,
                    "windspeed": float(data['wind_speed']) / 100
                }
            ]
        },
        "GlobalParameters": 1.0
    }

    body = str.encode(json.dumps(data))

    url = 'https://aad-online3.northeurope.inference.ml.azure.com/score'
    api_key = access_token.token
    headers = {'Content-Type': 'application/json', 'Authorization': ('Bearer ' + api_key),
               'azureml-model-deployment': 'blue3'}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        output = json.loads(result.decode().replace("'", '"'))
        print(output)
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the request ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))
    return render_template("index.html", output=str(output['Results'][0]) + ' bike rentals')


if __name__ == '__main__':
    app.run(debug=True)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
