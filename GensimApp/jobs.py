import pandas as pd

from connection import Connection
from database_query import DatabaseQuery

from transform import *



class Job:
    def __init__(self, engine):
        self.database = DatabaseQuery(engine)
        self.df_job = self.database.get_job()

        self.columns_used = {}

        self.preprocessing()
        self.get_columns_used()

    def preprocessing(self):
        self.df_job.set_index(['JobID'], inplace=True)
        self.df_job.fillna('', inplace=True)
        self.df_job.replace('none', '', inplace=True)
        self.df_job.replace('None', '', inplace=True)

        # menggabungkan kolom Requirement ke dalam Description
        self.df_job.Description = self.df_job.Description.str.cat(self.df_job.Requirement, sep=' ')
        self.df_job.drop(columns=['Requirement'], inplace=True)

        # preprocessing every column
        self.age()
        self.salary()
        self.city()
        self.province()
        self.education()
        self.major()
        self.license()
        self.glasses()
        self.gender()
        self.status()
        self.title()
        self.description()

    '''numeric'''
    def age(self):
        # Age
        self.df_job.Age = self.df_job.Age.replace('', 0)
        self.df_job.Age = self.df_job.Age.astype(int)

    def salary(self):
        # SalaryMin
        self.df_job.SalaryMin = self.df_job.SalaryMin.apply(lambda x: x if x >= 1_000_000 else 0)
        self.df_job.SalaryMin = self.df_job.SalaryMin.astype(int)
        
        # SalaryMax
        self.df_job.SalaryMax = self.df_job.SalaryMax.apply(lambda x: x if x >= 1_000_000 else 0)
        self.df_job.SalaryMax = self.df_job.SalaryMax.astype(int)

        # Salary
        self.df_job.SalaryMin = (self.df_job.SalaryMax + self.df_job.SalaryMin) // 2
        self.df_job.rename(columns={'SalaryMin': 'Salary'}, inplace=True)
        self.df_job.Salary = self.df_job.Salary.apply(lambda x: 0 if x < 1_000_000 else x)
        self.df_job.drop(columns=['SalaryMax'], inplace=True)
    
    '''categoric'''
    def city(self):
        # CityName
        self.df_job.CityName = self.df_job.CityName.map(str.lower)
    
    def province(self):
        # ProvinceName
        self.df_job.ProvinceName = self.df_job.ProvinceName.map(str.lower)

    def education(self):
        # EducationLevelName
        self.df_job.EducationLevelName = self.df_job.EducationLevelName.map(str.lower)

    def major(self):
        # MajorName
        self.df_job.MajorName = self.df_job.MajorName.map(str.lower)

    def license(self):
        # DriverLicenseType
        self.df_job.DriverLicenseType = self.df_job.DriverLicenseType.map(str.lower)

    def glasses(self):
        # UsingGlasses
        self.df_job.UsingGlasses = self.df_job.UsingGlasses.astype(str).map(str.lower)

        if self.df_job.UsingGlasses.values[0] == 'true':
            self.df_job.UsingGlasses = 1
        elif self.df_job.UsingGlasses.values[0] == 'false':
            self.df_job.UsingGlasses = 0
        else:
            self.df_job.UsingGlasses = -1

    def gender(self):
        # Gender
        self.df_job.Gender = self.df_job.Gender.astype(str).map(str.lower)

    def status(self):
        # MaritalStatus
        self.df_job.MaritalStatus = self.df_job.MaritalStatus.astype(str).map(str.lower)

    '''text'''
    def title(self):
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
        ).map(str.lower)

    def description(self):
        # Description
        self.df_job.Description = self.df_job.Description.map(remove_html).map(str.lower)

    def get_JobID(self):
        return self.df_job.index
    
    def get_columns_used(self):
        """
        membuat dictionary yang berisi list kolom yang digunakan (not None)
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


    

    
    



