#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
COOKIE_FILE = os.path.join( os.path.expanduser('~'),
                            'diary_cookie.data')

import urllib
try:
    import urllib2
except ImportError as e:
    import urllib.request as urllib2
try:
    import cookielib
except ImportError as e:
    import http.cookies as cookielib

from DiaryRuInfo import DiaryRuInfo

import json
jsonLoads = json.loads
from re import search
import time

DIARY_MAIN_URL = 'http://www.diary.ru/'
DIARY_REQUEST_URL = "http://pay.diary.ru/yandex/online.php"

urllib2Request = urllib2.Request
urllib2urlopen = urllib2.urlopen

pexists = os.path.exists

class DiaryRuHTTPClient(object):
    def __init__(self):
        self.cookie = cookielib.LWPCookieJar()
        if pexists(COOKIE_FILE):
            self.cookie.load(COOKIE_FILE)
        urllib2.install_opener(urllib2.build_opener(
                                urllib2.HTTPCookieProcessor(self.cookie)
                                )
                            )
        self.headers = {
                        'Accept-encoding': 'utf-8',
                        'User-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:29.0) Gecko/20100101 Firefox/29.0'
                    }

    def auth(self, user, passw):
        """
        user and passwd must be in windows-1251 encoding!
        """
        #Take base cookie
        req = urllib2Request(DIARY_MAIN_URL, headers=self.headers)
        response = urllib2urlopen(req)
        the_page = response.read()
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
        data = urllib.urlencode(values)
        req = urllib2Request(DIARY_AUTH_URL, data=data, headers=self.headers)
        req.add_header('Referer', DIARY_MAIN_URL)
        response = urllib2urlopen(req)
        the_page = response.read()
        self.cookie.save(COOKIE_FILE)

    def request(self):
        req = urllib2Request(DIARY_REQUEST_URL, headers=self.headers)
        response = urllib2urlopen(req)
        the_page = response.read()
        return DiaryRuInfo(jsonLoads(the_page))

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