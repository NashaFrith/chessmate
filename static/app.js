document.addEventListener("DOMContentLoaded", function () {
    const moveButton = document.getElementById("getMoveBtn");
    const moveResult = document.getElementById("moveResult");

    
    async function fetchBestMove() {
        try {
            const response = await fetch('/api/move/');
            const data = await response.json();
            if (data.best_move) {
                moveResult.textContent = `Best move: ${data.best_move}`;
            } else {
                moveResult.textContent = "No move found!";
            }
        } catch (error) {
            moveResult.textContent = "Error fetching move.";
            console.error(error);
        }
    }
    
    moveButton.addEventListener("click", function () {
        fetchBestMove();
    });
});