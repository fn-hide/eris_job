import string
import nltk
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords

data = pd.read_csv('c:/users/eats/downloads/jobs/jobs/jobs.csv')

data.drop(columns='Unnamed: 0', inplace=True)

data.isna().sum()

text = " ".join(i for i in data["Key Skills"])
stopwords = set(STOPWORDS)
wordcloud = WordCloud(stopwords=stopwords, 
                      background_color="white").generate(text)
plt.figure( figsize=(15,10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()


