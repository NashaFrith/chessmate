import chess
import chess.engine


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

    def evaluate_board(self):
        if self.board.is_checkmate():
            return -1000000 if self.board.turn else 1000000
        if self.board.is_stalemate() or self.board.is_seventyfive_moves() or self.board.is_insufficient_material():
            return 0

        score = 0
        for sq, piece in self.board.piece_map().items():
            table = PIECE_TABLES[piece.piece_type]
            value = PIECE_VALUES[piece.piece_type]
            if piece.color == chess.WHITE:
                table_idx = (7 - sq // 8) * 8 + sq % 8
                score += value + table[table_idx]
            else:
                table_idx = sq
                score -= value + table[table_idx]
        return score

    def order_moves(self, moves):
        def move_score(move):
            if self.board.is_capture(move):
                victim = self.board.piece_at(move.to_square)
                attacker = self.board.piece_at(move.from_square)
                if victim and attacker:
                    return PIECE_VALUES[victim.piece_type] - PIECE_VALUES[attacker.piece_type]
                return 0
            return -1
        return sorted(moves, key=move_score, reverse=True)

    def quiescence(self, alpha, beta, maximizing_player):
        stand_pat = self.evaluate_board()

        if maximizing_player:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
            for move in self.order_moves(self.board.legal_moves):
                if not self.board.is_capture(move):
                    continue
                self.board.push(move)
                score = self.quiescence(alpha, beta, False)
                self.board.pop()
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return alpha
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)
            for move in self.order_moves(self.board.legal_moves):
                if not self.board.is_capture(move):
                    continue
                self.board.push(move)
                score = self.quiescence(alpha, beta, True)
                self.board.pop()
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return beta

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.board.is_game_over():
            return self.quiescence(alpha, beta, maximizing_player)

        if maximizing_player:
            maxchoice = -float('inf')
            for move in self.order_moves(self.board.legal_moves):
                self.board.push(move)
                eval = self.minimax(depth-1, alpha, beta, False)
                self.board.pop()
                maxchoice = max(maxchoice, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return maxchoice
        else:
            minchoice = float('inf')
            for move in self.order_moves(self.board.legal_moves):
                self.board.push(move)
                eval = self.minimax(depth-1, alpha, beta, True)
                self.board.pop()
                minchoice = min(minchoice, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return minchoice

    def best_move(self, depth=4):
        best_move = None
        if self.board.turn == chess.WHITE:
            best_value = -float('inf')
        else:
            best_value = float('inf')

        for move in self.order_moves(self.board.legal_moves):
            self.board.push(move)
            board_value = self.minimax(depth-1, -float('inf'), float('inf'), self.board.turn)
            self.board.pop()

            if self.board.turn == chess.WHITE:
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
            elif self.board.turn == chess.BLACK:
                if board_value < best_value:
                    best_value = board_value
                    best_move = move

        return self.board.san(best_move) if best_move else None
