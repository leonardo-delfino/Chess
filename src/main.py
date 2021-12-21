import pygame

from utils import constants as const
from gui import draw_board
from game.move_manager import MoveManager
from game import chess as game


def main():
    pygame.init()

    screen = pygame.display.set_mode((const.WIDTH, const.HEIGHT))
    clock = pygame.time.Clock()

    state = game.Chess()

    color_flag = 0
    draw = draw_board.DrawBoard(state, screen, color_flag)
    legal_moves = state.legal_moves()
    move_flag = False

    sel_cell = ()
    player_clicks = []

    game_over = False

    draw.laod_assets()

    running = True
    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                row = (mouse_position[1] + const.HALF_SQUARE) // const.SQ_SIZE
                col = (mouse_position[0] + const.HALF_SQUARE) // const.SQ_SIZE
                if row < 0 or row > 8 or col < 0 or col > 8 or game_over:
                    sel_cell, player_clicks = (), []
                    break

                row, col = row-1, col-1
                if sel_cell == (row, col) or (
                        len(player_clicks) == 0 and
                        (
                                state.board[row][col] == const.EMPTY_CELL or
                                (state.board[row][col][0] == 'b' and state.white_move) or
                                (state.board[row][col][0] == 'w' and not state.white_move)
                        )
                ):
                    sel_cell, player_clicks = (), []
                else:
                    sel_cell = (row, col)
                    player_clicks.append(sel_cell)

                if len(player_clicks) == 2:
                    move = MoveManager(player_clicks[0], player_clicks[1], state.board)
                    for i in range(len(legal_moves)):
                        if move == legal_moves[i]:
                            print(move.get_chess_notation())
                            state.move(legal_moves[i])
                            move_flag = True
                            sel_cell, player_clicks = (), []
                    if not move_flag:
                        player_clicks = [sel_cell]

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and not game_over:
                    state.undo()
                    move_flag = True

                if event.key == pygame.K_1:
                    color_flag = 0
                    draw = draw_board.DrawBoard(state, screen, color_flag)

                if event.key == pygame.K_2:
                    color_flag = 1
                    draw = draw_board.DrawBoard(state, screen, color_flag)

                if event.key == pygame.K_r:
                    state = game.Chess()
                    draw = draw_board.DrawBoard(state, screen, color_flag)
                    legal_moves = state.legal_moves()
                    sel_cell, player_clicks = (), []
                    move_flag = game_over = False

        if move_flag:
            legal_moves = state.legal_moves()
            move_flag = False

        draw.draw_game_state(legal_moves, sel_cell)

        if state.check_mate:
            game_over = True
            if state.white_move:
                print("Black wins")
            else:
                print("White wins")
        elif state.stale_mate:
            game_over = True
            print("Draw")

        clock.tick(const.MAX_FPS)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
