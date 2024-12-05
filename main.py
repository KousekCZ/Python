import asyncio
import discord
from discord.ext import commands
import websockets
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

connected = {}
ip_to_client = {}
user_info_list = []


async def websocket_handler(websocket, path):
    client_id = len(connected) + 1
    connected[client_id] = websocket
    user_agent = websocket.request_headers.get('User-Agent', 'Console')

    client_ip = websocket.request_headers.get('X-Forwarded-For', websocket.remote_address[0]).split(',')[0]

    user_info = {"client_id": client_id, "ip": client_ip, "user_agent": user_agent}
    user_info_list.append(user_info)

    print(
        f"-------------------------------------------------------------\nPYTHON: Client {client_id} with IP {client_ip} ({user_agent}) connected.")
    print(f"Current user list: {user_info_list}")

    try:
        async for message in websocket:
            current_time = datetime.now()
            time_in_future = current_time + timedelta(hours=2)
            time_in_future_str = time_in_future.strftime("%H:%M:%S")

            print(f"Client {client_id} ({user_agent}): {message}")

            for client in connected.values():
                message_with_time = f"{time_in_future_str} - ID {client_id}, {message}"
                await client.send(message_with_time)

    except websockets.exceptions.ConnectionClosedError:
        print(f"Client {client_id} with IP {client_ip} disconnected.")
    finally:
        del connected[client_id]


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


intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='', intents=intents)


@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} se připojil na server.')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        if "ip" in message.content.lower():
            if user_info_list:
                user_info_str = "\n".join(
                    [f"ID: {info['client_id']}, IP: {info['ip']}, User-Agent: {info['user_agent']}"
                     for info in user_info_list]
                )
            else:
                user_info_str = "Žádné připojené klienty nelze zobrazit."

            await message.channel.send(f"Informace o klientech:\n```{user_info_str}```")
        else:
            await message.channel.send(f"{message.author.mention}, CO MĚ PINGUJEŠ MORE?!")
    await bot.process_commands(message)


async def start_discord_bot():
    key = b'fHj_-hlO6CO-yrQMcR7ZsE3vGSJKsbGLEnbPvzUbMBE='
    encrypted_string = b'gAAAAABnUXao2YzHJ5twDKgpAkDMARAzrrhw8eRXYIaIH310zvt4EJfTinFAt9wokaegLILwnge2GjIoDwb2tcwAdlPWSlV46iMCNld_YrCUvIdaUi59hzFHD6WTi9c7l9ELKfiAm1oL47-NZjZ8U10uOqD6muvdm5Q31h7_tbydFcGXt0U9m7U='
    cipher = Fernet(key)
    xd = cipher.decrypt(encrypted_string).decode()

    try:
        await bot.start(xd)
    except Exception as e:
        print(f'Chyba při spuštění bota: {e}')


async def main():
    await asyncio.gather(
        start_websocket_server(),
        start_discord_bot()
    )


if __name__ == "__main__":
    asyncio.run(main())
