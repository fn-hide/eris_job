from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



class ErisRecommender:
    def __init__(self, df_original, df_train, col):
        self.df_original = df_original
        self.df = df_train
        self.col = col
        self.encoder = None
        self.bank = None
    
    def fit(self):
        self.encoder = TfidfVectorizer()
        self.bank = self.encoder.fit_transform(self.df[self.col])

    def recommend(self, keyword, top=10):
        # content = df.loc[idx, self.col]
        idx = self.df[self.col][self.df[self.col].str.contains(keyword)].index[0]
        print('Index yang ada', idx)
        content = self.df.loc[idx, self.col]
        # print('Keyword match "' + content + '" content.')
        code = self.encoder.transform([content])

        dist = cosine_similarity(code, self.bank)

        self.df.drop(columns=['Text'], inplace=True)

        self.df['JobTitle'] = self.df_original.JobTitle
        self.df['Description'] = self.df_original.Description
        self.df['Requirement'] = self.df_original.Requirement

        self.df['Similarity'] = dist[0]*100
        self.df.Similarity = self.df.Similarity.astype(int)

        # rec_idx = dist.argsort()[0, 1:top + 1]
        # return self.df.loc[rec_idx]
        
        return self.df[(self.df.Similarity > 75) & (self.df.Similarity < 100)]
        # return self.df.sort_values(by='Similarity', ascending=False)
