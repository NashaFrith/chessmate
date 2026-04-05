from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from functools import wraps
import os
import chess
import chess.engine
import chess.pgn
import io
import re
import datetime as dt
import requests as http
from chessdude import ChessDude

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get('SECRET_KEY', 'chessmate-dev-secret')
APP_PASSWORD = os.environ.get('APP_PASSWORD', 'chessmates')
engine = None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('authenticated'):
            if request.is_json or request.path.startswith('/review') or request.path.startswith('/move') or request.path.startswith('/reset'):
                return jsonify({'error': 'Unauthorized'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_engine():
    global engine
    if engine is None:
        engine = ChessDude()
    return engine

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('password') == APP_PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('home'))
        error = 'wrong password, try again'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@require_auth
def home():
    return render_template('index.html')

@app.route("/reset", methods=["POST"])
@require_auth
def reset():
    data = request.json or {}
    get_engine().reset(data.get('difficulty', 'medium'))
    return jsonify({"status": "ok"})

@app.route("/move", methods=["POST"])
@require_auth
def make_move():
    e = get_engine()
    data = request.json
    player_move_response = e.make_move_uci(data.get('from'), data.get('to'))
    player_move = player_move_response.get('move', '')

    if "error" in player_move_response:
        return jsonify(player_move_response), 400

    if e.board.is_game_over():
        return jsonify({"status": "Game Over", "result": e.board.result(), "fen": e.board.fen()})

    player_fen = e.board.fen()

    best = e.best_move()
    ai_move = best["move"]
    eval_score = best["eval"]

    if not ai_move:
        return jsonify({"error": "AI could not find a move"}), 500

    white_rooks_before = len(e.board.pieces(chess.ROOK, chess.WHITE))
    ai_move_response = e.make_move(ai_move)
    rook_captured = len(e.board.pieces(chess.ROOK, chess.WHITE)) < white_rooks_before

    if "error" in ai_move_response:
        return jsonify(ai_move_response), 500

    if e.board.is_game_over():
        return jsonify({
            "status": "Game Over",
            "result": e.board.result(),
            "player_fen": player_fen,
            "fen": e.board.fen(),
            "ai_move": ai_move_response['move']
        })

    check_square = None
    if e.board.is_check():
        check_square = chess.square_name(e.board.king(e.board.turn))

    moves_uci = [m.uci() for m in e.board.move_stack]
    is_italian = 'f1c4' in moves_uci[:8]

    return jsonify({
        "status": "Move made",
        "player_move": player_move,
        "ai_move": ai_move_response['move'],
        "player_fen": player_fen,
        "fen": e.board.fen(),
        "turn": e.turn,
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
@require_auth
def get_review_games():
    try:
        archives = http.get(
            f'https://api.chess.com/pub/player/{CHESS_COM_USERNAME}/games/archives',
            headers=CHESS_COM_HEADERS, timeout=10
        ).json().get('archives', [])

        all_games = []
        for url in reversed(archives):
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
                'opponent': opp_side.get('username', ''),
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

@app.route('/review/friend/<username>')
@require_auth
def friend_metrics(username):
    try:
        # Fetch Andrew's archives and friend's stats in parallel-ish
        archives = http.get(
            f'https://api.chess.com/pub/player/{CHESS_COM_USERNAME}/games/archives',
            headers=CHESS_COM_HEADERS, timeout=10
        ).json().get('archives', [])

        all_games = []
        for url in reversed(archives[-6:]):
            all_games.extend(http.get(url, headers=CHESS_COM_HEADERS, timeout=10).json().get('games', []))

        # Friend's global stats
        friend_stats = {}
        try:
            friend_stats = http.get(
                f'https://api.chess.com/pub/player/{username}/stats',
                headers=CHESS_COM_HEADERS, timeout=8
            ).json()
        except Exception:
            pass

        # Andrew's global stats for comparison
        andrew_stats = {}
        try:
            andrew_stats = http.get(
                f'https://api.chess.com/pub/player/{CHESS_COM_USERNAME}/stats',
                headers=CHESS_COM_HEADERS, timeout=8
            ).json()
        except Exception:
            pass

        h2h = [g for g in all_games if
               g.get('white', {}).get('username', '').lower() == username.lower() or
               g.get('black', {}).get('username', '').lower() == username.lower()]

        if not h2h:
            return jsonify({'error': f'No games found against {username} in the last 6 months'}), 404

        h2h_sorted = sorted(h2h, key=lambda g: g.get('end_time', 0))

        andrew_wins = 0; friend_wins = 0; draws = 0
        andrew_accs = []; friend_accs = []
        andrew_as_white = {}; andrew_as_black = {}
        friend_as_white = {}; friend_as_black = {}
        # Per-opening results for Andrew {opening: [wins, losses, draws]}
        opening_results = {}
        # Color results
        white_wins = 0; white_losses = 0; white_draws = 0
        black_wins = 0; black_losses = 0; black_draws = 0
        # Recent streak (last 5)
        recent = []

        for g in h2h_sorted:
            is_andrew_white = g.get('white', {}).get('username', '').lower() == CHESS_COM_USERNAME.lower()
            andrew_side = g.get('white' if is_andrew_white else 'black', {})
            andrew_result = andrew_side.get('result', '')
            result = 'win' if andrew_result == 'win' else ('draw' if andrew_result in DRAW_RESULTS else 'loss')

            if result == 'win': andrew_wins += 1
            elif result == 'loss': friend_wins += 1
            else: draws += 1

            recent.append(result)

            if is_andrew_white:
                if result == 'win': white_wins += 1
                elif result == 'loss': white_losses += 1
                else: white_draws += 1
            else:
                if result == 'win': black_wins += 1
                elif result == 'loss': black_losses += 1
                else: black_draws += 1

            accs = g.get('accuracies', {})
            if accs:
                a = accs.get('white' if is_andrew_white else 'black')
                f = accs.get('black' if is_andrew_white else 'white')
                if a is not None: andrew_accs.append(a)
                if f is not None: friend_accs.append(f)

            pgn_text = g.get('pgn', '')
            opening = opening_from_pgn(pgn_text)
            if opening:
                if opening not in opening_results:
                    opening_results[opening] = [0, 0, 0]
                if result == 'win': opening_results[opening][0] += 1
                elif result == 'loss': opening_results[opening][1] += 1
                else: opening_results[opening][2] += 1

                if is_andrew_white:
                    andrew_as_white[opening] = andrew_as_white.get(opening, 0) + 1
                    friend_as_black[opening] = friend_as_black.get(opening, 0) + 1
                else:
                    andrew_as_black[opening] = andrew_as_black.get(opening, 0) + 1
                    friend_as_white[opening] = friend_as_white.get(opening, 0) + 1

        recent5 = recent[-5:]
        total = len(h2h)

        # Pull ratings
        def get_rating(stats, tc):
            return stats.get(f'chess_{tc}', {}).get('last', {}).get('rating')

        friend_rapid  = get_rating(friend_stats, 'rapid')
        friend_blitz  = get_rating(friend_stats, 'blitz')
        andrew_rapid  = get_rating(andrew_stats, 'rapid')
        andrew_blitz  = get_rating(andrew_stats, 'blitz')

        suggestions = []

        # 1. Recent streak
        if len(recent5) >= 3:
            last3 = recent5[-3:]
            if all(r == 'loss' for r in last3):
                suggestions.append(f"You've lost your last {len([r for r in recent5 if r == 'loss'])} games against them — they've found something that works. Try a completely different opening next time.")
            elif all(r == 'win' for r in last3):
                suggestions.append(f"You're on a {len([r for r in recent5 if r == 'win'])}-game winning streak against them — whatever you're doing is working, don't overthink it.")

        # 2. Color imbalance
        white_total = white_wins + white_losses + white_draws
        black_total = black_wins + black_losses + black_draws
        if white_total >= 3 and black_total >= 3:
            white_wr = white_wins / white_total
            black_wr = black_wins / black_total
            if white_wr - black_wr > 0.25:
                suggestions.append(f"You win {round(white_wr*100)}% as White vs {round(black_wr*100)}% as Black against them — you're much stronger with the first move here. Play for the initiative early.")
            elif black_wr - white_wr > 0.25:
                suggestions.append(f"You win {round(black_wr*100)}% as Black vs {round(white_wr*100)}% as White against them — you actually do better defending. Stay solid and wait for their mistakes.")

        # 3. Best and worst openings
        good = [(op, w, l, d) for op, (w, l, d) in opening_results.items() if w + l + d >= 2 and w > l]
        bad  = [(op, w, l, d) for op, (w, l, d) in opening_results.items() if w + l + d >= 2 and l > w]
        if good:
            best = max(good, key=lambda x: x[1] - x[2])
            suggestions.append(f"You do well in the {best[0]} against them ({best[1]}W-{best[2]}L) — lean into it.")
        if bad:
            worst = max(bad, key=lambda x: x[2] - x[1])
            suggestions.append(f"You struggle in the {worst[0]} against them ({worst[1]}W-{worst[2]}L) — consider avoiding it or preparing it more deeply.")

        # 4. Most-used opening where Andrew also loses — most likely to appear AND most dangerous
        def dangerous_opening(friend_side_dict):
            # Filter to openings played >= 2 times, rank by Andrew's loss rate then frequency
            candidates = [
                (op, count, opening_results.get(op, [0, 0, 0]))
                for op, count in friend_side_dict.items()
                if count >= 2
            ]
            if not candidates:
                return None
            return max(candidates, key=lambda x: (x[2][1] / max(x[1], 1), x[1]))

        danger_black = dangerous_opening(friend_as_black)
        if danger_black:
            op, count, (w, l, d) = danger_black
            wr_str = f" — you're {w}W-{l}L in it" if w + l > 0 else ''
            suggestions.append(f"They play the {op} a lot as Black{wr_str}. This is where they hurt you most — prepare your White sidelines against it.")
        elif friend_as_black:
            fav = max(friend_as_black, key=friend_as_black.get)
            w, l, d = opening_results.get(fav, [0, 0, 0])
            wr_str = f" — you're {w}W-{l}L in it" if w + l > 0 else ''
            suggestions.append(f"They favour the {fav} as Black{wr_str}. Prepare your White sidelines against it.")

        danger_white = dangerous_opening(friend_as_white)
        if danger_white:
            op, count, (w, l, d) = danger_white
            wr_str = f" — you're {w}W-{l}L in it" if w + l > 0 else ''
            suggestions.append(f"They play the {op} a lot as White{wr_str}. This is where they hurt you most — have a solid Black response ready.")
        elif friend_as_white:
            fav = max(friend_as_white, key=friend_as_white.get)
            w, l, d = opening_results.get(fav, [0, 0, 0])
            wr_str = f" — you're {w}W-{l}L in it" if w + l > 0 else ''
            suggestions.append(f"They often play the {fav} as White{wr_str}. Have a solid Black response ready.")

        # 5. Accuracy gap vs them
        if andrew_accs and friend_accs:
            a_avg = sum(andrew_accs) / len(andrew_accs)
            f_avg = sum(friend_accs) / len(friend_accs)
            if f_avg > a_avg + 3:
                suggestions.append(f"They outaccuracy you in your H2H games ({f_avg:.1f}% vs {a_avg:.1f}%) — they're calculating more carefully. Slow down before committing to moves.")
            elif a_avg > f_avg + 3:
                suggestions.append(f"You're more accurate than them in your games ({a_avg:.1f}% vs {f_avg:.1f}%) — keep the precision up and convert your advantages.")

        # 6. Rating context from global stats
        if friend_rapid and andrew_rapid:
            diff = friend_rapid - andrew_rapid
            win_pct = round(andrew_wins / total * 100) if total else 0
            if diff > 100:
                suggestions.append(f"They're rated {diff} points above you in Rapid globally ({friend_rapid} vs {andrew_rapid}), but you're winning {win_pct}% of your H2H games — that's genuinely impressive.")
            elif diff < -100:
                suggestions.append(f"You're rated {-diff} points above them in Rapid globally ({andrew_rapid} vs {friend_rapid}). A win rate of {win_pct}% here is expected — push for higher.")
            else:
                suggestions.append(f"You're closely rated in Rapid ({andrew_rapid} vs {friend_rapid}) — these are your most competitive games. Small edge in preparation will decide it.")

        return jsonify({
            'total': total,
            'andrew_wins': andrew_wins,
            'friend_wins': friend_wins,
            'draws': draws,
            'andrew_avg_accuracy': round(sum(andrew_accs) / len(andrew_accs), 1) if andrew_accs else None,
            'friend_avg_accuracy': round(sum(friend_accs) / len(friend_accs), 1) if friend_accs else None,
            'andrew_as_white': sorted(andrew_as_white.items(), key=lambda x: -x[1])[:5],
            'andrew_as_black': sorted(andrew_as_black.items(), key=lambda x: -x[1])[:5],
            'friend_as_white': sorted(friend_as_white.items(), key=lambda x: -x[1])[:5],
            'friend_as_black': sorted(friend_as_black.items(), key=lambda x: -x[1])[:5],
            'friend_rapid': friend_rapid,
            'friend_blitz': friend_blitz,
            'suggestions': suggestions,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/review/eval', methods=['POST'])
@require_auth
def get_review_eval():
    data = request.json or {}
    fen = data.get('fen')
    if not fen:
        return jsonify({'error': 'No FEN'}), 400
    try:
        board = chess.Board(fen)
        result = get_engine().sf.play(board, chess.engine.Limit(time=0.05), info=chess.engine.INFO_SCORE)
        score = result.info.get('score')
        eval_val = score.white().score(mate_score=10000) if score else 0
        return jsonify({'eval': eval_val})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
