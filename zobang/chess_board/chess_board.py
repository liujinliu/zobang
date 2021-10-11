# -*- coding: utf-8 -*-
import random
from zobang.constant import ChessPieceType, CONFIG


class PiecePositionInfo:

    def __init__(self, row):
        self.row_num = row
        self._chess = [[0 for _ in range(row)] for _ in range(row)]
        self.__last_chess = None
        self.__left_edge = set()
        self.__up_edge = set()
        self.__left_up_edge = set()
        self.__right_up_edge = set()

    @property
    def all_chess(self):
        return self._chess

    def iter_all_chess(self):
        for x in range(self.row_num):
            for y in range(self.row_num):
                if self._chess[x][y] == 1:
                    yield x, y

    @property
    def last_chess(self):
        return self.__last_chess

    def add(self, x, y):
        self._chess[x][y] = 1
        self.__last_chess = (x, y)

    def remove(self, x, y):
        self._chess[x][y] = 0

    def random_piece(self):
        piece_set = []
        for x in range(self.row_num):
            for y in range(self.row_num):
                if self._chess[x][y] == 1:
                    piece_set.append((x, y))
        if not piece_set:
            return None
        return random.sample(piece_set, 1)[0]

    def __left_piece(self, x, y, i):
        return x, y - i

    def __right_piece(self, x, y, i):
        return x, y + i

    def __up_piece(self, x, y, i):
        return x - i, y

    def __down_piece(self, x, y, i):
        return x + i, y

    def __left_up_piece(self, x, y, i):
        return x - i, y - i

    def __right_up_piect(self, x, y, i):
        return x - i, y + i

    def __left_down_piece(self, x, y, i):
        return x + i, y - i

    def __right_down_piece(self, x, y, i):
        return x + i, y + i

    def __chess_edge_calc(self, x, y, piece_func):
        ret = (x, y)
        for i in range(1, CONFIG['WIN_LINE_LEN']):
            _x, _y = piece_func(x, y, i)
            if not (0 <= _x < self.row_num and 0 <= _y < self.row_num):
                break
            if self._chess[_x][_y] == 1:
                ret = piece_func(x, y, i)
            else:
                break
        return ret

    def __last_chess_edge(self, piece_func):
        x, y = self.__last_chess
        return self.__chess_edge_calc(x, y, piece_func)

    def __chess_left_edge(self, x, y):
        return self.__chess_edge_calc(x, y, self.__left_piece)

    def __chess_right_edge(self, x, y):
        return self.__chess_edge_calc(x, y, self.__right_piece)

    def __chess_up_edge(self, x, y):
        return self.__chess_edge_calc(x, y, self.__up_piece)

    def __chess_left_up_edge(self, x, y):
        return self.__chess_edge_calc(x, y, self.__left_up_piece)

    def __chess_left_down_edge(self, x, y):
        return self.__chess_edge_calc(x, y, self.__left_down_piece)

    def __chess_right_up_edge(self, x, y):
        return self.__chess_edge_calc(x, y, self.__right_up_piect)

    def __chess_right_down_edge(self, x, y):
        return self.__chess_edge_calc(x, y, self.__right_down_piece)

    def __last_chess_left_edge(self):
        return self.__last_chess_edge(self.__left_piece)

    def __last_chess_right_edge(self):
        return self.__last_chess_edge(self.__right_piece)

    def __last_chess_up_edge(self):
        return self.__last_chess_edge(self.__up_piece)

    def __last_chess_down_edge(self):
        return self.__last_chess_edge(self.__down_piece)

    def __last_chess_right_up_edge(self):
        return self.__last_chess_edge(self.__right_up_piect)

    def __last_chess_right_down_edge(self):
        return self.__last_chess_edge(self.__right_down_piece)

    def __last_chess_left_up_edge(self):
        return self.__last_chess_edge(self.__left_up_piece)

    def __last_chess_left_down_edge(self):
        return self.__last_chess_edge(self.__left_down_piece)

    def __search_win(self, piece_func):
        x, y = self.__last_chess_edge(piece_func)
        for i in range(1, CONFIG['WIN_LINE_LEN']):
            _x, _y = piece_func(x, y, -i)
            if not (0 <= _x < self.row_num and 0 <= _y < self.row_num):
                return False
            if self._chess[_x][_y] == 0:
                return False
        return True

    def __search_left_win(self):
        return self.__search_win(self.__left_piece)

    def __search_right_win(self):
        return self.__search_win(self.__right_piece)

    def __search_up_win(self):
        return self.__search_win(self.__up_piece)

    def __search_down_win(self):
        return self.__search_win(self.__down_piece)

    def __search_left_up_win(self):
        return self.__search_win(self.__left_up_piece)

    def __search_right_up_win(self):
        return self.__search_win(self.__right_up_piect)

    def __search_left_down_win(self):
        return self.__search_win(self.__left_down_piece)

    def __search_right_down_win(self):
        return self.__search_win(self.__right_down_piece)

    def is_win(self):
        return (self.__last_chess and (self.__search_left_win()
                or self.__search_right_win() or self.__search_up_win()
                or self.__search_down_win() or self.__search_left_up_win()
                or self.__search_right_up_win() or self.__search_left_down_win()
                or self.__search_right_down_win()))


class ChessBoard:

    def __init__(self):
        self._max_row = CONFIG['CHESS_MAX_ROW']
        self.white_position_info = PiecePositionInfo(self._max_row)
        self.black_position_info = PiecePositionInfo(self._max_row)
        self.no_piece_info = PiecePositionInfo(self._max_row)
        for x in range(self._max_row):
            for y in range(self._max_row):
                self.no_piece_info.add(x, y)

    @property
    def row_num(self):
        return self._max_row

    def update(self, row, col, chess_piece_type: ChessPieceType):
        if chess_piece_type == ChessPieceType.WHITE_CHESS_PIECE:
            self.white_position_info.add(row, col)
        else:
            self.black_position_info.add(row, col)
        self.no_piece_info.remove(row, col)

    def rollback(self, row, col, chess_piece_type: ChessPieceType):
        if chess_piece_type == ChessPieceType.WHITE_CHESS_PIECE:
            self.white_position_info.remove(row, col)
        else:
            self.black_position_info.remove(row, col)
        self.no_piece_info.add(row, col)

    def chess_board_paint(self):
        for x in range(self._max_row):
            line = ''
            for y in range(self._max_row):
                if self.no_piece_info.all_chess[x][y] == 1:
                    line += '. '
                    continue
                if self.white_position_info.all_chess[x][y] == 1:
                    if (x, y) == self.white_position_info.last_chess:
                        line += 'X '
                    else:
                        line += 'X '
                    continue
                if self.black_position_info.all_chess[x][y] == 1:
                    if (x, y) == self.black_position_info.last_chess:
                        line += 'O '
                    else:
                        line += 'O '
                    continue
            print(line)
