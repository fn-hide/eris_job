import tensorflow as tf
import numpy as np



class JobModel:
    def __init__(self, df_job, df_function, df_education, df_city, df_province, df_major):
        self.max_tokens = 10_000

        '''tables'''
        # load main table
        self.df_job = df_job
        # load reference table
        self.df_function = df_function
        self.df_education = df_education
        self.df_city = df_city
        self.df_province = df_province
        self.df_major = df_major

        '''numerical'''
        # adapt from Age in Job Table
        self.age_normalizer = tf.keras.layers.Normalization(axis=None)
        self.age_normalizer.adapt(self.df_job.UsiaMax)
        # adapt from SalaryMean in Job Table
        self.salary_normalizer = tf.keras.layers.Normalization(axis=None)
        self.salary_normalizer.adapt(self.df_job.SalaryMean)

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
        # adapt from JobTitle in Job Table
        self.title_vectorizer = tf.keras.layers.TextVectorization(max_tokens=self.max_tokens, output_mode='multi_hot')
        self.title_vectorizer.adapt(self.df_job.JobTitlePosition)
        # adapt from Description in Job Table
        self.description_vectorizer = tf.keras.layers.TextVectorization(max_tokens=self.max_tokens, output_mode='tf_idf')
        self.description_vectorizer.adapt(self.df_job.DescriptionRequirement)

        self.job_vector = self.get_vector([
            self.get_age(self.df_job.UsiaMax.values),
            self.get_salary(self.df_job.SalaryMean.values),
            self.get_city(self.df_job.CityName.values),
            self.get_province(self.df_job.ProvinceName.values),
            self.get_education(self.df_job.EducationLevelName.values),
            self.get_major(self.df_job.MajorName.values),
            self.get_license(self.df_job.DriverLicenseType.values),
            self.get_glasses(self.df_job.UsingGlasses.values),
            self.get_gender(self.df_job.Gender.values),
            self.get_status(self.df_job.MaritalStatus.values),
            self.get_title(self.df_job.JobTitlePosition.values),
            self.get_description(self.df_job.DescriptionRequirement.values),
        ])

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