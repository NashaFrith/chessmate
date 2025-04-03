from flask import Flask, jsonify, render_template, request
import chess
import chess.engine
import chess
from chessdude import get_best_move 

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/best-move", methods=["POST"])
def best_move():
    try:
        data = request.json
        fen = data.get("fen")  # Get the board position as FEN
        if not fen:
            return jsonify({"error": "FEN string is required"}), 400
        
        board = chess.Board(fen)
        move = get_best_move(board)

        if move:
            return jsonify({"best_move": board.san(move)})  # Convert move to SAN
        else:
            return jsonify({"error": "No valid moves found"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
