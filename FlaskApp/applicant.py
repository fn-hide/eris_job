import pandas as pd

from connection import Connection
from transform import *



class Applicant:
    def __init__(self, engine):
        self.applicant_columns = ['ApplicantID', 'Age', 'Strengthness', 'Weaknesses', 'CityName', 'ProvinceName']
        self.applicant_education_columns = ['Industry', 'JobDescription', 'Position', 'YearsOfExperience']
        self.applicant_education_columns = ['EducationLevelName', 'MajorName']

        # Applicant
        self.df_applicant = pd.DataFrame(engine.execute(
            """
            SELECT Applicant.ApplicantID, Applicant.Dob, Applicant.Strengthness, Applicant.Weaknesses, City.Name AS CityName, Province.Name AS ProvinceName
            FROM (((Applicant
            LEFT JOIN Pipeline ON Applicant.ApplicantID = Pipeline.ApplicantID)
            RIGHT JOIN City ON Applicant.CurrentAddressCityID = City.CityID)
            RIGHT JOIN Province ON Applicant.CurrentAddressProvinceID = Province.ProvinceID)
            WHERE StageID=9
            """
        ))

        # Applicant Education
        self.df_applicant_education = pd.DataFrame(engine.execute(
            """
            SELECT ApplicantEducation.ApplicantID, ApplicantEducation.DateStart, ApplicantEducation.DateEnd, EducationLevel.EducationLevelName, Major.MajorName
            FROM (((ApplicantEducation
            LEFT JOIN Pipeline ON ApplicantEducation.ApplicantID = Pipeline.ApplicantID)
            RIGHT JOIN EducationLevel ON ApplicantEducation.EducationLevelID = EducationLevel.EducationLevelID)
            RIGHT JOIN Major ON ApplicantEducation.MajorID = Major.MajorID)
            WHERE StageID=9
            """
        ))

        # Applicant Experience
        self.df_applicant_experience = pd.DataFrame(engine.execute(
            """
            SELECT ApplicantExperience.ApplicantID, ApplicantExperience.DateFrom, ApplicantExperience.DateTo, ApplicantExperience.Industry, ApplicantExperience.JobDescription, ApplicantExperience.Position
            FROM ApplicantExperience
            LEFT JOIN Pipeline ON ApplicantExperience.ApplicantID = Pipeline.ApplicantID
            WHERE StageID=9
            """
        ))

        self.df_applicant = self.df_applicant.drop_duplicates()

        # fillna
        self.df_applicant.fillna('', inplace=True)
        self.df_applicant_education.fillna('', inplace=True)
        self.df_applicant_experience.fillna('', inplace=True)

        # preprocess
        self.preprocess_applicant()
        self.preprocess_education()
        self.preprocess_experience()
        
        # merge all applicant dataframe
        self.merge_applicant_df()

        # cleansing
        self.preprocess()

        # user ApplicantID as index
        self.df_applicant.set_index(['ApplicantID'], inplace=True)

    def preprocess(self):
        self.df_applicant[self.df_applicant.select_dtypes(object).columns] = self.df_applicant[self.df_applicant.select_dtypes(object).columns].applymap(str.lower)

        for col in ['Strengthness', 'JobDescription', 'Industry', 'Position']:
            self.df_applicant[col] = self.df_applicant[col].map(clean_text)

        self.df_applicant.Age = self.df_applicant.Age.apply(lambda x: 'usia ' + str(x) + ' tahun' if int(x) != 0 else '')
        self.df_applicant.YearsOfExperience = self.df_applicant.YearsOfExperience.apply(lambda x: 'pengalaman ' + str(x) + ' tahun' if int(x) != 0 else '')
        self.df_applicant.EducationLevelName = self.df_applicant.EducationLevelName.apply(lambda x: 'lulusan ' + x.lower())


    def preprocess_applicant(self):
        self.df_applicant['Age'] = pd.to_datetime(
            self.df_applicant.Dob.map(pick_date).apply(lambda x: filter_date(x, 1958, 2006))
        ).map(get_age)

        self.df_applicant.drop(columns=['Dob'], inplace=True)

        self.df_applicant.Age = self.df_applicant.Age.fillna(0).astype(int)
    
    def preprocess_education(self):
        self.df_applicant_education.DateStart = pd.to_datetime(
            self.df_applicant_education.DateStart.map(pick_date).apply(lambda x: filter_date(x, 1980, 2023))
        )

        self.df_applicant_education.DateEnd = pd.to_datetime(
            self.df_applicant_education.DateEnd.map(pick_date).apply(lambda x: filter_date(x, 1980, 2023))
        )

        self.df_applicant_education = self.df_applicant_education[~(self.df_applicant_education.DateStart.isna()) & ~(self.df_applicant_education.DateEnd.isna())]
        self.df_applicant_education = self.df_applicant_education.sort_values('DateStart').groupby(['ApplicantID']).agg('last')

        self.df_applicant_education.drop(columns=['DateStart', 'DateEnd'], inplace=True)
    
    def preprocess_experience(self):
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
            'Industry': ' '.join,
            'JobDescription': ' '.join,
            'Position': ' '.join,
            'YearsOfExperience': 'sum',
        })

        self.df_applicant_experience.drop(columns=['DateFrom', 'DateTo'], inplace=True)

    def merge_applicant_df(self):
        self.df_applicant = pd.merge(self.df_applicant, self.df_applicant_experience, on=['ApplicantID'])
        self.df_applicant = pd.merge(self.df_applicant, self.df_applicant_education, on=['ApplicantID'])

        # remove weaknesses because of negative word will also positive in word
        # TODO: improve in the future version
        self.df_applicant = self.df_applicant.drop(columns=['Weaknesses'])





if __name__ == '__main__':
    database = Connection('huda', 'Vancha12', '127.0.0.1', 1433, 'HRSystemDB')
    database.connect()

    # print(database.engine.table_names())

    applicant = Applicant(database.engine)
    
    # print(applicant.df_applicant.shape)
    # print(applicant.df_applicant_education.shape)
    # print(applicant.df_applicant_experience.shape)
    # print(applicant.df_applicant_education.columns)
    # print(applicant.df_applicant_education.info())
    # print(applicant.df_applicant_education.head())

    # print(applicant.df_applicant_experience)
    # print(applicant.df_applicant_experience.columns)

    print(applicant.df_applicant)
    print(applicant.df_applicant.columns)
    # print(applicant.df_applicant.isna().sum())




