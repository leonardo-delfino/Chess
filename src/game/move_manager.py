from hashids import Hashids
from src.utils import constants as const


class MoveManager(object):
    ranks_to_rows = {
        "1": 7,
        "2": 6,
        "3": 5,
        "4": 4,
        "5": 3,
        "6": 2,
        "7": 1,
        "8": 0
    }

    rows_to_ranks = {
        v: k for k, v in ranks_to_rows.items()
    }

    files_to_cols = {
        "a": 0,
        "b": 1,
        "c": 2,
        "d": 3,
        "e": 4,
        "f": 5,
        "g": 6,
        "h": 7
    }

    cols_to_files = {
        v: k for k, v in files_to_cols.items()
    }

    def __init__(self, start, end, board, en_passant=False, pawn_promotion=False, castle=False):
        self.board = board

        self.start_row = start[0]
        self.start_col = start[1]
        self.end_row = end[0]
        self.end_col = end[1]

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        self.en_passant = en_passant
        if en_passant:
            self.piece_captured = const.BLACK_PAWN if self.piece_moved == const.WHITE_PAWN else const.WHITE_PAWN

        self.pawn_promotion = pawn_promotion

        self.castle = castle

        self.move_ID = Hashids().encode(self.start_row, self.start_col, self.end_row, self.end_col)

    def __get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]

    def get_chess_notation(self):
        return "{} {} {}".format(
            self.board[self.start_row][self.start_col],
            self.__get_rank_file(self.start_row, self.start_col),
            self.__get_rank_file(self.end_row, self.end_col)
        )

    def __eq__(self, obj):
        return (obj.move_ID == self.move_ID) if isinstance(obj, MoveManager) else False
