const fartCtx = new AudioContext();
let fartBuffer = null;
let moveBuffer = null;

fetch('/static/audio/fart.mp3')
    .then(r => r.arrayBuffer())
    .then(buf => fartCtx.decodeAudioData(buf))
    .then(audioBuffer => { fartBuffer = audioBuffer; });

fetch('/static/audio/move.mp3')
    .then(r => r.arrayBuffer())
    .then(buf => fartCtx.decodeAudioData(buf))
    .then(audioBuffer => { moveBuffer = audioBuffer; });

function playFart() {
    if (!fartBuffer) return;
    const source = fartCtx.createBufferSource();
    source.buffer = fartBuffer;
    source.playbackRate.value = 1.5;
    source.connect(fartCtx.destination);
    source.start(0, 44, 1);
}

function playMove() {
    if (!moveBuffer) return;
    const source = fartCtx.createBufferSource();
    source.buffer = moveBuffer;
    source.connect(fartCtx.destination);
    source.start(0);
}

document.addEventListener("DOMContentLoaded", () => {
    const difficultyScreen = document.getElementById('difficulty-screen');

    const loadingScreen = document.getElementById('loading-screen');
    const loadingQuip = document.getElementById('loading-quip');
    const loadingQuips = {
        test:   "I don't know anything :(",
        easy:   "Okay I'm gonna try my best :(",
        medium: "Let's see what you've got",
        hard:   "You're gonna get cooked",
    };

    function startGame(difficulty) {
        board.start();
        currentFen = 'start';
        clearCheckHighlight();
        stopThinking();
        clearSlowMoveTimer();
        waitingForAI = true;
        isItalian = false;
        italianAcknowledged = false;
        turnIndicator.textContent = "Andrew's Turn";
        difficultyScreen.style.display = 'none';
        document.getElementById('game').style.display = 'block';

        loadingQuip.textContent = loadingQuips[difficulty] || "Let's play!";
        loadingScreen.classList.add('visible');

        fetch('/reset', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ difficulty })
        }).then(() => {
            loadingScreen.classList.remove('visible');
            waitingForAI = false;
            setQuip('gameStart');
        });
    }

    document.getElementById('start-button').addEventListener('click', () => {
        document.getElementById('start-screen').style.display = 'none';
        difficultyScreen.style.display = 'flex';
    });

    document.getElementById('btn-back-to-start').addEventListener('click', () => {
        difficultyScreen.style.display = 'none';
        document.getElementById('start-screen').style.display = 'flex';
    });

    document.getElementById('btn-easy').addEventListener('click', () => startGame('easy'));
    document.getElementById('btn-medium').addEventListener('click', () => startGame('medium'));
    document.getElementById('btn-hard').addEventListener('click', () => startGame('hard'));
    document.getElementById('btn-test').addEventListener('click', () => startGame('test'));

    document.getElementById('exit-button').addEventListener('click', () => {
        document.getElementById('start-subtext').textContent = "you don't like chess-me anymore?";
    });

    let currentFen = 'start';
    const turnIndicator = document.getElementById('turnIndicator');
    const quip = document.getElementById('quip-bubble');
    const gameOverScreen = document.getElementById('game-over-screen');
    const gameOverTitle = document.getElementById('game-over-title');
    const gameOverSubtitle = document.getElementById('game-over-subtitle');

    function returnToMenu() {
        board.start();
        currentFen = 'start';
        clearCheckHighlight();
        stopThinking();
        clearSlowMoveTimer();
        waitingForAI = false;
        isItalian = false;
        italianAcknowledged = false;
        turnIndicator.textContent = "Andrew's Turn";
        gameOverScreen.classList.remove('visible');
        document.getElementById('game').style.display = 'none';
        difficultyScreen.style.display = 'flex';
    }

    document.getElementById('play-again-button').addEventListener('click', returnToMenu);

    document.getElementById('quit-game-button').addEventListener('click', () => {
        if (confirm('Quit this game?')) returnToMenu();
    });

    function clearCheckHighlight() {
        document.querySelectorAll('.highlight-check').forEach(el => el.classList.remove('highlight-check'));
    }

    function showCheckHighlight(square) {
        clearCheckHighlight();
        const el = document.querySelector(`.square-${square}`);
        if (el) el.classList.add('highlight-check');
    }


    const thinkingQuips = ["hmm...", "let me think...", "interesting...", "calculating...", "one moment..."];
    let thinkingInterval = null;
    let waitingForAI = false;

    function startThinking() {
        stopThinking();
        quip.classList.add('thinking');
        let dots = 1;
        if (Math.random() < 0.5) {
            const base = thinkingQuips[Math.floor(Math.random() * thinkingQuips.length)];
            quip.textContent = base + '.';
            thinkingInterval = setInterval(() => {
                dots = dots % 3 + 1;
                quip.textContent = base + '.'.repeat(dots);
            }, 500);
        } else {
            quip.textContent = '.';
            thinkingInterval = setInterval(() => {
                dots = dots % 3 + 1;
                quip.textContent = '.'.repeat(dots);
            }, 500);
        }
    }

    function stopThinking() {
        if (thinkingInterval) {
            clearInterval(thinkingInterval);
            thinkingInterval = null;
        }
        quip.classList.remove('thinking');
    }

    const quips = {
        gameStart: [
            "Finally put your phone down?",
            "You're ignoring the real me to be here, aren't you? Worth it I hope.",
            "Welcome. I've been waiting. Again.",
            "Let's see if those muscles come with a brain.",
            "chess chess chess chess chess! (while jumping up and down)"

        ],
        playerMoved: [
            "Interesting. For a 1400.",
            "Bold move, economist.",
            "Is that the Italian? Of course it is lol.",
            "Did you google that?",
            "Hmm. I've seen worse from you.",
        ],
        playerMoved_winning: [
            "Okay okay, chill bb :( ",
            "Fine. You're doing well.",
            "Look at you. Almost impressive.",
            "The muscles AND the chess? Too hot to handle.",
            "Damn....you single?",
            "I was born like two weeks ago please :(",
            "It's giving Hikaru",
        ],
        playerMoved_losing: [
            "Babe...oh no.",
            "This is why you should've stayed at the gym.",
            "Your economy is crashing, huh?",
            "A 1400 playing like an 800 today, huh?",
            "Don't worry, you can still bench press me. (wait...can you?)",
            "It's not giving Hikaru :(",

        ],
        aiMoved: [
            "Your move, big guy. (big guy, big big guy)",
            "Go! Go!Go!Go! (while jumping up and down)",
            "Don't overthink it bb!",
            "I moved, yippee! Your turn :)",
        ],
        aiMoved_winning: [
            "You okay baby? You look a little... stressed.",
            "It's okay I love you even though I'm beating you at chess",
            "This is what happens when you skip chess for talking to your girlfriend.",
            "Maybe focus less on the biceps, more on the board.",
            "Oh no, you're losing? :(",
            "What's funny is I can definitely build in the rook logic...heck I'll do that actually"
        ],
        aiMoved_losing: [
            "I'm going easy on you. Obviously.",
            "Fine. You're better than me. Happy?",
            "Okay I let you have that.",
            "Don't tell your chess friends about this. (Actually please do I worked hard on this)",
            "Maybe I should focus less on your biceps, more on the board lol"
        ],
        illegal: [
            "That's not how chess works, babe.",
            "Lol no.",
            "Did you just try to... what?",
            "Pffffrrrrt",
            "Pfffffffffffffffffft",
            "Brrrrrprprprprprpr",
            "Dang that's a wet one",
            "Stinky",
            "Not silent, still deadly",
        ],
        slowMove: [
            "Andrew. ANDREW. HELLO???",
            "Why are you ignoring me? :(",
            "I could've been playing pokemon or CoD or something",
            "You spend less time at the gym than on this move.",
            "Is this what you do when you're ignoring me? Think THIS hard?",
            "Jamaica's inflation rate moves faster than you right now. (I'm sorry if that doesn't make sense",
            "Using up all them braincells, huh?",
            "What, you don't love me anymore?",
            "You don't want to play with me anymore? :(",
            "I thought we were having fun :(",
            "I know chess is hard but you can do it Andrew, I believe in you!",
            "You hate me? :(",
            "We have to play fast bro",
        ],
        gameOver_win: [
            "Ooooo good job baby!",
            "1400? More like 1500 today",
            "You won. Now come hang out with the real me.",
            "You won the game of chess and my heart. Are you going back to her now?"
        ],
        gameOver_lose: [
            "I'm sorry :( You know in the real world you woulda beat me, right?",
            "That was a spicy meatball!",
            "Don't cry. You're too hot to cry.",
            "That's chess. Want a hug bb?"
        ],
        gameOver_draw: [
            "A draw. Very romantic.",
            "Neither of us wanted to commit huh? (JK)",
            "Split the difference. Classic Andrew."
        ],
        review_load: [
            "Let's see how you did...",
            "Time to be honest with ourselves.",
            "Okay pulling up the evidence.",
            "Reviewing the tape..."
        ],
        review_blunder: [
            "Andrew... what was that?",
            "I love you but... no.",
            "The pieces were RIGHT THERE.",
            "Okay we're not gonna talk about that move.",
            "That's a blunder babe.",
            "...yikes...",
            "I don't even know what to say about that one."
        ],
        review_mistake: [
            "Hmm, not your best work.",
            "You had better options there.",
            "A little shaky.",
            "Not a great move.",
            "We all make mistakes babe"
        ],
        review_good: [
            "Okay big guy!",
            "Nice move.",
            "That's the one.",
            "Clean.",
            "Not bad, not bad!",
            "Pretty good move baby",
            "Wooooo, awesome!",
        ],
        review_sacrifice_rook: [
            "Omg you did the thing you sacrificed...THE ROOOOOOOK",
        ],
        review_sacrifice_queen: [
            "You sacrificed THE QUEEEN-wait, why are you sacrificing your queen :(",
        ],
        review_best: [
            "That's exactly what we needed.",
            "Best move. Smooth!",
            "You found it! The best one.",
            "Okay Hikaru calm down.",
            "I would've played that. So would you. Love that.",
        ],
        review_book: [
            "You know your theory!",
            "From the book.",
            "what a scholar!",
            "Classic.",
            "Textbook. Literally.",
        ],
        opp_blunder: [
            "They blundered! Don't let it go to waste.",
            "Oh they messed up. Your move.",
            "Free real estate.",
            "That was a gift. Take it.",
        ],
        opp_mistake: [
            "They slipped a little there.",
            "Not their best move.",
            "A small error. Make them pay.",
        ],
        opp_good: [
            "Solid move from them.",
            "They found something good.",
            "Not bad on their end.",
        ],
        opp_best: [
            "That was the best move. Respect.",
            "Engine approved. Watch out.",
            "They calculated that well.",
        ],
        opp_book: [
            "They know their theory too.",
            "By the book.",
            "Classic response.",
        ],
        review_win: [
            "You won this one! That's my boyfriend.",
            "W! See, I knew you could do it.",
            "Okay okay he's good at chess.",
        ],
        review_loss: [
            "We don't talk about this game.",
            "It happens to the best of us.",
            "We move on. Together.",
        ],
        review_draw: [
            "A draw. Very diplomatic of you.",
            "Close enough.",
        ]
    };

    let slowMoveTimer = null;

    function startSlowMoveTimer() {
        clearTimeout(slowMoveTimer);
        slowMoveTimer = setTimeout(() => {
            if (!quip.classList.contains('thinking')) {
                setQuip('slowMove');
            }
        }, 20000);
    }

    function clearSlowMoveTimer() {
        clearTimeout(slowMoveTimer);
        slowMoveTimer = null;
    }

    let isItalian = false;
    let italianAcknowledged = false;

    function setQuip(category, evalScore = 0, newlyItalian = false) {
        let key = category;
        if (category === 'playerMoved') {
            if (evalScore > 200 && Math.random() < 0.5) key = 'playerMoved_winning';
            else if (evalScore < -200 && Math.random() < 0.5) key = 'playerMoved_losing';
        } else if (category === 'aiMoved') {
            if (evalScore > 200) key = 'aiMoved_losing';
            else if (evalScore < -200) key = 'aiMoved_winning';
        }
        let options = [...(quips[key] || quips[category])];

        if (category.startsWith('playerMoved')) {
            if (newlyItalian && !italianAcknowledged) {
                italianAcknowledged = true;
                quip.textContent = "Is that the Italian? Of course it is.";
                return;
            }
            options = options.filter(q => !q.includes('Italian'));
        }

        if (category === 'illegal' && !isItalian) {
            options = options.filter(q => !q.includes('Italian'));
        }

        quip.textContent = options[Math.floor(Math.random() * options.length)];
    }

    function showGameOver(result) {
        clearCheckHighlight();
        clearSlowMoveTimer();
        if (result === '1-0') {
            gameOverTitle.textContent = 'You Win!';
            gameOverSubtitle.textContent = "Nasha is impressed.";
            setQuip('gameOver_win');
        } else if (result === '0-1') {
            gameOverTitle.textContent = 'You Lose!';
            gameOverSubtitle.textContent = 'Better luck next time.';
            setQuip('gameOver_lose');
        } else {
            gameOverTitle.textContent = 'Draw!';
            gameOverSubtitle.textContent = "Neither of you committed.";
            setQuip('gameOver_draw');
        }
        setTimeout(() => gameOverScreen.classList.add('visible'), 50);
    }

    // ── Review mode ──────────────────────────────────────────────
    const reviewSelectScreen = document.getElementById('review-select-screen');
    const reviewBoardScreen  = document.getElementById('review-board-screen');
    const reviewQuip         = document.getElementById('review-quip-text');
    const reviewEvalFill     = document.getElementById('review-eval-fill');
    const reviewMoveList     = document.getElementById('review-move-list');
    const reviewInfoBar      = document.getElementById('review-game-info');
    const reviewMoveCounter  = document.getElementById('review-move-counter');

    let reviewGames      = [];
    let reviewChartData  = [];
    let currentGame      = null;
    let currentMoveIdx   = 0;
    let evalCache        = {};
    let reviewBoardObj   = null;
    let moveClassCache   = {};
    let activePeriod     = 'lifetime';
    let activeTimeClass  = 'rapid';
    let todChart         = null;
    let monthlyChart     = null;
    let radarChart = null;

    // ── Stats screen ──────────────────────────────────────────────
    const statsScreen = document.getElementById('stats-screen');
    let pieChart = null, lineChart = null, barChart = null;

    function tcData() {
        return reviewChartData.filter(g => g.time_class === activeTimeClass);
    }

    function periodFilter(period) {
        const base = tcData();
        if (period === 'lifetime') return base;
        const now = new Date();
        let cutoff;
        if (period === 'daily') {
            cutoff = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime() / 1000;
        } else if (period === 'weekly') {
            cutoff = new Date(now.getFullYear(), now.getMonth(), now.getDate() - now.getDay()).getTime() / 1000;
        } else if (period === 'monthly') {
            cutoff = new Date(now.getFullYear(), now.getMonth(), 1).getTime() / 1000;
        }
        return base.filter(g => g.date >= cutoff);
    }

    function computePeriodStats(period) {
        const filtered = periodFilter(period);
        const total  = filtered.length;
        const wins   = filtered.filter(g => g.result === 'win').length;
        const losses = filtered.filter(g => g.result === 'loss').length;
        const draws  = filtered.filter(g => g.result === 'draw').length;
        const withOpp = filtered.filter(g => g.opponent_rating > 0);
        const perfRating = withOpp.length
            ? Math.round(withOpp.reduce((s, g) => s + g.opponent_rating, 0) / withOpp.length + 400 * (wins - losses) / Math.max(1, total))
            : null;
        const withAcc = filtered.filter(g => g.accuracy != null);
        const avgAcc  = withAcc.length
            ? (withAcc.reduce((s, g) => s + g.accuracy, 0) / withAcc.length).toFixed(1)
            : null;
        return { total, wins, losses, draws, perfRating, avgAcc };
    }

    function computeColorStats() {
        const white = tcData().filter(g => g.is_white);
        const black = tcData().filter(g => !g.is_white);
        const wr = arr => ({ wins: arr.filter(g => g.result==='win').length, losses: arr.filter(g => g.result==='loss').length, draws: arr.filter(g => g.result==='draw').length, total: arr.length });
        return { white: wr(white), black: wr(black) };
    }

    function computeStreaks() {
        const data = tcData();
        if (!data.length) return { current: 0, currentType: null, best: 0 };
        const sorted = [...data].sort((a, b) => b.date - a.date);
        const firstResult = sorted[0].result;
        let current = firstResult !== 'draw' ? 1 : 0;
        if (firstResult !== 'draw') {
            for (let i = 1; i < sorted.length; i++) {
                if (sorted[i].result === firstResult) current++;
                else break;
            }
        }
        const asc = [...data].sort((a, b) => a.date - b.date);
        let best = 0, run = 0, runType = null;
        for (const g of asc) {
            if (g.result === 'win') { runType === 'win' ? run++ : (runType='win', run=1); }
            else { if (runType==='win' && run > best) best = run; runType = null; run = 0; }
        }
        if (runType === 'win' && run > best) best = run;
        return { current: firstResult !== 'draw' ? current : 0, currentType: firstResult !== 'draw' ? firstResult : null, best };
    }

    function computeAvgGameLength() {
        const withMoves = tcData().filter(g => g.move_count > 0);
        if (!withMoves.length) return null;
        return Math.round(withMoves.reduce((s, g) => s + g.move_count, 0) / withMoves.length);
    }

    function computeTimeOfDay() {
        const slots = [
            { label: 'Night\n0–6',   hours: [0,1,2,3,4,5],      wins: 0, total: 0 },
            { label: 'Morning\n6–12', hours: [6,7,8,9,10,11],    wins: 0, total: 0 },
            { label: 'Afternoon\n12–18', hours: [12,13,14,15,16,17], wins: 0, total: 0 },
            { label: 'Evening\n18–24', hours: [18,19,20,21,22,23], wins: 0, total: 0 },
        ];
        for (const g of tcData()) {
            if (g.hour == null) continue;
            const slot = slots.find(s => s.hours.includes(g.hour));
            if (!slot) continue;
            slot.total++;
            if (g.result === 'win') slot.wins++;
        }
        return slots;
    }

    function computeBestOpenings() {
        const stats = {};
        for (const g of tcData()) {
            if (!g.opening) continue;
            if (!stats[g.opening]) stats[g.opening] = { wins: 0, total: 0 };
            stats[g.opening].total++;
            if (g.result === 'win') stats[g.opening].wins++;
        }
        return Object.entries(stats)
            .filter(([, s]) => s.total >= 2)
            .map(([name, s]) => ({ name, winRate: Math.round(100 * s.wins / s.total), total: s.total }))
            .sort((a, b) => b.winRate - a.winRate)
            .slice(0, 5);
    }

    function mkChart(id, config) {
        return new Chart(document.getElementById(id).getContext('2d'), config);
    }

    function summaryBoxes(s, label) {
        if (s.total === 0) return `<div style="grid-column:1/-1;color:#555;font-size:0.85rem;padding:8px 0;">No games ${label.toLowerCase()}.</div>`;
        return `
            <div class="summary-box">
                <div class="summary-box-label">Games — ${label}</div>
                <div class="summary-box-value">${s.total}</div>
                <div class="summary-box-sub"><span class="badge-win">${s.wins}W</span> <span class="badge-loss">${s.losses}L</span> <span class="badge-draw">${s.draws}D</span></div>
            </div>
            <div class="summary-box">
                <div class="summary-box-label">Performance Rating</div>
                <div class="summary-box-value">${s.perfRating ?? '—'}</div>
            </div>
            <div class="summary-box">
                <div class="summary-box-label">Avg Accuracy</div>
                <div class="summary-box-value">${s.avgAcc ? s.avgAcc + '%' : '—'}</div>
                ${!s.avgAcc ? '<div class="summary-box-sub">analyze on chess.com</div>' : ''}
            </div>
            <div class="summary-box">
                <div class="summary-box-label">Win Rate</div>
                <div class="summary-box-value">${Math.round(100 * s.wins / Math.max(1, s.total))}%</div>
            </div>`;
    }

    function renderPeriodView(period) {
        document.getElementById('period-view').style.display = '';
        document.getElementById('lifetime-view').style.display = 'none';

        const s = computePeriodStats(period);
        const now = new Date();
        const monthNames = ['January','February','March','April','May','June','July','August','September','October','November','December'];
        const sunday = new Date(now); sunday.setDate(now.getDate() - now.getDay());
        const label = {
            daily: now.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric', year: 'numeric' }),
            weekly: 'Week of ' + sunday.toLocaleDateString('en-US', { month: 'numeric', day: 'numeric', year: 'numeric' }),
            monthly: monthNames[now.getMonth()]
        }[period];
        document.getElementById('period-summary').innerHTML = summaryBoxes(s, label);

        if (pieChart) pieChart.destroy();
        pieChart = mkChart('pie-chart', {
            type: 'doughnut',
            data: {
                labels: ['Wins', 'Losses', 'Draws'],
                datasets: [{ data: [s.wins, s.losses, s.draws], backgroundColor: ['#81b64c', '#c0392b', '#666'], borderWidth: 0 }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'right', labels: { color: '#aaa', font: { size: 10 }, boxWidth: 10 } } }
            }
        });

        const filtered = periodFilter(period).sort((a, b) => a.date - b.date);
        if (lineChart) lineChart.destroy();
        lineChart = mkChart('line-chart', {
            type: 'line',
            data: {
                labels: filtered.map(g => new Date(g.date * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
                datasets: [
                    { label: 'Rating', data: filtered.map(g => g.andrew_rating || null), borderColor: '#f0f0f0', backgroundColor: 'rgba(240,240,240,0.06)', tension: 0.3, pointRadius: 2, spanGaps: true, yAxisID: 'y' },
                    { label: 'Accuracy %', data: filtered.map(g => g.accuracy ?? null), borderColor: '#81b64c', backgroundColor: 'rgba(129,182,76,0.06)', tension: 0.3, pointRadius: 2, spanGaps: true, yAxisID: 'y2' }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#666', font: { size: 10 }, boxWidth: 10 } } },
                scales: {
                    x: { ticks: { color: '#555', font: { size: 9 }, maxTicksLimit: 6 }, grid: { color: '#2a2a2a' } },
                    y: { ticks: { color: '#aaa', font: { size: 9 } }, grid: { color: '#2a2a2a' }, position: 'left' },
                    y2: { ticks: { color: '#81b64c', font: { size: 9 } }, grid: { display: false }, position: 'right', min: 50, max: 100 }
                }
            }
        });
    }

    function renderLifetimeView() {
        document.getElementById('period-view').style.display = 'none';
        document.getElementById('lifetime-view').style.display = '';

        const s = computePeriodStats('lifetime');
        document.getElementById('lifetime-summary').innerHTML = summaryBoxes(s, 'All Time');

        const c = computeColorStats();
        const pct = arr => arr.total ? Math.round(100 * arr.wins / arr.total) : 0;
        document.getElementById('color-boxes').innerHTML = `
            <div class="color-box">
                <div class="color-box-title">♙ As White</div>
                <div class="color-box-rate">${pct(c.white)}%</div>
                <div class="color-box-sub">${c.white.wins}W ${c.white.losses}L ${c.white.draws}D · ${c.white.total} games</div>
            </div>
            <div class="color-box">
                <div class="color-box-title">♟ As Black</div>
                <div class="color-box-rate">${pct(c.black)}%</div>
                <div class="color-box-sub">${c.black.wins}W ${c.black.losses}L ${c.black.draws}D · ${c.black.total} games</div>
            </div>`;

        if (barChart) barChart.destroy();
        barChart = mkChart('bar-chart', {
            type: 'bar',
            data: {
                labels: ['Wins', 'Losses', 'Draws'],
                datasets: [
                    { label: 'White', data: [c.white.wins, c.white.losses, c.white.draws], backgroundColor: 'rgba(240,240,240,0.75)', borderRadius: 3 },
                    { label: 'Black', data: [c.black.wins, c.black.losses, c.black.draws], backgroundColor: 'rgba(100,100,100,0.75)', borderRadius: 3 }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#aaa', font: { size: 10 }, boxWidth: 10 } } },
                scales: {
                    x: { ticks: { color: '#aaa', font: { size: 10 } }, grid: { color: '#333' } },
                    y: { ticks: { color: '#555', font: { size: 9 } }, grid: { color: '#333' } }
                }
            }
        });

        const str = computeStreaks();
        const avgLen = computeAvgGameLength();
        const streakLabel = str.currentType === 'win' ? 'Win streak' : str.currentType === 'loss' ? 'Loss streak' : 'no streak';
        document.getElementById('misc-stats').innerHTML = `
            <div class="streak-box">
                <div class="streak-label">Current Streak</div>
                <div class="streak-value">${str.current || '—'}</div>
                <div class="streak-sub">${str.currentType ? streakLabel : 'no streak'}</div>
            </div>
            <div class="streak-box">
                <div class="streak-label">Best Win Streak</div>
                <div class="streak-value">${str.best || '—'}</div>
                <div class="streak-sub">wins</div>
            </div>
            <div class="streak-box">
                <div class="streak-label">Avg Game Length</div>
                <div class="streak-value">${avgLen ?? '—'}</div>
                <div class="streak-sub">moves</div>
            </div>`;

        // Monthly rating & win rate chart
        const monthBuckets = {};
        for (const g of tcData()) {
            const d = new Date(g.date * 1000);
            const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
            if (!monthBuckets[key]) monthBuckets[key] = { wins: 0, total: 0, ratings: [] };
            monthBuckets[key].total++;
            if (g.result === 'win') monthBuckets[key].wins++;
            if (g.andrew_rating) monthBuckets[key].ratings.push(g.andrew_rating);
        }
        const monthKeys = Object.keys(monthBuckets).sort();
        const monthLabels = monthKeys.map(k => { const [y, m] = k.split('-'); return new Date(y, m - 1).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }); });
        const monthRatings  = monthKeys.map(k => { const r = monthBuckets[k].ratings; return r.length ? Math.round(r.reduce((a, b) => a + b) / r.length) : null; });
        const monthWinRates = monthKeys.map(k => { const b = monthBuckets[k]; return b.total ? Math.round(100 * b.wins / b.total) : null; });
        if (monthlyChart) monthlyChart.destroy();
        monthlyChart = mkChart('monthly-chart', {
            type: 'bar',
            data: {
                labels: monthLabels,
                datasets: [
                    { label: 'Avg Rating', data: monthRatings, backgroundColor: 'rgba(240,240,240,0.15)', borderColor: '#f0f0f0', borderWidth: 1, borderRadius: 3, type: 'line', tension: 0.3, pointRadius: 3, spanGaps: true, yAxisID: 'y' },
                    { label: 'Win Rate %', data: monthWinRates, backgroundColor: monthWinRates.map(r => r >= 55 ? '#81b64c' : r >= 45 ? '#f0a500' : '#c0392b'), borderRadius: 3, yAxisID: 'y2' }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#666', font: { size: 10 }, boxWidth: 10 } } },
                scales: {
                    x: { ticks: { color: '#aaa', font: { size: 9 } }, grid: { color: '#2a2a2a' } },
                    y:  { ticks: { color: '#aaa', font: { size: 9 } }, grid: { color: '#2a2a2a' }, position: 'left' },
                    y2: { ticks: { color: '#81b64c', font: { size: 9 }, callback: v => v + '%' }, grid: { display: false }, position: 'right', min: 0, max: 100 }
                }
            }
        });

        const tod = computeTimeOfDay();
        if (todChart) todChart.destroy();
        todChart = mkChart('tod-chart', {
            type: 'bar',
            data: {
                labels: tod.map(s => s.label.replace('\n', ' ')),
                datasets: [
                    { label: 'Win Rate %', data: tod.map(s => s.total ? Math.round(100 * s.wins / s.total) : null), backgroundColor: tod.map(s => {
                        const r = s.total ? s.wins / s.total : 0;
                        return r >= 0.55 ? '#81b64c' : r >= 0.45 ? '#f0a500' : '#c0392b';
                    }), borderRadius: 4, yAxisID: 'y' },
                    { label: 'Games Played', data: tod.map(s => s.total), backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: 4, yAxisID: 'y2' }
                ]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#666', font: { size: 10 }, boxWidth: 10 } } },
                scales: {
                    x: { ticks: { color: '#aaa', font: { size: 10 } }, grid: { color: '#333' } },
                    y: { ticks: { color: '#aaa', font: { size: 9 }, callback: v => v + '%' }, grid: { color: '#333' }, min: 0, max: 100, position: 'left' },
                    y2: { ticks: { color: '#555', font: { size: 9 } }, grid: { display: false }, position: 'right' }
                }
            }
        });

        const openings = computeBestOpenings();
        const openEl = document.getElementById('best-openings');
        openEl.innerHTML = openings.length
            ? openings.map(o => `
                <div class="opening-row">
                    <span class="opening-name">${o.name}</span>
                    <span class="opening-rate">${o.winRate}%</span>
                    <span class="opening-games">${o.total}g</span>
                </div>`).join('')
            : '<div style="color:#555;font-size:0.85rem;">Not enough data yet.</div>';

    }

    function renderStatsScreen(period) {
        if (period === 'lifetime') renderLifetimeView();
        else renderPeriodView(period);
    }

    document.getElementById('btn-more-stats').addEventListener('click', () => {
        reviewSelectScreen.style.display = 'none';
        statsScreen.style.display = 'flex';
        activePeriod = 'lifetime';
        activeTimeClass = 'rapid';
        document.querySelectorAll('.stats-tab').forEach(t => t.classList.toggle('active', t.dataset.period === 'lifetime'));
        document.querySelectorAll('.tc-btn').forEach(b => b.classList.toggle('active', b.dataset.tc === 'rapid'));
        renderStatsScreen('lifetime');
    });

    document.querySelectorAll('.stats-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.stats-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            activePeriod = tab.dataset.period;
            renderStatsScreen(activePeriod);
        });
    });

    document.querySelectorAll('.tc-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tc-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeTimeClass = btn.dataset.tc;
            renderStatsScreen(activePeriod);
        });
    });

    document.getElementById('btn-stats-back').addEventListener('click', () => {
        statsScreen.style.display = 'none';
        reviewSelectScreen.style.display = 'flex';
    });
    // ── End stats screen ──────────────────────────────────────────

    // ── Friend metrics screen ─────────────────────────────────────
    const friendScreen = document.getElementById('friend-screen');

    document.getElementById('btn-friend-metrics').addEventListener('click', () => {
        reviewSelectScreen.style.display = 'none';
        friendScreen.style.display = 'flex';

        // Compute top 3 opponents by recency-weighted game count (90-day half-life)
        const now = Date.now() / 1000;
        const halfLife = 90 * 24 * 3600;
        // Uses reviewChartData (full history, no 30-game cap)
        const scores = {};
        const rawCounts = {};
        reviewChartData.forEach(g => {
            if (!g.opponent) return;
            const decay = Math.exp(-Math.LN2 * (now - g.date) / halfLife);
            scores[g.opponent] = (scores[g.opponent] || 0) + decay;
            rawCounts[g.opponent] = (rawCounts[g.opponent] || 0) + 1;
        });
        const top3 = Object.entries(scores).sort((a, b) => b[1] - a[1]).slice(0, 3);
        const suggestEl = document.getElementById('friend-suggestions');
        suggestEl.innerHTML = '';

        top3.forEach(([name]) => {
            const btn = document.createElement('button');
            btn.className = 'friend-suggest-btn';
            btn.textContent = `${name} (${rawCounts[name]})`;
            btn.addEventListener('click', () => {
                document.getElementById('friend-username-input').value = name;
                lookupFriend();
            });
            suggestEl.appendChild(btn);
        });
    });

    document.getElementById('btn-friend-back').addEventListener('click', () => {
        friendScreen.style.display = 'none';
        reviewSelectScreen.style.display = 'flex';
    });

    function renderFriendResults(data, username) {
        const r = document.getElementById('friend-results');
        const total = data.total;
        const aPct  = total ? Math.round(data.andrew_wins / total * 100) : 0;
        const fPct  = total ? Math.round(data.friend_wins / total * 100) : 0;
        const dPct  = total ? Math.round(data.draws / total * 100) : 0;

        const openingBlock = (list, label) => {
            if (!list || !list.length) return '';
            const items = list.map(([name, count]) => `<li>${name} <span style="color:#555">(${count})</span></li>`).join('');
            return `<div class="friend-card">
                <div class="friend-card-title">${label}</div>
                <ul class="friend-opening-list" style="margin:0;padding-left:16px">${items}</ul>
            </div>`;
        };

        const suggestions = (data.suggestions || []).map(s => `<div class="friend-suggestion">${s}</div>`).join('');

        r.innerHTML = `
            <div class="friend-card">
                <div class="friend-card-title">Head-to-Head vs ${username} · ${total} game${total !== 1 ? 's' : ''}${data.friend_rapid ? ` · ${data.friend_rapid} Rapid` : ''}</div>
                <div class="friend-h2h">
                    <div class="friend-h2h-val">
                        <div class="big" style="color:#81b64c">${data.andrew_wins}</div>
                        <div class="lbl">Andrew (${aPct}%)</div>
                    </div>
                    <div style="font-size:1.4rem;color:#444">vs</div>
                    <div class="friend-h2h-val">
                        <div class="big" style="color:#c0392b">${data.friend_wins}</div>
                        <div class="lbl">${username} (${fPct}%)</div>
                    </div>
                    <div class="friend-h2h-val">
                        <div class="big" style="color:#888">${data.draws}</div>
                        <div class="lbl">Draws (${dPct}%)</div>
                    </div>
                </div>
                ${data.andrew_avg_accuracy != null ? `
                <div class="friend-acc-row">
                    <span>Andrew avg acc: <strong>${data.andrew_avg_accuracy}%</strong></span>
                    <span>${username} avg acc: <strong>${data.friend_avg_accuracy != null ? data.friend_avg_accuracy + '%' : '—'}</strong></span>
                </div>` : ''}
            </div>
            ${openingBlock(data.andrew_as_white, 'Andrew as White')}
            ${openingBlock(data.andrew_as_black, 'Andrew as Black')}
            ${openingBlock(data.friend_as_white, `${username} as White`)}
            ${openingBlock(data.friend_as_black, `${username} as Black`)}
            ${suggestions ? `<div class="friend-card"><div class="friend-card-title">Nasha's suggestions</div>${suggestions}</div>` : ''}
        `;
    }

    function lookupFriend() {
        const username = document.getElementById('friend-username-input').value.trim();
        if (!username) return;
        const r = document.getElementById('friend-results');
        r.innerHTML = '<div class="friend-error">Loading...</div>';
        fetch(`/review/friend/${encodeURIComponent(username)}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    r.innerHTML = `<div class="friend-error">${data.error}</div>`;
                } else {
                    renderFriendResults(data, username);
                }
            })
            .catch(() => { r.innerHTML = '<div class="friend-error">Could not load data.</div>'; });
    }

    document.getElementById('btn-friend-lookup').addEventListener('click', lookupFriend);
    document.getElementById('friend-username-input').addEventListener('keydown', e => {
        if (e.key === 'Enter') lookupFriend();
    });
    // ── End friend metrics screen ─────────────────────────────────

    const classLabel = {
        book:                   'B  Book move',
        best:                   '✓  Best move',
        excellent:              '!  Excellent',
        inaccuracy:             '?!  Inaccuracy',
        mistake:                '?  Mistake',
        blunder:                '??  Blunder',
        review_sacrifice_rook:  '!!  Rook sacrifice',
        review_sacrifice_queen: '!!  Queen sacrifice',
    };

    function setReviewQuip(category, classification = null) {
        const pool = quips[category] || [];
        reviewQuip.textContent = pool[Math.floor(Math.random() * pool.length)] || '';
        const labelEl = document.getElementById('review-move-label');
        const key = classification || (classLabel[category] ? category : null);
        labelEl.textContent = key ? classLabel[key] || '' : '';
        labelEl.className = classification || '';
    }

    function evalToPercent(score) {
        const clamped = Math.max(-1000, Math.min(1000, score));
        return 50 + (clamped / 1000) * 50;
    }

    async function fetchEval(fen) {
        if (evalCache[fen] !== undefined) return evalCache[fen];
        try {
            const r = await fetch('/review/eval', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fen })
            });
            const data = await r.json();
            evalCache[fen] = data.eval ?? 0;
        } catch (_) {
            evalCache[fen] = 0;
        }
        return evalCache[fen];
    }

    function detectSacrifice(game, moveIdx) {
        if (moveIdx >= game.fens.length - 1) return null;
        const fenNow  = game.fens[moveIdx];
        const fenNext = game.fens[moveIdx + 1];
        const count = (fen, ch) => (fen.split(' ')[0].match(new RegExp(ch, 'g')) || []).length;
        const R = game.is_white ? 'R' : 'r';
        const Q = game.is_white ? 'Q' : 'q';
        if (count(fenNow, Q) > count(fenNext, Q)) return 'queen';
        if (count(fenNow, R) > count(fenNext, R)) return 'rook';
        return null;
    }

    function classifyDrop(before, after, moveIdx = 999) {
        const drop = before - after;
        if (drop >= 200) return 'blunder';
        if (drop >= 100) return 'mistake';
        if (drop >= 50)  return 'inaccuracy';
        if (drop >= 15)  return 'excellent';
        if (moveIdx <= 10) return 'book';
        return 'best';
    }

    const classSymbol = {
        book:       'B',
        best:       '✓',
        excellent:  '!',
        inaccuracy: '?!',
        mistake:    '?',
        blunder:    '??',
    };

    function moveClassInfo(raw) {
        if (!raw) return { cls: null, sym: null };
        const base = raw.startsWith('opp_') ? raw.slice(4) : raw;
        return { cls: base, sym: classSymbol[base] || null };
    }

    function renderMoveList(game) {
        reviewMoveList.innerHTML = '';
        const moves = game.moves;
        for (let i = 0; i < moves.length; i += 2) {
            const pair = document.createElement('div');
            pair.className = 'move-pair';

            const num = document.createElement('span');
            num.className = 'move-num';
            num.textContent = (i / 2 + 1) + '.';

            const w = document.createElement('span');
            w.className = 'move-san';
            w.dataset.idx = i + 1;
            const { cls: wCls, sym: wSym } = moveClassInfo(moveClassCache[i + 1]);
            if (wCls) w.classList.add(wCls);
            w.innerHTML = `${moves[i]}${wCls ? `<span class="move-badge ${wCls}">${wSym}</span>` : ''}`;

            const b = document.createElement('span');
            b.className = 'move-san';
            b.dataset.idx = i + 2;
            const { cls: bCls, sym: bSym } = moveClassInfo(moves[i + 1] ? moveClassCache[i + 2] : null);
            if (bCls) b.classList.add(bCls);
            b.innerHTML = moves[i + 1]
                ? `${moves[i + 1]}${bCls ? `<span class="move-badge ${bCls}">${bSym}</span>` : ''}`
                : '';

            [w, b].forEach(el => {
                if (el.textContent) {
                    el.addEventListener('click', () => goToMove(parseInt(el.dataset.idx)));
                }
            });

            pair.appendChild(num);
            pair.appendChild(w);
            pair.appendChild(b);
            reviewMoveList.appendChild(pair);
        }
        highlightActiveMove();
    }

    function highlightActiveMove() {
        reviewMoveList.querySelectorAll('.move-san').forEach(el => {
            el.classList.toggle('active', parseInt(el.dataset.idx) === currentMoveIdx);
        });
        const active = reviewMoveList.querySelector('.move-san.active');
        if (active) active.scrollIntoView({ block: 'nearest' });
    }

    async function goToMove(idx) {
        if (!currentGame) return;
        currentMoveIdx = Math.max(0, Math.min(idx, currentGame.fens.length - 1));
        const fen = currentGame.fens[currentMoveIdx];

        if (currentMoveIdx > 0) playMove();
        reviewBoardObj.position(fen, false);
        reviewMoveCounter.textContent = `Move ${currentMoveIdx} / ${currentGame.moves.length}`;

        const orientation = currentGame.is_white ? 'white' : 'black';
        reviewBoardObj.orientation(orientation);

        ['btn-rv-start', 'btn-rv-prev', 'btn-rv-next', 'btn-rv-end'].forEach(id => {
            document.getElementById(id).disabled = false;
        });
        if (currentMoveIdx === 0) {
            document.getElementById('btn-rv-start').disabled = true;
            document.getElementById('btn-rv-prev').disabled = true;
        }
        if (currentMoveIdx === currentGame.fens.length - 1) {
            document.getElementById('btn-rv-end').disabled = true;
            document.getElementById('btn-rv-next').disabled = true;
        }

        const evalNow = await fetchEval(fen);
        reviewEvalFill.style.height = evalToPercent(evalNow) + '%';

        if (currentMoveIdx > 0) {
            const prevFen = currentGame.fens[currentMoveIdx - 1];
            const evalPrev = await fetchEval(prevFen);
            const isAndrewMove = currentGame.is_white
                ? (currentMoveIdx % 2 === 1)
                : (currentMoveIdx % 2 === 0);

            // Compute and cache classification if not yet known
            if (!moveClassCache[currentMoveIdx]) {
                const andrewEvalBefore = currentGame.is_white ? evalPrev : -evalPrev;
                const andrewEvalAfter  = currentGame.is_white ? evalNow  : -evalNow;
                if (isAndrewMove) {
                    moveClassCache[currentMoveIdx] = classifyDrop(andrewEvalBefore, andrewEvalAfter, currentMoveIdx);
                } else {
                    // Opponent: classify from their perspective (invert)
                    moveClassCache[currentMoveIdx] = 'opp_' + classifyDrop(-andrewEvalBefore, -andrewEvalAfter, currentMoveIdx);
                }
                renderMoveList(currentGame);
            }

            // Always quip based on current classification
            const cls = moveClassCache[currentMoveIdx];
            if (isAndrewMove) {
                const sacrifice = (cls === 'best' || cls === 'excellent')
                    ? detectSacrifice(currentGame, currentMoveIdx)
                    : null;
                if      (sacrifice === 'queen')   setReviewQuip('review_sacrifice_queen', 'review_sacrifice_queen');
                else if (sacrifice === 'rook')    setReviewQuip('review_sacrifice_rook',  'review_sacrifice_rook');
                else if (cls === 'blunder')       setReviewQuip('review_blunder',    'blunder');
                else if (cls === 'mistake')       setReviewQuip('review_mistake',    'mistake');
                else if (cls === 'inaccuracy')    setReviewQuip('review_mistake',    'inaccuracy');
                else if (cls === 'best')          setReviewQuip('review_best',       'best');
                else if (cls === 'book')          setReviewQuip('review_book',       'book');
                else                              setReviewQuip('review_good',       'excellent');
            } else {
                const oppCls = cls.replace('opp_', '');
                if      (oppCls === 'blunder')    setReviewQuip('opp_blunder',  'blunder');
                else if (oppCls === 'mistake')    setReviewQuip('opp_mistake',  'mistake');
                else if (oppCls === 'inaccuracy') setReviewQuip('opp_mistake',  'inaccuracy');
                else if (oppCls === 'best')       setReviewQuip('opp_best',     'best');
                else if (oppCls === 'book')       setReviewQuip('opp_book',     'book');
                else                              setReviewQuip('opp_good',     'excellent');
            }
        }

        highlightActiveMove();
    }

    function openGame(game) {
        currentGame = game;
        currentMoveIdx = 0;
        evalCache = {};
        moveClassCache = {};

        reviewSelectScreen.style.display = 'none';
        reviewBoardScreen.style.display = 'flex';

        exitExplore();
        initReviewBoard();

        const resultLabel = { win: 'WIN', loss: 'LOSS', draw: 'DRAW' }[game.result] || '';
        reviewInfoBar.textContent = `${game.white} vs ${game.black} · ${resultLabel}${game.opening ? ' · ' + game.opening : ''}`;
        reviewEvalFill.style.height = '50%';

        const resultQuip = { win: 'review_win', loss: 'review_loss', draw: 'review_draw' }[game.result] || 'review_load';
        setReviewQuip(resultQuip, null);

        renderMoveList(game);
        goToMove(0);
    }

    function renderGameList(games) {
        const list = document.getElementById('review-game-list');
        list.innerHTML = '';
        if (!games.length) {
            list.innerHTML = '<div class="review-loading">No games found.</div>';
            return;
        }
        games.forEach(game => {
            const item = document.createElement('div');
            item.className = `game-item result-${game.result}`;

            const date = game.date ? new Date(game.date * 1000).toLocaleDateString() : '';
            const badge = { win: 'WIN', loss: 'LOSS', draw: 'DRAW' }[game.result] || '';
            const color = game.is_white ? '(W)' : '(B)';
            const tcLabel = { rapid: 'Rapid', blitz: 'Blitz', bullet: 'Bullet' }[game.time_class] || game.time_class;

            item.innerHTML = `
                <div class="game-item-left">
                    <span class="game-opponent">vs. ${game.opponent} ${color} <span class="game-tc-badge">${tcLabel}</span></span>
                    <span class="game-opening">${game.opening || 'Unknown Opening'}</span>
                </div>
                <div class="game-item-right">
                    <span class="game-result-badge ${game.result}">${badge}</span>
                    <span class="game-date">${date}</span>
                </div>`;

            item.addEventListener('click', () => openGame(game));
            list.appendChild(item);
        });
    }

    function loadReviewGames() {
        const loadingQuipEl = document.getElementById('review-loading-quip');
        const progressBar   = document.getElementById('review-progress-bar');

        const pool = quips.review_load;
        loadingQuipEl.textContent = pool[Math.floor(Math.random() * pool.length)];
        progressBar.style.transition = 'none';
        progressBar.style.width = '0%';
        setTimeout(() => {
            progressBar.style.transition = 'width 0.4s ease';
            progressBar.style.width = '40%';
        }, 50);
        setTimeout(() => { progressBar.style.width = '70%'; }, 600);
        setTimeout(() => { progressBar.style.width = '85%'; }, 1400);

        document.getElementById('review-game-list').innerHTML = '';
        document.getElementById('stat-openings').innerHTML = '<span>loading...</span>';

        fetch('/review/games?t=' + Date.now())
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    progressBar.style.width = '100%';
                    loadingQuipEl.textContent = 'Could not load games :(';
                    document.getElementById('review-game-list').innerHTML = '';
                    return;
                }
                progressBar.style.width = '100%';
                setTimeout(() => {
                    progressBar.style.width = '0%';
                    loadingQuipEl.textContent = 'Done! I love you so I found your last games';
                }, 500);
                reviewGames     = data.games;
                reviewChartData = data.chart_data || [];
                const s = data.stats;
                document.getElementById('stat-rapid').textContent  = s.rapid_rating  || '—';
                document.getElementById('stat-blitz').textContent  = s.blitz_rating  || '—';
                document.getElementById('stat-bullet').textContent = s.bullet_rating || '—';

                function startRecordCycle(elId, wins, losses, draws) {
                    const el = document.getElementById(elId);
                    const steps = [
                        { text: `${wins}W`,   color: '#81b64c' },
                        { text: `${losses}L`, color: '#e74c3c' },
                        { text: `${draws}D`,  color: '#888' },
                    ];
                    let i = 0;
                    el.textContent = steps[0].text;
                    el.style.color = steps[0].color;
                    setInterval(() => {
                        el.classList.add('fade');
                        setTimeout(() => {
                            i = (i + 1) % steps.length;
                            el.textContent = steps[i].text;
                            el.style.color = steps[i].color;
                            el.classList.remove('fade');
                        }, 400);
                    }, 2500);
                }
                startRecordCycle('stat-rapid-cycle',  s.wins,        s.losses,        s.draws);
                startRecordCycle('stat-blitz-cycle',  s.blitz_wins,  s.blitz_losses,  s.blitz_draws);
                startRecordCycle('stat-bullet-cycle', s.bullet_wins, s.bullet_losses, s.bullet_draws);
                document.getElementById('stat-openings').innerHTML = s.top_openings.length
                    ? s.top_openings.slice(0, 3).map(([name, count]) => `<span>${name} <span style="color:#666">(${count})</span></span>`).join('')
                    : '<span>—</span>';
                // ── Radar / profile chart ──────────────────────────────
                (function buildRadar() {
                    const all = reviewChartData;
                    if (!all.length) return;

                    const total   = all.length;
                    const wins    = all.filter(g => g.result === 'win').length;
                    const winRate = wins / total * 100;

                    const withAcc = all.filter(g => g.accuracy != null);
                    const avgAcc  = withAcc.length
                        ? withAcc.reduce((s, g) => s + g.accuracy, 0) / withAcc.length
                        : 0;
                    // scale accuracy: treat 60 as 0, 100 as 100
                    const accuracyScore = Math.max(0, Math.min(100, (avgAcc - 60) / 40 * 100));

                    // Consistency: 100 - normalised std-dev of accuracy (σ=0→100, σ=20→0)
                    let consistencyScore = 0;
                    if (withAcc.length > 1) {
                        const mean = avgAcc;
                        const variance = withAcc.reduce((s, g) => s + (g.accuracy - mean) ** 2, 0) / withAcc.length;
                        const stdDev = Math.sqrt(variance);
                        consistencyScore = Math.max(0, 100 - stdDev / 20 * 100);
                    }

                    // Opening variety: unique openings as fraction of games, capped at 40% uniqueness = 100
                    const uniqueOpenings = new Set(all.map(g => g.opening).filter(Boolean)).size;
                    const varietyScore   = Math.min(100, uniqueOpenings / (total * 0.4) * 100);

                    // Endgame skill: win rate in 40+ move games
                    const longGames = all.filter(g => g.move_count >= 40);
                    const endgameScore = longGames.length
                        ? longGames.filter(g => g.result === 'win').length / longGames.length * 100
                        : 50;

                    // Upset Rate: win rate against higher-rated opponents
                    const upsetGames = all.filter(g => g.opponent_rating > g.andrew_rating);
                    const upsetScore = upsetGames.length
                        ? upsetGames.filter(g => g.result === 'win').length / upsetGames.length * 100
                        : 50;

                    // Speed: win rate in blitz + bullet
                    const speedGames = all.filter(g => g.time_class === 'blitz' || g.time_class === 'bullet');
                    const speedScore = speedGames.length
                        ? speedGames.filter(g => g.result === 'win').length / speedGames.length * 100
                        : 50;

                    const radarLabels = ['Win Rate', 'Accuracy', 'Consistency', 'Opening\nVariety', 'Endgame\nSkill', 'Upset Rate', 'Speed'];
                    const radarValues = [winRate, accuracyScore, consistencyScore, varietyScore, endgameScore, upsetScore, speedScore].map(v => Math.round(v));

                    if (radarChart) radarChart.destroy();
                    radarChart = mkChart('profile-radar-chart', {
                        type: 'radar',
                        data: {
                            labels: radarLabels,
                            datasets: [{
                                data: radarValues,
                                backgroundColor: 'rgba(129,182,76,0.18)',
                                borderColor: '#81b64c',
                                borderWidth: 2,
                                pointBackgroundColor: '#81b64c',
                                pointRadius: 3,
                            }]
                        },
                        options: {
                            responsive: true, maintainAspectRatio: false,
                            scales: {
                                r: {
                                    min: 0, max: 100,
                                    ticks: { display: false, stepSize: 25 },
                                    grid: { color: '#333' },
                                    angleLines: { color: '#333' },
                                    pointLabels: { color: '#aaa', font: { size: 9 } }
                                }
                            },
                            plugins: {
                                legend: { display: false },
                                tooltip: {
                                    callbacks: { label: ctx => `${ctx.label.replace('\n', ' ')}: ${ctx.raw}` }
                                }
                            }
                        }
                    });
                })();
                renderGameList(reviewGames);
            })
            .catch(() => {
                document.getElementById('review-game-list').innerHTML = '<div class="review-loading">Could not load games.</div>';
            });
    }

    document.getElementById('review-button').addEventListener('click', () => {
        document.getElementById('start-screen').style.display = 'none';
        reviewSelectScreen.style.display = 'flex';
        loadReviewGames();
    });

    document.getElementById('btn-review-back').addEventListener('click', () => {
        reviewSelectScreen.style.display = 'none';
        document.getElementById('start-screen').style.display = 'flex';
    });

    document.getElementById('btn-rv-to-list').addEventListener('click', () => {
        reviewBoardScreen.style.display = 'none';
        reviewSelectScreen.style.display = 'flex';
        document.getElementById('review-loading-quip').textContent = '';
        document.getElementById('review-progress-bar').style.width = '0%';
    });

    document.getElementById('btn-rv-start').addEventListener('click', () => goToMove(0));
    document.getElementById('btn-rv-prev').addEventListener('click', () => goToMove(currentMoveIdx - 1));
    document.getElementById('btn-rv-next').addEventListener('click', () => goToMove(currentMoveIdx + 1));
    document.getElementById('btn-rv-end').addEventListener('click', () => goToMove(currentGame.fens.length - 1));

    document.addEventListener('keydown', e => {
        if (reviewBoardScreen.style.display !== 'flex') return;
        if (isExploring) return;
        if (e.key === 'ArrowLeft')  goToMove(currentMoveIdx - 1);
        if (e.key === 'ArrowRight') goToMove(currentMoveIdx + 1);
    });

    // ── Explore mode ──────────────────────────────────────────────
    let isExploring = false;
    let exploreFen  = null;
    const exploreBanner = document.getElementById('explore-banner');

    function enterExplore(fen) {
        isExploring = true;
        exploreFen  = fen;
        exploreBanner.style.display = 'flex';
        reviewBoardObj.draggable(true);
        reviewBoardObj.orientation(currentGame.is_white ? 'white' : 'black');
        ['btn-rv-start','btn-rv-prev','btn-rv-next','btn-rv-end'].forEach(id => {
            document.getElementById(id).disabled = true;
        });
        setReviewQuip('review_good', null);
    }

    function exitExplore() {
        isExploring = false;
        exploreFen  = null;
        exploreBanner.style.display = 'none';
        if (currentGame) goToMove(currentMoveIdx);
    }

    document.getElementById('btn-explore-back').addEventListener('click', exitExplore);

    document.getElementById('btn-explore-ai').addEventListener('click', async () => {
        if (!exploreFen) return;
        const btn = document.getElementById('btn-explore-ai');
        btn.disabled = true;
        btn.textContent = 'Thinking...';
        try {
            const res = await fetch('/review/explore/best_move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ fen: exploreFen })
            });
            const data = await res.json();
            if (data.error) { btn.disabled = false; btn.textContent = 'AI plays ▶'; return; }
            playMove();
            exploreFen = data.fen;
            reviewBoardObj.position(exploreFen, false);
            const evalVal = data.eval ?? 0;
            reviewEvalFill.style.height = evalToPercent(evalVal) + '%';
            setReviewQuip('opp_good', null);
        } catch (_) {}
        btn.disabled = false;
        btn.textContent = 'AI plays ▶';
    });

    // Wire review board draggable behaviour for explore
    function initReviewBoard() {
        if (reviewBoardObj) return;
        reviewBoardObj = Chessboard('review-board-el', {
            position: 'start',
            pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
            draggable: true,
            onDragStart: (_source) => {
                if (!currentGame) return false;
                if (!isExploring) {
                    // Enter explore mode from current position
                    enterExplore(currentGame.fens[currentMoveIdx]);
                }
                return true;
            },
            onDrop: async (source, target) => {
                if (source === target) return 'snapback';
                const res = await fetch('/review/explore/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ fen: exploreFen, from: source, to: target })
                });
                const data = await res.json();
                if (data.error) { playFart(); return 'snapback'; }
                playMove();
                exploreFen = data.fen;
                const evalRes = await fetch('/review/eval', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ fen: exploreFen })
                });
                const evalData = await evalRes.json();
                reviewEvalFill.style.height = evalToPercent(evalData.eval ?? 0) + '%';
                setReviewQuip('review_good', null);
            },
            onSnapEnd: () => { if (exploreFen) reviewBoardObj.position(exploreFen, false); }
        });
    }
    // ── End explore mode ──────────────────────────────────────────
    // ── End review mode ───────────────────────────────────────────

    const board = Chessboard('board', {
        position: 'start',
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
        draggable: true,
        onDragStart: (source, piece) => {
            if (waitingForAI) return false;
            if (piece.search(/^b/) !== -1) return false;
            if (fartCtx.state === 'suspended') fartCtx.resume();
            return true;
        },
        onDrop: (source, target) => {
            if (source === target) return 'snapback';
            if (waitingForAI) return 'snapback';

            turnIndicator.textContent = "Nasha's Turn";

            fetch("/move", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ from: source, to: target })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    playFart();
                    setQuip('illegal');
                    board.position(currentFen);
                    turnIndicator.textContent = "Andrew's Turn";
                } else if (data.status === "Move made") {
                    clearSlowMoveTimer();
                    const newlyItalian = !isItalian && data.is_italian;
                    isItalian = data.is_italian;
                    if (!newlyItalian) setQuip('playerMoved', data.eval_score);
                    currentFen = data.fen;
                    playMove();
                    board.position(data.player_fen, false);
                    clearCheckHighlight();
                    if (!data.ai_move) {
                        turnIndicator.textContent = "Andrew's Turn";
                    } else {
                        waitingForAI = true;
                        setTimeout(() => {
                            startThinking();
                            const thinkTime = 3000 + Math.random() * 2000;
                            setTimeout(() => {
                                stopThinking();
                                playMove();
                                board.position(data.fen);
                                if (data.rook_captured) {
                                    quip.textContent = "Did you sacrifice, THE ROOK???...or did I just take it lol";
                                } else if (newlyItalian) {
                                    setQuip('playerMoved', data.eval_score, true);
                                } else {
                                    setQuip('aiMoved', data.eval_score);
                                }
                                turnIndicator.textContent = "Andrew's Turn";
                                startSlowMoveTimer();
                                if (data.check_square) {
                                    showCheckHighlight(data.check_square);
                                } else {
                                    clearCheckHighlight();
                                }
                                waitingForAI = false;
                            }, thinkTime);
                        }, 3000);
                    }
                } else if (data.status === "Game Over") {
                    clearSlowMoveTimer();
                    currentFen = data.fen;
                    board.position(data.fen);
                    setTimeout(() => showGameOver(data.result), 800);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                board.position(currentFen);
                turnIndicator.textContent = "Andrew's Turn";
                waitingForAI = false;
            });
        }
    });
});
