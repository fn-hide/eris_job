import re

import numpy as np
import pandas as pd

from datetime import datetime

from bs4 import BeautifulSoup




def pick_date(datetime: str):
    if len(str(datetime)) < 10:
        return str(0)
    return datetime[:10]

def filter_date(date: str, minyear: int, maxyear: int):
    if type(date) == pd.NaT:
        return pd.NaT

    year = date.split('-')[0]

    if minyear <= int(year) <= maxyear:
        return date
    else:
        return np.nan

def get_age(date):
    return (datetime.now() - date) // np.timedelta64(1, 'Y')

def substract_months(datestart, dateend):
    return round((dateend - datestart) / np.timedelta64(1, 'M'))

def remove_html(text: str):
    # <[^<]+?>
    return BeautifulSoup(text, features='lxml').get_text(separator=' ')

def remove_enumerate(text: str):
    return re.sub('\d\.[^0-9]', ' ', text)

def maintain_alpha(text: str):
    return re.sub('[^a-zA-Z0-9]', ' ', text)

def remove_single(text: str):
    return re.sub('((?<=^)|(?<= ))[a-zA-Z]((?=$)|(?= ))', ' ', text)

def remove_morespace(text: str):
    return re.sub('\s+', ' ', text)

def clean_text(text: str):
    return remove_morespace(
        remove_single(
            maintain_alpha(
                remove_enumerate(
                    remove_html(
                        text.lower()
                    )
                )
            )
        )
    ).strip()

def remove_insideparentheses(text: str):
    return re.sub('\(.+\)', '', text)

def remove_standalonesymbols(text: str):
    return re.sub('/|(\s&)|\.|(\s-)', ' ', text)

def repair_salary(salary):
    if 0 < salary <= 100:
        return int(salary*1_000_000)
    elif 1000 <= salary <= 10_000:
        return int(salary*1_000)
    elif (100 < salary < 1000) or (10_000 < salary < 1_000_000):
        return 0
    else:
        return int(salary)
    
def txt_tolist(filepath):
    f = open(filepath, "r")
    stopword_list = []
    for line in f:
        stripped_line = line.strip()
        line_list = stripped_line.split()
        stopword_list.append(line_list[0])
    f.close()
    
    print('There are', len(stopword_list), 'data.')

    return stopword_list

def totext_age(usiamin=15, usiamax=65):
    age = []
    for usia in range(usiamin, usiamax + 1):
        age.append('U' + str(usia))
    return ' '.join(age)

def totext_iq(iqmin=80, iqmax=200):
    iq = []
    for q in range(iqmin, iqmax + 1):
        iq.append('IQ' + str(q))
    return ' '.join(iq)

def stopwords_remover(stopwords, text: str):
    words = text.split(' ')
    for word in words:
        if word in stopwords:
            words.remove(word)

    return ' '.join(words)

    

