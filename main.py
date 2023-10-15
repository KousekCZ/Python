import asyncio
import websockets
from datetime import datetime, timedelta

connected = {}  # Slovník pro ukládání připojených klientů
banned_ips = set()  # Množina pro ukládání banovaných IP adres


# Funkce pro zpracování zpráv
async def websocket_handler(websocket, path):
    client_id = len(connected) + 1  # Přiřazení jedinečného ID klientovi
    connected[client_id] = websocket  # Uložení klienta do slovníku

    user_agent = websocket.request_headers.get('User-Agent', 'Console')
    client_ip = websocket.remote_address[0]  # Získání IP adresy klienta

    try:
        async for message in websocket:
            current_time = datetime.now()
            time_in_future = current_time + timedelta(hours=2)
            time_in_future_str = time_in_future.strftime("%H:%M:%S")

            print(f"Client {client_id} ({user_agent}): {message}")

            if client_ip in banned_ips:
                await websocket.send("Jste banován, nelze posílat zprávy.")
                # Pokud je IP adresa banovaná, odpojíme ho
                await websocket.close()
                continue

            if "Rum" in message:
                # Banování IP adresy klienta
                banned_ips.add(client_ip)  # Přidání IP adresy do seznamu banovaných
                await websocket.send(
                    "Byla zabanována Vaše IP adresa za použití zakázaného slova 'Rum'. Budete odbanováni za 10s")
                await websocket.close()
                await asyncio.sleep(10)  # Počkej 10 sekund
                banned_ips.discard(client_ip)

            # Odeslání zprávy všem klientům s časem
            for client in connected.values():
                message_with_time = f"{time_in_future_str} - ID {client_id}, {message}"
                await client.send(message_with_time)

    except websockets.exceptions.ConnectionClosedError:
        # Odpojení klienta
        print(f"Client {client_id} ({user_agent}) disconnected.")
    finally:
        # Smažeme odpojeného klienta z evidovaných
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
