document.addEventListener("DOMContentLoaded", () => {
    let currentFen = 'start';

    const board = Chessboard('board', {
        position: 'start',
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
        draggable: true,
        onDrop: (source, target) => {
            if (source === target) return 'snapback';

            fetch("/move", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ from: source, to: target })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    board.position(currentFen);
                } else if (data.status === "Move made") {
                    currentFen = data.fen;
                    board.position(data.player_fen);
                    if (data.ai_move) {
                        setTimeout(() => {
                            board.position(data.fen);
                        }, 800);
                    }
                } else if (data.status === "Game Over") {
                    currentFen = data.fen;
                    board.position(data.fen);
                    alert("Game Over: " + data.result);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                board.position(currentFen);
            });
        }
    });
});
