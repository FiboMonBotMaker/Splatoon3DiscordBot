from datetime import time
import traceback
from discord.ext import commands, tasks
from discord import SlashCommandGroup, ApplicationContext, Permissions, TextChannel, Option, OptionChoice
from discord.errors import NotFound
from model.splamodel import StageStatus
import joblib

GUILDS_FILE_NAME = "./data/guild.dat"


class SplaCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.guilds: dict[int, TextChannel] = {}
        self.embeds: list[StageStatus] = {}
        self.flg = True
        self.update.start()

    admin_command = SlashCommandGroup(
        name="setup",
        description="Command to set splabot",
        default_member_permissions=Permissions(
            administrator=True,
            moderate_members=True
        )
    )

    stage_check = SlashCommandGroup(
        name="stage",
        description="stage check"
    )

    @commands.cooldown(rate=3, per=10, type=commands.BucketType.guild)
    @admin_command.command(name="channel", description="２時間毎にこのチャンネルに対してステージ情報を受け取る設定を行います(1サーバー1チャンネルです）")
    async def set_channel(
        self,
        ctx: ApplicationContext,
    ):
        await ctx.interaction.response.send_message(
            content="一定時間毎にこのチャネルに通知を行います。（この設定は1サーバーにつき1チャネルのみ有効です。）",
            embed=self.embeds[0]
        )
        self.guilds[ctx.guild_id] = ctx.channel
        joblib.dump(
            value={guild_id: v.id for guild_id, v in self.guilds.items()},
            filename=GUILDS_FILE_NAME,
            compress=3
        )

    @commands.cooldown(rate=3, per=10, type=commands.BucketType.guild)
    @admin_command.command(name="lift", description="登録したチャネルを解除します。")
    async def remove_channel(
        self,
        ctx: ApplicationContext,
    ):
        if ctx.guild_id in self.guilds:
            self.guilds.pop(ctx.guild_id)
            joblib.dump(
                value={guild_id: v.id for guild_id, v in self.guilds.items()},
                filename=GUILDS_FILE_NAME,
                compress=3
            )
            await ctx.interaction.response.send_message(content="通知の登録の解除を行いました。")
        else:
            await ctx.interaction.response.send_message(content="まだ登録をしていないようです。")

    @commands.cooldown(rate=3, per=10, type=commands.BucketType.user)
    @stage_check.command(name="check", description="現在予定されているステージ情報を取得できます。")
    async def check(
        self,
        ctx: ApplicationContext,
        later: Option(
            int,
            choices=[
                OptionChoice(name="今の試合", value=0),
                OptionChoice(name="次の試合", value=1),
                OptionChoice(name="次の*2試合", value=2),
                OptionChoice(name="次の*3試合", value=3),
                OptionChoice(name="次の*4試合", value=4),
                OptionChoice(name="次の*5試合", value=5),
                OptionChoice(name="次の*6試合", value=6),
                OptionChoice(name="次の*7試合", value=7),
            ],
            default=0,
            description="現在のステージを基準として8個目までのステージ情報を選択できます"
        )
    ):
        await ctx.interaction.response.send_message(embed=self.embeds[later], ephemeral=True)

    @tasks.loop(time=[time(hour=h*2, second=30) for h in range(12)])
    async def update(self):
        try:
            self.embeds = await StageStatus.getStageEmbeds()
        except:
            print(traceback.format_exc())

    @tasks.loop(time=[time(hour=h*2+1, minute=30) for h in range(12)])
    async def sender(self):
        for guild_id, channel in self.guilds.items():
            try:
                await channel.send(embed=self.embeds[1])
            except NotFound:
                self.guilds.pop(guild_id)
            except:
                print(traceback.format_exc())

    @update.before_loop
    async def _update(self):
        try:
            await self.bot.wait_until_ready()
            self.embeds = await StageStatus.getStageEmbeds()
            self.sender.start()
            data: dict[int, int] = joblib.load(filename=GUILDS_FILE_NAME)
            for key, value in data.items():
                try:
                    self.guilds: dict[int, TextChannel] = {
                        key: await self.bot.fetch_channel(value)
                    }
                except NotFound:
                    print(f"lost guild [{key}] channel [{value}]")
        except:
            print(traceback.format_exc())


def setup(bot: commands.Bot):
    bot.add_cog(SplaCog(bot))
