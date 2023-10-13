import asyncio
import websockets
from datetime import datetime

connected = {}  # Slovník pro ukládání připojených klientů
banned_users = set()  # Množina pro ukládání banovaných uživatelů


# Funkce pro zpracování zpráv
async def websocket_handler(websocket, path):
    client_id = len(connected) + 1  # Přiřazení jedinečného ID klientovi
    connected[client_id] = websocket  # Uložení klienta do slovníku

    user_agent = websocket.request_headers.get('User-Agent', 'Console')
    try:
        async for message in websocket:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"Client {client_id} ({user_agent}): {message}")

            if client_id in banned_users:
                await websocket.send("Jste banován, nelze posílat zprávy.")
                # Pokud je klient banovaný, odpojíme ho
                await websocket.close()
                continue

            if "Rum" in message:
                # Banování klienta
                banned_users.add(client_id)  # Přidání klienta do seznamu banovaných
                await websocket.send("Byl jste banován za použití zakázaného slova 'Rum'. Budete odbanován za 10s")
                await websocket.close()
                await asyncio.sleep(10)  # Počkej 10 sekund
                banned_users.discard(client_id)

            # Odeslání zprávy všem klientům s časem
            for client in connected.values():
                message_with_time = f"{current_time} - Konzole {client_id}: {message}"
                await client.send(message_with_time)

    except websockets.exceptions.ConnectionClosedError:
        # Odpojení klienta
        print(f"Client {client_id} ({user_agent}) disconnected.")
    finally:
        # Smažeme odpojeného klienta z evidovaných
        del connected[client_id]
        banned_users.discard(client_id)


    # Funkce pro spuštění WebSocket serveru
async def start_websocket_server():
    ip_address = "0.0.0.0"
    port = 6789

    server = await websockets.serve(
        websocket_handler,
        ip_address,
        port
    )

    print(f"WebSocket server is running at ws://{ip_address}:{port}")

    await server.wait_closed()
    
async def connect_to_server():
    uri = "ws://0.0.0.0:6789"  # Změňte na správnou adresu a port vašeho serveru
    async with websockets.connect(uri) as websocket:
        while True:
            message = input("Zadejte zprávu: ")
            await websocket.send(message)
            response = await websocket.recv()
            print("Přijato od serveru:", response)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_websocket_server())
