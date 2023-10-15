import asyncio
import websockets
from datetime import datetime, timedelta

connected = {}  # Dictionary to store connected clients
banned_ips = {}  # Dictionary to store banned IP addresses for each client


# Function for handling messages
async def websocket_handler(websocket, path):
    client_id = len(connected) + 1  # Assign a unique ID to the client
    connected[client_id] = websocket  # Store the client in the dictionary

    user_agent = websocket.request_headers.get('User-Agent', 'Console')
    client_ip = websocket.remote_address[0]  # Get the client's IP address

    try:
        async for message in websocket:
            current_time = datetime.now()
            time_in_future = current_time + timedelta(hours=2)
            time_in_future_str = time_in_future.strftime("%H:%M:%S")

            print(f"Client {client_id} ({user_agent}): {message}")

            if client_id not in banned_ips:
                banned_ips[client_id] = set()  # Create a set for the client if it doesn't exist

            if client_ip in banned_ips[client_id]:
                await websocket.send("You are banned and cannot send messages.")
                await websocket.close()
                continue

            if "Rum" in message:
                # Ban the client's IP address
                banned_ips[client_id].add(client_ip)
                await websocket.send(
                    "Your IP address has been banned for using the prohibited word 'Rum'. You will be unbanned in 10 seconds.")
                await websocket.close()
                await asyncio.sleep(10)  # Wait for 10 seconds
                banned_ips[client_id].discard(client_ip)  # Remove the IP from the set when unbanned

            # Send the message to all clients with the current time
            for client in connected.values():
                message_with_time = f"{time_in_future_str} - ID {client_id}, {message}"
                await client.send(message_with_time)

    except websockets.exceptions.ConnectionClosedError:
        # Client disconnected
        print(f"Client {client_id} ({user_agent}) disconnected.")
    finally:
        # Remove the disconnected client from the dictionary
        del connected[client_id]


# Function for starting the WebSocket server
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
