#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
})

# 先登入
login_url = "http://www2.jkes.tp.edu.tw/index.asp"
session.get(login_url)

# 嘗試不同的登入方式
login_attempts = [
    {'username': '114097', 'password': '2793'},
    {'userid': '114097', 'pwd': '2793'},
]

for login_data in login_attempts:
    try:
        session.post(login_url, data=login_data, timeout=10)
    except:
        pass

# 訪問社團列表
url = "http://www2.jkes.tp.edu.tw/list.asp"
response = session.get(url)
response.encoding = 'big5'

soup = BeautifulSoup(response.text, 'html.parser')
print(soup.prettify())
