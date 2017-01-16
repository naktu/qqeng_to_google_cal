import requests
from bs4 import BeautifulSoup
from datetime import datetime

from credentials import *

class site():
    def __init__(self, url):
        self.url = url
        self.page = ''
        self.auth_data = {}
        self.cookies = ''

    def auth(self, auth_data):
        self.auth_data = auth_data

        r = requests.post(self.url, self.auth_data)
        self.cookies = r.cookies

    def get_page(self, url):
        r = requests.get(url, cookies = self.cookies)
        return(r.content)

def get_date(page):
    next_lesson = []

    soup = BeautifulSoup(page, 'lxml')
    for i in soup.find_all('section'):
        tag_class = i.get('class')
        tag_class.sort()
        if tag_class == ['latestlesson', 'mb15']:
            next_lesson = i.text.split()

    lesson = {
        'date': datetime.strptime(next_lesson[2], '%Y-%m-%d').date(),
        'time_start': datetime.strptime(next_lesson[3].split('-')[0], '%H:%M').time(),
        'time_end': datetime.strptime(next_lesson[3].split('-')[1], '%H:%M').time()
    }

    return (lesson)

if __name__ == '__main__':
    qq_eng_site = {
        '.login': 1,
        'email': qq_eng['email'],
        'passwd': qq_eng['password'],
        'keep': '1'
    }
    qq = site('https://ru.qqeng.com/q/mypage/')
    qq.auth(qq_eng_site)

    lesson = get_date(qq.get_page('https://ru.qqeng.com/q/mypage/').decode())
    print(lesson)
