#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для проверки новых сообщений на сервисе diary.ru, написанный с использованием
Python 2.7 и кросплатфореммного GUI wxWidgets.
При появлении новых сообщений меняет цвет иконки на панели управления.
"""

TIMER_INTERVAL = 5*60 # value in seconds

import wx
import os

TRAY_TOOLTIP = 'DiaryRuInfo'
pjoin = os.path.join
pdirname = os.path.dirname
res_path = pjoin(pdirname(pdirname(__file__)), 'images')
TRAY_ICON = pjoin(res_path, 'icon.png')
TRAY_ICON_NEW_MESS = pjoin(res_path, 'icon2.png')

try:
    from requestsDiaryRuHTTPClient import DiaryRuHTTPClient
except ImportError as e:
    from urllibDiaryRuHTTPClient import DiaryRuHTTPClient

wxID_OK = wx.ID_OK
wxOK = wx.OK
try:
    import urllib2
except ImportError as e:
    import urllib.request as urllib2

def call_auth_dialog():
    """
    Call AuthDialog and then
    return (user, password) or (None, None)
    """
    from wxAuthDialog import AuthDialog
    dialog = AuthDialog()
    account = None, None
    if dialog.ShowModal() == wxID_OK:
        u, p = dialog.GetValues()
        USER = u.encode('windows-1251')
        PASSW = p.encode('windows-1251')
        account = USER, PASSW
    wx.CallAfter(dialog.Destroy)
    return account

ID_ICON_TIMER = wx.NewId()

wxMenuItem = wx.MenuItem
wxEVT_MENU = wx.EVT_MENU

def create_menu_item(menu, label, func):
    item = wxMenuItem(menu, -1, label)
    menu.Bind(wxEVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)

def show_message_box(message, title=u'Diary.Ru Error'):
    if not isinstance(message, unicode):
        message = unicode(message)
    if not isinstance(title, unicode):
        title = unicode(title)
    dlg = wx.MessageDialog(None, message, title,
              wxOK | wx.ICON_WARNING)
    dlg.ShowModal()

class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, diary):
        super(TaskBarIcon, self).__init__()
        self.default_icon = TaskBarIcon.load_icon(TRAY_ICON)
        self.new_mess_icon = TaskBarIcon.load_icon(TRAY_ICON_NEW_MESS)
        self.SetIcon(self.default_icon)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.diary = diary
        self.favorite_url = None
        self.menu = self.CreatePopupMenu()
        self.icon_timer = None
        self.time = TIMER_INTERVAL

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Open Umails', self.on_open_diary_umails)
        create_menu_item(menu, 'Open favorite', self.on_open_diary_favorite)
        menu.AppendSeparator()
        create_menu_item(menu, 'Check diary', self.timer_event_handler)
        create_menu_item(menu, 'Set timer interval', self.on_set_timer_interval)
        create_menu_item(menu, 'Authorization', self.on_authorization)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    @staticmethod
    def load_icon(path):
        return wx.IconFromBitmap(wx.Bitmap(path))

    def set_default_icon(self, tooltip=TRAY_TOOLTIP):
        if not isinstance(tooltip, unicode):
            tooltip = unicode(tooltip)
        self.SetIcon(self.default_icon, tooltip)

    def set_new_messages_icon(self, tooltip=TRAY_TOOLTIP):
        if not isinstance(tooltip, unicode):
            tooltip = unicode(tooltip)
        self.SetIcon(self.new_mess_icon, tooltip)

    def on_left_down(self, event):
        self.PopupMenu(self.menu)

    def on_open_diary_umails(self, event):
        from webbrowser import open as wopen
        wopen("http://www.diary.ru/u-mail/folder/?f_id=1")

    def on_open_diary_favorite(self, event):
        from webbrowser import open as wopen
        wopen(self.favorite_url or DIARY_MAIN_URL)

    def on_exit(self, event):
        self.icon_timer.Stop()
        self.diary.close()
        self.Destroy()

    def set_icon_timer(self, time=None):
        if time is not None:
            self.time = time * 1000 # secunds
        if self.icon_timer is None:
            self.icon_timer = wx.Timer(self, ID_ICON_TIMER)
            wx.EVT_TIMER(self, ID_ICON_TIMER, self.timer_event_handler)
        self.icon_timer.Start(self.time)

    def do_diary_request(self):
        data = self.diary.request()
        if data is None:
            self.set_default_icon(self.diary.error)
            show_message_box(self.diary.error)
        elif data.has_error():
            self.icon_timer.Stop()
            show_message_box(data)
            self.set_default_icon(data)
            self.on_authorization(None)
        elif data.is_empty():
            self.set_default_icon(data)
        else:
            self.set_new_messages_icon(data)
            if self.favorite_url is None:
                self.favorite_url = "http://%s.diary.ru/?favorite" %data.get_shortusername()

    def timer_event_handler(self, event):
        wx.CallAfter(self.do_diary_request)

    def on_authorization(self, event):
        self.icon_timer.Stop()
        u, p = call_auth_dialog()
        if u is not None and p is not None:
            if self.diary.auth(u, p) is not None:
                show_message_box(self.diary.error)
                return
            self.do_diary_request()
            self.icon_timer.Start(self.time)

    def on_set_timer_interval(self, event):
        self.icon_timer.Stop()
        dialog = wx.TextEntryDialog(None,
            "What timer interval you want to set?",
            "Timer interval", "300", style=wxOK|wx.CANCEL)
        if dialog.ShowModal() == wxID_OK:
            self.set_icon_timer(int(dialog.GetValue()))
        else:
            self.set_icon_timer()
        dialog.Destroy()


class App(wx.PySimpleApp):
    def OnInit(self):
        d = DiaryRuHTTPClient()
        if (not d.is_cookie_exists()) or d.is_cookie_expired():
            u, p = call_auth_dialog()
            if u is None or p is None:
                app.Exit()
                exit()
            if d.auth(u, p) is not None:
                show_message_box(d.error)
        t = TaskBarIcon(d)
        wx.CallAfter(t.do_diary_request)
        t.set_icon_timer(TIMER_INTERVAL)
        return True

def main():
    app = App()
    app.MainLoop()

if __name__ == '__main__':
    main()