#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Скрипт для проверки новых сообщений на сервисе diary.ru, написанный с использованием
Python 2.7 и кросплатфореммного GUI wxWidgets.
При появлении новых сообщений меняет цвет иконки на панели управления.
"""
from DiaryRuInfo.wxdiary import main

if __name__ == '__main__':
    main()