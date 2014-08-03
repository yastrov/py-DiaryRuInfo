#!/usr/bin/env python
# -*- coding: utf-8 -*-

class DiaryRuInfo(object):
    def __init__(self, data):
        self.jsonData = data

    def has_error(self):
        if self.jsonData.get('error', None) is not None:
            return True
        return False

    def is_empty(self):
        if self.jsonData["newcomments"]["count"] != "0":
            return True
        elif self.jsonData["discuss"]["count"] != "0":
            return True
        elif self.jsonData["umails"]["count"] != "0":
            return True

    def get_shortusername(self):
        return self.jsonData["userinfo"]["shortname"]

    def __unicode__(self):
        data = self.jsonData
        return u"".join((data["userinfo"]["username"], u"\n",
                u"Comments: ", data["newcomments"]["count"], u"\n",
                u"Discuss: ", data["discuss"]["count"], u"\n",
                u"Umails: ", data["umails"]["count"],)
                )

    def to_unicode_str(self):
        return self.__unicode__()