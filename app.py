from flask import Flask, request, render_template
import string
import requests
import bs4
from bs4.element import Comment
import csv
import config  #---> c'est le API key du Yelp api
# from docx import Document



from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk
nltk.download('punkt')


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
        
            final[i] = add.copy()
        except:
            return False

    
    return final




def isfloat(num):
    try:
        float(num)
        if '.' in num:
            return True
        return False
    except ValueError:
        return False

def isnum(num):
    try:
        float(num)
        return True
    except:
        return False

def GetText(link, look_at, SENTENCES_COUNT, country, university):
    if not link:
        return ''
    url = link.split('%')[0]
    print(url)
    parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    final = []
    if look_at == 'needed+grades':
        a = ScrapGoogle(university, f'+{country}+university+average+gpa')
        a = a.split('All results')[-1]
        a = (a.split('. ')[0].strip() + '.').split(' ')
        for index, item in enumerate(a):
            if isfloat(item.strip(".")):
                a[index] += f' (or {round(float(item.strip("."))*5, 2)}/20 in france)'
                a = ' '.join(a)      
                final.append(str(a))
                break
    if summarizer(parser.document, SENTENCES_COUNT):
        for sentence in summarizer(parser.document, SENTENCES_COUNT):
            final.append(sentence)
        final = list(dict.fromkeys(final))
        final = list(final)
        return final, look_at, url
    return False




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


def tag_visible(element):
    if not element.parent.name in ['div', 'span', 'b']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def bold(element):
    if not element.parent.name in ['b']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def opendayuk(uni):
    url = 'https://www.google.com/search?q=' + uni + '+uk+open+day+'
    headers = {"User-Agent": "Mozilla/5.0"}
    cookies = {"CONSENT": "YES+cb.20210720-07-p0.en+FX+410"}
    request_result = requests.get(url, headers=headers, cookies=cookies)
    soup = bs4.BeautifulSoup(request_result.text, "html.parser")
    soup = soup.find('div', {'class': 'taw'}).contents[-1].strip()
    texts = soup.findAll(text=True)
    visible_texts = filter(bold, texts)  
    return u" ".join(t.strip() for t in visible_texts)



LANGUAGE = "english"

def ReturnFirstURLs(university, degree, item, country='us'):
    URLs = []
    url = 'https://www.google.com/search?q=' + university + '+' + country + '+' + degree + '+' + item
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
                if '.ac.uk' in item and (not 'default/files/styles/' in item) and (not '.png' in item) and (not 'images' in item.lower()):
                    print(item)
                    return item


def DoForEach(university, degree, SENTENCES_COUNT, list=['needed grades', 'undergraduate application', 'undergraduate cost'], country='US'):
    returnn = []
    for item in list:
        if ' ' in item:
            item = '+'.join(item.split(' '))
        if country == 'UK':
            l = GetText(filterLink(ReturnFirstURLs(university, degree, item, country), country), item, SENTENCES_COUNT, country, university)
            if l:
                returnn.append(l)
        else:
            l = GetText(filterLink(ReturnFirstURLs(university, degree, item)), item, SENTENCES_COUNT, country, university)
            if l:
                returnn.append(l)
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
 
# Flask time babyyyyyyyyyyyy
app = Flask(__name__)


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
    if uni.lower() == 'imperial':
        uni = 'Imperial College'
    listy = request.args.getlist("listy")
    SENTENCES_COUNT = request.args.get("lines")
    degree = request.args.get("degree")

    if not SENTENCES_COUNT:
        SENTENCES_COUNT = 10
    
    all = {
        'courses': False,
        'sources': False,
        'acceptance rate': False,
        'location': False,
        'deadline': False,
        'openday': False
    }

    for item in all:
        if item in listy:
            listy.remove(item)
            all[item] = True

    all_text = DoForEach(uni, degree, SENTENCES_COUNT, listy, 'UK')
    print(all_text)
    if all_text[0] == all_text[-1]:
        all_text = all_text[0]
        print('1st')
    

    links = []
    text = []
    useStuffHead = []
    useStuff = []
    headers = []
    for item in all_text:
        headers.append(item[1].replace("+", " ").capitalize())
        text.append(item[0])
        links.append(item[-1])
    
    if all['acceptance rate']:
        a = ScrapGoogle(uni, '+uk+university+acceptance+rate').split('All results')[-1]
        a = a.split('MIT admissions is extremely selective with an acceptance rate of 7% . Students that get into MIT have an average SAT score between 1510-1580 or an average ACT score of 34-36. Massachusetts Institute of Technology Admissions - Niche www.niche.com › ')[-1]
        for a_index, item in enumerate(a):
                # a.remove('%')
                # for num in a.split(' '):
                #     if isfloat(num):
                #         useStuffHead.append("Acceptance Rate")
                #         useStuff.append(f'The acceptance rate for {uni} is {num}%')
            if item == '%':
                for ind in range(5):
                    slice = a[(a_index-5+ind):(a_index)]
                    print(slice)
                    if isnum(slice):
                        slice = slice.replace('-', '')
                        useStuffHead.append("Acceptance Rate")
                        useStuff.append(f'The acceptance rate for {uni} is {slice}%')
                        break
                break


    if all['courses']:
        courses = filterLink(ReturnFirstURLs(uni, degree, 'courses'), 'uk')
        useStuffHead.append("Courses")
        useStuff.append(courses)
    if all['deadline']:
        try:
            try:
                deadline = ScrapGoogle(uni, '+uk+university+application+deadline+date', 2).split('\n\n')[1]
                deadline = adFilter(check(deadline.replace('. ', ' .').replace('?', ' .').replace('›', ' .').replace('...', ' .').split(' .')).strip()).replace('\n', ' ') 
            except:
                deadline = ScrapGoogle(uni, '+uk+university+application+deadline+date', 2).split('Verbatim')[1]
                deadline = adFilter(check(deadline.replace('. ', ' .').replace('?', ' .').replace('›', ' .').replace('...', ' .').split(' .')).strip()).replace('\n', ' ') 
            if deadline[-1] != '.':
                deadline += '.'
            useStuffHead.append('Deadline')
            useStuff.append(deadline)
        except:
            pass
    if all['location']:
        z = ScrapGoogle(uni, '+uk+university+location').split('All results')[-1].split('- Wikipedia')[0].split('See results')[0].replace('›', '.').replace('|', '.').replace('/', '').replace('\\', '').split('.')
        for senty in z:   
            nearYou = PyYelp(senty.strip())
            if nearYou:
                useStuffHead.append("Near You")
                useStuff.append(nearYou)
                useStuffHead.append("Location")
                useStuff.append(senty)
                break
    l = 0
    if all['openday']:
        openday = ScrapGoogle(uni, '+uk+university+open+day').replace(' - ', '. ').split('. ')
        print(openday)
        for sentence in openday:
            for word in sentence.split(' '):
                if isnum(word) and int(word.replace(',', '')) < 32:
                    useStuffHead.append("Open Day")
                    useStuff.append(sentence.split('All results')[-1])
                    l = 1
                    break
            if l ==1:
                break

    if all['sources']:
        useStuffHead.append("Sources")
        useStuff.append(links)
    
    print(useStuff)
    print('----------------------------')
    print(useStuffHead)

    return render_template('greet.html', text=text, headers=headers, country='UK', uni=uni, useStuff=useStuff, useStuffHead=useStuffHead)







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
def ussearch():
    uni = request.args.get("name").capitalize()
    listy = request.args.getlist("listy")
    degree = request.args.get("degree")
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


    all_text = DoForEach(uni, degree, SENTENCES_COUNT, listy, 'US')
    if len(all_text) == 1:
        all_text = all_text[0]

    links = []
    headers = []
    text = []
    useStuffHead = []
    useStuff = []
    print(all_text)
    for item in all_text:
        if item and not isnum(item):
            print(item)
            print(f'item 1: {item[0]}')
            print(f'item 2: {item[1]}')
            print(f'item 3: {item[-1]}')
            headers.append(item[1].replace("+", " ").capitalize())

            text.append(item[0])
            links.append(item[-1])
    
    # doc = MakeDoc(headers, text, useStuff, useStuffHead, uni, 'US')
    # useStuffHead.append("Document")
    # useStuff.append(doc)


    if all['acceptance rate']:
        a = ScrapGoogle(uni, '+university+acceptance+rate').split('All results')[-1]
        print(a)
        for a_index, item in enumerate(a):
                # a.remove('%')
                # for num in a.split(' '):
                #     if isfloat(num):
                #         useStuffHead.append("Acceptance Rate")
                #         useStuff.append(f'The acceptance rate for {uni} is {num}%')
            if item == '%':
                for ind in range(5):
                    slice = (a[(a_index-5+ind):(a_index)])
                    print(slice)
                    if isnum(slice):
                        slice = slice.replace('-', '')
                        useStuffHead.append("Acceptance Rate")
                        useStuff.append(f'The acceptance rate for {uni} is {slice}%')
                        break
                break


    if all['major']:
        majors = filterLink(ReturnFirstURLs(uni, degree, 'major'), 'us')
        useStuffHead.append("Majors")
        useStuff.append(majors)
    if all['deadline']:
        l=0
        deadline = ScrapGoogle(uni, '+university+application+deadline+date', 2).split('All results')[-1].split('Verbatim')[-1].replace('- ', '.').replace('›', '.').split('.')
        for sentence in deadline:
            for word in sentence.split(' '):
                if isnum(word) and int(word.replace(',', '')) < 32:
                    useStuffHead.append("Deadline")
                    useStuff.append(sentence)
                    l = 1
                    break
            if l ==1:
                break
        
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















