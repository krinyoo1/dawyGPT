import discord
import asyncio
import yt_dlp
import helpers
import os
import random
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

YTDL_OPTS = {"format": "bestaudio/best", "noplaylist": True, "quiet": True, "default_search": "ytsearch"}
FFMPEG_OPTS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn",}

bot = commands.Bot(
    command_prefix='+',
    intents=intents,
    help_command=None,
    owner_id=918389840813359124
)

loop_state = False

@bot.event
async def on_ready():
    print(f"[{bot.user.name}] Bot has successfully started!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.CheckFailure, commands.NotOwner, commands.CommandNotFound)):
        return
    if isinstance(error, (commands.CommandOnCooldown)):
        await ctx.message.delete()
        await ctx.author.send(embed=discord.Embed(title="Too fast!", description="Slow down buckaroo! Getting rate limited is NOT my thing.", color=discord.Color.blue()))
        return
    await ctx.reply(embed=discord.Embed(title="Uh oh..", description=f"An error has occured. [{error}]", color=discord.Color.blue()))

''' CURRENTLY NOT USING BOT CHECKS
@bot.check
async def owner_only(ctx: commands.Context) -> bool:
    return ctx.author.id == bot.owner_id
'''

global_cd = commands.CooldownMapping.from_cooldown(
    1, 2, commands.BucketType.user
)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    for guild in bot.guilds:
        vc = guild.voice_client
        if not vc or not vc.channel:
            continue

        humans = [m for m in vc.channel.members if not m.bot]
        if len(humans) == 0:
            await vc.disconnect()

@bot.check
async def global_cooldown(ctx: commands.Context) -> bool:
    bucket = global_cd.get_bucket(ctx.message)
    retry_after = bucket.update_rate_limit()
    if retry_after:
        raise commands.CommandOnCooldown(bucket, retry_after, commands.BucketType.guild)
    return True

@bot.command() # +help
async def help(ctx: commands.Context):
    general_commmands = '''
    `+help` - opens up this command help menu.
    `+say` - the bot says anything after you type the command
    '''

    money_commands = '''
    `+beg` - you can beg for 60 - 900 bucks every 3 minutes
    `+slots` [amount] - you can play slots, if you lose, you lose the amount you put in, but if you win it gets doubled and put into your balance
    `+balance` - shows you your balance
    `+editbalance [target user] [type (can be: "add" | "remove" | "edit" | "read"] [amount]` - ADMIN-ONLY command, you can add, remove or edit your balance.
    '''

    voice_commands = '''
    `+play` [song name] - you can play any songs or videos from youtube
    `+stop` - you can stop any currently playing songs in the vc
    `+loop` - if a song is playing, you can turn looping on and off with this command
    '''

    embed = discord.Embed(title="**dawyGPT Command List**", description="Hello, I am dawyGPT. I use the '+' prefix. Commands are added frequently, so make sure to check out this command for new commands.", color=discord.Color.blue())
    embed.add_field(name="General Commands 🤖", value=general_commmands)
    embed.add_field(name="Money Commands 💰", value=money_commands, inline=False)
    embed.add_field(name="Voice Commands 🎵", value=voice_commands, inline=False)
    embed.set_footer(text="dawyGPT - made by dawy")
    await ctx.reply(embed=embed)

@bot.command() # +say
async def say(ctx: commands.Context, *, msg):
    await ctx.message.delete()
    await ctx.send(msg)

@bot.command() # +dice
async def dice(ctx: commands.Context):
    count = 3
    msg = await ctx.reply(embed=discord.Embed(description=f"Rolling the dice in **{count}** ", color=discord.Color.blue()))
    for i in range(0, 3):
        await asyncio.sleep(1)
        count -= 1
        await msg.edit(embed=discord.Embed(description=f"Rolling the dice in **{count}**", color=discord.Color.blue()))

    await asyncio.sleep(1)
    await msg.edit(embed=discord.Embed(description=f"You have rolled a **{random.randint(1, 6)}** 🎲", color=discord.Color.blue()))

@bot.command() # +beg
async def beg(ctx: commands.Context):
    is_cooldown = helpers.beg_cooldown(str(ctx.author.id), "read")

    if is_cooldown:
        await ctx.reply(embed=discord.Embed(title="Uh oh..", description=f"You are on cooldown! You may only beg every **3 minutes**! ⏱️", color=discord.Color.blue()))
        return

    begged_money = random.randint(60, 900)

    helpers.edit_balance(user_id=str(ctx.author.id), type="add", amount=begged_money)
    helpers.beg_cooldown(user_id=str(ctx.author.id), type="write")

    await ctx.reply(embed=discord.Embed(title="Begged on the streets!", description=f"You successfully begged on the streets graciously! You managed to gather **{begged_money}$**", color=discord.Color.blue()))

@bot.command() # +slots
async def slots(ctx: commands.Context, amount: str):
    WINNING_MULTIPLIER = 2
    REQUIRED_AMOUNT = 100

    amount = int(amount)

    balance = helpers.edit_balance(user_id=str(ctx.author.id), type="read", amount=0)
    if balance < amount:
        await ctx.reply(embed=discord.Embed(title="Uh oh..",description=f"You do not have enough money! Your amount is **{amount}$**, but your balance is **{balance}**$!", color=discord.Color.blue()))
        return

    if REQUIRED_AMOUNT > amount:
        await ctx.reply(embed=discord.Embed(title="Uh oh..", description=f"The amount you put in is below the required amount! The required amount is **{REQUIRED_AMOUNT}$**, your amount is **{amount}$**!", color=discord.Color.blue()))
        return

    randColor1 = "⚪"
    randColor2 = "⚪"
    randColor3 = "⚪"

    msg = await ctx.reply(embed=discord.Embed(title="Pulling the slot machine's lever...", description=f"{randColor1, randColor2, randColor3}", color=discord.Color.blue()))
    await asyncio.sleep(1)

    color_dict = {
        1: "🔴",
        2: "🟢",
        3: "🔵"
    }

    for i in range(1, 5):
        await asyncio.sleep(1)
        randColor1 = color_dict[random.randint(1, 3)]
        randColor2 = color_dict[random.randint(1, 3)]
        randColor3 = color_dict[random.randint(1, 3)]
        await msg.edit(embed=discord.Embed(title="Rolling the slots!", description=f"{randColor1, randColor2, randColor3}", color=discord.Color.blue()))

    await asyncio.sleep(1)
    if randColor1 == randColor2 and randColor1 == randColor3:
        helpers.edit_balance(user_id=str(ctx.author.id), type="add", amount=amount * WINNING_MULTIPLIER)
        await msg.edit(embed=discord.Embed(title="You win!",description=f"{randColor1, randColor2, randColor3}",color=discord.Color.blue()))
    else:
        helpers.edit_balance(user_id=str(ctx.author.id), type="remove", amount=amount)
        await msg.edit(embed=discord.Embed(title="You lost.", description=f"{randColor1, randColor2, randColor3}", color=discord.Color.blue()))

@bot.command() # +balance
async def balance(ctx: commands.Context):
    balance = helpers.edit_balance(user_id=str(ctx.author.id), type="read", amount=0)
    await ctx.reply(embed=discord.Embed(description=f"Your balance is **{balance}$** 💵", color=discord.Color.blue()))

@bot.command() # +editbalance
@commands.is_owner() # // OWNER ONLY
async def editbalance(ctx: commands.Context, target: discord.Member, type: str, amount: str):
    userID = target.id
    balance = helpers.edit_balance(user_id=str(userID), type=type, amount=int(amount))
    await ctx.reply(embed=discord.Embed(description=f"{target}'s new balance is **{balance}$** 💵", color=discord.Color.blue()))

@bot.command()
async def play(ctx: commands.Context, *, query):
    if not ctx.author.voice:
        return await ctx.reply(embed=discord.Embed(title="Uh oh..",description="You need to join a voice channel first!", color=discord.Color.blue()))

    vc = ctx.voice_client or await ctx.author.voice.channel.connect()

    with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
        info = ydl.extract_info(f"ytsearch: {query}", download=False)
        title = info["entries"][0]["title"]

    async def play_fresh():
        if not vc or not vc.is_connected():
            return
        with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
            loop_info = ydl.extract_info(f"ytsearch: {query}", download=False)
            loop_url = loop_info["entries"][0]["url"]
        fresh_source = discord.FFmpegPCMAudio(loop_url, **FFMPEG_OPTS)
        vc.play(fresh_source, after=after_play)

    if vc.is_playing():
        vc.stop()

    def after_play(error):
        if error:
            print(f"An error has occured. [{error}]")
            return

        if not loop_state:
            fut = vc.disconnect()
            asyncio.run_coroutine_threadsafe(fut, bot.loop)
            return

        fut = asyncio.run_coroutine_threadsafe(play_fresh(), bot.loop)
        try:
            fut.result()
        except Exception as e:
            print(f"Loop replay error: [{e}]")

    await play_fresh()
    await ctx.reply(embed=discord.Embed(title="Now Playing.. 🎵",description=f"Now playing **{title}** in {ctx.author.voice.channel.mention}", color=discord.Color.blue()))

@bot.command()
async def stop(ctx: commands.Context):
    vc = ctx.voice_client

    if not vc:
        await ctx.reply(embed=discord.Embed(title="Uh oh..",description="I am not playing any songs!", color=discord.Color.blue()))
        return

    channel = vc.channel

    if vc.is_playing() or vc.is_paused():
        vc.stop()

    await vc.disconnect()
    await ctx.reply(embed=discord.Embed(title="Stopped", description=f"Music stopped in {channel.mention}", color=discord.Color.blue()))

@bot.command()
async def loop(ctx: commands.Context):
    global loop_state
    vc = ctx.voice_client

    if not vc:
        await ctx.reply(embed=discord.Embed(title="Uh oh..",description="No songs playing to loop!", color=discord.Color.blue()))
        return

    if not loop_state:
        loop_state = True
        await ctx.reply(embed=discord.Embed(title="Looping.. 🌀", description="Looping has been turned on!", color=discord.Color.blue()))
    else:
        loop_state = False
        await ctx.reply(embed=discord.Embed(title="Looping.. 🌀", description="Looping has been turned off!",color=discord.Color.blue()))

bot.run(token)
