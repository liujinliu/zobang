# -*- coding: utf-8 -*-
from enum import Enum


CONFIG = {
    'CHESS_MAX_ROW': 20,
    'WIN_LINE_LEN': 5,
    'WIN_SCORE': 10 ** 40
}


class ChessPieceType(Enum):
    NO_CHESS_PIECE = 0
    WHITE_CHESS_PIECE = 1
    BLACK_CHESS_PIECE = 2
