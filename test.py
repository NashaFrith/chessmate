from flask import Flask, jsonify, render_template, request
import chess
import chess.engine
from chessdude import ChessDude

def test_board_state():
    chess_game = ChessDude()
    moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6"]

    for move in moves:
        print(f"Move: {move}")
        print(f"FEN: {chess_game.board.fen()}")
        print("-------------------------")

test_board_state()