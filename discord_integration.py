import discord
from secret import token
from discord.ext import commands, voice_recv
import datetime
import ffmpeg
import asyncio
import os


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

discord.opus._load_default()

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents.all())

class AudioHandler:
    def __init__(self, pcm_path, audio_dir, threshold_size_mb=30):
        self.pcm_path = pcm_path
        self.audio_dir = audio_dir
        self.threshold_size = threshold_size_mb * 1024 * 1024

    def write_pcm_data(self, data):
        with open(self.pcm_path, "ab") as pcm_file:
            pcm_file.write(data)

    def convert_pcm_to_mp3(self):
        if self.is_conversion_needed():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            mp3_file_path = os.path.join(self.audio_dir, f"audio_{timestamp}.mp3")
            self._convert(mp3_file_path)
            self._cleanup()

    def is_conversion_needed(self):
        return os.path.exists(self.pcm_path) and os.path.getsize(self.pcm_path) > self.threshold_size

    def _convert(self, mp3_file_path):
        if not os.path.exists(mp3_file_path):
            ffmpeg.input(self.pcm_path, format='s16le', ar='48000', ac='2').output(mp3_file_path, audio_bitrate='48k').run()
            print(f"Converted to {mp3_file_path}")
        else:
            print(f"{mp3_file_path} already exists")

    def _cleanup(self):
        if os.path.exists(self.pcm_path):
            os.remove(self.pcm_path)
            print(f"Deleted {self.pcm_path}")

audio_handlers = {}

def voice_callback(user, data: voice_recv.VoiceData):
    source_name = str(user)
    audio_directory = f"./audio/{source_name}"
    create_directory(audio_directory)
    pcm_file_path = os.path.join(audio_directory, "audio.pcm")

    if source_name not in audio_handlers:
        audio_handlers[source_name] = AudioHandler(pcm_file_path, audio_directory)
    
    audio_handler = audio_handlers[source_name]

    print(f"Got packet from {user} at {datetime.datetime.now()} from source {source_name}")
    audio_handler.write_pcm_data(data.pcm)
    audio_handler.convert_pcm_to_mp3()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await connect_to_voice_channel(1250016469237108748)

async def connect_to_voice_channel(channel_id):
    channel = bot.get_channel(channel_id)
    if channel and isinstance(channel, discord.VoiceChannel):
        vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
        await bot.change_presence(status=discord.Status.online)
        print(f"Connected to voice channel: {channel.name}")
        vc.listen(voice_recv.BasicSink(voice_callback))
    else:
        print("Voice channel not found")

bot.run(token)
