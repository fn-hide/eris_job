import pandas as pd

from connection import Connection
from transform import *

from googletrans import Translator

from re import sub


class Job:
    def __init__(self, engine):
        self.columns_used = {}

        self.df_job = pd.DataFrame(engine.execute(
            """
            SELECT Job.JobID, Job.UsiaMax, Job.SalaryMin, Job.SalaryMax, City.Name AS CityName, Province.Name AS ProvinceName, EducationLevel.EducationLevelName, Major.MajorName, Job.DriverLicenseType, Job.UsingGlasses, Job.Gender, Job.MaritalStatus, Job.JobTitle, Job.Description, Job.Requirement
            FROM ((((Job
            RIGHT JOIN EducationLevel ON Job.EducationLevelID = EducationLevel.EducationLevelID)
            RIGHT JOIN City ON Job.CityID = City.CityID)
            RIGHT JOIN Province ON Job.ProvinceID = Province.ProvinceID)
            RIGHT JOIN Major ON Job.MajorID = Major.MajorID)
            WHERE JobStatus='Publish'
            """
        ))
        self.df_job.set_index(['JobID'], inplace=True)
        self.df_job.fillna('', inplace=True)

        for col in ['EducationLevelName', 'CityName', 'ProvinceName', 'MajorName']:
            self.df_job[col] = self.df_job[col].map(str.lower)

        self.df_job.replace('none', '', inplace=True)

        self.pre_processing()

    
    def pre_processing(self):
        # numerical
        self.preprocess_usia_max()
        self.preprocess_salary_mean()
        # categorical
        self.preprocess_driver_license_type()
        self.preprocess_gender()
        self.preprocess_marital_status()
        self.preprocess_using_glasses()
        # textual
        self.preprocess_job_title()
        self.preprocess_description()
        self.preprocess_requirement()
        
    def preprocess_salary_mean(self):
        # SalaryMin
        self.df_job.SalaryMin = self.df_job.SalaryMin.apply(lambda x: x if x >= 1_000_000 else 0)
        self.df_job.SalaryMin = self.df_job.SalaryMin.astype(int)
        
        # SalaryMax
        self.df_job.SalaryMax = self.df_job.SalaryMax.apply(lambda x: x if x >= 1_000_000 else 0)
        self.df_job.SalaryMax = self.df_job.SalaryMax.astype(int)

        # SalaryMean
        self.df_job.SalaryMin = (self.df_job.SalaryMax + self.df_job.SalaryMin) // 2
        self.df_job.rename(columns={'SalaryMin': 'SalaryMean'}, inplace=True)
        self.df_job.SalaryMean = self.df_job.SalaryMean.apply(lambda x: 0 if x < 1_000_000 else x)
        self.df_job.drop(columns=['SalaryMax'], inplace=True)
    
    def preprocess_driver_license_type(self):
        # DriverLicenseType
        self.df_job.DriverLicenseType = self.df_job.DriverLicenseType.map(str.lower)

    def preprocess_using_glasses(self):
        # UsingGlasses
        self.df_job.UsingGlasses = self.df_job.UsingGlasses.astype(str).map(str.lower)

    def preprocess_gender(self):
        # Gender
        self.df_job.Gender = self.df_job.Gender.astype(str).map(str.lower)

    def preprocess_marital_status(self):
        # MaritalStatus
        self.df_job.MaritalStatus = self.df_job.MaritalStatus.astype(str).map(str.lower)

    def preprocess_job_title(self):
        # JobTitle
        self.df_job.JobTitle = self.df_job.JobTitle.map(
            remove_parenthesesnumber
        ).map(
            remove_standalonesymbols
        ).map(
            remove_morespace
        ).map(
            str.strip
        ).apply(
            lambda x: ' '.join(list(set(x.split())))
        )

    def preprocess_description(self):
        # Description
        self.df_job.Description = self.df_job.Description.map(
            clean_text
        )

    def preprocess_requirement(self):
        # Requirement
        self.df_job.Requirement = self.df_job.Requirement.map(
            clean_text
        )
    
    def preprocess_usia_max(self):
        # UsiaMax
        self.df_job.UsiaMax = self.df_job.UsiaMax.replace('', 0)
        self.df_job.UsiaMax = self.df_job.UsiaMax.astype(int)

    def translate_id(self):
        translator = Translator(service_urls=['translate.googleapis.com'])

        print('Translating job ...')

        for col in self.df_job.columns:
            self.df_job[col] = self.df_job[col].apply(lambda x: translator.translate(x, dest='id').text.lower())
    
    def get_JobID(self):
        return self.df_job.index
    
    def get_columns_used(self):
        """
        membuat dictionary yang berisi list kolom yang digunakan (tidak Null)
        """
        for index in self.df_job.index:
            used_cols = []
            for col in self.df_job.columns:
                value = self.df_job[col].loc[index]
                if value != '' and value != 0:
                    used_cols.append(col)
            
            self.columns_used[index] = used_cols


if __name__ == '__main__':
    database = Connection('huda', 'Vancha12', '127.0.0.1', 1433, 'HRSystemDB')
    database.connect()

    job = Job(database.engine)

    job.get_columns_used()

    for key, value in job.columns_used.items():
        print(f'{key} > {value}')
    

    
    



