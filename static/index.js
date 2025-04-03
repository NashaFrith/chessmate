
// Add event listener for the submit button
document.addEventListener("DOMContentLoaded", () => {
    const moveInput = document.getElementById('moveInput'); 
    const submitButton = document.getElementById('submitButton'); 

    submitButton.addEventListener('click', () => {
        const move = moveInput.value; 

        // send post request to server endpoint
        if (move) {
            fetch("/move", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ move: move})  
            })

            //server responds by sending back a json object or an error
            .then(response => response.json())
            .then(data => {
                console.log("Response:", data);
                if (data.status === "Move made") {
                    
                    if (data.ai_move) {
                        alert("AI Move: " + data.ai_move);  
                    }
                } else {
                    alert("Error: " + data.error);
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
        }
    });
});