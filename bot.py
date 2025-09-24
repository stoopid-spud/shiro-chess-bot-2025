#!/usr/bin/env python3
# Example Python bot using the Chess API

from pychessapi import API, PieceType, Board, Move, PlayerColor, BitBoard
import math

POINTS_VALUE, POSITION_VALUE = 70, 30 # points and position adds to 100. The bot will weigh the position with these.

SEARCH_DEPTH = 5 # number of moves to search for (each played piece is a move so 1 white play and 1 black play is counted as 2)

PIECE_VALUES = {
    PieceType.QUEEN: 9,
    PieceType.ROOK: 5,
    PieceType.BISHOP: 3,
    PieceType.KNIGHT: 3,
    PieceType.PAWN: 1
}


def get_positions_from_bitboard(bitboard: BitBoard):
    for i in range(64):
        if (bitboard >> i) & 1:
            yield i


def get_white_point_value(white_piece_value: int, black_piece_value: int):
    return max(min(white_piece_value - black_piece_value, POINTS_VALUE), -POINTS_VALUE) # limit it POINTS_VALUE


# evaluates the position of that board and gives it a score. The higher the score, the better it is for white.
# scores range from -100 to 100 where 0 indicates an equal position
def evaluate_board(board: Board) -> int:
    white_bitboard = board.get_bitboard(PlayerColor.WHITE)
    white_piece_value = sum(PIECE_VALUES[board.get_piece_from_index(pos)] for pos in get_positions_from_bitboard(white_bitboard))

    black_bitboard = board.get_bitboard(PlayerColor.WHITE)
    black_piece_value = sum(PIECE_VALUES[board.get_piece_from_index(pos)] for pos in get_positions_from_bitboard(black_bitboard))

    white_point_value = get_white_point_value(white_piece_value, black_piece_value)

    return white_point_value


# takes a board and considers the legal moves. then returns the move with the highest score and the associated score.
def consider_moves(board: Board) -> tuple[Move, int]:
    is_white = board.is_white_turn()

    best_move = [None, -math.inf if is_white else math.inf]

    for move in board.get_legal_moves():
        # make the move
        board.make_move(move)
        score = evaluate_board(board)
        if is_white and score > best_move[1]:
            best_move = [move, score]
        elif not is_white and score < best_move[1]:
            best_move = [move, score]

    return best_move


while True:
    # get the current board
    board = API.get_board()
    # get all legal moves for the position
    moves = board.get_legal_moves()

    # evaluate moves
    chosen_move, score = evaluate_board(board)

    # play one at random
    API.push(chosen_move)
    # end our turn
    API.done()

