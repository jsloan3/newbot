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
intents.voice_states = True
client = Client(intents=intents)
tree = app_commands.CommandTree(client)

current_voice = None
queue = []

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

    ydl_opts = {'format': 'bestaudio', 'audio-format': 'opus'}

    await interaction.response.send_message(f"downloading {search} to directory")
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)
    url_retrieved = info['entries'][0]['url']
    print(url_retrieved)
    if current_voice.is_playing == False:
        play_next(interaction)
    
def play_next(interaction):
    ffmpeg_opts = {'options': '-vn'}
    print("song finished")
    if len(queue) == 0:
        return
    next_url = queue.pop(0)
    current_voice.play(FFmpegPCMAudio(next_url, **ffmpeg_opts,), after=lambda e: play_next())
    
    
@tree.command(
    name="stop",
    description="stops all music and clears the queue",
    guild=Object(id=GUILD)
)
async def stop(interaction):
    current_voice.stop()
    await interaction.response.send_message("stopping music")

@tree.command(
    name="join",
    description="join your voice channel",
    guild=Object(id=GUILD)
)
async def join(interaction):
    global current_voice

    voicech_name = str(interaction.user.voice.channel)
    if current_voice != None:
        await interaction.response.send_message(f"i'm already in the channel {voicech_name}")
        return
    user_voicech_id = interaction.user.voice.channel.id
    if user_voicech_id == None:
        await interaction.response.send_message("you must be in a channel to use /play")
    user_voicech = client.get_channel(user_voicech_id)
    voice_client = await user_voicech.connect()
    current_voice = voice_client
    await interaction.response.send_message(f"joined channel {voicech_name}")

@tree.command(
    name="leave",
    description="make the bot disconnect",
    guild=Object(id=GUILD)
)
async def leave(interaction):
    global current_voice

    if current_voice == None:
        await interaction.response.send_message("i'm not in a channel")
        return
    await current_voice.disconnect()
    await interaction.response.send_message("goodbye")
    current_voice = None
    return
    


@client.event
async def on_ready():
    await tree.sync(guild=Object(id=GUILD))
    print("ready")

client.run(TOKEN)

# yt-dlp 'https://www.youtube.com/watch?v=56hqrlQxMMI' -o - | mpv -