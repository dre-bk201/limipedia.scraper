import requests
import semver

from tinydb import TinyDB, where
from tinydb.database import Document
from tinydb_smartcache import SmartCacheTable  # caching needs to be done on the API
from BetterJSONStorage import BetterJSONStorage
from datetime import datetime
from pathlib import Path

from limipedia.scraper.utils import dataclass

databases = {
    "weapons": TinyDB("databases/weapons.json"),
    "defgears": TinyDB("databases/defgears.json"),
    "monsters": TinyDB("databases/monsters.json"),
    "furniture": TinyDB("databases/furniture.json"),
    "abilities": TinyDB("databases/abilities.json"),
}

@dataclass
class Version:
    version: str
    description: str
    patch_date: str

def bump_version(db_name: str):
    global databases

    metadata_table = databases[db_name].table("metadata")
    version = semver.Version.parse(metadata_table.get(where("version").exists())["version"])

    if version.patch <= 20:
        metadata_table.upsert(
            { "version": str(version.bump_patch()) },
            where("version") == str(version)
        )
    else:
        version.patch = 0
        metadata_table.upsert({"version": str(version.bump_minor())}, where("version") == str(version))


def init_database():
    global databases

    latest_release = "https://github.com/dre-bk201/limipedia.scraper/releases/latest/download/{}.json"
    database_names = ["weapons", "monsters", "defgears", "abilities", "furniture"]

    for db_name in database_names:
        try:
            response = requests.get(latest_release.format(db_name))
            if response.status_code != 200: raise Exception("Request Error")
            with open(f"databases/{db_name}.json", "wb") as f:
                f.write(response.content)
        except Exception as _:
            f = open(f"databases/{db_name}.json", "wb")
            f.close()

    for database in databases.values():
        if True:
            # with database as db:
            metadata = database.table("metadata")
            print(metadata.get(where("version").exists()))
            if metadata.get(where("version").exists()):
                continue

            metadata.insert(
                Document(
                    Version(
                        version="0.0.1",
                        description="initial scraping",
                        patch_date=str(datetime.now()),
                    ).asdict(),
                    doc_id=1,
                ),
            )
