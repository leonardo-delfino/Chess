import numpy as np
from src.utils import constants as const
from src.game.move_manager import MoveManager


class Chess(object):
    def __init__(self):
        self.board = np.array(
            [
                [const.BLACK_ROOK,const.BLACK_KNIGHT, const.BLACK_BISHOP, const.BLACK_QUEEN, const.BLACK_KING, const.BLACK_BISHOP, const.BLACK_KNIGHT, const.BLACK_ROOK],
                [const.BLACK_PAWN, const.BLACK_PAWN, const.BLACK_PAWN, const.BLACK_PAWN, const.BLACK_PAWN, const.BLACK_PAWN, const.BLACK_PAWN, const.BLACK_PAWN],
                [const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL],
                [const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL],
                [const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL],
                [const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL, const.EMPTY_CELL],
                [const.WHITE_PAWN, const.WHITE_PAWN, const.WHITE_PAWN, const.WHITE_PAWN, const.WHITE_PAWN, const.WHITE_PAWN, const.WHITE_PAWN, const.WHITE_PAWN],
                [const.WHITE_ROOK, const.WHITE_KNIGHT, const.WHITE_BISHOP, const.WHITE_QUEEN, const.WHITE_KING, const.WHITE_BISHOP, const.WHITE_KNIGHT, const.WHITE_ROOK]
            ]
        )

        self.moves_map = {
            "P": self.__pawn_moves,
            "R": self.__rook_moves,
            "N": self.__knight_moves,
            "B": self.__bishop_moves,
            "Q": self.__queen_moves,
            "K": self.__king_moves
        }

        self.white_move = True

        self.moves = []
        self.pins = []
        self.checks = []

        self.check = False
        self.check_mate = False
        self.stale_mate = False
        self.wk_cell = (7, 4)
        self.bk_cell = (0, 4)

        self.en_passant = ()

        self.wc_short = True
        self.wc_long = True
        self.bc_short = True
        self.bc_long = True
        self.castling = [
            (
                self.wc_short,
                self.wc_short,
                self.bc_short,
                self.wc_long
            )
        ]

    def __under_attack(self, r, c, ally):
        enemy = "w" if ally == "b" else "b"
        directions = (
            (-1, 0), (0, -1), (1, 0), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        )
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    piece = self.board[end_row][end_col]
                    if piece[0] == ally:
                        break
                    elif piece[0] == enemy:
                        piece_type = piece[1]
                        if (0 <= j <= 3 and piece_type == "R") or \
                                (4 <= j <= 7 and piece_type == "B") or \
                                (i == 1 and piece_type == "P" and (
                                        (enemy == "w" and 6 <= j <= 7) or
                                        (enemy == "b" and 4 <= j <= 5))) or \
                                (piece_type == "Q") or \
                                (i == 1 and piece_type == "K"):
                            return True
                        else: break
                else: break

        knight_directions = (
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1)
        )
        for move in knight_directions:
            end_row = r + move[0]
            end_col = c + move[1]
            if 0 <= end_row < const.DIM and 0 <= end_col < const.DIM:
                piece = self.board[end_row][end_col]
                if piece[0] == enemy and piece[1] == "N":
                    return True
        return False

    def __possible_moves(self):
        moves = []
        for r in range(const.DIM):
            for c in range(const.DIM):
                first_piece_char = self.board[r][c][0]
                if (first_piece_char == "w" and self.white_move) or \
                        (first_piece_char == "b" and not self.white_move):
                    piece = self.board[r][c][1]
                    self.moves_map[piece](r, c, moves)
        return moves

    def __pins_and_checks(self):
        pins = []
        checks = []
        check = False

        if self.white_move:
            enemy = "b"
            ally = "w"
            start_row = self.wk_cell[0]
            start_col = self.wk_cell[1]
        else:
            enemy = "w"
            ally = "b"
            start_row = self.bk_cell[0]
            start_col = self.bk_cell[1]

        directions = (
            (0, 1),
            (0, -1),
            (1, 0),
            (1, 1),
            (1, -1),
            (-1, 0),
            (-1, 1),
            (-1, -1)
        )
        for j in range(len(directions)):
            d = directions[j]
            possible_pins = ()
            for i in range(1, const.DIM):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < const.DIM and 0 <= end_col < const.DIM:
                    piece = self.board[end_row][end_col]

                    if piece[0] == ally and piece[1] != "K":
                        if possible_pins == ():
                            possible_pins = (end_row, end_col, d[0], d[1])
                        else: break
                    elif piece[0] == enemy:
                        piece_type = piece[1]
                        if (0 <= j <= 3 and piece_type == "R") or \
                                (4 <= j <= 7 and piece_type == "B") or \
                                (
                                        i == 1 and
                                        piece_type == "P" and
                                        ((enemy == "w" and 6 <= j <= 7) or (enemy == "b" and 4 <= j <= 5))
                                ) or \
                                (piece_type == "Q") or \
                                (i == 1 and piece_type == "K"):
                            if possible_pins == ():
                                check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                            else:
                                pins.append(possible_pins)
                            break
                        else: break
                else: break

        knight_directions = (
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1)
        )
        for move in knight_directions:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row < const.DIM and 0 <= end_col < const.DIM:
                piece = self.board[end_row][end_col]
                if piece[0] == enemy and piece[1] == "N":
                    check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return pins, checks, check

    def legal_moves(self):
        valid_moves = []
        self.pins, self.checks, self.check = self.__pins_and_checks()

        if self.white_move:
            k_row = self.wk_cell[0]
            k_col = self.wk_cell[1]
        else:
            k_row = self.bk_cell[0]
            k_col = self.bk_cell[1]

        if self.check:
            if len(self.checks) == 1:
                valid_moves = self.__possible_moves()
                check = self.checks[0]
                check_row, check_col = check[0], check[1]
                enemy = self.board[check_row][check_col]
                valid_cells = []
                if enemy[1] == "N":
                    valid_cells = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (k_row + check[2] * i, k_col + check[3] * i)
                        valid_cells.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                for i in range(len(valid_moves) - 1, -1, -1):
                    if valid_moves[i].piece_moved[1] != "K":
                        if not (valid_moves[i].end_row, valid_moves[i].end_col) in valid_cells:
                            valid_moves.remove(valid_moves[i])
            else:
                self.__king_moves(k_row, k_col, valid_moves)
        else:
            valid_moves = self.__possible_moves()

        if len(valid_moves) == 0:
            if self.check:
                self.check_mate = True
            else:
                self.stale_mate = True
        else:
            self.check_mate = self.stale_mate = False
        return valid_moves


    def __short_castle(self, r, c, moves, ally):
        if self.board[r][c+1] == const.EMPTY_CELL and \
                self.board[r][c+2] == const.EMPTY_CELL and not \
                self.__under_attack(r, c+1, ally) and not \
                self.__under_attack(r, c+2, ally):
            moves.append(
                MoveManager(
                    (r, c),
                    (r, c+2),
                    self.board,
                    castle=True
                )
            )

    def __long_castle(self, r, c, moves, ally):
        if self.board[r][c-1] == const.EMPTY_CELL and \
                self.board[r][c-2] == const.EMPTY_CELL and \
                self.board[r][c-3] == const.EMPTY_CELL and not \
                self.__under_attack(r, c-1, ally) and not \
                self.__under_attack(r, c-2, ally):
            moves.append(
                MoveManager(
                    (r, c),
                    (r, c-2),
                    self.board,
                    castle=True
                )
            )

    def __update_castle(self, move):
        if move.piece_moved == const.WHITE_KING:
            self.wc_short = self.wc_long = False
        elif move.piece_moved == const.BLACK_KING:
            self.bc_short = self.bc_long = False
        elif move.piece_moved == const.WHITE_ROOK:
            if move.start_row == 7:
                if move.start_col == 7:
                    self.wc_short = False
                elif move.start_col == 0:
                    self.wc_long = False
        elif move.piece_moved == const.BLACK_ROOK:
            if move.start_row == 0:
                if move.start_col == 7:
                    self.bc_short = False
                elif move.start_col == 0:
                    self.bc_long = False

    def __castle(self, r, c, moves, ally):
        if self.__under_attack(r, c, ally): return
        if (self.white_move and self.wc_short) or (not self.white_move and self.bc_short):
            self.__short_castle(r, c, moves, ally)
        if (self.white_move and self.wc_long) or (not self.white_move and self.bc_long):
            self.__long_castle(r, c, moves, ally)

    def __pawn_moves(self, r, c, moves):
        pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pin_direction = (
                    self.pins[i][2],
                    self.pins[i][3]
                )
                self.pins.remove(self.pins[i])
                break

        opponent = "b"
        start_r = 6
        back_r = 0
        d = -1
        if not self.white_move:
            opponent = "w"
            start_r = 1
            back_r = 7
            d = 1
        pawn_promotion = False

        if self.board[r+d][c] == const.EMPTY_CELL:
            if not pinned or pin_direction == (d, 0):
                if r + d == back_r:
                    pawn_promotion = True
                moves.append(
                    MoveManager(
                        (r, c),
                        (r+d, c),
                        self.board,
                        pawn_promotion=pawn_promotion
                    )
                )
                if r == start_r and self.board[r+2*d][c] == const.EMPTY_CELL:
                    moves.append(
                        MoveManager(
                            (r, c),
                            (r+2*d, c), self.board
                        )
                    )
        if c - 1 >= 0:
            if not pinned or pin_direction == (d, -1):
                if self.board[r+d][c-1][0] == opponent:
                    if r + d == back_r:
                        pawn_promotion = True
                    moves.append(
                        MoveManager(
                            (r, c),
                            (r+d, c-1),
                            self.board,
                            pawn_promotion=pawn_promotion
                        )
                    )
                if (r + d, c - 1) == self.en_passant:
                    moves.append(
                        MoveManager(
                            (r, c),
                            (r+d, c-1),
                            self.board,
                            en_passant=True
                        )
                    )
        if c + 1 <= 7:
            if not pinned or pin_direction == (d, 1):
                if self.board[r+d][c+1][0] == opponent:
                    if r + d == back_r:
                        pawn_promotion = True
                    moves.append(
                        MoveManager(
                            (r, c),
                            (r+d, c+1),
                            self.board,
                            pawn_promotion=pawn_promotion
                        )
                    )
                    if (r+d, c+1) == self.en_passant:
                        moves.append(
                            MoveManager(
                                (r, c),
                                (r+d, c+1),
                                self.board,
                                en_passant=True
                            )
                        )

    def __rook_moves(self, r, c, moves):
        pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pin_direction = (
                    self.pins[i][2],
                    self.pins[i][3]
                )
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = (
            (-1, 0), (0, -1),
            (1, 0), (0, 1)
        )
        enemy = "b" if self.white_move else "w"
        for direction in directions:
            for i in range(1, const.DIM):
                end_row = r + direction[0] * i
                end_col = c + direction[1] * i
                if 0 <= end_row < const.DIM and 0 <= end_col < const.DIM:
                    if not pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                        piece = self.board[end_row][end_col]
                        if piece == const.EMPTY_CELL:
                            moves.append(
                                MoveManager(
                                    (r, c),
                                    (end_row, end_col),
                                    self.board
                                )
                            )
                        elif piece[0] == enemy:
                            moves.append(
                                MoveManager(
                                    (r, c),
                                    (end_row, end_col),
                                    self.board
                                )
                            )
                            break
                        else: break
                else: break

    def __knight_moves(self, r, c, moves):
        pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                self.pins.remove(self.pins[i])
                break

        directions = (
            (-2, -1), (-2, 1),
            (-1, -2), (-1, 2),
            (1, -2), (1, 2),
            (2, -1), (2, 1)
        )
        ally = "w" if self.white_move else "b"
        for move in directions:
            end_row = r + move[0]
            end_col = c + move[1]
            if 0 <= end_row < const.DIM and 0 <= end_col < const.DIM:
                if not pinned:
                    piece = self.board[end_row][end_col]
                    if piece[0] != ally:
                        moves.append(
                            MoveManager(
                                (r, c),
                                (end_row, end_col),
                                self.board
                            )
                        )

    def __bishop_moves(self, r, c, moves):
        pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pin_direction = (
                    self.pins[i][2],
                    self.pins[i][3]
                )
                self.pins.remove(self.pins[i])
                break

        directions = (
            (-1, -1), (-1, 1),
            (1, -1), (1, 1)
        )
        enemy = "b" if self.white_move else "w"
        for direction in directions:
            for i in range(1, const.DIM):
                end_row = r + direction[0] * i
                end_col = c + direction[1] * i
                if 0 <= end_row < const.DIM and 0 <= end_col < const.DIM:
                    if not pinned or pin_direction == direction or pin_direction == (-direction[0], -direction[1]):
                        piece = self.board[end_row][end_col]
                        if piece == const.EMPTY_CELL:
                            moves.append(
                                MoveManager(
                                    (r, c),
                                    (end_row, end_col),
                                    self.board
                                )
                            )
                        elif piece[0] == enemy:
                            moves.append(
                                MoveManager(
                                    (r, c),
                                    (end_row, end_col),
                                    self.board
                                )
                            )
                            break
                        else: break
                else: break

    def __queen_moves(self, r, c, moves):
        self.__rook_moves(r, c, moves)
        self.__bishop_moves(r, c, moves)

    def __king_moves(self, r, c, moves):
        row = (-1, -1, -1, 0, 0, 1, 1, 1)
        col = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally = "w" if self.white_move else "b"
        for i in range(const.DIM):
            end_row = r + row[i]
            end_col = c + col[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                piece = self.board[end_row][end_col]
                if piece[0] != ally:
                    if ally == "w": self.wk_cell = (end_row, end_col)
                    else: self.bk_cell = (end_row, end_col)
                    pins, checks, is_check = self.__pins_and_checks()
                    if not is_check:
                        moves.append(
                            MoveManager(
                                (r, c),
                                (end_row, end_col),
                                self.board
                            )
                        )
                    if ally == "w":
                        self.wk_cell = (r, c)
                    else:
                        self.bk_cell = (r, c)
        self.__castle(r, c, moves, ally)

    def move(self, move):
        self.moves.append(move)
        self.board[move.start_row][move.start_col] = const.EMPTY_CELL
        self.board[move.end_row][move.end_col] = move.piece_moved

        self.white_move = not self.white_move

        self.en_passant = ()

        if move.piece_moved == const.WHITE_KING:
            self.wk_cell = (move.end_row, move.end_col)
        elif move.piece_moved == const.BLACK_KING:
            self.bk_cell = (move.end_row, move.end_col)

        if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
            self.en_passant = (
                (move.end_row + move.start_row) // 2,
                move.end_col
            )
        if move.en_passant:
            self.board[move.start_row][move.end_col] = const.EMPTY_CELL

        if move.pawn_promotion:
            while True:
                promoted = input("Promote to a queen (\"Q\") or a knight (\"N\")?")
                if promoted == "Q" or promoted == "N":
                    break

            self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted

        self.__update_castle(move)
        self.castling.append(
            (
                self.wc_short,
                self.bc_short,
                self.wc_long,
                self.bc_long
            )
        )

        if move.castle:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1]
                self.board[move.end_row][move.end_col+1] = const.EMPTY_CELL
            else:
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2]
                self.board[move.end_row][move.end_col-2] = const.EMPTY_CELL

    def undo(self):
        if len(self.moves) != 0:
            move = self.moves.pop()
            self.white_move = not self.white_move
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured

            if move.piece_moved == const.WHITE_KING:
                self.wk_cell = (move.start_row, move.start_col)
            elif move.piece_moved == const.BLACK_KING:
                self.bk_cell = (move.start_row, move.start_col)

            if move.en_passant:
                self.en_passant = (move.end_row, move.end_col)
                self.board[move.end_row][move.end_col] = const.EMPTY_CELL
                self.board[move.start_row][move.end_col] = move.piece_captured

            if move.piece_moved[1] == "P" and abs(move.start_row - move.end_row) == 2:
                self.en_passant = ()

            self.castling.pop()
            tmp_castle = self.castling[-1]
            self.wc_short = tmp_castle[0]
            self.wc_long = tmp_castle[1]
            self.bc_short = tmp_castle[2]
            self.bc_long = tmp_castle[3]
            if move.castle:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col-1] = const.EMPTY_CELL
                else:
                    self.board[move.end_row][move.end_col-2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col+1] = const.EMPTY_CELL
