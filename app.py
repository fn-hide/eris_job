from flask import Flask, jsonify, request



app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    req_json = request.json
    name = req_json['name']

    return jsonify(
        {'recommendation': 'Hi ' + name}
    )

@app.route('/test/', methods=['GET'])
def test():
    return 'Hai'
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
