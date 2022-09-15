from datetime import time
import traceback
from discord.ext import commands, tasks
from discord import SlashCommandGroup, ApplicationContext, Permissions, TextChannel, Option, OptionChoice
from model.splamodel import StageStatus
import joblib

GUILDS_FILE_NAME = "./data/guild.dat"


class SplaCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        self.embeds: dict[str, list[StageStatus]] = {}
        self.flg = True
        self.update.start()
        self.sender.start()

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
    @admin_command.command(name="channel", description="２時間毎にこのチャンネルに対してステージ情報を受け取る設定を行います")
    async def set_channel(
        self,
        ctx: ApplicationContext,
    ):
        data: dict = joblib.load(filename=GUILDS_FILE_NAME)
        self.guilds: dict[int, TextChannel] = {
            key: await self.bot.fetch_channel(value) for key, value in data.items()
        }
        await ctx.interaction.response.send_message(content="一定時間毎にこのチャネルに通知を行います(サーバー管理者のみ実行可能です）", embed=self.embeds[0])
        self.guilds[ctx.guild_id] = ctx.channel
        joblib.dump(
            value={ctx.guild_id: ctx.channel_id},
            filename=GUILDS_FILE_NAME,
            compress=3
        )

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

    @update.before_loop
    async def _update(self):
        try:
            await self.bot.wait_until_ready()
            self.embeds = await StageStatus.getStageEmbeds()
            data: dict = joblib.load(filename=GUILDS_FILE_NAME)
            self.guilds: dict[int, TextChannel] = {
                key: await self.bot.fetch_channel(value) for key, value in data.items()
            }
        except:
            print(traceback.format_exc())

    @tasks.loop(time=[time(hour=h*2+1, minute=30) for h in range(12)])
    async def sender(self):
        try:
            for channel in self.guilds.values():
                await channel.send(embed=self.embeds[1])
        except:
            print(traceback.format_exc())

    @sender.before_loop
    async def _sender(self):
        await self.bot.wait_until_ready()


def setup(bot: commands.Bot):
    bot.add_cog(SplaCog(bot))
