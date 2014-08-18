#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
COOKIE_FILE = os.path.join( os.path.expanduser('~'),
                            'diary_cookie.data')

import requests
try:
    import cookielib
except ImportError as e:
    import http.cookiejar as cookielib

from DiaryRuInfo import DiaryRuInfo

from re import search
import time

DIARY_MAIN_URL = 'http://www.diary.ru/'
DIARY_REQUEST_URL = "http://pay.diary.ru/yandex/online.php"

pexists = os.path.exists

class DiaryRuHTTPClient(object):
    def __init__(self):
        self.cookie = cookielib.LWPCookieJar()
        if pexists(COOKIE_FILE):
            self.cookie.load(COOKIE_FILE)
        self.session = requests.Session()
        self.session.cookies = self.cookie
        headers = self.session.headers
        headers['Accept-encoding'] = 'utf-8'
        headers['User-agent'] = 'Mozilla/5.0 (Windows NT 6.1; rv:29.0) Gecko/20100101 Firefox/29.0'
        self.session.headers = headers

    def auth(self, user, passw):
        """
        user and passwd must be in windows-1251 encoding!
        """
        #Take base cookie
        req = self.session.get(DIARY_MAIN_URL)
        the_page = req.text
        # auth
        m = search('(login.php.+?)"', the_page)
        DIARY_AUTH_URL = ''.join((DIARY_MAIN_URL, m.group() ))
        m = search('name="signature" value="(.+?)"', the_page)
        sig = m.group(1)
        values = {'user_login' : user,
          'user_pass' : passw,
          'save': 'on',
          'signature': sig,
          }
        req = self.session.post(DIARY_AUTH_URL, data=values)
        self.cookie.save(COOKIE_FILE)

    def request(self):
        req = self.session.get(DIARY_REQUEST_URL)
        return DiaryRuInfo(req.json())

    def close(self):
        self.cookie.save(COOKIE_FILE)

    def is_cookie_expired(self):
        """
        Cookie checker. True if cookies is expired.
        """
        epoha = int(time.time())
        for __cook in self.cookie:
            if __cook.is_expired(now=epoha):
                return True
        return False

    def is_cookie_exists(self):
        return pexists(COOKIE_FILE)