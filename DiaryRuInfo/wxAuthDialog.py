#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx

class AuthDialog(wx.Dialog):
    def __init__(self, title="Authorization"):
        wx.Dialog.__init__(self, None, -1, title)
        wxStaticText= wx.StaticText
        wxTextCtrl = wx.TextCtrl
        wxButton = wx.Button
        about = wxStaticText(self, -1, "Enter login and password")
        login_l = wxStaticText(self, -1, "login:")
        pass_l = wxStaticText(self, -1, "password:")

        self.login_t = wxTextCtrl(self)
        self.pass_t = wxTextCtrl(self)
        okay = wxButton(self, wx.ID_OK)
        okay.SetDefault()
        cancel = wxButton(self, wx.ID_CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizerAdd = sizer.Add
        sizerAdd(about, 0, wx.ALL, 5)
        sizerAdd(wx.StaticLine(self), 0, wx.EXPAND|wx.ALL, 5)

        fgs = wx.FlexGridSizer(3, 2, 5, 5)
        fgsAdd = fgs.Add
        fgsAdd(login_l, 0, wx.ALIGN_RIGHT)
        fgsAdd(self.login_t, 0, wx.EXPAND)
        fgsAdd(pass_l, 0, wx.ALIGN_RIGHT)
        fgsAdd(self.pass_t, 0, wx.EXPAND)
        fgs.AddGrowableCol(1)
        sizerAdd(fgs, 0, wx.EXPAND|wx.ALL, 5)

        btns = wx.StdDialogButtonSizer()
        btnsAddButton = btns.AddButton
        btnsAddButton(okay)
        btnsAddButton(cancel)
        btns.Realize()
        sizerAdd(btns, 0, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

    def GetValues(self):
        return self.login_t.GetValue(), self.pass_t.GetValue()