let websocket = null;
let reconnecting = false;
const messageInput = document.getElementById("message");
const connectionStatus = document.getElementById("connection-status");
let userName;

// Funkce pro zadání jména uživatele
async function getUserName() {
    while (!userName) {
        userName = prompt("Zadejte sve jmeno:");
    }
}

// Zavolání asynchronní funkce pro zadání jména uživatele
getUserName()
    .then(() => createWebSocket())
    .catch((error) => console.error(error));

function createWebSocket() {
    if (reconnecting) {
        const messagesDiv = document.getElementById("messages");
        messagesDiv.innerHTML = "<p>Odpojen. Obnovuji spojení...</p>" + messagesDiv.innerHTML;
    }

    websocket = new WebSocket("wss://wa-websockets.onrender.com");
    reconnecting = true;

    websocket.onmessage = function (event) {
        const messagesDiv = document.getElementById("messages");
        const message = event.data;
        messagesDiv.innerHTML = `<p>${message}</p>` + messagesDiv.innerHTML;
    };

    websocket.onclose = function (event) {
        setTimeout(function () {
            createWebSocket();
        }, 1000);
        connectionStatus.innerText = "Nepripojen";
        connectionStatus.style.color = "red";
    };

    websocket.onopen = function () {
        if (reconnecting) {
            // Odešleme uživatelovo jméno na server
            websocket.send(`User: ${userName} - Pripojen/a!`);
        }
        connectionStatus.innerText = "Pripojen";
        connectionStatus.style.color = "green";
    }
}

document.getElementById("send").addEventListener("click", function () {
    sendMessage();
});

messageInput.addEventListener("keyup", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

function sendMessage() {
    const message = messageInput.value;
    if (message.trim() !== "") {
        // Odešleme zprávu s uživatelovým jménem na server
        websocket.send(`User: ${userName}, Zprava: ${message}`);
        messageInput.value = "";
    }
}
