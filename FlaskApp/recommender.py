import pandas as pd

from transform import *

from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

from nltk import download
from nltk.corpus import stopwords

from re import sub

from connection import Connection
from jobs import Job
from applicants import Applicants

from applicant import Applicant

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity





class Recommender:
    def __init__(self, job, applicant, translate=False):
        self.job = job
        self.applicant = applicant
        self.translate = translate

        self.job_train = self.job.job_train

    def fit(self):
        if self.translate:
            self.job.translate_id()

        self.tfidf_encoder = TfidfVectorizer()
        self.tfidf_encoder = CountVectorizer()
        self.job_bank = self.tfidf_encoder.fit_transform(self.job_train.Text)
    
    def predict(self, applicant):
        text = applicant.applicant_train.loc[applicant.applicant_id].values[0]
        code = self.tfidf_encoder.transform([text])

        dist = cosine_similarity(code, self.job_bank)[0]

        self.job.df_job['Similarity'] = dist*100

        similarity = self.job.df_job.Similarity.max()

        return int(self.job.df_job[self.job.df_job.Similarity == similarity].index[0]), round(similarity, 2)
    


    '''optional'''
    def translate_by_words(self):
        # self.job.df_job[col] = self.job.df_job[col].apply(lambda x: ' '.join([translator.translate(i, dest='id').text for i in x.split(' ')])).map(str.lower)
        pass
    '''optional'''
    def download_stopwords(self):
        # download nltk stopwords
        download('stopwords')

        # stopwords
        sastrawi_stopwords = StopWordRemoverFactory().get_stop_words()
        nltk_stopwords =  stopwords.words('indonesian')
        custom_stopwords = ['perusahaan', 'sesuai', 'become', 'becoming', 'gunawangsa', 'hotel', 'merr', 'yg', 'mnrt', '']
        
        self.stopwords = list(set(
            sastrawi_stopwords + nltk_stopwords + custom_stopwords
        ))



if __name__ == '__main__':
    import pickle


    # connect to database
    database = Connection('huda', 'Vancha12', '127.0.0.1', 1433, 'HRSystemDB')
    database.connect()

    re_train = False
    applicant_id = 31379

    if re_train:
        job = Job(database.engine)
        applicant = Applicant(database.engine, applicant_id)

        recommender = Recommender(job, applicant, translate=True)
        recommender.fit()
    else:
        applicant = Applicant(database.engine, applicant_id)
        recommender = pickle.load(open('data/model.pkl', 'rb'))

    # [33513, 31861, 31891, 31790, 31797, 31698, 31700, 31604, 31379, 29821, 35778, 35187, 33631, 38226, 27292, 29243, 39827, 31567, 30254, 31968]
    
    print(recommender.predict(applicant))




