# -*- coding: utf-8 -*-


class ActionMessage:

    def __init__(self, *, row, col, **kwargs):
        self.row = row
        self.col = col
