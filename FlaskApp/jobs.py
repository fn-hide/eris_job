import pandas as pd

from connection import Connection
from transform import *

from googletrans import Translator

from re import sub


class Job:
    def __init__(self, engine):
        # columns view
        self.job_columns = ['JobID', 'JobTitle', 'FunctionPositionName', 'EducationLevelName', 'CityName', 'ProvinceName', 'Description', 'Requirement', 'MajorName']

        self.df_job = pd.DataFrame(engine.execute(
            """
            SELECT Job.JobID, Job.JobTitle, FunctionPosition.FunctionPositionName, EducationLevel.EducationLevelName, City.Name AS CityName, Province.Name AS ProvinceName, Major.MajorName, Job.Description, Job.Requirement
            FROM (((((Job
            RIGHT JOIN FunctionPosition ON Job.FunctionPositionID = FunctionPosition.FunctionPositionID)
            RIGHT JOIN EducationLevel ON Job.EducationLevelID = EducationLevel.EducationLevelID)
            RIGHT JOIN City ON Job.CityID = City.CityID)
            RIGHT JOIN Province ON Job.ProvinceID = Province.ProvinceID)
            RIGHT JOIN Major ON Job.MajorID = Major.MajorID)
            WHERE JobStatus='Publish'
            """
        ))

        self.preprocess()

    def preprocess(self):
        self.cleansing()
        self.create_traindata()
        self.remove_stopwords()

    def cleansing(self):
        self.df_job.set_index(['JobID'], inplace=True)

        self.df_job.fillna('', inplace=True)

        self.df_job.Description = self.df_job.Description.map(clean_text)
        self.df_job.Requirement = self.df_job.Requirement.map(clean_text)
        
        self.df_job.JobTitle = self.df_job.JobTitle.map(remove_insideparentheses).map(remove_standalonesymbols).map(remove_morespace).map(str.lower).map(str.strip)
        self.df_job.FunctionPositionName = self.df_job.FunctionPositionName.map(remove_standalonesymbols).map(remove_parenthesesnumber).map(remove_morespace).map(str.lower).map(str.strip)

        for col in ['EducationLevelName', 'CityName', 'ProvinceName', 'MajorName']:
            self.df_job[col] = self.df_job[col].map(str.lower)

    def translate_id(self):
        translator = Translator(service_urls=['translate.googleapis.com'])

        print('Translating job ...')

        for col in self.df_job.columns:
            self.df_job[col] = self.df_job[col].apply(lambda x: translator.translate(x, dest='id').text.lower())

    def create_traindata(self):
        self.job_train = pd.DataFrame([], index=self.df_job.index)

        new_series = []
        for row in self.df_job.values:
            new_series.append(' '.join(row))

        self.job_train['Text'] = new_series
    
    def remove_stopwords(self):
        self.stopwords = [i[0] for i in pd.read_csv('data/stopwords.csv', header=None, names=['words'], na_filter=False).values]

        self.job_train.Text = self.job_train.Text.apply(lambda x: sub('\s+', '   ', '   ' + x + '   ')).apply(lambda x: sub('(' + ' | '.join(self.stopwords) + ')', ' ', x)).map(remove_morespace).map(str.strip)




if __name__ == '__main__':
    database = Connection('huda', 'Vancha12', '127.0.0.1', 1433, 'HRSystemDB')
    database.connect()

    # print(database.engine.table_names())

    job = Job(database.engine)
    
    print(job.df_job)
    print(job.df_job.columns)

    
    



