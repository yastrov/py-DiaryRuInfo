#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
COOKIE_FILE = os.path.join( os.path.expanduser('~'),
                            'diary_cookie.data')

import requests
from requests.exceptions import (
            ConnectionError,
            ConnectTimeout,
            ReadTimeout,
            HTTPError)
try:
    import cookielib
except ImportError as e:
    import http.cookiejar as cookielib

from DiaryRuInfo.DiaryRuInfo import DiaryRuInfo

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
        self.__get = self.session.get
        self.__post = self.session.post
        self.session.cookies = self.cookie
        headers = self.session.headers
        headers['Accept-encoding'] = 'utf-8'
        headers['User-agent'] = 'Mozilla/5.0 (Windows NT 6.1; rv:29.0) Gecko/20100101 Firefox/29.0'
        self.session.headers = headers
        self.error = None

    def auth(self, user, passw):
        """
        Auth on service.
        Return None or error!
        user and passwd must be in windows-1251 encoding!
        """
        if not isinstance(user, bytes):
            user = user.encode('windows-1251')
        if not isinstance(passw, bytes):
            passw = passw.encode('windows-1251')
        #Take base cookie
        the_page = None
        self.error = None
        try:
            req = self.__get(DIARY_MAIN_URL)
            if req.status_code != 200:
                self.error = req.reason
                return self.error
            the_page = req.text
        except ConnectionError:
            self.error = "DNS Exception! Can't find diary.ru domain."
        except ConnectTimeout:
            self.error = "Too slow for receiving response!"
        except ReadTimeout:
            self.error = "Waited too long between bytes."
        except HTTPError as e:
            self.error = e.message
        if self.error: return self.error
        # auth
        m = search('(login.php.+?)"', the_page)
        DIARY_AUTH_URL = ''.join((DIARY_MAIN_URL, m.group() ))
        m = search('name="signature" value="(.+?)"', the_page)
        self.error = None
        try:
            req = self.__post(DIARY_AUTH_URL, data=
                                {'user_login': user,
                                  'user_pass': passw,
                                  'save': 'on',
                                  'signature': m.group(1),})
            if req.status_code != 200:
                self.error = req.reason
                return self.error
            self.cookie.save(COOKIE_FILE)
        except ConnectionError:
            self.error="DNS Exception! Can't find diary.ru domain."
        except ConnectTimeout:
            self.error="Too slow for receiving response!"
        except ReadTimeout:
            self.error="Waited too long between bytes."
        except HTTPError as e:
            self.error=e.message
        return self.error

    def request(self):
        """
        Request, return DiaryRuInfo or, if error: None.
        For get message, take DiaryRuHTTPClient().error.
        """
        self.error = None
        try:
            req = self.__get(DIARY_REQUEST_URL)
            if req.status_code != 200:
                self.error = req.reason
                return None
            return DiaryRuInfo(req.json())
        except ValueError:
            self.error='Cant decode as JSON: %s' %req.text
        except ConnectionError:
            self.error="DNS Exception! Can't find diary.ru domain."
        except ConnectTimeout:
            self.error="Too slow for receiving response!"
        except ReadTimeout:
            self.error="Waited too long between bytes."
        except HTTPError as e:
            self.error=e.message
        return None

    def close(self):
        self.session.close()
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