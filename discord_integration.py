import discord
from secret import token
from discord.ext import commands, voice_recv

discord.opus._load_default()

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents.all())

def voice_callback(user, data: voice_recv.VoiceData):
    print(f"got packet from {user}")

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")
    channel = bot.get_channel(1250016469237108748)  # Reemplaza con tu ID de canal de voz
    if channel and isinstance(channel, discord.VoiceChannel):
        vc = await channel.connect(cls=voice_recv.VoiceRecvClient)
        vc.listen(voice_recv.BasicSink(voice_callback))
        print(f"connected to voice channel: {channel.name}")
        await bot.change_presence(status=discord.Status.online)
    else:
        print("not found")

bot.run(token)