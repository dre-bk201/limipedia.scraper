import pprint, httpx

from typing import Any, Union, List, Optional, Self
from collections import defaultdict
from pathlib import Path

from bs4 import Tag, BeautifulSoup
from limipedia.scraper.models import Item, dataclass


class Route:
    def __init__(self, route: str):
        self._route = route

    def join(self, route: Union[str, List[str], None]) -> Self:
        if route is None:
            return self

        if isinstance(route, list):
            return self.__class__(Route._join(self._route, route))
        else:
            return self.__class__(Route._join(self._route, route))

    @property
    def route(self):
        return self._route

    @classmethod
    def _join(cls, *routes: Union[str, List[str]]):
        if not routes:
            return ""

        # Start with the first route and preserve leading scheme if present
        base_route = routes[0].rstrip("/")

        # Process the remaining routes
        cleaned_routes = [route.strip("/") for route in routes[1:] if route]

        # Join the routes
        return base_route + ("/" if cleaned_routes else "") + "/".join(cleaned_routes)

    def __str__(self):
        return self.route


def soupify(url: str, endpoint: str = "", name: Optional[str] = None) -> BeautifulSoup:
    content: bytes
    name = name.replace('"', "'", 10).replace("?", "", 10) if name else name
    path = Path(f"pages/{endpoint}/{name or extract_id(url)}.html")

    if not path.exists():
        content = httpx.get(url).content
        with open(path, "wb") as f:
            f.write(httpx.get(url).content)
    else:
        with open(path, "rb") as f:
            content = f.read()
    return BeautifulSoup(content, "lxml")


def parse_int_or(value, or_=None) -> int | None:
    try:
        return int(value)
    except Exception as e:
        return or_


def extract_id(url: str) -> str:
    return url.split("/")[-1].split(".")[0]


def pp(*arg: Any, indent: int = 4):
    pp = pprint.PrettyPrinter(indent)
    pp.pprint(*arg)


def extract_items(URL: Route, desc_list: Tag, titles: List[str]):
    items = {key: None for key in titles}
    for dl in desc_list:
        for desc_term, dd in zip(dl.select("dt"), dl.select("dd")):
            kind = desc_term.get_text().rstrip().strip()

            if kind in titles:
                if dd.get_text().rstrip().strip() != "-":
                    gear_image, *overlay = dd.select("img")
                    items[kind] = Item(
                        id=extract_id(dd.select_one("a").attrs["href"]),
                        name=dd.select_one("p").get_text(),
                        image=URL.join(gear_image.get("data-src")).route,
                        element_overlay=None
                        if len(overlay) <= 0
                        else URL.join(overlay[0].get("data-src")).route,
                    )
    return items
