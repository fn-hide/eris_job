import pandas as pd

from connection import Connection
from transform import *


class Job:
    def __init__(self, engine):
        self.job_columns = ['JobID', 'JobTitle', 'FunctionPositionName', 'EducationLevelName', 'CityName', 'ProvinceName', 'Description', 'Requirement', 'MajorName']

        # Job
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

        # cleansing
        self.preprocess()

    def preprocess(self):
        self.df_job.set_index(['JobID'], inplace=True)

        self.df_job.fillna('', inplace=True)

        self.df_job.Description = self.df_job.Description.map(clean_text)
        self.df_job.Requirement = self.df_job.Requirement.map(clean_text)
        
        self.df_job.JobTitle = self.df_job.JobTitle.map(remove_insideparentheses).map(remove_standalonesymbols).map(remove_morespace).map(str.lower).map(str.strip)
        self.df_job.FunctionPositionName = self.df_job.FunctionPositionName.map(remove_standalonesymbols).map(remove_parenthesesnumber).map(remove_morespace).map(str.lower).map(str.strip)

        for col in ['EducationLevelName', 'CityName', 'ProvinceName', 'MajorName']:
            self.df_job[col] = self.df_job[col].map(str.lower)
        


if __name__ == '__main__':
    database = Connection('huda', 'Vancha12', '127.0.0.1', 1433, 'HRSystemDB')
    database.connect()

    # print(database.engine.table_names())

    job = Job(database.engine)
    
    print(job.df_job)
    print(job.df_job.columns)

    
    



