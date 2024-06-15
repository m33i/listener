import discord
from secret import token
from discord.ext import commands, voice_recv
from datetime import date
import ffmpeg
import asyncio

pcm_file_path = "audio.pcm"
mp3_file_path = "audio.mp3"

discord.opus._load_default()

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents.all())

def voice_callback(user, data: voice_recv.VoiceData):
    #print(f"got packet from {user}")
    #rint(date.isoformat(data.packet.timestamp))
    payload = data.pcm
    with open(pcm_file_path, "ab") as pcm_file:
        pcm_file.write(payload)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")
    channel = bot.get_channel(1250016469237108748)  # Reemplaza con tu ID de canal de voz
    if channel and isinstance(channel, discord.VoiceChannel):
        vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
        vc.listen(voice_recv.BasicSink(voice_callback))
        print(f"connected to voice channel: {channel.name}")
        await bot.change_presence(status=discord.Status.online)
        bot.loop.create_task(save_audio_periodically())
    else:
        print("not found")

async def save_audio_periodically():
    while True:
        await asyncio.sleep(10)
        convert_pcm_to_mp3()

def convert_pcm_to_mp3():
    try:
        ffmpeg.input(pcm_file_path, format='s16le', ar='48000', ac='2').output(mp3_file_path).run()
        print(f"Audio guardado y convertido a {mp3_file_path}")
    except Exception as e:
        print(f"Error al convertir el audio: {e}")

bot.run(token)