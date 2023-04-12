from re import sub
from bs4 import BeautifulSoup
from numpy import nan, timedelta64
from datetime import datetime



def remove_html(text: str):
    # <[^<]+?>
    return BeautifulSoup(text, features='lxml').get_text(separator=' ')

def remove_enumerate(text: str):
    return sub('\d\.[^0-9]', ' ', text)

def maintain_alphanum(text: str):
    return sub('[^a-zA-Z0-9]', ' ', text)

def remove_single(text: str):
    return sub('((?<=^)|(?<= ))[a-zA-Z]((?=$)|(?= ))', ' ', text)

def remove_morespace(text: str):
    return sub('\s+', ' ', text)

# remove inside parentheses
def remove_insideparentheses(text: str):
    return sub('\(.+\)', '', text)

# remove standalone symbols
def remove_standalonesymbols(text: str):
    return sub('/|(\s&)|\.|(\s-)', ' ', text)

# remove parentheses and number
def remove_parenthesesnumber(text: str):
    return sub('[\(\)0-9]', '', text)

def clean_text(text: str):
    return remove_morespace(
        remove_single(
            maintain_alphanum(
                remove_enumerate(
                    remove_html(
                        text.lower()
                    )
                )
            )
        )
    ).strip()

def maintain_alphabet(text: str):
    return sub('[^a-zA-Z]', ' ', text)




def pick_date(datetime: str):
    datetime = str(datetime)

    if len(datetime) < 10:
        return ''
    return datetime[:10]

def filter_date(date: str, minyear: int, maxyear: int):
    if date == '':
        return nan
    
    year = date.split('-')[0]

    if minyear <= int(year) <= maxyear:
        return date
    else:
        # print('Bad year is', year)
        return nan
    
def substract_months(datestart, dateend):
    result = round(
        (dateend - datestart) / timedelta64(1, 'M')
    )

    result = result.values

    for i in range(len(result)):
        if result[i] > 1:
            result[i] = int(result[i]/12)
        else:
            result[i] = 0
    return result.astype(int)

def get_age(date):
    return (datetime.now() - date) // timedelta64(1, 'Y')


'''additional functions'''
def remove_rows_by_values(df, col, values):
    return df[~df[col].isin(values)]

def filter_rows_by_values(df, col, values):
    return df[df[col].isin(values)]

