from re import sub
from bs4 import BeautifulSoup
from numpy import nan, timedelta64
from datetime import datetime

from googletrans import Translator


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
            result[i] = result[i]/12
        else:
            result[i] = 0
    return result.astype(float)

def get_age(date):
    return (datetime.now() - date) // timedelta64(1, 'Y')


'''additional functions'''
def remove_rows_by_values(df, col, values):
    return df[~df[col].isin(values)]

def filter_rows_by_values(df, col, values):
    return df[df[col].isin(values)]

'''from content_based_4.ipynb'''
def change_slangwords(slangwords, teks):
    """mengubah slangwords menjadi goodwords

    Args:
        slangwords (dict): dictionary of slangwords
        teks (text): text to be changed

    Returns:
        str: text clean from slangwords
    """
    if type(teks) == str:
        teks = teks.split(' ')

    for i in range(len(teks)):
        if teks[i] in slangwords:
            teks[i] = slangwords[teks[i]]
    return ' '.join(teks)

def translate_teks(translator: Translator, teks):
    if teks == '':
        return ''
    result = translator.translate(teks, dest='id', src='en').text
    if result != teks:
        print(f'Translating {teks[:25]} ...')
    return result.lower()

def stemmer_words(stemmer, teks):
    if teks == '':
        return ''
    return stemmer.stem(teks)



def function_replacement(text):
    dict_function = {
        'r&d': 'research development',
        'asst.': 'assistant',
        'hrd': 'human resources development',
        'spv.': 'supervisor',
        'and': '',
        '&': '',
        '-': '',
    }
    
    list_text = text.split(' ')

    for i in range(len(list_text)):
        if list_text[i] in dict_function:
            list_text[i] = dict_function[list_text[i]]
    
    return ' '.join(list_text)

