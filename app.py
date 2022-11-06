from flask import Flask, request, render_template
from functionv2 import DoForEach, filterLink, ReturnFirstURLs
 
# Flask constructor
app = Flask(__name__)  
 
# A decorator used to tell the application
# which URL is associated function
@app.route('/')
def index():
   return render_template("index.html")

@app.route('/murder')
def greet():
    name = request.args.get("name")
    uni = name.capitalize()
    all_text = list(DoForEach(uni))
    majors = 'Here is a link with a list of possible majors: \n'+ filterLink(ReturnFirstURLs(uni, 'major'))

    links = []
    headers = []
    text = []
    for item in list(all_text):
        headers.append(item[1].replace("+", " ").capitalize())

        text.append(item[0])
        links.append(item[2])

    headers.append("Majors")
    text.append(majors)


    headers.append("Sources")
    text.append('\n'.join(links))
    return render_template('greet.html', text=text, headers=headers)