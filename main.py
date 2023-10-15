import asyncio
import websockets
import re  # Přidejte modul pro regulární výrazy

banned_clients = set()  # Množina pro ukládání banovaných klientů
connected = {}  # Slovník pro ukládání připojených klientů


async def websocket_handler(websocket, path):
    client_id = len(connected) + 1  # Přiřazení jedinečného ID klientovi
    connected[client_id] = websocket  # Uložení klienta do slovníku

    user_agent = websocket.request_headers.get('User-Agent', 'Console')
    client_ip = websocket.remote_address[0]  # Získání IP adresy klienta

    try:
        async for message in websocket:
            print(f"Client {client_id} ({user_agent}): {message}")

            if client_id in banned_clients:  # Kontrola, zda klient je v banovaných
                await websocket.send("Jste banován, nelze posílat zprávy.")
                # Pokud je klient banovaný, odpojíme ho
                await websocket.close()
                continue

            if re.search(r'\bRum\b', message, re.I):  # Hledání slova "Rum" (neovlivňuje velikost písmen)
                # Banování klienta
                banned_clients.add(client_id)
                await websocket.send("Byli jste zabanováni za použití zakázaného slova 'Rum'. Budete odbanováni za 10s")
                await websocket.close()
                await asyncio.sleep(10)  # Počkej 10 sekund
                banned_clients.discard(client_id)

            # Odeslání zprávy všem klientům
            for client in connected.values():
                await client.send(f"Client {client_id}: {message}")

    except websockets.exceptions.ConnectionClosedError:
        # Odpojení klienta
        print(f"Client {client_id} ({user_agent}) disconnected.")
    finally:
        # Smažeme odpojeného klienta ze seznamu připojených
        del connected[client_id]


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


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_websocket_server())
