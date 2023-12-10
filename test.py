from flask import Flask, request, render_template
import requests
import bs4
from bs4.element import Comment
import browser_cookie3

def bold(element):
    if not element.parent.name in ['b']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def opendayuk(uni):
    url = 'https://www.google.com/search?q=' + uni + '+uk+open+day'
    headers = {"User-Agent": "Mozilla/5.0"}
    # Load cookies directly from the browser
    cookies = browser_cookie3.chrome()
    # Send the GET request with cookies
    request_result = requests.get(url, headers=headers, cookies=cookies)
    print(request_result.text)
    
    # Rest of your code...
    # ...

# Remember to use this function cautiously and ensure that you are not violating Google's TOS.
print(opendayuk('cambridge'))
