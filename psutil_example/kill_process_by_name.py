#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


import psutil

for process in psutil.process_iter():
    if process.name() == 'calc.exe':
        process.kill()
