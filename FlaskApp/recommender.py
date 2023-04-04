import pandas as pd

from transform import *

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

from re import sub

from connection import Connection
from job import Job
from applicant import Applicant

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity




class Recommender:
    def __init__(self, job, applicant):
        self.job = job
        self.applicant = applicant

        self.job_train = pd.DataFrame([], index=self.job.df_job.index)
        self.job_train['Text'] = self.create_traindata(self.job.df_job)

        self.applicant_train = pd.DataFrame([], index=self.applicant.df_applicant.index)
        self.applicant_train['Text'] = self.create_traindata(self.applicant.df_applicant)

        # stopwords
        sastrawi_stopwords = StopWordRemoverFactory().get_stop_words()
        nltk_stopwords =  stopwords.words('indonesian') + stopwords.words('english')
        custom_stopwords = ['perusahaan', 'sesuai', 'become', 'becoming', 'gunawangsa', 'hotel', 'merr', 'yg']
        self.stopwords = list(set(
            sastrawi_stopwords + nltk_stopwords + custom_stopwords
        ))

        # remove stopwords
        self.preprocess_train()

        self.tfidf_encoder = TfidfVectorizer()
        self.job_bank = self.tfidf_encoder.fit_transform(self.job_train.Text)

        pd.DataFrame(self.tfidf_encoder.get_feature_names_out()).to_csv('data/job_feature.csv')

    def preprocess_train(self):
        self.applicant_train.Text = self.applicant_train.Text.apply(lambda x: sub('\s+', '   ', '   ' + x + '   ')).apply(lambda x: sub('(' + ' | '.join(self.stopwords) + ')', ' ', x)).map(remove_morespace).map(str.strip)
        self.job_train.Text = self.job_train.Text.apply(lambda x: sub('\s+', '   ', '   ' + x + '   ')).apply(lambda x: sub('(' + ' | '.join(self.stopwords) + ')', ' ', x)).map(remove_morespace).map(str.strip)

    def create_traindata(self, df: pd.DataFrame):
        new_series = []
        for row in df.values:
            new_series.append(' '.join(row))
        return new_series
    
    def predict(self, applicant_id):
        text = self.applicant_train.loc[applicant_id].values[0]
        code = self.tfidf_encoder.transform([text])

        dist = cosine_similarity(code, self.job_bank)[0]

        self.job.df_job['Similarity'] = dist*100

        similarity = self.job.df_job.Similarity.max()

        return self.job.df_job[self.job.df_job.Similarity == similarity].index[0], similarity



if __name__ == '__main__':
    database = Connection('huda', 'Vancha12', '127.0.0.1', 1433, 'HRSystemDB')
    database.connect()

    job = Job(database.engine)
    applicant = Applicant(database.engine)

    # print(job.df_job)
    # print(job.df_job.columns)

    # print(applicant.df_applicant)
    # print(applicant.df_applicant.columns)

    recommender = Recommender(job, applicant)

    # print(recommender.job_train)
    # print(recommender.applicant_train)

    # print(recommender.job_bank.todense())

    # [33513, 31861, 31891, 31790, 31797, 31698, 31700, 31604, 31379, 29821, 35778, 35187, 33631, 38226, 27292, 29243, 39827, 31567, 30254, 31968]
    # print(applicant.df_applicant.index)

    print(recommender.predict(33513))




