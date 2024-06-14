import discord
from secret import token
from discord.ext import commands, voice_recv

discord.opus._load_default()

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=discord.Intents.all())

class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx):
        print(f"test")
        def callback(user, data: voice_recv.VoiceData):
            print(f"Got packet from {user}")

            # voice power level, how loud the user is speaking
            ext_data = data.extension_data.get(voice_recv.ExtensionID.audio_power)
            value = int.from_bytes(ext_data, 'big')
            power = 127 - (value & 127)
            print('#' * int(power * (79 / 128)))
            # instead of 79 you can use shutil.get_terminal_size().columns-1

        vc = await ctx.author.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
        vc.listen(voice_recv.BasicSink(callback))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    channel = bot.get_channel(1250016469237108748) # wkh
    await channel.connect()
    await bot.change_presence(status=discord.Status.online)

async def setup_hook():
    await bot.add_cog(Main(bot))

bot.run(token)