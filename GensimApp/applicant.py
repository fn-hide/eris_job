import pandas as pd

from connection import Connection
from database_query import DatabaseQuery

from transform import *



class Applicant:
    applicant_columns = ['ApplicantID', 'Age', 'Strengthness', 'Weaknesses', 'CityName', 'ProvinceName']
    applicant_experience_columns = ['Industry', 'JobDescription', 'Position', 'YearsOfExperience']
    applicant_education_columns = ['EducationLevelName', 'MajorName']

    def __init__(self, engine, applicant_id):
        self.database = DatabaseQuery(engine)

        self.applicant_id = applicant_id

        # Applicant
        self.df_applicant = self.database.get_applicant(self.applicant_id)
        self.df_applicant_education = self.database.get_applicant_education(self.applicant_id)
        self.df_applicant_experience = self.database.get_applicant_experience(self.applicant_id)

        # preprocessing
        self.preprocessing()
        
    
    def preprocessing(self):
        # fillna
        self.df_applicant.fillna('', inplace=True)
        self.df_applicant_education.fillna('', inplace=True)
        self.df_applicant_experience.fillna('', inplace=True)

        # rename
        self.df_applicant.rename(columns={
            'ExpectedSalary': 'Salary',
            'IsUsingGlasses': 'UsingGlasses',
        }, inplace=True)
        self.df_applicant_experience.rename(columns={
            'JobDescription': 'Description', 'Position': 'JobTitle'
        }, inplace=True)

        # preprocessing each dataframe
        self.applicant()
        self.education()
        self.experience()
        
        # merge all dataframe
        self.merge_applicant_df()

        # menggabungkan kolom Strengthness ke dalam kolom Description
        self.df_applicant.Description = self.df_applicant.Description.str.cat(self.df_applicant.Strengthness, sep=' ')
        self.df_applicant.drop(columns=['Strengthness'], inplace=True)

        # preprocessing merged dataframe
        self.df_applicant.set_index(['ApplicantID'], inplace=True)
        self.df_applicant[self.df_applicant.select_dtypes(object).columns] = self.df_applicant[self.df_applicant.select_dtypes(object).columns].applymap(str.lower)
        self.df_applicant.JobTitle = self.df_applicant.JobTitle.map(remove_html)
        self.df_applicant.Description = self.df_applicant.Description.map(remove_html)

    def applicant(self):
        '''numeric'''
        # Age
        self.df_applicant['Age'] = pd.to_datetime(
            self.df_applicant.Dob.map(pick_date).apply(lambda x: filter_date(x, 1958, 2006))
        ).map(get_age)
        self.df_applicant.drop(columns=['Dob'], inplace=True)
        self.df_applicant.Age = self.df_applicant.Age.fillna(0).astype(int)
        # Salary
        self.df_applicant.Salary = self.df_applicant.Salary.apply(lambda x: 0 if x < 1_000_000 else x)
        self.df_applicant.Salary = self.df_applicant.Salary.astype(int)

        '''categoric'''
        # UsingGlasses
        self.df_applicant.UsingGlasses = self.df_applicant.UsingGlasses.astype(str).map(str.lower)
        if self.df_applicant.UsingGlasses.values == 'true':
            self.df_applicant.UsingGlasses = 1
        elif self.df_applicant.UsingGlasses.values == 'false':
            self.df_applicant.UsingGlasses = 0
        else:
            self.df_applicant.UsingGlasses = -1

    def education(self):
        self.df_applicant_education.DateStart = pd.to_datetime(
            self.df_applicant_education.DateStart.map(pick_date).apply(lambda x: filter_date(x, 1980, 2023))
        )

        self.df_applicant_education.DateEnd = pd.to_datetime(
            self.df_applicant_education.DateEnd.map(pick_date).apply(lambda x: filter_date(x, 1980, 2023))
        )

        self.df_applicant_education = self.df_applicant_education[~(self.df_applicant_education.DateStart.isna()) & ~(self.df_applicant_education.DateEnd.isna())]
        self.df_applicant_education = self.df_applicant_education.sort_values('DateStart').groupby(['ApplicantID']).agg('last')

        self.df_applicant_education.drop(columns=['DateStart', 'DateEnd'], inplace=True)

    def experience(self):
        self.df_applicant_experience.DateFrom = pd.to_datetime(
            self.df_applicant_experience.DateFrom.map(pick_date).apply(lambda x: filter_date(x, 1980, 2023))
        )

        self.df_applicant_experience.DateTo = pd.to_datetime(
            self.df_applicant_experience.DateTo.map(pick_date).apply(lambda x: filter_date(x, 1980, 2023))
        )

        self.df_applicant_experience = self.df_applicant_experience[~(self.df_applicant_experience.DateFrom.isna()) & ~(self.df_applicant_experience.DateTo.isna())]

        # add YearsOfExperience column
        self.df_applicant_experience['YearsOfExperience'] = substract_months(
            self.df_applicant_experience.DateFrom, self.df_applicant_experience.DateTo
        )

        self.df_applicant_experience = self.df_applicant_experience.sort_values('DateFrom').groupby(['ApplicantID']).agg({
            'DateFrom': 'last',
            'DateTo': 'last',
            'Description': ' '.join,
            'JobTitle': ' '.join,
            'YearsOfExperience': 'sum',
        })

        self.df_applicant_experience.drop(columns=['DateFrom', 'DateTo', 'YearsOfExperience'], inplace=True)

    def merge_applicant_df(self):
        self.df_applicant = pd.merge(self.df_applicant, self.df_applicant_experience, on=['ApplicantID'])
        self.df_applicant = pd.merge(self.df_applicant, self.df_applicant_education, on=['ApplicantID'])


if __name__ == '__main__':
    database = Connection('huda', 'Vancha12', '127.0.0.1', 1433, 'HRSystemDB')
    database.connect()

    applicant_id = 33513
    applicant = Applicant(database.engine, applicant_id)

    for col,val in zip(applicant.df_applicant.columns, applicant.df_applicant.values[0]):
        print(str(col).rjust(25), '❌', str(val).ljust(25))




