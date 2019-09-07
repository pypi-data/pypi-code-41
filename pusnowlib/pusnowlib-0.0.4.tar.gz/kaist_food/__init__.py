import asyncio
import re

from aiohttp import ClientSession

BASE_URL = "https://www.kaist.ac.kr/_prog/fodlst/index.php?site_dvs_cd=kr&menu_dvs_cd=050303&dvs_cd=%s&site_dvs=mobile"
DVS_DS = [
    ("fclt", "카이마루"),
    ("west", "서맛골"),
    ("east1", "동맛골"),
    ("east2", "동맛골 교직원식당"),
    ("emp", "교수회관"),
    ("icc", "문지캠퍼스"),
    ("hawam", "화암기숙사"),
    ("seoul", "서울캠퍼스"),
]

TABLE = re.compile(
    r"<table.*?class=\"menuTb\".*?>.*?<tbody>(.*?)</tbody>.*?</table>",
    re.DOTALL)
MENU = re.compile(r"<td.*?>(.*?)</td>", re.DOTALL)


async def fetch_ds(entry):
    async with ClientSession() as session:
        url = BASE_URL % entry[0]
        async with session.get(url) as response:
            assert response.status == 200
            body = await response.text()
            menus = [
                re.sub(r"<.*?>", "", menu).replace("&lt;", "<").replace(
                    "&gt;", ">").replace("&amp;",
                                         "&").replace("&quot;", "\"").replace(
                                             "\\", "₩").replace("-운영없음-", "")
                for menu in MENU.findall(body)
            ]
            if len(menus) != 3:
                return {
                    "ds": entry[1],
                    "url": url,
                }

            return {
                "ds": entry[1],
                "url": url,
                "breakfast": menus[0],
                "lunch": menus[1],
                "dinner": menus[2],
            }


async def future_get_foods():
    tasks = []
    for entry in DVS_DS:
        task = asyncio.ensure_future(fetch_ds(entry))
        tasks.append(task)
    responses = await asyncio.gather(*tasks)
    return responses


def get_foods():
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(future_get_foods())
    foods = loop.run_until_complete(future)
    return foods
