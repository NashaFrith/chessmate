import chess

#Consider converting using Stockfish
import chess.engine


#Now using a class for the chess engine
class ChessDude:

    #Intialize the chessboard, with the starting player being white
    def __init__(self):
        self.board = chess.Board() 
        self.turn = 'w'

    def make_move(self, move):
        #Users no longer need to put in the fen string, instead automatically generates
        #Instead, uses SAN (Standard Algebraic Notation)
        try:
            chess_move = self.board.parse_san(move)
            if chess_move in self.board.legal_moves:
                self.board.push(chess_move)
                self.turn = 'b' if self.board.turn == chess.BLACK else 'w'
                return {"status": "Move made", "move": move, "fen": self.board.fen(), "turn": self.turn}
            else:
                return {"error": "Illegal move"}
        except:
            return {"error": "Invalid move format"}


    def evaluate_board(self):
        # Implement a simple evaluation function
        #this function is used to evaluate the state of the board, ie determine if there is a winner at a particular game state. it utilizes functions from the chess library to 
        #check for checkmate(and whether black or white wins) or stalemate/tie
        if self.board.is_checkmate():
            if self.board.turn:
                return -9999  #Black wins
            else:
                return 9999  #White wins
            
        elif self.board.is_stalemate() or self.board.is_seventyfive_moves() or self.board.is_insufficient_material():
            return 0  #Draw  
         
        #----Old----#
        #for piece in board.piece_map().values():
            #material_count += pieceval(piece)
        #----Old----#

        #if not in a game state that ends the game, like above, then it will evaluate the value of the board state based on piece values. A helper function is used to assign these values
        material_count = 0
        
        #This loops through pieces and now uses a bitboard to check board and assign the values
        for piece_type in range(1, 7): 
            white_bitboard = self.board.pieces(piece_type, chess.WHITE)
            black_bitboard = self.board.pieces(piece_type, chess.BLACK)
            material_count += self.pieceval(piece_type, white_bitboard, black_bitboard)
        return material_count

    #this, the afformentioned helper, simply assigns values to the pieces
    def pieceval(self,piece,white_bitboard, black_bitboard):
        #----Old----#
        # if piece.piece_type == chess.PAWN:
        #     return 1 if piece.color == chess.WHITE else -1
        # elif piece.piece_type == chess.KNIGHT or piece.piece_type == chess.BISHOP:
        #     return 3 if piece.color == chess.WHITE else -3
        # elif piece.piece_type == chess.ROOK:
        #     return 5 if piece.color == chess.WHITE else -5
        # elif piece.piece_type == chess.QUEEN:
        #     return 9 if piece.color == chess.WHITE else -9
        #return 0
        #----Old----#

        #Updated to use bitboards
        #Also uses a dictionary for pieces instead of if statements because...come on now
        values = {
            chess.PAWN: 1, 
            chess.KNIGHT: 3, 
            chess.BISHOP: 3, 
            chess.ROOK: 5, 
            chess.QUEEN: 9, 
            #Now valuing king, but should I keep it as zero or 100?
            chess.KING: 100
        }

        white_count = bin(white_bitboard).count('1')
        black_count = bin(black_bitboard).count('1')
        return values.get(piece, 0) * (white_count - black_count)



    def minimax(self, depth, alpha, beta, maximizing_player):
        # Implement the minimax algorithm with alpha-beta pruning

        #base case
        if depth == 0 or self.board.is_game_over():
            return self.evaluate_board()
        
        #this goes through the minimax algorithm, starting by initializing max (like alpha) to negative infinity. Then it tests the move, and if alpha is greater than beta,
        #we don't check any moe of the children
        #recursive, and switches to false (with the minimizing statement switching to true) so that it goes from max to min to max to min like the algorithm
        if maximizing_player:
            maxchoice = -float('inf')

            for move in self.board.legal_moves:
                self.board.push(move)
                eval = self.minimax(depth-1, alpha, beta, False)
                self.board.pop()
                maxchoice = max(maxchoice, eval)
                alpha = max(alpha, eval)

                if beta <= alpha:
                    break

            return maxchoice
        
        #if it isn't the maximizing player doing the move, then instead we would initialize to positive infinity, and again go through the algorithm
        else:
            minchoice = float('inf')

            for move in self.board.legal_moves:
                self.board.push(move)
                eval = self.minimax(depth-1, alpha, beta, True)
                self.board.pop()
                minchoice = min(minchoice, eval)
                beta = min(beta, eval)

                if beta <= alpha:
                    break

            return minchoice


    #this function initializes to negative and positive infinity for maximizer and minimizer respectively, then calls minmax function to update the player's move to best move
    #Attempting to adjust the depth so that the AI is a bit...smarter, but not too smart to take forever
    #Add functionality to adjust difficulty in the future

    def best_move(self, depth=6):
        # Use minimax to get the best move
        best_move = None
        if self.board.turn == chess.WHITE:
            best_value = -float('inf')
        else:
            best_value = float('inf')
        
        for move in self.board.legal_moves:
            self.board.push(move)
            board_value = self.minimax(depth-1, -float('inf'), float('inf'), not self.board.turn)
            self.board.pop()
            
            if self.board.turn == chess.WHITE:
                if board_value > best_value:
                    best_value = board_value
                    best_move = move

            elif self.board.turn == chess.BLACK:
                if board_value < best_value:
                    best_value = board_value
                    best_move = move
                    
        return best_move.uci() if best_move else None    


    # def play_game():
    #     board = chess.Board()
    #     while not board.is_game_over():
    #         print(board)
    #         if board.turn == chess.WHITE:
    #             # Human's turn
    #             move = input("Enter your move: ")
    #             board.push_san(move)
    #         else:
    #             # Agent's turn
    #             move = best_move(board, depth=3)
    #             board.push(move)

    #     print("Game over:", board.result())

    # if __name__ == "__main__":
    #     play_game()

