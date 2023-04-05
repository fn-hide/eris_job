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

from googletrans import Translator



class Recommender:
    def __init__(self, job, applicant, translate=False):
        self.job = job
        self.applicant = applicant

        # translate to indonesia
        if translate:
            self.translate()

        self.job_train = pd.DataFrame([], index=self.job.df_job.index)
        self.job_train['Text'] = self.create_traindata(self.job.df_job)

        self.applicant_train = pd.DataFrame([], index=self.applicant.df_applicant.index)
        self.applicant_train['Text'] = self.create_traindata(self.applicant.df_applicant)

        # download nltk stopwords
        download('stopwords')

        # stopwords
        sastrawi_stopwords = StopWordRemoverFactory().get_stop_words()
        nltk_stopwords =  stopwords.words('indonesian')
        custom_stopwords = ['perusahaan', 'sesuai', 'become', 'becoming', 'gunawangsa', 'hotel', 'merr', 'yg', 'mnrt', '']
        
        self.stopwords = list(set(
            sastrawi_stopwords + nltk_stopwords + custom_stopwords
        ))

        # remove stopwords
        self.preprocess_train()

        # create job_bank
        self.fit()

        pd.DataFrame(self.tfidf_encoder.get_feature_names_out()).to_csv('data/job_feature.csv')
    
    def translate(self):
        translator = Translator(service_urls=['translate.googleapis.com'])
        
        for col in self.job.df_job.columns:
            self.job.df_job[col] = self.job.df_job[col].apply(lambda x: translator.translate(x, dest='id').text.lower())
            # # translate by word
            # self.job.df_job[col] = self.job.df_job[col].apply(lambda x: ' '.join([translator.translate(i, dest='id').text for i in x.split(' ')])).map(str.lower)

        for col in self.applicant.df_applicant.columns:
            self.applicant.df_applicant[col] = self.applicant.df_applicant[col].apply(lambda x: translator.translate(x, dest='id').text.lower())

    def preprocess_train(self):
        self.applicant_train.Text = self.applicant_train.Text.apply(lambda x: sub('\s+', '   ', '   ' + x + '   ')).apply(lambda x: sub('(' + ' | '.join(self.stopwords) + ')', ' ', x)).map(remove_morespace).map(str.strip)
        self.job_train.Text = self.job_train.Text.apply(lambda x: sub('\s+', '   ', '   ' + x + '   ')).apply(lambda x: sub('(' + ' | '.join(self.stopwords) + ')', ' ', x)).map(remove_morespace).map(str.strip)

    def create_traindata(self, df: pd.DataFrame):

        # df.JobTitle = df.JobTitle.str.cat(
        #     df.FunctionPositionName.str.cat(
        #         df.MajorName
        #     , sep=' ')
        # , sep=' ').apply(lambda x: ' '.join(set(x.split(' '))))

        # df.drop(columns=['FunctionPositionName', 'MajorName'], inplace=True)

        new_series = []
        for row in df.values:
            new_series.append(' '.join(row))
        return new_series
    
    def fit(self):
        self.tfidf_encoder = TfidfVectorizer()
        self.job_bank = self.tfidf_encoder.fit_transform(self.job_train.Text)
    
    def predict(self, applicant_id):
        text = self.applicant_train.loc[applicant_id].values[0]
        code = self.tfidf_encoder.transform([text])

        dist = cosine_similarity(code, self.job_bank)[0]

        self.job.df_job['Similarity'] = dist*100

        similarity = self.job.df_job.Similarity.max()

        return self.job.df_job[self.job.df_job.Similarity == similarity].index[0], similarity



if __name__ == '__main__':
    import time
    start_time = time.time()



    database = Connection('huda', 'Vancha12', '127.0.0.1', 1433, 'HRSystemDB')
    database.connect()

    print('Connection time(s):', (time.time() - start_time))
    start_time = time.time()

    job = Job(database.engine)

    print('Job time(s):', (time.time() - start_time))
    start_time = time.time()

    applicant = Applicant(database.engine, 33513)

    print('Applicant time(s):', (time.time() - start_time))
    start_time = time.time()

    # print(job.df_job)
    # print(job.df_job.columns)

    # print(applicant.df_applicant)
    # print(applicant.df_applicant.columns)

    recommender = Recommender(job, applicant, translate=True)

    # print(recommender.job_train)
    # print(recommender.applicant_train)

    # print(recommender.job_bank.todense())

    # [33513, 31861, 31891, 31790, 31797, 31698, 31700, 31604, 31379, 29821, 35778, 35187, 33631, 38226, 27292, 29243, 39827, 31567, 30254, 31968]
    # print(applicant.df_applicant.index)

    print(recommender.predict(33513))

    print('Running time(s):', (time.time() - start_time))




