import discord
from secret import token
from discord.ext import commands, voice_recv
import datetime
import ffmpeg
import asyncio
import os

pcm_file_path = "audio.pcm"

discord.opus._load_default()

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents.all())

def voice_callback(user, data: voice_recv.VoiceData):
    print(f"got packet from {user} at {datetime.datetime.now()}")
    with open(pcm_file_path, "ab") as pcm_file:
        pcm_file.write(data.pcm)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")
    channel = bot.get_channel(1250016469237108748)  # channel id
    if channel and isinstance(channel, discord.VoiceChannel):

        vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
        await bot.change_presence(status=discord.Status.online)

        print(f"connected to voice channel: {channel.name}")
        vc.listen(voice_recv.BasicSink(voice_callback))
        bot.loop.create_task(save_audio())
    else:
        print("not found")

# pcm to mp3
async def save_audio():
    while True:
        await asyncio.sleep(10)
        convert_pcm_to_mp3()

def convert_pcm_to_mp3():
    try:
        if os.path.exists(pcm_file_path):
            pcm_file_size = os.path.getsize(pcm_file_path)
            #if pcm_file_size > 5 * 1024 * 1024:  # 5 MB
            if pcm_file_size > 30 * 1024 * 1024:  # 30 MB
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                mp3_file_path = f"audio_{timestamp}.mp3"

                if not os.path.exists(mp3_file_path):
                    # pcm to mp3
                    ffmpeg.input(pcm_file_path, format='s16le', ar='48000', ac='2').output(mp3_file_path, audio_bitrate='48k').run() # 64k, 32k
                    print(f"converted to {mp3_file_path}")

                    # deletes pcm
                    os.remove(pcm_file_path)
                    print(f"deleted {pcm_file_path}")
                else:
                    print(f"{mp3_file_path} already exists")
            else:
                print(f"{pcm_file_path} size is less than 30 MB")
        else:
            print(f"{pcm_file_path} does not exist")
    except Exception as e:
        print(f"conversion error: {e}")

bot.run(token)