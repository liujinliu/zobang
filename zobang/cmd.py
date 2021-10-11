# -*- coding: utf-8 -*-
from zobang.man_play import ManPlay
from zobang.constant import ChessPieceType


def game_start():
    ManPlay(piece_type=ChessPieceType.WHITE_CHESS_PIECE).run()
