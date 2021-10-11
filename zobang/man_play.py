# -*- coding: utf-8 -*-

from tkinter import Tk, Canvas, messagebox
from zobang.chess_board.chess_board import ChessBoard
from zobang.constant import ChessPieceType
from zobang.strategy.max_min_play import MaxMinPlay
from zobang.strategy.action_message import ActionMessage


# pylint: disable=too-many-instance-attributes
class ManPlay:

    def __init__(self, piece_type=ChessPieceType.WHITE_CHESS_PIECE):
        self.lattice_width = 30
        self.chess_board = ChessBoard()
        self.lattice_number = self.chess_board.row_num
        self.piece_type = piece_type
        if piece_type == ChessPieceType.WHITE_CHESS_PIECE:
            self.opposite_piece_type = ChessPieceType.BLACK_CHESS_PIECE
        else:
            self.opposite_piece_type = ChessPieceType.WHITE_CHESS_PIECE
        self.peer_player = MaxMinPlay(
            chess_board=self.chess_board,
            piece_type=self.opposite_piece_type)
        self.__window_init()
        self.__peer_last_move_sign = []

    @property
    def position_info(self):
        if self.piece_type == ChessPieceType.WHITE_CHESS_PIECE:
            return self.chess_board.white_position_info
        if self.piece_type == ChessPieceType.BLACK_CHESS_PIECE:
            return self.chess_board.black_position_info
        raise Exception('not get self piece type')

    @property
    def play_color(self):
        if self.piece_type == ChessPieceType.WHITE_CHESS_PIECE:
            return 'red'
        if self.piece_type == ChessPieceType.BLACK_CHESS_PIECE:
            return 'black'
        raise Exception('not get self piece type')

    @property
    def peer_color(self):
        return 'black' if self.play_color == 'red' else 'red'

    def __window_init(self):
        windows = Tk()
        windows.title('Checker board')
        # 设置画布的大小为640 * 640的正方形
        canvas = Canvas(windows, width=self.lattice_width * self.lattice_number,
                        height=self.lattice_width * self.lattice_number,
                        bg='white')
        # 将canvas放入容器中
        canvas.pack()
        for i in range(self.lattice_number):
            x1 = 0
            y1 = 0 + i * self.lattice_width
            x2 = self.lattice_width
            y2 = self.lattice_width + i * self.lattice_width
            for _ in range(self.lattice_number):
                canvas.create_rectangle(x1, y1, x2, y2)
                x1 += self.lattice_width
                x2 += self.lattice_width
        self.windows = windows
        self.canvas = canvas
        self.windows.bind('<Button-1>', self.__click)

    def run(self):
        self.windows.mainloop()

    def __move(self, row, col, piece_type, color):
        x1 = col * self.lattice_width
        y1 = row * self.lattice_width
        x2 = x1 + self.lattice_width
        y2 = y1 + self.lattice_width
        self.chess_board.update(row, col, piece_type)
        self.canvas.create_oval(x1, y1, x2, y2, fill=color)

    def __player_move(self, row, col):
        self.__move(row, col, self.piece_type, self.play_color)

    def __peer_move(self, row, col):
        if self.__peer_last_move_sign:
            for s in self.__peer_last_move_sign:
                self.canvas.delete(s)
        self.__move(row, col, self.opposite_piece_type, self.peer_color)
        x1 = col * self.lattice_width
        y1 = row * self.lattice_width
        x2 = x1 + self.lattice_width
        y2 = y1 + self.lattice_width
        sign_x, sign_y = (x1+x2) / 2, (y1+y2) / 2
        sign_len = 3
        self.__peer_last_move_sign = [
            self.canvas.create_line(sign_x-sign_len, sign_y,
                                    sign_x+sign_len, sign_y, fill='yellow'),
            self.canvas.create_line(sign_x, sign_y - sign_len,
                                    sign_x, sign_y + sign_len, fill='yellow')]

    def __click(self, event):
        row = int(event.y / self.lattice_width)
        col = int(event.x / self.lattice_width)
        self.__player_move(row, col)
        if self.position_info.is_win():
            print(f'{self.piece_type.name} WIN!!')
            messagebox.showinfo('消息', '你赢了!!!')
            return
        msg = ActionMessage(row=row, col=col)
        ret_peer = self.peer_player.react(action_msg=msg)
        self.react(ret_peer)

    def react(self, ret_peer):
        action_msg = ret_peer['msg']
        self.__peer_move(action_msg.row, action_msg.col)
        if ret_peer['finished']:
            if ret_peer['win']:
                messagebox.showinfo('消息', '你输了!!!')
