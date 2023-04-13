import numpy as np

from job_model import JobModel



class AppModel:
    def __init__(self, job_model:JobModel, df_applicant):
        self.job = job_model
        self.df_app = df_applicant

        self.app_vector = np.concatenate([
            self.job.get_age(self.df_app.Age.values),
            self.job.get_salary(self.df_app.ExpectedSalary.values),
            self.job.get_city(self.df_app.CityName.values),
            self.job.get_province(self.df_app.ProvinceName.values),
            self.job.get_education(self.df_app.EducationLevelName.values),
            self.job.get_major(self.df_app.MajorName.values),
            self.job.get_license(self.df_app.DriverLicenseType.values),
            self.job.get_glasses(self.df_app.IsUsingGlasses.values),
            self.job.get_gender(self.df_app.Gender.values),
            self.job.get_status(self.df_app.MaritalStatus.values),
            self.job.get_title(self.df_app.Position.values),
            self.job.get_description(self.df_app.DescriptionStrengthness.values)
        ], axis=1)
