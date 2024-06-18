import discord
from secret import token
from discord.ext import commands, voice_recv
import datetime
import ffmpeg
import os
import sys

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

discord.opus._load_default()

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents.all())

class AudioHandler:
    def __init__(self, pcm_path, audio_dir, threshold_size_mb=7): # 30mb , 20mb ... pcm size
        self.pcm_path = pcm_path
        self.audio_dir = audio_dir
        self.threshold_size = threshold_size_mb * 1024 * 1024

    def write_pcm_data(self, data):
        with open(self.pcm_path, "ab") as pcm_file:
            pcm_file.write(data)

    # pcm to mp3
    def convert_pcm_to_mp3(self, user_prefix):
        if self.is_conversion_needed():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            mp3_file_path = os.path.join(self.audio_dir, f"{user_prefix}_audio_{timestamp}.mp3")
            self._convert(mp3_file_path)
            self._cleanup()

    def is_conversion_needed(self):
        return os.path.exists(self.pcm_path) and os.path.getsize(self.pcm_path) > self.threshold_size

    def _convert(self, mp3_file_path):
        if not os.path.exists(mp3_file_path):
            ffmpeg.input(self.pcm_path, format='s16le', ar='48000', ac='2').output(mp3_file_path, audio_bitrate='48k').run() # 32k, 64k .. bitrate
            print(f"converted to {mp3_file_path}")
        else:
            print(f"{mp3_file_path} already exists")

    def _cleanup(self):
        if os.path.exists(self.pcm_path):
            os.remove(self.pcm_path)
            print(f"deleted {self.pcm_path}")

audio_handlers = {}

def voice_callback(user, data: voice_recv.VoiceData):
    
    recording_type = sys.argv[1] # by default it will record each voice separately
    user_prefix = ""
        
    if recording_type == "groupmode":
        print(f"using mode: {recording_type}")
        audio_directory = f"./audio/groupcall"
        create_directory(audio_directory)
        pcm_file_path = os.path.join(audio_directory, "audio.pcm")
        audio_handler = AudioHandler(pcm_file_path, audio_directory)
        user_prefix = "groupcall"
    else:
        print(f"using mode: singlemode")
        audio_directory = f"./audio/{user}"
        create_directory(audio_directory)
        pcm_file_path = os.path.join(audio_directory, "audio.pcm")

        if user not in audio_handlers:
            audio_handlers[user] = AudioHandler(pcm_file_path, audio_directory)
        audio_handler = audio_handlers[user]
        user_prefix = user

    print(f"got packet and source from {user} at {datetime.datetime.now()}")
    audio_handler.write_pcm_data(data.pcm)
    audio_handler.convert_pcm_to_mp3(user_prefix)   

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")
    await connect_to_voice_channel(1250016469237108748) # channel id

async def connect_to_voice_channel(channel_id):
    channel = bot.get_channel(channel_id)
    if channel and isinstance(channel, discord.VoiceChannel):
        vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
        await bot.change_presence(status=discord.Status.online)
        print(f"connected to voice channel: {channel.name}")
        vc.listen(voice_recv.BasicSink(voice_callback))
    else:
        print("voice channel not found")

bot.run(token)
