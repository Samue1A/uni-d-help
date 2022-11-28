from flask import Flask, request, render_template
import string
import requests
import bs4
from bs4.element import Comment
import csv
import config
# from docx import Document


from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk



#do this later (current error, it only works in my computer so u should learn some github documentation if it exists to reverse the connection,
# could also be the secret to a faster website: you have a database of things that have already been looked up and use them if the uni has already been looked up)
# def MakeDoc(headers, text, useStuff, useStuffHead, uni, country):
#     document = Document()
#     for index, title in enumerate(headers):
#         if text[index]:
#             document.add_heading(title.capitalize(), 0)
#             for item in text[index]:
#                 document.add_paragraph(str(item))
    
#     for index, title in enumerate(useStuffHead):
#         if useStuff[index]:
#             document.add_heading(title.capitalize(), 0)
#             if useStuffHead[index] == 'Sources':
#                 for item in useStuff[index]:
#                     document.add_paragraph(str(item))
#             elif useStuffHead[index] == 'Near You':
#                 for place in useStuff[index]:
#                     document.add_paragraph(place)
#                     for item in useStuff[index][place]:
#                         if str(item) == 'nothing found':
#                             document.add_paragraph(str(item))      
#                         else:
#                             for key in item:
#                                 document.add_paragraph(f'{key}: {item[key]}')
#             elif useStuffHead[index] == 'Subjects' or useStuffHead[index] == 'Majors':
#                 if country == 'UK':
#                     document.add_paragraph(f'Here is a link with a list of possible courses: {useStuff[index]}')
#                 elif country == 'US':
#                     document.add_paragraph(f'Here is a link with a list of possible majors: {useStuff[index]}')
#             else:
#                 document.add_paragraph(useStuff[index].replace((uni + ' University /'), ''))

#     document.save('static\\' + uni + 'Research.docx')
#     return document


def PyYelp(location):
    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {
        "Authorization": "Bearer " + config.api_key
    }

    final = {
        'coffee shop': None,
        'Pizzeria': None,
        'Grocery Store': None,
        'Library': None
    }
    for i in final:
        add = []
        params = {
            "term": i,
            "location": f"{location}"
        }
        response = requests.get(url, headers=headers, params=params)
        try:
            businesses = response.json()["businesses"]
                
            yelpItems = [
                (sorted(businesses, key=lambda item: (item["rating"], (item["distance"]*-1)))),
                (sorted(businesses, key=lambda item: (item["distance"], (item["rating"]*-1)))).reverse()
            ]
            print(yelpItems[0])
            print('-----------------------------')
            print(yelpItems[1])
            
            for yelpItem in yelpItems:
                for OneToTwo in range(2):
                    try:
                        add.append( {
                            'name': yelpItem[(OneToTwo + 1)*-1]["name"],
                            'location': (yelpItem[(OneToTwo + 1)*-1]['location'])["address1"],
                            'rating': yelpItem[(OneToTwo + 1)*-1]["rating"],
                            'phone': yelpItem[(OneToTwo + 1)*-1]["phone"],
                            'distance': str(round(yelpItem[(OneToTwo + 1)*-1]["distance"])) +'m'
                        })
                    except:
                        pass 
            #learn how to sort by distance!
        
            final[i] = add.copy()
        except:
            final[i] = 'nothing found'
        
    for location in final:
        if location != 'nothing found':
            return final
    return False




def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def isint(num):
    try:
        int(num)
        return True
    except ValueError:
        return False

def GetText(link, look_at, SENTENCES_COUNT, country, university):
    url = link.split('%')[0]
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    # or for plain text files
    # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
    # parser = PlaintextParser.from_string("Check this out.", Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    final = []
    if look_at == 'needed+grades' and country == 'US':
        a = ScrapGoogle(university, '+university+average+gpa')
        a = a.split('All results')[-1]
        a = (a.split('. ')[0].strip() + '.').split(' ')
        for index, item in enumerate(a):
            if isfloat(item.strip(".")) or isint(item.strip(".")):
                a[index] += f' (or {round(float(item.strip("."))*5, 2)}/20 in france)'
                a = ' '.join(a)      
                final.append(str(a))
                break
    
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        final.append(sentence)
    final = list(dict.fromkeys(final))
    return final, look_at, url




def ScrapGoogle(university, message, num=1):
    url = 'https://www.google.com/search?q=' + university + message
    headers = {"User-Agent": "Mozilla/5.0"}
    cookies = {"CONSENT": "YES+cb.20210720-07-p0.en+FX+410"}
    request_result = requests.get(url, headers=headers, cookies=cookies)
    soup = bs4.BeautifulSoup(request_result.text, "html.parser")
    texts = soup.findAll(text=True)
    if num == 1:
        visible_texts = filter(tag_visible, texts)  
    else:
        visible_texts = filter(tag_visible2, texts)  
    return u" ".join(t.strip() for t in visible_texts)
#idk why but only the second link with .edu works, the first one is weird
#try to remove the limit of lines you can print cuz i think they erase the first ones


def tag_visible(element):
    if not element.parent.name in ['div', 'span', 'b']:
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

def filterLink(links, country='us'):
    for item in links:
        if 'http' in item:
            if country.lower() == 'us':
                if '.edu' in item and (not 'default/files/styles/' in item) and (not '.png' in item):
                    return item
            else:
                if '.ac.uk' in item and (not 'default/files/styles/' in item) and (not '.png' in item):
                    return item


def DoForEach(university, SENTENCES_COUNT, list=['needed grades', 'application', 'cost'], country='US'):
    #major should be replaced by courses if it is a british uni
    #acceptance rate doesn't work, for ssome reason it is the link just after but we should learn how to take the number from the center of the web page
    returnn = []
    for item in list:
        if ' ' in item:
            item = '+'.join(item.split(' '))
        if country == 'UK':
            returnn.append(GetText(filterLink(ReturnFirstURLs(university, item), 'uk'), item, SENTENCES_COUNT, country, university))
        else:
            returnn.append(GetText(filterLink(ReturnFirstURLs(university, item)), item, SENTENCES_COUNT, country, university))
    return returnn



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


def tag_visible2(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 
# Flask constructor
app = Flask(__name__)

commments = [
    ["comment", "file"]
]

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
    uni = request.args.get("name").capitalize()
    listy = request.args.getlist("listy")
    SENTENCES_COUNT = request.args.get("lines")

    if not SENTENCES_COUNT:
        SENTENCES_COUNT = 10
    
    all = {
        'major': False,
        'sources': False,
        'acceptance rate': False,
    }

    for item in all:
        if item in listy:
            listy.remove(item)
            all[item] = True


    all_text = list(DoForEach(uni, SENTENCES_COUNT, listy, 'UK'))

    links = []
    headers = []
    text = []
    useStuffHead = []
    useStuff = []
    for item in list(all_text):
        headers.append(item[1].replace("+", " ").capitalize())

        text.append(item[0])
        links.append(item[-1])
    
    if all['acceptance rate']:
        a = ScrapGoogle(uni, '+university+acceptance+rate').split('All results')[-1]
        a = a.split('%')[0]
        a = a.strip() + '%'
        useStuffHead.append("Acceptance Rate")
        useStuff.append(a)
    if all['major']:
        majors = filterLink(ReturnFirstURLs(uni, 'major'), 'uk')
        useStuffHead.append("Subjects")
        useStuff.append(majors)
    if all['sources']:
        useStuffHead.append("Sources")
        useStuff.append(links)



    return render_template('greet.html', text=text, headers=headers, country='UK', uni=uni)







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
                    if x == 0:
                        titles = row.copy()
                    else:
                        
                        if row != []:
                            
                            items.append(row)
                    x += 1
            return render_template('admin.html', items=items, titles=titles)
    return render_template('admin.html')






@app.route('/ussearch')
def greet():
    uni = request.args.get("name").capitalize()
    listy = request.args.getlist("listy")
    SENTENCES_COUNT = request.args.get("lines")

    if not SENTENCES_COUNT:
        SENTENCES_COUNT = 10
    
    all = {
        'major': False,
        'sources': False,
        'acceptance rate': False,
        'location': False,
        'deadline': False
    }

    for item in all:
        if item in listy:
            listy.remove(item)
            all[item] = True


    all_text = list(DoForEach(uni, SENTENCES_COUNT, listy, 'US'))

    links = []
    headers = []
    text = []
    useStuffHead = []
    useStuff = []
    for item in list(all_text):
        headers.append(item[1].replace("+", " ").capitalize())

        text.append(item[0])
        links.append(item[-1])
    
    # doc = MakeDoc(headers, text, useStuff, useStuffHead, uni, 'US')
    # useStuffHead.append("Document")
    # useStuff.append(doc)


    if all['acceptance rate']:
        a = ScrapGoogle(uni, '+university+acceptance+rate').split('All results')[-1]
        a = a.split('%')[0]
        a = a.strip() + '%'
        for item in (a.split('. ')):
            if '%' in item:
                useStuffHead.append("Acceptance Rate")
                useStuff.append(a)
                break
    if all['major']:
        majors = filterLink(ReturnFirstURLs(uni, 'major'), 'us')
        useStuffHead.append("Majors")
        useStuff.append(majors)
    if all['deadline']:
        try:
            try:
                deadline = ScrapGoogle(uni, '+university+application+deadline+date', 2).split('\n\n')[1]
                deadline = adFilter(check(deadline.replace('. ', ' .').replace('?', ' .').replace('›', ' .').replace('...', ' .').split(' .')).strip()).replace('\n', ' ') 
            except:
                deadline = ScrapGoogle(uni, '+university+application+deadline+date', 2).split('Verbatim')[1]
                deadline = adFilter(check(deadline.replace('. ', ' .').replace('?', ' .').replace('›', ' .').replace('...', ' .').split(' .')).strip()).replace('\n', ' ') 
            if deadline[-1] != '.':
                deadline += '.'
            useStuffHead.append('Deadline')
            useStuff.append(deadline)
        except:
            pass
    if all['location']:
        z = ScrapGoogle(uni, '+university+location').split('All results')[-1].split('- Wikipedia')[0].split('See results')[0].replace('›', '.').replace('|', '.').replace('/', '').replace('\\', '').split('.')
        for senty in z:   
            nearYou = PyYelp(senty.strip())
            if nearYou:
                useStuffHead.append("Near You")
                useStuff.append(nearYou)
                useStuffHead.append("Location")
                useStuff.append(senty)


                break
    if all['sources']:
        useStuffHead.append("Sources")
        useStuff.append(links)
    



    return render_template('greet.html', text=text, headers=headers, country='US', uni=uni, useStuff=useStuff, useStuffHead=useStuffHead)
