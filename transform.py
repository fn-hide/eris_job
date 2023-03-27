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

def maintain_alpha(text: str):
    return re.sub('[^a-zA-Z]', ' ', text)

def remove_single(text: str):
    return re.sub('((?<=^)|(?<= )).((?=$)|(?= ))', ' ', text)

def remove_morespace(text: str):
    return re.sub('\s+', ' ', text)

def remove_html(text: str):
    # <[^<]+?>
    return BeautifulSoup(text).get_text()

def repair_salary(salary):
    if 0 < salary <= 100:
        return int(salary*1_000_000)
    elif 1000 <= salary <= 10_000:
        return int(salary*1_000)
    elif (100 < salary < 1000) or (10_000 < salary < 1_000_000):
        return 0
    else:
        return int(salary)
    

