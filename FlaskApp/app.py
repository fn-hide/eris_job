from flask import Flask, jsonify, request

from connection import Connection
from job import Job
from applicant import Applicant
from recommender import Recommender



app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    req_json = request.json
    applicant_id = req_json['ApplicantID']

    database = Connection('huda', 'Vancha12', '127.0.0.1', 1433, 'HRSystemDB')
    database.connect()

    job = Job(database.engine)
    applicant = Applicant(database.engine)
    recommender = Recommender(job, applicant)

    job_id, similarity = recommender.predict(applicant_id)

    job_id, similarity = int(job_id), int(similarity)

    return jsonify(
        {
            'JobID': job_id,
            'Similarity': similarity
        }
    )
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
