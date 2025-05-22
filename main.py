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
music_queue = []

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
    global music_queue

    if current_voice == None:
        await interaction.response.send_message(f"i must be in a channel to play music, use /join first")
        return

    text_chan = interaction.channel
    ydl_opts_proc = {'format': 'bestaudio/best', 'extract_flat': False}
    ydl_opts = {'format': 'bestaudio', 'audio-format': 'opus', 'extract_flat': True}

    await interaction.response.send_message(f"searching for '{search}' . . .")
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)
    with YoutubeDL(ydl_opts_proc) as ydl_proc:
        proc_info = ydl_proc.extract_info(f"ytsearch:{search}", download=False)
    url_retrieved = info['entries'][0]['url']
    proc_url = proc_info['entries'][0]['url']
    print(proc_url)
    print(url_retrieved)
    print(info)
    songtitle = info['entries'][0]['title']
    await text_chan.send(f"adding [{songtitle}](<{url_retrieved}>) to the queue")

    music_queue.append(proc_url)

    print("before")
    if current_voice.is_playing() == False:
        print("after")
        play_next(interaction)
    
def play_next(interaction):
    ffmpeg_opts = {'before_options': '-reconnect 1 -rtbufsize 500M', 'options': '-vn'}
    print("song finished")
    if len(music_queue) == 0:
        return
    next_url = music_queue.pop(0)
    current_voice.play(FFmpegOpusAudio(next_url, **ffmpeg_opts,), after=lambda e: play_next(interaction))
    
    
@tree.command(
    name="stop",
    description="stops all music and clears the queue",
    guild=Object(id=GUILD)
)
async def stop(interaction):
    global music_queue
    music_queue = []
    current_voice.stop()
    await interaction.response.send_message("stopping music")

@tree.command(
    name="skip",
    description="skips the currently playing song",
    guild=Object(id=GUILD)
)
async def skip(interaction):
    current_voice.stop()

@tree.command(
    name="queue",
    description="shows the current queue",
    guild=Object(id=GUILD)
)
async def queue(interaction):
    await interaction.response.send_message(f"not done yet noob lol")


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