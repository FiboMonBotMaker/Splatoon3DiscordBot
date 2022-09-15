from discord.ext import commands
import os
import pathlib
import discord


intent = discord.Intents.all()

bot = commands.Bot(
    debug_guilds=os.getenv("GUILDS").split(","),
    intent=intent
)
TOKEN = os.getenv('TOKEN')

path = "./cogs"


@bot.event
async def on_ready():
    print(f"Bot名:{bot.user} On ready!!")


@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error: Exception):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(content="このコマンドが呼ばれすぎています。少し時間が経ってからお試しください。", ephemeral=True)
    else:
        raise error


# @bot.event
# async def on_message(message: discord.Message):
#     if message.channel.id in threads[message.guild.id]:


dir = "cogs"
files = pathlib.Path(dir).glob("*.py")
for file in files:
    print(f"{dir}.{file.name[:-3]}")
    bot.load_extension(name=f"{dir}.{file.name[:-3]}", store=False)


bot.run(TOKEN)
