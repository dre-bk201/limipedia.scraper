from tinydb import TinyDB
from BetterJSONStorage import BetterJSONStorage
from pathlib import Path


def main():
    from limipedia.scraper.utils import dataclass

    @dataclass
    class BasicInfo:
        rarity: str = ""
        element: str = ""
        gear_cost: int = -1

    @dataclass
    class Weapon:
        id: str = ""
        name: str = ""
        basic_info: BasicInfo = BasicInfo.asdict()

    wpn = Weapon()
    print(wpn)

    # path = Path("custom.db")
    # with TinyDB(
    #     path, access_mode="r+", storage=BetterJSONStorage, _ignore_multiple_size=True
    # ) as db:
    #     db.table("persons").insert({"name": "Aundre"})
