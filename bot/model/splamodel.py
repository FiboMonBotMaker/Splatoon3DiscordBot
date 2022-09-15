from datetime import datetime
from urllib.error import HTTPError
import aiohttp
import os
from lib.base_embed import BaseEmbed

USER_AGENT = os.getenv("USER_AGENT")
HEADERS = {"User-Agent": USER_AGENT}
URL = "https://spla3.yuu26.com/api/schedule"  # 全ステージ情報API


class StageStatus(BaseEmbed):

    def __init__(self, data: dict):
        super().__init__(
            title=StageStatus.__perse_datetime(
                dt=data["regular"]["start_time"]
            ).strftime(f"%-m月%-d日 %-H時からのステージ"),
            description=StageStatus.__perse_datetime(
                dt=data["regular"]["end_time"]
            ).strftime(f"%-m月%-d日 %-H時 まで")
        )
        self.add_field(
            name="🦑ナワバリ",
            value=data["regular"]["rule"]["name"]
        )
        self.add_field(
            name="ステージ",
            value=f"{data['regular']['stages'][0]['name']}\n{data['regular']['stages'][1]['name']}",
            inline=False
        )
        self.add_field(
            name="🐙チャレンジ",
            value=data["bankara_challenge"]["rule"]["name"]
        )
        self.add_field(
            name="ステージ",
            value=f"{data['bankara_challenge']['stages'][0]['name']}\n{data['bankara_challenge']['stages'][1]['name']}",
            inline=False
        )
        self.add_field(
            name="🍣オープン",
            value=data["bankara_open"]["rule"]["name"]
        )
        self.add_field(
            name="ステージ",
            value=f"{data['bankara_open']['stages'][0]['name']}\n{data['bankara_open']['stages'][1]['name']}",
            inline=False
        )

    async def getStageEmbeds():
        json = await StageStatus.__get_stage()
        stage_json = json["result"]

        stages = {data["start_time"][11:13]: {}
                  for data in stage_json["regular"]}
        for key, value in stage_json.items():
            for v in value:
                stages[v["start_time"][11:13]][key] = v
        embeds = [StageStatus(value) for value in stages.values()]
        return embeds

    def __perse_datetime(dt: str):
        return datetime.fromisoformat(f"{dt[:-6]}.000{dt[-6:]}")

    async def __get_stage() -> dict[str, dict[str, any]]:
        async with aiohttp.ClientSession() as session:
            async with session.request("get", url=URL, headers=HEADERS) as response:
                if response.status == 200:
                    json = await response.json()
                    return json
                else:
                    raise HTTPError(url=URL, code=response.status, msg=(await response.json())["message"])
