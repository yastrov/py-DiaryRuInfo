#!/usr/bin/env python
# -*- coding: utf-8 -*-

class DiaryRuInfo(object):
    def __init__(self, data):
        self._jsonData = data

    def has_error(self):
        if self._jsonData.get('error', None) is not None:
            return True
        return False

    def is_empty(self):
        if self._jsonData["newcomments"]["count"] != "0":
            return False
        elif self._jsonData["discuss"]["count"] != "0":
            return False
        elif self._jsonData["umails"]["count"] != "0":
            return False
        return True

    def get_shortusername(self):
        return self._jsonData["userinfo"]["shortname"]

    def __unicode__(self):
        error = self._jsonData.get('error', None)
        if not error is None:
            return unicode(error)
        data = self._jsonData
        return u"".join((data["userinfo"]["username"], u"\n",
                u"Comments: ", data["newcomments"]["count"], u"\n",
                u"Discuss: ", data["discuss"]["count"], u"\n",
                u"Umails: ", data["umails"]["count"],)
                )

    def __str__(self):
        error = self._jsonData.get('error', None)
        if not error is None:
            return error
        data = self._jsonData
        return "".join((data["userinfo"]["username"], "\n",
                "Comments: ", data["newcomments"]["count"], "\n",
                "Discuss: ", data["discuss"]["count"], "\n",
                "Umails: ", data["umails"]["count"],)
                )