<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Client</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        #message-panel {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
            margin-bottom: 10px;
        }

        #messages {
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            padding: 10px;
            margin-bottom: 10px;
            max-height: 300px;
            overflow-y: scroll;
            width: 100%;
        }

        p {
            margin: 0;
            padding: 5px;
        }

        #message {
            width: 80%;
            padding: 5px;
        }

        #send {
            background-color: #0074d9;
            color: #fff;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
        }

        #send:hover {
            background-color: #0056b3;
        }

        #connection-status {
            color: red;
            animation: blinker 1s linear infinite;
        }

        #connected {
            color: green;
        }

        @keyframes blinker {
            50% {
                opacity: 0;
            }
        }
    </style>
</head>
<body>
<div id="message-panel">
    <div id="status-panel">
        <span id="connection-status">Nepřipojen</span>
    </div>
    <input type="text" id="message" placeholder="Message">
    <button id="send">Odeslat</button>
</div>
<div id="messages"></div>

<script>
    let websocket = null;  // Inicializace proměnné pro WebSocket spojení
    let reconnecting = false;  // Indikátor pro obnovování spojení
    const messageInput = document.getElementById("message");
    const connectionStatus = document.getElementById("connection-status");

    // Funkce pro vytvoření WebSocket spojení
    function createWebSocket() {
        if (reconnecting) {
            // Pokud probíhá obnovování spojení, zobraz "Obnovuji připojení"
            const messagesDiv = document.getElementById("messages");
            messagesDiv.innerHTML = "<p>Odpojen. Obnovuji spojeni...</p>" + messagesDiv.innerHTML;
        }

        websocket = new WebSocket("ws://localhost:8080");
        reconnecting = true;

        // Funkce pro zpracování přijatých zpráv
        websocket.onmessage = function (event) {
            const messagesDiv = document.getElementById("messages");
            const message = event.data;
            messagesDiv.innerHTML = `<p>${message}</p>` + messagesDiv.innerHTML;

            if (message === "Byl jste banován za použití zakázaného slova 'Rum'.") {
                websocket.close();  // Uzavři spojení, klient je banován
            }
        };

        // Funkce pro zpracování události odpojení
        websocket.onclose = function (event) {
            setTimeout(function () {
                createWebSocket();
            }, 1000);
            connectionStatus.innerText = "Nepripojen";
            connectionStatus.style.color = "red";
        };

        // Odešli zprávu "Spojení obnoveno" na server po úspěšném znovupřipojení
        websocket.onopen = function () {
            if (reconnecting) {
                websocket.send("Spojeni navazano");
            }
            connectionStatus.innerText = "Pripojen";
            connectionStatus.style.color = "green";
        };
    }

    // Vytvoření WebSocket spojení při načtení stránky
    createWebSocket();

    // Odeslání zprávy z formuláře při kliknutí na tlačítko "Odeslat"
    document.getElementById("send").addEventListener("click", function () {
        sendMessage();
    });

    // Odeslání zprávy z formuláře po stisknutí klávesy Enter
    messageInput.addEventListener("keyup", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    // Funkce pro odeslání zprávy na server a vyprázdnění pole pro zprávu
    function sendMessage() {
        const message = messageInput.value;
        if (message.trim() !== "") {
            websocket.send(`Web: ${message}`);
            messageInput.value = "";
        }
    }
</script>
</body>
</html>