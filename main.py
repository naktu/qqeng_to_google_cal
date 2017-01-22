import requests
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from bs4 import BeautifulSoup
from datetime import datetime
from credentials import *

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
GMT_OFF = '+03:00'

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

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser(os.getcwd())
    credential_dir = os.path.join(home_dir, '.credentials')
    print(credential_dir)
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_date(page):
    next_lesson = []

    soup = BeautifulSoup(page, 'lxml')
    for i in soup.find_all('section'):
        tag_class = i.get('class')
        tag_class.sort()
        if tag_class == ['latestlesson', 'mb15']:
            next_lesson = i.text.split()

    if len(next_lesson) < 3:
        return []
    else:
        lesson = {
            'date': datetime.strptime(next_lesson[2], '%Y-%m-%d').date(),
            'time_start': datetime.strptime(next_lesson[3].split('-')[0], '%H:%M').time(),
            'time_end': datetime.strptime(next_lesson[3].split('-')[1], '%H:%M').time()
        }

    return lesson

def add_event(date, start, end, event_name):
    # TODO add args like start, end, name
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    start = str(start)
    end = str(end)
    date = str(date)
    # TODO
    start = date + "T" + start + GMT_OFF
    end = date + "T" + end + GMT_OFF
    event = {
        'summary': event_name,
        'start': {'dateTime': start},
        'end':   {'dateTime': end},
    }
    service.events().insert(calendarId=calendar, sendNotifications=True, body=event).execute()

def main():
    event_name = 'English lesson'
    qq_eng_site = {
        '.login': 1,
        'email': qq_eng['email'],
        'passwd': qq_eng['password'],
        'keep': '1'
    }
    qq = site('https://ru.qqeng.com/q/mypage/')
    qq.auth(qq_eng_site)

    lesson = get_date(qq.get_page('https://ru.qqeng.com/q/mypage/').decode())
    if lesson == []:
        print("No new lessons")
    else:
        add_event(
            date       = lesson['date'],
            start      = lesson['time_start'],
            end        = lesson['time_end'],
            event_name = event_name
        )
if __name__ == '__main__':
    main()
