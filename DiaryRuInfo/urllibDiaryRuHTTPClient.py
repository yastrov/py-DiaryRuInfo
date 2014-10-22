#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
COOKIE_FILE = os.path.join( os.path.expanduser('~'),
                            'diary_cookie.data')

import urllib
import urllib.request as urllib_request
from urllib.error import URLError, HTTPError
import http.cookiejar as cookielib
from urllib.parse import urlencode

from DiaryRuInfo.DiaryRuInfo import DiaryRuInfo

import json
jsonLoads = json.loads
from re import search
import time

DIARY_MAIN_URL = 'http://www.diary.ru/'
DIARY_REQUEST_URL = "http://pay.diary.ru/yandex/online.php"

urllib_req = urllib_request.Request
urllib_uopen = urllib_request.urlopen

pexists = os.path.exists

class DiaryRuHTTPClient(object):
    def __init__(self):
        self.cookie = cookielib.LWPCookieJar()
        if pexists(COOKIE_FILE):
            self.cookie.load(COOKIE_FILE)
        urllib_request.install_opener(urllib_request.build_opener(
                                urllib_request.HTTPCookieProcessor(self.cookie)
                                )
                            )
        self.headers = {
                        'Accept-encoding': 'utf-8',
                        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:29.0) Gecko/20100101 Firefox/29.0'
                    }
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
            req = urllib_req(DIARY_MAIN_URL,
                                    headers=self.headers)
            response = urllib_uopen(req)
            the_page = response.read()
        except URLError as e:
            self.error = e.reason
        except HTTPError as e:
            self.error = e.reason
        if self.error: return self.error
        # auth
        m = search('(login.php.+?)"',
                    the_page.decode('windows-1251', 'ignore'))
        DIARY_AUTH_URL = ''.join((DIARY_MAIN_URL, m.group() ))
        m = search('name="signature" value="(.+?)"',
                    the_page.decode('windows-1251', 'ignore'))
        data = urlencode({'user_login': user,
                          'user_pass': passw,
                          'save': 'on',
                          'signature': m.group(1),
                          })
        self.error = None
        try:
            req = urllib_req(DIARY_AUTH_URL,
                                data=data.encode('windows-1251'),
                                headers=self.headers)
            req.add_header('Referer', DIARY_MAIN_URL)
            response = urllib_uopen(req)
            the_page = response.read()
        except URLError as e:
            self.error = e.reason
        except HTTPError as e:
            self.error = e.reason
        self.cookie.save(COOKIE_FILE)
        return self.error

    def request(self):
        """
        Request, return DiaryRuInfo or, if error: None.
        For get message, take DiaryRuHTTPClient().error.
        """
        self.error = None
        try:
            req = urllib_req(DIARY_REQUEST_URL,
                             headers=self.headers)
            response = urllib_uopen(req)
            the_page = response.read()
            return DiaryRuInfo(jsonLoads(
                    the_page.decode('utf-8', 'ignore')))
        except ValueError:
            self.error='Cant decode as JSON: %s' %the_page
        except URLError as e:
            self.error = e.reason
        except HTTPError as e:
            self.error = e.reason
        return None

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