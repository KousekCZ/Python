let websocket = null;
let reconnecting = false;
const messageInput = document.getElementById("message");
const connectionStatus = document.getElementById("connection-status");

function createWebSocket() {
    if (reconnecting) {
        const messagesDiv = document.getElementById("messages");
        messagesDiv.innerHTML = "<p>Odpojen. Obnovuji spojeni...</p>" + messagesDiv.innerHTML;
    }

    websocket = new WebSocket("wss://wa-websockets.onrender.com");
    reconnecting = true;

    websocket.onmessage = function (event) {
        const messagesDiv = document.getElementById("messages");
        const message = event.data;
        messagesDiv.innerHTML = `<p>${message}</p>` + messagesDiv.innerHTML;

        if (message === "Byl jste zabanován za použití zakázaného slova 'Rum'.") {
            websocket.close();
        }
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
            websocket.send("Spojeni navazano");
        }
        connectionStatus.innerText = "Pripojen";
        connectionStatus.style.color = "green";
    }
}

createWebSocket();

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
        websocket.send(`Web: ${message}`);
        messageInput.value = "";
    }
}
