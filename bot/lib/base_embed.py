from discord import Embed, Color


class BaseEmbed(Embed):
    def __init__(self, *, title: str, description: str):
        super().__init__(color=Color.green(), title=title, description=description)
        self.set_footer(
            text="made by nikawamikan",
            icon_url="https://avatars.githubusercontent.com/u/66500373?s=100"
        )
        self.set_thumbnail(
            url="https://pbs.twimg.com/media/Fcp7mv-akAAIgTR?format=png&name=360x360")
