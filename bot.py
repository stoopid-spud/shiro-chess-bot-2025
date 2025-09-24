#!/usr/bin/env python3
# Example Python bot using the Chess API

from pychessapi import API, PieceType, Board, Move, PlayerColor, BitBoard
import math
import sys
from random import shuffle, choice

POINTS_VALUE, POSSIBLE_MOVES_VALUE = 80, 20 # points and position adds to 100. The bot will weigh the position with these.

SEARCH_DEPTH = 4 # number of moves to search for (each played piece is a move so 1 white play and 1 black play is counted as 2)
THROWAWAY_THRESHOLD = -10 # point threshhold at which to throw away the board

VERSION = 0.2
NAME = f"SpudBot_v{VERSION}"

sys.stderr = open('errors.txt', 'w')

PIECE_VALUES = {
    PieceType.QUEEN: 9,
    PieceType.ROOK: 5,
    PieceType.BISHOP: 3,
    PieceType.KNIGHT: 3,
    PieceType.PAWN: 1
}


def move_heuristic(move: Move, board: Board):
    capture = 0 if not move.capture else PIECE_VALUES[board.get_piece_from_bitboard(move.target)]
    
    return capture


def get_moves(board: Board):
    moves = board.get_legal_moves()
    # moves.sort(key=lambda move: move_heuristic(move, board), reverse=board.is_black_turn())
    shuffle(moves)
    return moves


def get_positions_from_bitboard(bitboard: BitBoard):
    for i in range(64):
        if (bitboard >> i) & 1:
            yield i


def get_white_point_value(white_piece_value: int, black_piece_value: int):
    difference = white_piece_value - black_piece_value
    total = white_piece_value + black_piece_value

    return max(min(difference / total * POINTS_VALUE, POINTS_VALUE), -POINTS_VALUE) # limit it POINTS_VALUE


def get_possible_moves_value(possible_moves: int):
    factor = 0.5

    return max(min(possible_moves * factor, POSSIBLE_MOVES_VALUE), -POSSIBLE_MOVES_VALUE) # limit it POINTS_VALUE


# evaluates the position of that board and gives it a score. The higher the score, the better it is for white.
# scores range from -100 to 100 where 0 indicates an equal position
def evaluate_board(board: Board) -> int:
    if board.in_checkmate():
        if board.is_white_turn():
            return -1000 # white is checkmated
        return 1000

    white_piece_value = sum(value * sum(1 for _ in get_positions_from_bitboard(board.get_bitboard(PlayerColor.WHITE, piece))) for piece, value in PIECE_VALUES.items())

    black_piece_value = sum(value * sum(1 for _ in get_positions_from_bitboard(board.get_bitboard(PlayerColor.BLACK, piece))) for piece, value in PIECE_VALUES.items())

    white_point_value = get_white_point_value(white_piece_value, black_piece_value)

    if board.is_white_turn():
        possible_moves_value = get_possible_moves_value(len(board.get_legal_moves()))
    else:
        board.skip_turn()
        possible_moves_value = -get_possible_moves_value(len(board.get_legal_moves()))
        
    return white_point_value + possible_moves_value


# takes a board where it is blacks's turn and considers the legal moves. then returns the move with the highest score and the associated score.
def consider_black_moves(board: Board, depth: int, alpha: int, beta: int) -> tuple[Move, int]:
    if depth == 0:
        # final iteration
        return [None, evaluate_board(board)]

    best_move = [None, math.inf]

    for move in get_moves(board):
        board.make_move(move)
        _, score = consider_white_moves(board, depth-1, alpha, beta)
        board.undo_move()

        if score < best_move[1]:
            best_move = [move, score]
            if beta > score:
                beta = score
                if alpha >= beta:
                    break

    return best_move


# takes a board where it is white's turn and considers the legal moves. then returns the move with the highest score and the associated score.
def consider_white_moves(board: Board, depth: int, alpha: int, beta: int) -> tuple[Move, int]:
    if depth == 0:
        # final iteration
        return [None, evaluate_board(board)]

    best_move = [None, -math.inf]

    for move in get_moves(board):
        board.make_move(move)
        _, score = consider_black_moves(board, depth-1, alpha, beta)
        board.undo_move()

        if score > best_move[1]:
            best_move = [move, score]
            if alpha < score:
                alpha = score
                if alpha >= beta:
                    break

    return best_move


while True:
    # get the current board
    board = API.get_board()
    # get all legal moves for the position

    # evaluate moves
    if board.is_white_turn():
        chosen_move, _ = consider_white_moves(board, SEARCH_DEPTH, -math.inf, math.inf)
    else:
        chosen_move, _ = consider_black_moves(board, SEARCH_DEPTH, -math.inf, math.inf)

    if chosen_move == None:
        with open("./log.txt", "w") as l:
            l.write("chosen move was none")
        
        moves = get_moves(board)
        chosen_move = choice(moves)

    # play one at random
    API.push(chosen_move)
    # end our turn
    API.done()
