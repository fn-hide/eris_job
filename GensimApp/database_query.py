import pandas as pd
from connection import Connection


class DatabaseQuery:
    def __init__(self, engine):
        self.engine = engine

    def get_applicant(self, id):
        return pd.DataFrame(self.engine.execute(
            f"""
            SELECT Applicant.ApplicantID, Applicant.Dob, Applicant.ExpectedSalary AS Salary, City.Name AS CityName, Province.Name AS ProvinceName, Applicant.DriverLicenseType, Applicant.IsUsingGlasses, Applicant.Gender, Applicant.MaritalStatus, Applicant.Strengthness
            FROM ((Applicant
            RIGHT JOIN City ON Applicant.CurrentAddressCityID = City.CityID)
            RIGHT JOIN Province ON Applicant.CurrentAddressProvinceID = Province.ProvinceID)
            WHERE ApplicantID={id}
            """
        ))

    def get_applicant_education(self, id):
        return pd.DataFrame(self.engine.execute(
            f"""
            SELECT ApplicantEducation.ApplicantID, ApplicantEducation.DateStart, ApplicantEducation.DateEnd, EducationLevel.EducationLevelName, Major.MajorName
            FROM ((ApplicantEducation
            RIGHT JOIN EducationLevel ON ApplicantEducation.EducationLevelID = EducationLevel.EducationLevelID)
            RIGHT JOIN Major ON ApplicantEducation.MajorID = Major.MajorID)
            WHERE ApplicantID={id}
            """
        ))
    
    def get_applicant_experience(self, id):
        return pd.DataFrame(self.engine.execute(
            f"""
            SELECT ApplicantExperience.ApplicantID, ApplicantExperience.DateFrom, ApplicantExperience.DateTo, ApplicantExperience.JobDescription, ApplicantExperience.Position
            FROM ApplicantExperience
            WHERE ApplicantID={id}
            """
        ))

    def get_job(self):
        return pd.DataFrame(self.engine.execute(
            """
            SELECT Job.JobID, Job.UsiaMax AS Age, Job.SalaryMin, Job.SalaryMax, City.Name AS CityName, Province.Name AS ProvinceName, EducationLevel.EducationLevelName, Major.MajorName, Job.DriverLicenseType, Job.UsingGlasses, Job.Gender, Job.MaritalStatus, Job.JobTitle, Job.Description, Job.Requirement
            FROM ((((Job
            RIGHT JOIN EducationLevel ON Job.EducationLevelID = EducationLevel.EducationLevelID)
            RIGHT JOIN City ON Job.CityID = City.CityID)
            RIGHT JOIN Province ON Job.ProvinceID = Province.ProvinceID)
            RIGHT JOIN Major ON Job.MajorID = Major.MajorID)
            WHERE JobStatus='Publish'
            """
        ))
    
    def get_city(self):
        return pd.DataFrame(self.engine.execute(
            """
            SELECT CityID, Name AS CityName
            FROM City
            """
        ))

    def get_province(self):
        return pd.DataFrame(self.engine.execute(
            """
            SELECT ProvinceID, Name AS ProvinceName
            FROM Province
            """
        ))

    def get_education(self):
        return pd.DataFrame(self.engine.execute(
            """
            SELECT EducationLevelID, EducationLevelName
            FROM EducationLevel
            """
        ))
    
    def get_major(self):
        return pd.DataFrame(self.engine.execute(
            """
            SELECT MajorID, MajorName
            FROM Major
            """
        ))
