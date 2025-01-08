from tinydb import TinyDB, where
from tinydb.database import Document
from tinydb_smartcache import SmartCacheTable  # caching needs to be done on the API
from BetterJSONStorage import BetterJSONStorage
from datetime import datetime
from pathlib import Path

from limipedia.scraper.utils import dataclass

w_db = TinyDB("releases/weapons.json")
d_db = TinyDB("releases/defgears.json")
m_db = TinyDB("releases/monsters.json")
a_db = TinyDB("releases/abilities.json")
f_db = TinyDB("releases/furnitures.json")

# w_db = TinyDB(
#     Path("releases/weapons.json"),
#     access_mode="r+",
#     storage=BetterJSONStorage,
#     _ignore_multiple_size=True,
# )
# d_db = TinyDB(
#     Path("releases/defgears.json"),
#     access_mode="r+",
#     storage=BetterJSONStorage,
#     _ignore_multiple_size=True,
# )
# m_db = TinyDB(
#     Path("releases/monsters.json"),
#     access_mode="r+",
#     storage=BetterJSONStorage,
#     _ignore_multiple_size=True,
# )
# a_db = TinyDB(
#     Path("releases/abilities.json"),
#     access_mode="r+",
#     storage=BetterJSONStorage,
#     _ignore_multiple_size=True,
# )
# f_db = TinyDB(
#     Path("releases/furnitures.json"),
#     access_mode="r+",
#     storage=BetterJSONStorage,
#     _ignore_multiple_size=True,
# )


@dataclass
class Version:
    version: str
    description: str
    patch_date: str


def init_db():
    for db in [w_db, d_db, m_db, a_db, f_db]:
        if True:
            # with database as db:
            metadata = db.table("metadata")
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
