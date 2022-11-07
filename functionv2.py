import string
import requests
import bs4
from bs4.element import Comment
import urllib.request


from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


LANGUAGE = "english"
SENTENCES_COUNT = 10

def ReturnFirstURLs(university, item):
    URLs = []
    url = 'https://www.google.com/search?q=' + university + '+' + item
    headers = {"User-Agent": "Mozilla/5.0"}
    cookies = {"CONSENT": "YES+cb.20210720-07-p0.en+FX+410"}
    request_result = requests.get(url, headers=headers, cookies=cookies)
    soup = bs4.BeautifulSoup(request_result.text, "html.parser")
    heading_object = soup.find_all( 'a')
    for href in heading_object:
        URLs.append(href.get('href').split("/url?q=")[-1].split("&")[0])
    return URLs
    #idk why but only the second link with .edu works, the first one is weird
    #try to remove the limit of lines you can print cuz i think they erase the first ones

def filterLink(links):
    for item in links:
        if 'http' in item:
            if '.edu' in item and not 'default/files/styles/' in item:
                #we should change the filter if it is about british unis i think they got .ac.uk
                return item

def GetText(link, look_at):
    url = link
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    # or for plain text files
    # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
    # parser = PlaintextParser.from_string("Check this out.", Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    final = ''
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        final += str(sentence)
    return final, look_at, url


def DoForEach(university):
    list = ['needed grades', 'application', 'cost']
    #major should be replaced by courses if it is a british uni
    #acceptance rate doesn't work, for ssome reason it is the link just after but we should learn how to take the number from the center of the web page
    returnn = []
    for item in list:
        if ' ' in item:
            item = '+'.join(item.split(' '))
        returnn.append(GetText(filterLink(ReturnFirstURLs(university, item)), item))
    return returnn



#.find_all('p')



