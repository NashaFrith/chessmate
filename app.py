from flask import Flask, jsonify, render_template, request
import chess
import chess.engine
import chess.pgn
import io
import re
import datetime as dt
import requests as http
from chessdude import ChessDude

app = Flask(__name__, static_folder="static", template_folder="templates")
engine = ChessDude()

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/reset", methods=["POST"])
def reset():
    data = request.json or {}
    engine.reset(data.get('difficulty', 'medium'))
    return jsonify({"status": "ok"})

@app.route("/move", methods=["POST"])
def make_move():
    
    data = request.json
    player_move_response = engine.make_move_uci(data.get('from'), data.get('to'))
    player_move = player_move_response.get('move', '')
    
    
    if "error" in player_move_response:
        return jsonify(player_move_response), 400
    
    if engine.board.is_game_over():
        return jsonify({"status": "Game Over", "result": engine.board.result(), "fen": engine.board.fen()})

    player_fen = engine.board.fen()

    best = engine.best_move()
    ai_move = best["move"]
    eval_score = best["eval"]

    if not ai_move:
        return jsonify({"error": "AI could not find a move"}), 500

    white_rooks_before = len(engine.board.pieces(chess.ROOK, chess.WHITE))
    ai_move_response = engine.make_move(ai_move)
    rook_captured = len(engine.board.pieces(chess.ROOK, chess.WHITE)) < white_rooks_before

    if "error" in ai_move_response:
        return jsonify(ai_move_response), 500

    if engine.board.is_game_over():
        return jsonify({
            "status": "Game Over",
            "result": engine.board.result(),
            "player_fen": player_fen,
            "fen": engine.board.fen(),
            "ai_move": ai_move_response['move']
        })

    check_square = None
    if engine.board.is_check():
        check_square = chess.square_name(engine.board.king(engine.board.turn))

    moves_uci = [m.uci() for m in engine.board.move_stack]
    is_italian = 'f1c4' in moves_uci[:8]

    return jsonify({
        "status": "Move made",
        "player_move": player_move,
        "ai_move": ai_move_response['move'],
        "player_fen": player_fen,
        "fen": engine.board.fen(),
        "turn": engine.turn,
        "check_square": check_square,
        "eval_score": eval_score,
        "is_italian": is_italian,
        "rook_captured": rook_captured
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
    
CHESS_COM_USERNAME = 'AndrewN077'
CHESS_COM_HEADERS = {'User-Agent': 'chessmate/1.0'}
DRAW_RESULTS = {'agreed', 'stalemate', 'repetition', 'insufficient', 'timevsinsufficient', '50move'}

def opening_from_pgn(pgn_text):
    for line in pgn_text.split('\n'):
        if line.startswith('[ECOUrl '):
            url = line.split('"')[1] if '"' in line else ''
            match = re.search(r'/openings/([^?"]+)', url)
            if match:
                parts = match.group(1).replace('-', ' ').split()
                name = []
                for p in parts:
                    if p and p[0].isdigit():
                        break
                    name.append(p)
                return ' '.join(name)
    return ''

def parse_pgn(pgn_text):
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    if not game:
        return [], []
    board = game.board()
    fens = [board.fen()]
    moves = []
    for move in game.mainline_moves():
        moves.append(board.san(move))
        board.push(move)
        fens.append(board.fen())
    return fens, moves

@app.route('/review/games')
def get_review_games():
    try:
        archives = http.get(
            f'https://api.chess.com/pub/player/{CHESS_COM_USERNAME}/games/archives',
            headers=CHESS_COM_HEADERS, timeout=10
        ).json().get('archives', [])

        all_games = []
        for url in reversed(archives[-3:]):
            all_games.extend(http.get(url, headers=CHESS_COM_HEADERS, timeout=10).json().get('games', []))

        stats_data = http.get(
            f'https://api.chess.com/pub/player/{CHESS_COM_USERNAME}/stats',
            headers=CHESS_COM_HEADERS, timeout=10
        ).json()

        rapid_games  = [g for g in all_games if g.get('time_class') == 'rapid']
        blitz_games  = [g for g in all_games if g.get('time_class') == 'blitz']
        bullet_games = [g for g in all_games if g.get('time_class') == 'bullet']
        recent = sorted(rapid_games + blitz_games + bullet_games, key=lambda x: x.get('end_time', 0), reverse=True)[:30]

        processed = []
        for g in recent:
            is_white = g.get('white', {}).get('username', '').lower() == CHESS_COM_USERNAME.lower()
            side = g.get('white' if is_white else 'black', {})
            andrew_result = side.get('result', '')
            result = 'win' if andrew_result == 'win' else ('draw' if andrew_result in DRAW_RESULTS else 'loss')
            opponent = g.get('black' if is_white else 'white', {}).get('username', '')

            pgn_text = g.get('pgn', '')
            fens, moves = parse_pgn(pgn_text)
            opening = opening_from_pgn(pgn_text)

            andrew_acc = g.get('accuracies', {}).get('white' if is_white else 'black')
            opponent_rating = g.get('black' if is_white else 'white', {}).get('rating', 0)
            andrew_rating = side.get('rating', 0)

            processed.append({
                'white': g.get('white', {}).get('username', ''),
                'black': g.get('black', {}).get('username', ''),
                'is_white': is_white,
                'opponent': opponent,
                'result': result,
                'opening': opening,
                'date': g.get('end_time', 0),
                'fens': fens,
                'moves': moves,
                'accuracy': andrew_acc,
                'andrew_rating': andrew_rating,
                'opponent_rating': opponent_rating,
                'time_class': g.get('time_class', 'rapid'),
            })

        openings = {}
        for g in rapid_games:
            op = opening_from_pgn(g.get('pgn', ''))
            if op:
                openings[op] = openings.get(op, 0) + 1

        rapid_stats  = stats_data.get('chess_rapid',  {})
        blitz_stats  = stats_data.get('chess_blitz',  {})
        bullet_stats = stats_data.get('chess_bullet', {})
        record = rapid_stats.get('record', {})

        # Compact game history for charts (all time classes, tagged)
        chart_data = []
        for g in rapid_games + blitz_games + bullet_games:
            is_w = g.get('white', {}).get('username', '').lower() == CHESS_COM_USERNAME.lower()
            side = g.get('white' if is_w else 'black', {})
            opp_side = g.get('black' if is_w else 'white', {})
            ar = side.get('result', '')
            res = 'win' if ar == 'win' else ('draw' if ar in DRAW_RESULTS else 'loss')
            pgn_text = g.get('pgn', '')
            move_nums = [int(m) for m in re.findall(r'(\d+)\.(?!\.)', pgn_text) if int(m) < 500]
            ts = g.get('end_time', 0)
            hour = dt.datetime.fromtimestamp(ts).hour if ts else None
            chart_data.append({
                'date': ts,
                'result': res,
                'is_white': is_w,
                'time_class': g.get('time_class', 'rapid'),
                'andrew_rating': side.get('rating', 0),
                'opponent_rating': opp_side.get('rating', 0),
                'accuracy': g.get('accuracies', {}).get('white' if is_w else 'black'),
                'opening': opening_from_pgn(pgn_text),
                'move_count': max(move_nums) if move_nums else 0,
                'hour': hour,
            })
        chart_data.sort(key=lambda x: x['date'])

        return jsonify({
            'games': processed,
            'chart_data': chart_data,
            'stats': {
                'rapid_rating':  rapid_stats.get('last',  {}).get('rating', 0),
                'blitz_rating':  blitz_stats.get('last',  {}).get('rating', 0),
                'bullet_rating': bullet_stats.get('last', {}).get('rating', 0),
                'wins':   record.get('win',  0),
                'losses': record.get('loss', 0),
                'draws':  record.get('draw', 0),
                'blitz_wins':   blitz_stats.get('record', {}).get('win',  0),
                'blitz_losses': blitz_stats.get('record', {}).get('loss', 0),
                'blitz_draws':  blitz_stats.get('record', {}).get('draw', 0),
                'bullet_wins':   bullet_stats.get('record', {}).get('win',  0),
                'bullet_losses': bullet_stats.get('record', {}).get('loss', 0),
                'bullet_draws':  bullet_stats.get('record', {}).get('draw', 0),
                'top_openings': sorted(openings.items(), key=lambda x: -x[1])[:7]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/review/eval', methods=['POST'])
def get_review_eval():
    data = request.json or {}
    fen = data.get('fen')
    if not fen:
        return jsonify({'error': 'No FEN'}), 400
    try:
        board = chess.Board(fen)
        result = engine.sf.play(board, chess.engine.Limit(time=0.05), info=chess.engine.INFO_SCORE)
        score = result.info.get('score')
        eval_val = score.white().score(mate_score=10000) if score else 0
        return jsonify({'eval': eval_val})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
