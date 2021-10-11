# -*- coding: utf-8 -*-
from collections import defaultdict
from contextlib import contextmanager
from typing import List
from zobang.chess_board.chess_board import ChessBoard
from zobang.constant import ChessPieceType, CONFIG
from zobang.strategy.action_message import ActionMessage


class WholeChessPosition:

    def __init__(self, *, chess_board: ChessBoard,
                 player_piece_type=ChessPieceType.WHITE_CHESS_PIECE):
        self.board_len = chess_board.row_num
        self.chess_board = chess_board
        self._position = [[ChessPieceType.NO_CHESS_PIECE
                           for _ in range(chess_board.row_num)]
                          for _ in range(chess_board.row_num)]
        for x, y in chess_board.white_position_info.iter_all_chess():
            self._position[x][y] = ChessPieceType.WHITE_CHESS_PIECE
        for x, y in chess_board.black_position_info.iter_all_chess():
            self._position[x][y] = ChessPieceType.BLACK_CHESS_PIECE
        self.player_piece_type = player_piece_type
        self.peer_piece_type = self.__opposite_piece_type(player_piece_type)
        self.last_move = []
        self.peer_last_move = []
        self.debug_is_win_point = False

    @staticmethod
    def __opposite_piece_type(piece_type: ChessPieceType):
        if piece_type == ChessPieceType.BLACK_CHESS_PIECE:
            return ChessPieceType.WHITE_CHESS_PIECE
        return ChessPieceType.BLACK_CHESS_PIECE

    @staticmethod
    def __patter(row, start, end):
        core_pattern = row[start: end + 1]
        if start - 1 >= 0 and row[start - 1] == ChessPieceType.NO_CHESS_PIECE:
            core_pattern = row[start - 1: end + 1]
        if end + 1 < len(row) and row[end+1] == ChessPieceType.NO_CHESS_PIECE:
            core_pattern.append(ChessPieceType.NO_CHESS_PIECE)
        for i, v in enumerate(core_pattern):
            if v != ChessPieceType.NO_CHESS_PIECE:
                core_pattern[i] = 1
            else:
                core_pattern[i] = 0
        return core_pattern

    def __single_row_pattern(self, *, piece_type: ChessPieceType,
                             row_position: List[ChessPieceType]):
        opposite_piece = self.__opposite_piece_type(piece_type)
        start_index, end_index, blank_num = None, None, 0
        pattern = []
        for i, p in enumerate(row_position):
            if p == piece_type:
                if start_index is None:
                    # 模式的起点
                    start_index = i
                end_index = i
                continue
            if start_index is not None:
                # 判断是否到了模式的终点, 当出现对方棋子，或是连续两个空位置时候，则为模式
                # 结束位置，开始下一轮模式的寻找
                if p == opposite_piece:
                    pattern.append(self.__patter(row_position, start_index,
                                                 end_index))
                    start_index, end_index, blank_num = None, None, 0
                    continue
                if p == ChessPieceType.NO_CHESS_PIECE:
                    blank_num += 1
                    if blank_num == 2:
                        pattern.append(self.__patter(row_position, start_index,
                                                     end_index))
                        start_index, end_index, blank_num = None, None, 0
                        continue
        if start_index is not None:
            pattern.append(self.__patter(row_position, start_index,
                                         end_index))
        return pattern

    @contextmanager
    def __fill_one_zero(self, row, index, value=1):
        origin = row[index]
        row[index] = value
        yield row
        row[index] = origin

    @staticmethod
    def __count_max_concurrent(row):
        max_count, count = 0, 0
        for v in row:
            if v == 1:
                count += 1
            else:
                if count > max_count:
                    max_count = count
                count = 0
        return max(max_count, count)

    def __row_count(self, row):
        pattern_count = defaultdict(int)
        for i, v in enumerate(row):
            if v == 0:
                with self.__fill_one_zero(row, i) as new_row:
                    pattern_count[self.__count_max_concurrent(new_row)] += 1
        if pattern_count:
            max_count = max(pattern_count.keys())
            return max_count, pattern_count[max_count]
        return len(row), 1

    def __row_score(self, row):
        if self.__count_max_concurrent(row) >= CONFIG['WIN_LINE_LEN']:
            return CONFIG['WIN_SCORE']
        count, number = self.__row_count(row)
        return (10 ** count) * number

    # pylint: disable=too-many-locals
    def __all_cared_rows(self, x, y):
        """
        only care the rows that in-line with (x, y)
        """
        edge_left = max(0, y - CONFIG['WIN_LINE_LEN'] + 1)
        edge_right = min(y + CONFIG['WIN_LINE_LEN'] - 1, self.board_len - 1)
        edge_up = max(0, x - CONFIG['WIN_LINE_LEN'] + 1)
        edge_down = min(x + CONFIG['WIN_LINE_LEN'] - 1, self.board_len - 1)
        row_l2r, row_u2d, row_lu2rd, row_ru2ld = [], [], [], []
        for _y in range(edge_left, edge_right + 1):
            row_l2r.append((x, _y))
        for _x in range(edge_up, edge_down + 1):
            row_u2d.append((_x, y))
        gap_left_up = min(x - edge_up, y - edge_left)
        gap_rigth_down = min(edge_down - x, edge_right - y)
        for i in range(-gap_left_up, gap_rigth_down + 1):
            _x, _y = x + i, y + i
            row_lu2rd.append((_x, _y))
        gap_right_up = min(x - edge_up, edge_right - y)
        gap_left_down = min(edge_down - x, y - edge_left)
        for i in range(-gap_right_up, gap_left_down + 1):
            _x, _y = x + i, y - i
            row_ru2ld.append((_x, _y))
        return [row_l2r, row_u2d, row_lu2rd, row_ru2ld]

    def __iter_all_player_cared_rows(self):
        for row in self.__all_cared_rows(self.last_move[-1][0],
                                         self.last_move[-1][1]):
            yield [self._position[x][y] for x, y in row]

    def __iter_all_peer_cared_rows(self):
        for row in self.__all_cared_rows(self.peer_last_move[-1][0],
                                         self.peer_last_move[-1][1]):
            yield [self._position[x][y] for x, y in row]

    def update(self, row, col, chess_piece_type: ChessPieceType):
        # print(row, col, chess_piece_type)
        if self._position[row][col] != ChessPieceType.NO_CHESS_PIECE:
            raise Exception('error update')
        self._position[row][col] = chess_piece_type
        self.chess_board.update(row, col, chess_piece_type)
        if chess_piece_type == self.player_piece_type:
            self.last_move.append((row, col))
        else:
            self.peer_last_move.append((row, col))

    def rollback(self, row, col, chess_piece_type: ChessPieceType):
        self._position[row][col] = ChessPieceType.NO_CHESS_PIECE
        self.chess_board.rollback(row, col, chess_piece_type)
        if chess_piece_type == self.player_piece_type:
            self.last_move.pop()
        else:
            self.peer_last_move.pop()

    @contextmanager
    def dry_run_update(self, row, col, chess_piece_type: ChessPieceType):
        self.update(row, col, chess_piece_type)
        yield
        self.rollback(row, col, chess_piece_type)

    def __min_search(self, possible_moves: List[tuple]):
        """
        这里的chess_piece_type一定是对方
        """
        min_score = 10 ** 50
        # print('需要在min层搜索的落子位置数: ', len(possible_moves))
        for x, y in possible_moves:
            player_score, peer_score = 0, 0
            # print('begin>>>>', datetime.now().strftime('%H:%M:%S'))
            with self.dry_run_update(x, y, self.peer_piece_type):
                for r in self.__iter_all_player_cared_rows():
                    for pattern in self.__single_row_pattern(
                            piece_type=self.player_piece_type, row_position=r):
                        if not pattern:
                            continue
                        player_score += self.__row_score(pattern)
                        if player_score >= CONFIG['WIN_SCORE']:
                            return CONFIG['WIN_SCORE']
                for r in self.__iter_all_peer_cared_rows():
                    for pattern in self.__single_row_pattern(
                            piece_type=self.peer_piece_type, row_position=r):
                        if not pattern:
                            continue
                        peer_score += self.__row_score(pattern)
            # print('end>>>>', datetime.now().strftime('%H:%M:%S'))
            if player_score - peer_score < min_score:
                min_score = player_score - peer_score
        return min_score

    def __nearby_moves(self, x, y):
        blank_positions = set()
        near_len = 1
        y_left = max(y - near_len, 0)
        y_right = min(y + near_len, CONFIG['CHESS_MAX_ROW'] - 1)
        x_up = max(x - near_len, 0)
        x_down = min(x + near_len, CONFIG['CHESS_MAX_ROW'] - 1)
        for _x in range(x_up, x_down + 1):
            for _y in range(y_left, y_right + 1):
                if self._position[_x][_y] == ChessPieceType.NO_CHESS_PIECE:
                    blank_positions.add((_x, _y))
        return blank_positions

    def __cared_pieces(self, x, y, chess_piece_type: ChessPieceType):
        ret = set()
        for row in self.__all_cared_rows(x, y):
            for _x, _y in row:
                if self._position[_x][_y] == chess_piece_type:
                    ret.add((_x, _y))
        return ret

    def __player_cared_moves(self):
        blank_positions = set()
        if not self.last_move:
            blank_positions |= set(self.__middle_two_position())
        else:
            for x, y in self.__cared_pieces(
                    self.last_move[-1][0], self.last_move[-1][1],
                    self.player_piece_type):
                blank_positions |= self.__nearby_moves(x, y)
        return blank_positions

    def __peer_cared_moves(self):
        blank_positions = set()
        if not self.peer_last_move:
            blank_positions |= set(self.__middle_two_position())
        else:
            for x, y in self.__cared_pieces(
                    self.peer_last_move[-1][0], self.peer_last_move[-1][1],
                    self.peer_piece_type):
                blank_positions |= self.__nearby_moves(x, y)
        return blank_positions

    def __possible_near_moves(self):
        blank_positions = set()
        blank_positions |= self.__player_cared_moves()
        blank_positions |= self.__peer_cared_moves()
        return blank_positions

    def __middle_two_position(self):
        mid = int(self.board_len / 2)
        blank_positions = set()
        for x in [mid, mid + 1]:
            if self._position[x][mid] == ChessPieceType.NO_CHESS_PIECE:
                blank_positions.add((x, mid))
        # print("MID===", blank_positions)
        return blank_positions

    def __possible_moves(self):
        return self.__possible_near_moves()

    def __max_min_search(self, possible_moves: List[tuple]):
        """
        这里的chess_piece_type一定是本方
        """
        max_score, move = - (10 ** 60), None
        for x, y in possible_moves:
            with self.dry_run_update(x, y, self.player_piece_type):
                # 首先需要生成此种情况下对方可能的moves
                min_layer_moves = self.__possible_moves()
                # print("MIN>>>", min_layer_moves)
                min_score = self.__min_search(min_layer_moves)
                if min_score > max_score:
                    max_score = min_score
                    move = (x, y)
                    # print(max_score, move)
        return move

    def max_min_search(self):
        possible_moves = self.__possible_moves()
        # print('MAX层节点数目: ', len(possible_moves))
        return self.__max_min_search(possible_moves)


class MaxMinPlay:

    def __init__(self, chess_board: ChessBoard, piece_type: ChessPieceType):
        self.chess_board = chess_board
        self.player = WholeChessPosition(chess_board=self.chess_board,
                                         player_piece_type=piece_type)
        self.piece_type = piece_type
        if piece_type == ChessPieceType.WHITE_CHESS_PIECE:
            self.opposite_piece_type = ChessPieceType.BLACK_CHESS_PIECE
        else:
            self.opposite_piece_type = ChessPieceType.WHITE_CHESS_PIECE

    @property
    def position_info(self):
        if self.piece_type == ChessPieceType.WHITE_CHESS_PIECE:
            return self.chess_board.white_position_info
        if self.piece_type == ChessPieceType.BLACK_CHESS_PIECE:
            return self.chess_board.black_position_info
        raise Exception('not get self piece type')

    def react(self, action_msg: ActionMessage):
        ret = dict(finished=False, equal=False, win=False, msg=None)
        self.player.update(action_msg.row, action_msg.col,
                           self.opposite_piece_type)
        move = self.player.max_min_search()
        self.player.update(move[0], move[1], self.player.player_piece_type)
        msg = ActionMessage(row=move[0], col=move[1])
        ret['msg'] = msg
        if self.position_info.is_win():
            ret['finished'] = True
            ret['win'] = True
        return ret
