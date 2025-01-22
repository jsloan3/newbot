import os
from discord import *
from dotenv import load_dotenv
from yt_dlp import YoutubeDL

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('GUILD_ID')
print(TOKEN)

intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(
    name="ping",
    description="ping pong",
    guild=Object(id=GUILD)
)
@app_commands.describe(arg1="argument test")
async def ping(interaction, arg1: str):
    await interaction.response.send_message(f"pong {arg1}")

@tree.command(
    name="play",
    description="play a song",
    guild=Object(id=GUILD)
)
@app_commands.describe(search="youtube video url")
async def play(interaction, search: str):
    await interaction.response.send_message(f"downloading {search} to directory")
    URL = [search]
    with YoutubeDL() as ydl:
        ydl.download(URL)
    

@client.event
async def on_ready():
    await tree.sync(guild=Object(id=GUILD))
    print("ready")

client.run(TOKEN)