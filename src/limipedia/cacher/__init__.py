import requests
import operator
import os

from pathlib import Path
from tinydb import TinyDB
from functools import reduce

databases = {
    "weapons": TinyDB("databases/weapons.json", access_mode="r"),
    "monsters": TinyDB("databases/monsters.json", access_mode="r"),
    "defgears": TinyDB("databases/defgears.json", access_mode="r"),
}


def getFromDict(dataDict, mapList, default=None):
    for key in mapList:
        if key is None or not isinstance(dataDict, dict) or key not in dataDict:
            return default
        dataDict = dataDict[key]
    return dataDict
    # return reduce(operator.getitem, mapList, dataDict)


def cache(directory: Path, url: str):
    r = requests.get(url)

    filename = url.split("/")[-1:][0]
    pathname = directory.joinpath(filename)

    if pathname.exists():
        return

    try:
        os.makedirs(directory)
    except FileExistsError as e:
        pass

    with open(pathname, "wb") as f:
        f.write(r.content)

    print("caching: ", directory.joinpath(filename))


def main():
    cache_dir = Path("cache")
    table_names = ["weapons", "monsters", "defgears"]

    cache_fields = {
        "monsters": [
            "image",
            "thumbnail",
            "element_overlay_img",
            "reforge_info.before_reforging.image",
            "reforge_info.after_reforging.image",
            "enlightening_info.before_enlightening.image",
            "enlightening_info.after_enlightening.image",
            "awakening_info.before_awakening.image",
            "awakening_info.after_awakening.image",
            "reforge_materials",
            "materials_needed_gear",
            "materials_needed_item",
            "reforge_materials",
        ],
        "weapons": [
            "image",
            "thumbnail",
            "element_overlay_img",
            "reforge_info.before_reforging.image",
            "reforge_info.after_reforging.image",
            "ability_effect.ability.image",
            "reforge_materials",
            "awakening_info.before_awakening.image",
            "awakening_info.after_awakening.image",
            "awakening_gears",
            "awakening_items",
        ],
        "defgears": [
            "image",
            "thumbnail",
            "element_overlay_img",
            "reforge_info.before_reforging.image",
            "reforge_info.after_reforging.image",
            "reforge_materials",
            "awakening_info.before_awakening.image",
            "awakening_info.after_awakening.image",
            "awakening_gears",
            "awakening_items",
        ],

    }

    for table_name in table_names:
        database = databases[table_name].table(table_name)

        for gear in database.all()[:450]:
            print(f"[CACHING]: {gear.get("name")}")
            for field in cache_fields[table_name]:
                obj = getFromDict(gear, field.split("."))
                if obj is None:
                    continue

                if field == "image":
                    cache(cache_dir.joinpath(table_name).joinpath("image"), obj)
                    continue

                if isinstance(obj, list):
                    for item in obj:
                        image_url = getFromDict(item, ["image"])
                        cache(
                            cache_dir.joinpath(table_name).joinpath("thumbnail"),
                            image_url,
                        )
                    continue

                cache(cache_dir.joinpath(table_name).joinpath("thumbnail"), obj)
