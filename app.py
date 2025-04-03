from flask import Flask, jsonify, render_template, request
import chess
import chess.engine
from chessdude import ChessDude

app = Flask(__name__, static_folder="static", template_folder="templates")
engine = ChessDude()

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/move", methods=["POST"])
def make_move():
    
    player_move = request.json.get('move')
    player_move_response = engine.make_move(player_move)
    
    
    if "error" in player_move_response:
        return jsonify(player_move_response), 400
    
    print(f"Board after player move: {engine.board.fen()}")
    
    if engine.board.is_game_over():
        return jsonify({"status": "Game Over", "result": engine.board.result(), "fen": engine.board.fen()})
    
    
    ai_move = engine.best_move(depth=6)
    ai_move_response = engine.make_move(ai_move)
    
    
    if engine.board.is_game_over():
        return jsonify({
            "status": "Game Over", 
            "result": engine.board.result(), 
            "fen": engine.board.fen(), 
            "ai_move": ai_move_response['move']
        })
    
    return jsonify({
        "status": "Move made", 
        "player_move": player_move, 
        "ai_move": ai_move_response['move'], 
        "fen": engine.board.fen(), 
        "turn": engine.turn
    })

 #----Old----#
# @app.route("/move", methods=["POST"])
# def make_move():
#     data = request.json
#     move = data.get('move')
#     if move:
#         response = engine.make_move(move)
#         if response.get("status") == "Move made" and engine.turn == 'b':
#             ai_move = engine.best_move()
#             engine.make_move(ai_move)
#             response["ai_move"] = ai_move
#         return jsonify(response)
#     return jsonify({"error": "Invalid move"}), 400
 #----Old----#
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
