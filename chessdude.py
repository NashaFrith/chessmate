import chess
import chess.engine
import chess.polyglot
import random
import os
import shutil

def _find_stockfish():
    sf = shutil.which("stockfish")
    if sf:
        return sf
    base = os.path.dirname(os.path.abspath(__file__))
    for name in ("stockfish_linux", "stockfish", "stockfish.exe"):
        path = os.path.join(base, name)
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Stockfish not found. Install it or place the binary in the project folder.")

STOCKFISH_PATH = _find_stockfish()

OPENING_BOOK = {
    "e2e4":                                         ["e7e5", "c7c5", "e7e6", "c7c6"],
    "d2d4":                                         ["d7d5", "g8f6", "e7e6"],
    "g1f3":                                         ["d7d5", "g8f6", "c7c5"],
    "c2c4":                                         ["e7e5", "g8f6", "c7c5"],
    "b1c3":                                         ["d7d5", "g8f6", "e7e5"],
    "g2g3":                                         ["d7d5", "g8f6"],
    "f2f4":                                         ["d7d5", "g8f6"],
    "b2b3":                                         ["e7e5", "d7d5"],

    "e2e4 e7e5 g1f3":                               ["b8c6", "g8f6", "d7d6"],
    "e2e4 e7e5 f1c4":                               ["g8f6", "b8c6", "f8c5"],
    "e2e4 e7e5 b1c3":                               ["b8c6", "g8f6", "f8c5"],
    "e2e4 e7e5 d2d4":                               ["e5d4", "d7d6"],
    "e2e4 e7e5 f2f4":                               ["d7d5", "e5f4"],

    "e2e4 c7c5 g1f3":                               ["d7d6", "b8c6", "e7e6"],
    "e2e4 c7c5 b1c3":                               ["b8c6", "g8f6", "e7e6"],
    "e2e4 c7c5 d2d4":                               ["c5d4"],

    "e2e4 e7e6 d2d4":                               ["d7d5"],
    "e2e4 c7c6 d2d4":                               ["d7d5"],
    "e2e4 c7c6 d2d4 d7d5":                          ["b8d7", "g8f6", "d5e4"],

    "d2d4 d7d5 c2c4":                               ["e7e6", "c7c6", "d5c4"],
    "d2d4 d7d5 g1f3":                               ["g8f6", "c7c6", "e7e6"],
    "d2d4 d7d5 b1c3":                               ["g8f6", "e7e6", "c7c6"],

    "d2d4 g8f6 c2c4":                               ["e7e6", "g7g6", "c7c5"],
    "d2d4 g8f6 g1f3":                               ["e7e6", "g7g6", "d7d5"],

    "e2e4 e7e5 g1f3 b8c6 f1b5":                     ["a7a6", "g8f6", "f8c5"],
    "e2e4 e7e5 g1f3 b8c6 f1c4":                     ["f8c5", "g8f6"],
    "e2e4 e7e5 g1f3 b8c6 d2d4":                     ["e5d4", "g8f6"],

    "e2e4 e7e5 g1f3 b8c6 f1b5 a7a6":               ["f1b5 a7a6 b5a4", "f1b5 a7a6 b5c6"],
    "e2e4 e7e5 g1f3 b8c6 f1c4 f8c5":               ["g8f6", "d7d6"],
    "e2e4 e7e5 g1f3 b8c6 f1c4 g8f6":               ["d7d6", "f8c5"],

    "d2d4 d7d5 c2c4 e7e6 b1c3":                     ["g8f6", "f8e7", "c7c5"],
    "d2d4 d7d5 c2c4 c7c6 g1f3":                     ["g8f6", "e7e6"],
    "d2d4 g8f6 c2c4 e7e6 b1c3":                     ["f8b4", "d7d5", "c7c5"],
    "d2d4 g8f6 c2c4 g7g6 b1c3":                     ["f8g7", "d7d5"],
}


PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_TABLE = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]

PIECE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}


class ChessDude:

    def __init__(self):
        self.board = chess.Board()
        self.turn = 'w'
        self.think_time = 0.1
        self.sf = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self.sf.configure({"UCI_LimitStrength": True, "UCI_Elo": 1320})

    def reset(self, difficulty='medium'):
        self.board = chess.Board()
        self.turn = 'w'
        if difficulty == 'test':
            self.think_time = 0.05
            self.sf.configure({"UCI_LimitStrength": False, "Skill Level": 1})
        elif difficulty == 'easy':
            self.think_time = 0.1
            self.sf.configure({"UCI_LimitStrength": True, "UCI_Elo": 800, "Skill Level": 3})
        elif difficulty == 'hard':
            self.think_time = 0.1
            self.sf.configure({"UCI_LimitStrength": True, "UCI_Elo": 1500, "Skill Level": 14})
        else:
            self.think_time = 0.1
            self.sf.configure({"UCI_LimitStrength": True, "UCI_Elo": 1200, "Skill Level": 8})

    def make_move_uci(self, from_sq, to_sq):
        try:
            uci = from_sq + to_sq
            piece = self.board.piece_at(chess.parse_square(from_sq))
            if piece and piece.piece_type == chess.PAWN:
                to_rank = chess.parse_square(to_sq) // 8
                if (piece.color == chess.WHITE and to_rank == 7) or (piece.color == chess.BLACK and to_rank == 0):
                    uci += 'q'
            move = chess.Move.from_uci(uci)
            if move in self.board.legal_moves:
                san = self.board.san(move)
                self.board.push(move)
                self.turn = 'b' if self.board.turn == chess.BLACK else 'w'
                return {"status": "Move made", "move": san, "fen": self.board.fen(), "turn": self.turn}
            return {"error": "Illegal move"}
        except Exception:
            return {"error": "Invalid move"}

    def make_move(self, move):
        try:
            chess_move = self.board.parse_san(move)
            if chess_move in self.board.legal_moves:
                self.board.push(chess_move)
                self.turn = 'b' if self.board.turn == chess.BLACK else 'w'
                return {"status": "Move made", "move": move, "fen": self.board.fen(), "turn": self.turn}
            else:
                return {"error": "Illegal move"}
        except Exception:
            return {"error": "Invalid move format"}

    # Removing for stockfish for gift purposes. Will readd for personal development
    # def evaluate_board(self):
    #     if self.board.is_checkmate():
    #         return -1000000 if self.board.turn else 1000000
    #     if self.board.is_stalemate() or self.board.is_seventyfive_moves() or self.board.is_insufficient_material():
    #         return 0
    #
    #     score = 0
    #     for sq, piece in self.board.piece_map().items():
    #         table = PIECE_TABLES[piece.piece_type]
    #         value = PIECE_VALUES[piece.piece_type]
    #         if piece.color == chess.WHITE:
    #             table_idx = (7 - sq // 8) * 8 + sq % 8
    #             score += value + table[table_idx]
    #         else:
    #             table_idx = sq
    #             score -= value + table[table_idx]
    #     return score

    # def order_moves(self, moves):
    #     def move_score(move):
    #         if self.board.is_capture(move):
    #             victim = self.board.piece_at(move.to_square)
    #             attacker = self.board.piece_at(move.from_square)
    #             if victim and attacker:
    #                 return PIECE_VALUES[victim.piece_type] - PIECE_VALUES[attacker.piece_type]
    #             return 0
    #         return -1
    #     return sorted(moves, key=move_score, reverse=True)

    # def quiescence(self, alpha, beta, maximizing_player):
    #     stand_pat = self.evaluate_board()
    #     if maximizing_player:
    #         if stand_pat >= beta:
    #             return beta
    #         alpha = max(alpha, stand_pat)
    #         for move in self.order_moves(self.board.legal_moves):
    #             if not self.board.is_capture(move):
    #                 continue
    #             self.board.push(move)
    #             score = self.quiescence(alpha, beta, False)
    #             self.board.pop()
    #             alpha = max(alpha, score)
    #             if beta <= alpha:
    #                 break
    #         return alpha
    #     else:
    #         if stand_pat <= alpha:
    #             return alpha
    #         beta = min(beta, stand_pat)
    #         for move in self.order_moves(self.board.legal_moves):
    #             if not self.board.is_capture(move):
    #                 continue
    #             self.board.push(move)
    #             score = self.quiescence(alpha, beta, True)
    #             self.board.pop()
    #             beta = min(beta, score)
    #             if beta <= alpha:
    #                 break
    #         return beta

    # def minimax(self, depth, alpha, beta, maximizing_player):
    #     if depth == 0 or self.board.is_game_over():
    #         return self.quiescence(alpha, beta, maximizing_player)
    #     if maximizing_player:
    #         maxchoice = -float('inf')
    #         for move in self.order_moves(self.board.legal_moves):
    #             self.board.push(move)
    #             eval = self.minimax(depth-1, alpha, beta, False)
    #             self.board.pop()
    #             maxchoice = max(maxchoice, eval)
    #             alpha = max(alpha, eval)
    #             if beta <= alpha:
    #                 break
    #         return maxchoice
    #     else:
    #         minchoice = float('inf')
    #         for move in self.order_moves(self.board.legal_moves):
    #             self.board.push(move)
    #             eval = self.minimax(depth-1, alpha, beta, True)
    #             self.board.pop()
    #             minchoice = min(minchoice, eval)
    #             beta = min(beta, eval)
    #             if beta <= alpha:
    #                 break
    #         return minchoice

    # def best_move(self, depth=4):
    #     try:
    #         with chess.polyglot.open_reader("book.bin") as reader:
    #             entry = reader.weighted_choice(self.board)
    #             return self.board.san(entry.move)
    #     except Exception:
    #         pass
    #     move_history = " ".join(m.uci() for m in self.board.move_stack)
    #     if move_history in OPENING_BOOK:
    #         candidates = OPENING_BOOK[move_history]
    #         random.shuffle(candidates)
    #         for uci in candidates:
    #             try:
    #                 move = chess.Move.from_uci(uci)
    #                 if move in self.board.legal_moves:
    #                     return self.board.san(move)
    #             except Exception:
    #                 pass
    #     best_move = None
    #     if self.board.turn == chess.WHITE:
    #         best_value = -float('inf')
    #     else:
    #         best_value = float('inf')
    #     for move in self.order_moves(self.board.legal_moves):
    #         self.board.push(move)
    #         board_value = self.minimax(depth-1, -float('inf'), float('inf'), self.board.turn)
    #         self.board.pop()
    #         if self.board.turn == chess.WHITE:
    #             if board_value > best_value:
    #                 best_value = board_value
    #                 best_move = move
    #         elif self.board.turn == chess.BLACK:
    #             if board_value < best_value:
    #                 best_value = board_value
    #                 best_move = move
    #     return self.board.san(best_move) if best_move else None

    def best_move(self):
        try:
            with chess.polyglot.open_reader("book.bin") as reader:
                entry = reader.weighted_choice(self.board)
                return {"move": self.board.san(entry.move), "eval": 0}
        except Exception:
            pass

        result = self.sf.play(self.board, chess.engine.Limit(time=self.think_time), info=chess.engine.INFO_SCORE)
        move_san = self.board.san(result.move)
        score = result.info.get('score')
        eval_score = score.white().score(mate_score=10000) if score else 0
        return {"move": move_san, "eval": eval_score}
