import pygame
from utils import constants as const


class DrawBoard(object):
    def __init__(self, state, screen, color):
        self.state = state
        self.screen = screen
        self.color = color
        self.colors = [
            const.COLORS[self.color][0],
            const.COLORS[self.color][1]
        ]

    @staticmethod
    def laod_assets():
        pieces = [
            const.WHITE_ROOK,
            const.WHITE_KNIGHT,
            const.WHITE_BISHOP,
            const.WHITE_QUEEN,
            const.WHITE_KING,
            const.WHITE_PAWN,

            const.BLACK_ROOK,
            const.BLACK_KNIGHT,
            const.BLACK_BISHOP,
            const.BLACK_QUEEN,
            const.BLACK_KING,
            const.BLACK_PAWN
        ]

        for piece in pieces:
            const.IMAGES[piece] = pygame.transform.scale(
                pygame.image.load(
                    "./img/assets/{}.png".format(piece)
                ),
                (const.SQ_SIZE, const.SQ_SIZE)
            )

        for i in range(1, 9):
            const.NUMBERS[str(i)] = pygame.transform.scale(
                pygame.image.load(
                    "./img/numbers/{}.png".format(str(i))
                ),
                (const.SQ_SIZE, const.SQ_SIZE)
            )
            const.LETTERS[chr(ord('a') + i - 1)] = pygame.transform.scale(
                pygame.image.load(
                    "./img/letters/{}.png".format(chr(ord('a')+i-1))
                ),
                (const.SQ_SIZE, const.SQ_SIZE)
            )

    def __draw_board(self):
        for row in range(const.DIM):
            for col in range(const.DIM):
                color = self.colors[((row+col) % 2)]

                if row == 0:
                    pygame.draw.rect(
                        self.screen,
                        const.EDGES_RGB,
                        pygame.Rect(
                            col * const.SQ_SIZE,
                            row * const.SQ_SIZE,
                            const.SQ_SIZE, const.HALF_SQUARE
                        )
                    )

                if row == const.DIM - 1:
                    if col == const.DIM - 1:
                        pygame.draw.rect(
                            self.screen,
                            const.EDGES_RGB,
                            pygame.Rect(
                                col * const.SQ_SIZE + const.SQ_SIZE,
                                row * const.SQ_SIZE + const.SQ_SIZE,
                                const.SQ_SIZE, const.SQ_SIZE
                            )
                        )
                    self.screen.blit(
                        const.LETTERS[chr(ord('a') + col)],
                        pygame.draw.rect(
                            self.screen,
                            const.EDGES_RGB,
                            pygame.Rect(
                                col * const.SQ_SIZE + const.HALF_SQUARE,
                                row * const.SQ_SIZE + const.SQ_SIZE + const.HALF_SQUARE,
                                const.SQ_SIZE, const.HALF_SQUARE
                            )
                        )
                    )

                if col == 0:
                    if row == const.DIM - 1:
                        pygame.draw.rect(
                            self.screen,
                            const.EDGES_RGB,
                            pygame.Rect(
                                col * const.SQ_SIZE,
                                row * const.SQ_SIZE + const.SQ_SIZE,
                                const.HALF_SQUARE, const.SQ_SIZE
                            )
                        )
                    self.screen.blit(
                        const.NUMBERS[str(const.DIM - row)],
                        pygame.draw.rect(
                            self.screen,
                            const.EDGES_RGB,
                            pygame.Rect(
                                col * const.SQ_SIZE,
                                row * const.SQ_SIZE + const.HALF_SQUARE,
                                const.HALF_SQUARE, const.SQ_SIZE
                            )
                        )
                    )

                if col == const.DIM - 1:
                    if row == 0:
                        pygame.draw.rect(
                            self.screen,
                            const.EDGES_RGB,
                            pygame.Rect(
                                (col + 1) * const.SQ_SIZE, row * const.SQ_SIZE,
                                const.SQ_SIZE, const.HALF_SQUARE
                            )
                        )
                    pygame.draw.rect(
                        self.screen,
                        const.EDGES_RGB,
                        pygame.Rect(
                            col * const.SQ_SIZE + const.SQ_SIZE + const.HALF_SQUARE,
                            row * const.SQ_SIZE + const.HALF_SQUARE,
                            const.HALF_SQUARE, const.SQ_SIZE
                        )
                    )

                pygame.draw.rect(
                    self.screen,
                    color,
                    pygame.Rect(
                        col * const.SQ_SIZE + const.HALF_SQUARE,
                        row * const.SQ_SIZE + const.HALF_SQUARE,
                        const.SQ_SIZE, const.SQ_SIZE
                    )
                )

    def __draw_pieces(self):
        for row in range(const.DIM):
            for col in range(const.DIM):
                piece = self.state.board[row][col]
                if piece != const.EMPTY_CELL:
                    self.screen.blit(
                        const.IMAGES[piece],
                        pygame.Rect(
                            col * const.SQ_SIZE + const.HALF_SQUARE,
                            row * const.SQ_SIZE + const.HALF_SQUARE,
                            const.SQ_SIZE, const.SQ_SIZE
                        )
                    )

    def __highlight_cells(self, selected_square, valid_moves):
        if selected_square != ():
            r, c = selected_square
            if self.state.board[r][c][0] == ("w" if self.state.white_move else "b"):
                surface_1 = pygame.Surface((const.SQ_SIZE, const.SQ_SIZE))
                surface_2 = pygame.Surface((const.SQ_SIZE, const.SQ_SIZE))

                surface_1.set_alpha(200)
                surface_2.set_alpha(120 if self.color == 0 else 160)
                # yellow, blue
                surface_1.fill((253, 216, 53) if self.color == 0 else (1, 87, 155))
                self.screen.blit(surface_1, (c * const.SQ_SIZE + const.HALF_SQUARE, r * const.SQ_SIZE + const.HALF_SQUARE))
                # green, yellow
                surface_2.fill((100, 221, 23) if self.color == 0 else (253, 216, 53))
                for move in valid_moves:
                    if move.start_row == r and move.start_col == c:
                        self.screen.blit(
                            surface_2,
                            (const.SQ_SIZE * move.end_col + const.HALF_SQUARE,
                             const.SQ_SIZE * move.end_row + const.HALF_SQUARE)
                        )

    def __highlight_king(self):
        if self.state.check:
            surface = pygame.Surface((const.SQ_SIZE, const.SQ_SIZE))
            surface.set_alpha(200)
            # red
            surface.fill((250, 10, 0))
            r, c = self.state.wk_cell if self.state.white_move else self.state.bk_cell
            self.screen.blit(
                surface,
                (const.SQ_SIZE * c + const.HALF_SQUARE,
                 const.SQ_SIZE * r + const.HALF_SQUARE)
            )

    def draw_game_state(self, valid_moves, selected_square):
        self.__draw_board()
        if selected_square != () and selected_square[0] != -1 and selected_square[1] != -1:
            self.__highlight_cells(selected_square, valid_moves)
        self.__highlight_king()
        self.__draw_pieces()

