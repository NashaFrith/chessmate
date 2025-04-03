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
    data = request.json
    move = data.get('move')
    if move:
        response = engine.make_move(move)
        if response.get("status") == "Move made" and engine.turn == 'b':
            ai_move = engine.best_move()
            engine.make_move(ai_move)
            response["ai_move"] = ai_move
        return jsonify(response)
    return jsonify({"error": "Invalid move"}), 400

    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
