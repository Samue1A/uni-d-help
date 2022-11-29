from flask import Flask, request, render_template
import string
import requests
import bs4
from bs4.element import Comment
import csv
import config

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk
nltk.download('punkt')




def check(text):
    months = ['january', 'jebruary', 'jarch', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    for sentence in text:
        for month in months:
            if month in sentence.lower():
                return sentence
    return 'no date'


def adFilter(text):
    if 'Ad' in text:
        return text.split('.')[-1]
    return text



def ScrapGoogle2(university, message):
    url = 'https://www.google.com/search?q=' + university + message
    print(url)
    headers = {"User-Agent": "Mozilla/5.0"}
    cookies = {"CONSENT": "YES+cb.20210720-07-p0.en+FX+410"}
    request_result = requests.get(url, headers=headers, cookies=cookies)
    soup = bs4.BeautifulSoup(request_result.text, "html.parser")
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible2, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def tag_visible2(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


uni = 'Imperial uk'

try:
    a = ScrapGoogle2(uni, '+university+application+deadline+date').split('\n\n')[1]
    text = adFilter(check(a.replace('. ', ' .').replace('?', ' .').replace('›', ' .').replace('...', ' .').split(' .')).strip()).replace('\n', ' ') 
except:
    a = ScrapGoogle2(uni, '+university+application+deadline+date').split('Verbatim')[1]
    text = adFilter(check(a.replace('. ', ' .').replace('?', ' .').replace('›', ' .').replace('...', ' .').split(' .')).strip()).replace('\n', ' ') 


if text[-1] != '.':
    text += '.'



print(text)

