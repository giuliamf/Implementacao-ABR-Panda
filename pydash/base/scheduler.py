# -*- coding: utf-8 -*-
"""
@author: Marcos F. Caetano (mfcaetano@unb.br) 11/03/2020

@description: PyDash Project

The Scheduler is a Singleton class implementation
"""

import pydash.base.singleton as singleton


class Scheduler(metaclass=singleton.Singleton):

    def __init__(self):
        self.events = []

    def add_event(self, event):
        self.events.append(event)

    def get_event(self):
        return self.events.pop(0)

    def is_empty(self):
        return bool(self.events == [])
