#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
})

url = "http://www2.jkes.tp.edu.tw/list.asp?ClassID=6"
response = session.get(url)
response.encoding = 'big5'

soup = BeautifulSoup(response.text, 'html.parser')
print(soup.prettify())
