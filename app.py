from flask import Flask, request, render_template
import string
import requests
import bs4
from bs4.element import Comment
import csv

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk
nltk.download('punkt')


def ScrapGoogle(university, message):
    URLs = []
    url = 'https://www.google.com/search?q=' + university + message
    print('looked up ' + url)
    headers = {"User-Agent": "Mozilla/5.0"}
    cookies = {"CONSENT": "YES+cb.20210720-07-p0.en+FX+410"}
    request_result = requests.get(url, headers=headers, cookies=cookies)
    soup = bs4.BeautifulSoup(request_result.text, "html.parser")
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)
#idk why but only the second link with .edu works, the first one is weird
#try to remove the limit of lines you can print cuz i think they erase the first ones


def tag_visible(element):
    if not element.parent.name in ['div']:
        return False
    if isinstance(element, Comment):
        return False
    return True



LANGUAGE = "english"

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


def filterLinkUK(links):
    for item in links:
        if 'http' in item:
            if '.ac.uk' in item and not 'default/files/styles/' in item:
                #we should change the filter if it is about british unis i think they got .ac.uk
                return item

def GetText(link, look_at, SENTENCES_COUNT, country, university):
    url = link
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    # or for plain text files
    # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
    # parser = PlaintextParser.from_string("Check this out.", Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    final = []
    print(0)
    print(f"look at: {look_at}               country: {country}")
    if look_at == 'needed+grades' and country == 'US':
        a = ScrapGoogle(university, '+university+average+gpa').split('All results')[-1]

        final.append(str(a))
        print(1)
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        final.append(sentence)
    final = list(dict.fromkeys(final))
    

    return final, look_at, url


def DoForEach(university, SENTENCES_COUNT, list=['needed grades', 'application', 'cost'], country='US'):
    #major should be replaced by courses if it is a british uni
    #acceptance rate doesn't work, for ssome reason it is the link just after but we should learn how to take the number from the center of the web page
    returnn = []
    for item in list:
        if ' ' in item:
            item = '+'.join(item.split(' '))
        if country == 'UK':
            returnn.append(GetText(filterLinkUK(ReturnFirstURLs(university, item)), item, SENTENCES_COUNT, country, university))
        else:
            returnn.append(GetText(filterLink(ReturnFirstURLs(university, item)), item, SENTENCES_COUNT, country, university))
    return returnn

#-----------------------------------------------------------------------------------------------------------------------
 
# Flask constructor
app = Flask(__name__)

commments = [
    ["comment", "file"]
]
 
# A decorator used to tell the application
# which URL is associated function
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        comment = request.form.get("comment")
        fil = request.form.get("fil")
        if not comment:
            comment = '(No value)'
        if not fil:
            fil = '(No value)'
        with open("comments.csv", "a") as file:
            Writer = csv.writer(file)
            Writer.writerow([comment, fil])
    return render_template("index.html")


@app.route('/uksearch', methods=['GET', 'POST'])
def uksearch():
    name = request.args.get("name")
    listy = request.args.getlist("listy")
    SENTENCES_COUNT = request.args.get("lines")

    major = False
    sources = False
    if not SENTENCES_COUNT:
        SENTENCES_COUNT = 10
    if 'major' in listy:
        major = True
        listy.remove('major')
    if 'sources' in listy:
        sources = True
        listy.remove('sources')
    if 'location' in listy:
        location = True
        listy.remove('location')
    if 'acceptance rate' in listy:
        acceptance_rate = True
        listy.remove('acceptance rate')

    
    

    uni = name.capitalize()

    all_text = list(DoForEach(uni, SENTENCES_COUNT, listy, 'UK'))
    for bob in all_text:
        for bobb in bob:
            print(bobb)
    if major:
        majors = filterLinkUK(ReturnFirstURLs(uni, 'major'))

    links = []
    headers = []
    text = []
    for item in list(all_text):
        headers.append(item[1].replace("+", " ").capitalize())

        text.append(item[0])
        links.append(item[-1])

    
    if major:
        headers.append("Subjects")
        text.append(majors)

    if sources:
        headers.append("Sources")
        text.append(links)



    print(text[-1])
    print('\n\n\n' + str(SENTENCES_COUNT))
    print(listy)
    return render_template('greet.html', text=text, headers=headers, country='UK')







@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        items = []
        titles = []
        x = 0
        username = request.form.get("username")
        password = request.form.get("password")
        if (username == 'samuel' and password == 'verycomplexpassword') or (username == 'oskar' and password == 'password'):
            with open("comments.csv", "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    print(row)
                    if x == 0:
                        titles = row.copy()
                    else:
                        print(1)
                        if row != []:
                            print(2)
                            items.append(row)
                    x += 1
            print(items)
            return render_template('admin.html', items=items, titles=titles)
    return render_template('admin.html')






@app.route('/ussearch')
def greet():
    name = request.args.get("name")
    listy = request.args.getlist("listy")
    SENTENCES_COUNT = request.args.get("lines")

    major = False
    sources = False
    if not SENTENCES_COUNT:
        SENTENCES_COUNT = 10
    if 'major' in listy:
        major = True
        listy.remove('major')
    if 'sources' in listy:
        sources = True
        listy.remove('sources')
    if 'location' in listy:
        location = True
        listy.remove('location')
    if 'acceptance rate' in listy:
        acceptance_rate = True
        listy.remove('acceptance rate')

    uni = name.capitalize()

    all_text = list(DoForEach(uni, SENTENCES_COUNT, listy, 'US'))
    for bob in all_text:
        for bobb in bob:
            print(bobb)
    if major:
        majors = filterLink(ReturnFirstURLs(uni, 'major'))

    links = []
    headers = []
    text = []
    for item in list(all_text):
        headers.append(item[1].replace("+", " ").capitalize())

        text.append(item[0])
        links.append(item[-1])

    
    if major:
        headers.append("Majors")
        text.append(majors)
    if acceptance_rate:
        a = ScrapGoogle(uni, '+university+acceptance+rate').split('All results')[-1]
        a = a.split('%')[0]
        a = a.strip() + '%'
        headers.append("Acceptance Rate")
        text.append(a)

    if location:
        z = ScrapGoogle(uni, '+university+acceptance+rate').split('All results')[-1].split('- Wikipedia')[0].split(',').pop()
        text.append(z) 
    if sources:
        headers.append("Sources")
        text.append(links)
    




    print(text[-1])
    print(len(text))
    print('\n\n\n' + str(SENTENCES_COUNT))
    print(listy)
    return render_template('greet.html', text=text, headers=headers, country='US')