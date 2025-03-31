#Nasha Frith
#620140159

# chess_agent.py


import chess
import chess.engine

def evaluate_board(board):
    # Implement a simple evaluation function
    #this function is used to evaluate the state of the board, ie determine if there is a winner at a particular game state. it utilizes functions from the chess library to 
    #check for checkmate(and whether black or white wins) or stalemate/tie
    if board.is_checkmate():
        if board.turn:
            return -9999  #Black wins
        else:
            return 9999  #White wins
        
    elif board.is_stalemate() or board.is_seventyfive_moves() or board.is_insufficient_material():
        return 0  #Draw   

    #if not in a game state that ends the game, like above, then it will evaluate the value of the board state based on piece values. A helper function is used to assign these values
    material_count = 0

    for piece in board.piece_map().values():
        material_count += pieceval(piece)

    return material_count

#this, the afformentioned helper, simply assigns values to the pieces
def pieceval(piece):

    if piece.piece_type == chess.PAWN:
        return 1 if piece.color == chess.WHITE else -1
    elif piece.piece_type == chess.KNIGHT or piece.piece_type == chess.BISHOP:
        return 3 if piece.color == chess.WHITE else -3
    elif piece.piece_type == chess.ROOK:
        return 5 if piece.color == chess.WHITE else -5
    elif piece.piece_type == chess.QUEEN:
        return 9 if piece.color == chess.WHITE else -9
    
    return 0


def minimax(board, depth, alpha, beta, maximizing_player):
    # Implement the minimax algorithm with alpha-beta pruning

    #base case
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)
    
    #this goes through the minmax algorithm, starting by initializing max (like alpha) to negative infinity. Then it tests the move, and if alpha is greater than beta,
    #we don't check any moe of the children
    #recursive, and switches to false (with the minimizing statement switching to true) so that it goes from max to min to max to min like the algorithm
    if maximizing_player:
        maxchoice = -float('inf')

        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth-1, alpha, beta, False)
            board.pop()
            maxchoice = max(maxchoice, eval)
            alpha = max(alpha, eval)

            if beta <= alpha:
                break

        return maxchoice
    
    #if it isn't the maximizing player doing the move, then instead we would initialize to positive infinity, and again go through the algorithm
    else:
        minchoice = float('inf')

        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth-1, alpha, beta, True)
            board.pop()
            minchoice = min(minchoice, eval)
            beta = min(beta, eval)

            if beta <= alpha:
                break

        return minchoice


#this function initializes to negative and positive infinity for maximizer and minimizer respectively, then calls minmax function to update the player's move to best move
def get_best_move(board, depth):
    # Use minimax to get the best move
    best_move = None
    if board.turn == chess.WHITE:
        best_value = -float('inf')
    else:
        best_value = float('inf')
    
    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth-1, -float('inf'), float('inf'), not board.turn)
        board.pop()
        
        if board.turn == chess.WHITE:
            if board_value > best_value:
                best_value = board_value
                best_move = move

        else:
            if board_value < best_value:
                best_value = board_value
                best_move = move
                
    return best_move    

def play_game():
    board = chess.Board()
    while not board.is_game_over():
        print(board)
        if board.turn == chess.WHITE:
            # Human's turn
            move = input("Enter your move: ")
            board.push_san(move)
        else:
            # Agent's turn
            move = get_best_move(board, depth=3)
            board.push(move)

    print("Game over:", board.result())

if __name__ == "__main__":
    play_game()