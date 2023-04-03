from flask import Flask, jsonify, request
import pandas as pd



app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    req_json = request.json
    name = req_json['name']

    return jsonify(
        {'recommendation': 'Hi ' + name}
    )
    

if __name__ == '__main__':
    app.run(host='192.168.168.18', port=5000)
