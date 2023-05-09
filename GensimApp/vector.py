import numpy as np
import pandas as pd
import tensorflow as tf

from connection import Connection
from transform import *

from database_query import DatabaseQuery
from jobs import Job
from applicant import Applicant


class Vector:
    def __init__(self, engine):
        self.database = DatabaseQuery(engine)

        self.job = Job(engine)
        self.applicant = Applicant(engine, 33513)
        self.applicant.df_applicant = self.applicant.df_applicant[self.job.df_job.columns]
        
        self.function_mapping = {
            'Age': (self.get_age, self.job.df_job.Age),
            'Salary': (self.get_salary, self.job.df_job.Salary),
            'CityName': (self.get_city, self.job.df_job.CityName),
            'ProvinceName': (self.get_province, self.job.df_job.ProvinceName),
            'EducationLevelName': (self.get_education, self.job.df_job.EducationLevelName),
            'MajorName': (self.get_major, self.job.df_job.MajorName),
            'DriverLicenseType': (self.get_license, self.job.df_job.DriverLicenseType),
            'UsingGlasses': (self.get_glasses, self.job.df_job.UsingGlasses),
            'Gender': (self.get_gender, self.job.df_job.Gender),
            'MaritalStatus': (self.get_status, self.job.df_job.MaritalStatus),
            'JobTitle': (self.get_title, self.job.df_job.JobTitle),
            'Description': (self.get_description, self.job.df_job.Description),
        }

        self.df_city = self.database.get_city()
        self.df_province = self.database.get_province()
        self.df_education = self.database.get_education()
        self.df_major = self.database.get_major()

        # instantiation
        self.max_tokens = 10_000

        '''numerical'''
        # adapt from Age in Job Table
        self.age_normalizer = tf.keras.layers.Normalization(axis=None)
        self.age_normalizer.adapt(self.job.df_job.Age)

        # adapt from Salary in Job Table
        self.salary_normalizer = tf.keras.layers.Normalization(axis=None)
        self.salary_normalizer.adapt(self.job.df_job.Salary)

        '''categorical'''
        # adapt from Job Table
        self.city_encoder = tf.keras.layers.StringLookup(output_mode='multi_hot', vocabulary=self.df_city.CityName.values)
        self.province_encoder = tf.keras.layers.StringLookup(output_mode='multi_hot', vocabulary=self.df_province.ProvinceName.values)
        self.education_encoder = tf.keras.layers.StringLookup(output_mode='multi_hot', vocabulary=self.df_education.EducationLevelName.values)
        self.major_encoder = tf.keras.layers.StringLookup(output_mode='multi_hot', vocabulary=self.df_major.MajorName.values)

        self.license_encoder = tf.keras.layers.StringLookup(output_mode='multi_hot', vocabulary=['a', 'c', 'd', 'b1', 'b2'])
        self.glasses_encoder = tf.keras.layers.StringLookup(output_mode='multi_hot', vocabulary=['true', 'false'])
        self.gender_encoder = tf.keras.layers.StringLookup(output_mode='multi_hot', vocabulary=['male', 'female'])
        self.status_encoder = tf.keras.layers.StringLookup(output_mode='multi_hot', vocabulary=['single', 'married', 'divorced', 'widowed'])

        '''textual'''
        # ditangani oleh doc2vec model

        self.job_vector_list = []
    
    '''helper function'''
    def get_vector(self, features_vector: list):
        return np.concatenate(features_vector, axis=1)
    
    def areshape(self, vector):
        return np.array(vector).reshape(-1, 1)
    
    def aloop(self, function, values):
        return np.array([function(i) for i in values])

    '''encoder functions'''
    def get_age(self, values):
        return self.areshape(self.age_normalizer(values))

    def get_salary(self, values):
        return self.areshape(self.salary_normalizer(values))

    def get_city(self, values):
        return self.aloop(self.city_encoder, values)

    def get_province(self, values):
        return self.aloop(self.province_encoder, values)
    
    def get_education(self, values):
        return self.aloop(self.education_encoder, values)

    def get_major(self, values):
        return self.aloop(self.major_encoder, values)
    
    def get_license(self, values):
        return self.aloop(self.license_encoder, values)
    
    def get_glasses(self, values):
        return self.aloop(self.glasses_encoder, values)
    
    def get_gender(self, values):
        return self.aloop(self.gender_encoder, values)
    
    def get_status(self, values):
        return self.aloop(self.status_encoder, values)

    def get_title(self, values):
        return self.title_vectorizer(values)

    def get_description(self, values):
        return self.description_vectorizer(values)
    
    '''additional functions'''
    def get_vector_shape(self):
        return self.job_vector.shape


if __name__ == '__main__':
    database = Connection('huda', 'Vancha12', '127.0.0.1', 1433, 'HRSystemDB')
    database.connect()

    vector = Vector(database.engine)
    
    print(vector.job.df_job.columns)
    print(vector.applicant.df_applicant.columns)

    print(vector.job.df_job)
    print(vector.applicant.df_applicant)

    

    
    



