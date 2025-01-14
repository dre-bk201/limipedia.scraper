from limipedia.scraper.database import w_db
from tinydb import Query, where
from typing import Mapping

def contains(record: str, *values: str) -> bool:
    found = True

    for value in values:
        found = found and value.lower() in record.lower()

    return found

def startswith(record: str, value: str) -> bool:
    return record.lower().startswith(value.lower())


def main():
    weapons_table = w_db.table("weapons")
    # print(weapons_table.search(~(Weapon.id == "1015005")))
    # print(weapons_table.search(Weapon.id.exists()))

    # print(weapons_table.search(Weapon.basic_info.rarity == "SSR")[:10])
    # print(weapons_table.search(Weapon.basic_info.rarity == "UR"))
    name = "xeno"
    gear_type = "lance"
    Weapon = Query()

    # print(weapons_table.all()[0:10])
    c = weapons_table.update({"enlightening_info": {}}, Weapon.enlightening_info.exists())
    print(c)

    # for weapon in weapons_table.search(
    #         Weapon.id == 1015064
    #         # (Weapon.name.test(contains, "xeno", "spear")) &
    #         # (Weapon.basic_info.gear_cost >= 42) &
    #         # (Weapon.basic_info.gear_cost <= 45)
    #     ):
    #     # c: Document = weapon
    #     print(weapon)
