import pickle, os

from flask import Flask, jsonify, request

from connection import Connection
from jobs import Job
from applicant import Applicant
from recommender import Recommender



app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    req_json = request.json
    applicant_id = req_json['ApplicantID']

    re_train = True

    database = Connection('huda', 'Vancha12', '127.0.0.1', 1433, 'HRSystemDB')
    database.connect()

    if re_train:
        job = Job(database.engine)
        applicant = Applicant(database.engine, applicant_id)

        recommender = Recommender(job, applicant)
        recommender.fit(translate=False)

        pickle.dump(recommender, open('data/model.pkl', 'wb'))
    else:
        applicant = Applicant(database.engine, applicant_id)
        recommender = pickle.load(open('data/model.pkl', 'rb'))
        recommender.fit(False)

    job_id, similarity = recommender.predict(applicant_id)

    return jsonify(
        {
            'JobID': job_id,
            'Similarity': similarity
        }
    )
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

    # TODO: buat applicant selalu di translate

    # TODO: improve translate
    # TODO: cleansing stopwords



