from collections import defaultdict
from tinydb import where
from tinydb.table import Document

from limipedia.scraper.models import *
from limipedia.scraper.constants import Constants as cn
from limipedia.scraper.utils import *
from limipedia.scraper.database import *

timeouts = [1, 4, 2, 3, 6, 8, 9, 7]

class Scraper:
    def __init__(self):
        init_database()
        self._weapons()
        self._defgears()
        self._monsters()
        self._abilities()
        self._furnitures()

    def _weapons(self):
        rarity_routes = [
            "/en/equip_list/1_2.html",
            "/en/equip_list/1_5.html",
            "/en/equip_list/1_1.html",
            "/en/equip_list/1_3.html",
            "/en/equip_list/1_4.html",
        ]
        weapons_table = databases["weapons"].table("weapons")

        for route in rarity_routes:
            # for route in rarity_routes:
            soup = soupify(cn.URL.join(route).route, endpoint="weapons")
            for td_a in soup.select("td a")[:200]:
                wpn, basic_info, stats = Weapon(), {}, defaultdict(list)
                thumbnail, *ele_overlay = td_a.select("img")

                wpn.thumbnail = cn.URL.join(thumbnail.get("data-src")).route
                wpn.id = extract_id(wpn.thumbnail)
                wpn.name = td_a.select_one("p").get_text()
                wpn.element_overlay_img = (
                    cn.URL.join(ele_overlay[0].get("data-src")).route
                    if len(ele_overlay) > 0
                    else None
                )

                # checks if gear exists in database, and skips if found
                matches = weapons_table.search(where("id") == wpn.id)
                if len(matches) > 0:
                    print(f"[STATUS]: found {wpn.id}, skipping...")
                    continue

                # shuffle(timeouts)
                # time.sleep(timeouts[0])

                details_page_soup = soupify(
                    cn.URL.join(td_a.get("href")).route,
                    endpoint="weapons",
                )
                # details_page_soup = soupify("https://jam-capture-unisonleague-ww.ateamid.com/en/equip_detail/1015157.html", endpoint="weapons", name=f"Absolute Xenoblade-1015157")
                # details_page_soup = BeautifulSoup(httpx.get("https://jam-capture-unisonleague-ww.ateamid.com/en/equip_detail/1025015.html").text, 'lxml')
                # details_page_soup = BeautifulSoup(httpx.get("https://jam-capture-unisonleague-ww.ateamid.com/en/equip_detail/1015091.html").text, 'lxml')

                # wpn.name = details_page_soup.select_one("p.name__text").get_text()
                wpn.image = cn.URL.join(
                    details_page_soup.select_one(".detail__img-block > img").attrs[
                        "data-src"
                    ]
                ).route

                print(f"[STATUS]: scraping {wpn.name}")

                for title_bar in details_page_soup.select(".title_bar"):
                    match title_bar.select_one(".title_bar--text").text.strip():
                        case cn.BASIC_INFO:
                            basic_info_table = title_bar.find_next_sibling()

                            labels = [
                                label.get_text()
                                for label in basic_info_table.select("dt")
                            ]
                            values = [
                                value.get_text()
                                for value in basic_info_table.select("dd")
                            ]

                            for label, value in zip(labels, values):
                                basic_info[label.lower().replace(" ", "_")] = (
                                    parse_int_or(value, value)
                                )

                            wpn.basic_info = BasicInfo(**basic_info)

                        case cn.STATS:
                            stats_table = title_bar.find_next_sibling()
                            for column in stats_table.select("dl")[1:]:
                                values = [
                                    parse_int_or(value.get_text())
                                    for value in column.select("dd")[1:]
                                ]
                                stats["ATK"].append(values[0])
                                stats["MATK"].append(values[1])
                                stats["DEF"].append(values[2])
                                stats["MDEF"].append(values[3])

                            wpn.stats = Stats(**stats)

                        case cn.SKILL:
                            skill_table = title_bar.find_next_sibling()
                            name, effect = skill_table.select("dd")
                            wpn.skill = Skill(
                                name=name.get_text(), effect=effect.get_text()
                            )

                        case cn.ABILITY_EFFECT:
                            ability_datalist = title_bar.find_next_sibling()
                            ability, *effect = ability_datalist.select("dd")

                            wpn.ability_effect = AbilityEffect(
                                ability=Item(  # pyright: ignore
                                    id=extract_id(  # pyright: ignore
                                        ability.select_one("a").attrs["href"]
                                    ),
                                    name=ability.select_one("p").get_text(),
                                    image=cn.URL.join(
                                        ability.select_one("img").attrs["data-src"]
                                    ).route,
                                    element_overlay=None,
                                ),
                                effect=effect[0].get_text(),
                                combo_effect=parse_int_or(
                                    None if len(effect) <= 1 else effect[1].get_text()
                                ),
                            )

                        case cn.REFORGE_INFO:
                            desc_terms = ["Before Reforging", "After Reforging"]
                            items = extract_items(
                                cn.URL, [title_bar.find_next_sibling()], desc_terms
                            )

                            wpn.reforge_info = ReforgeInfo(
                                before_reforging=items[desc_terms[0]],
                                after_reforging=items[desc_terms[1]],
                            )

                        case cn.AWAKENING_INFO:
                            desc_terms = ["Before Awakening", "After Awakening"]
                            items = extract_items(
                                cn.URL,
                                details_page_soup.select("dl.detail__reincarnation"),
                                desc_terms,
                            )

                            wpn.awakening_info = AwakeningInfo(
                                before_awakening=items[desc_terms[0]],
                                after_awakening=items[desc_terms[1]],
                            )

                            titles = details_page_soup.select("div.sp_evo_title")
                            for title in titles:
                                match title.text.strip():
                                    case cn.AWAKENING_MATERIALS_GEAR:
                                        content = title.find_next_sibling().select("td:not(.no_boder)")
                                        print("len: ", len(content))
                                        wpn.awakening_gears = []

                                        for element in content:
                                            gear_image, *overlay = element.select("img")
                                            wpn.awakening_gears.append(
                                                Item(
                                                    id=extract_id(  # pyright: ignore
                                                        gear_image.get("data-src")
                                                    ),
                                                    name=element.select_one("p").get_text(),
                                                    image=cn.URL.join(
                                                        gear_image.get("data-src")
                                                    ).route,
                                                    element_overlay=None
                                                    if len(overlay) <= 0
                                                    else cn.URL.join(
                                                        overlay[0].get("data-src")
                                                    ).route,
                                                )
                                            )

                                    case cn.AWAKENING_MATERIALS_ITEMS:
                                        items = title.find_next_sibling().select("td:not(.no_boder)")
                                        wpn.awakening_items = []

                                        for item in items:
                                            wpn.awakening_items.append(
                                                Item(
                                                    id=extract_id(  # pyright: ignore
                                                        item.select_one("img").attrs["data-src"]
                                                    ),
                                                    name=item.select_one("p").get_text(),
                                                    image=cn.URL.join(
                                                        item.select_one("img").attrs["data-src"]
                                                    ).route,
                                                    element_overlay=None
                                                    if len(overlay) <= 0
                                                    else cn.URL.join(
                                                        overlay[0].get("data-src")
                                                    ).route,
                                                )
                                            )


                        case cn.REFORGE_MATERIALS:
                            items = title_bar.find_next_sibling().select("dd")
                            wpn.reforge_materials = []
                            for item in items:
                                gear_image, *overlay = item.select("img")
                                wpn.reforge_materials.append(
                                    Item(
                                        id=extract_id(  # pyright: ignore
                                            item.select_one("a").attrs["href"]
                                        ),
                                        name=item.select_one("p").get_text(),
                                        image=cn.URL.join(
                                            gear_image.get("data-src")
                                        ).route,
                                        element_overlay=None
                                        if len(overlay) <= 0
                                        else cn.URL.join(
                                            overlay[0].get("data-src")
                                        ).route,
                                    )
                                )

                weapons_table.insert(Document(wpn.asdict(), doc_id=wpn.id))
                bump_version("weapons")

    def _defgears(self):
        rarity_routes = [
            "/en/equip_list/23_5.html",
            "/en/equip_list/23_1.html",
            "/en/equip_list/23_2.html",
            "/en/equip_list/23_3.html",
            "/en/equip_list/23_4.html",
        ]

        defgears_table = databases["defgears"].table("defgears")

        for route in rarity_routes[:]:
            soup = soupify(cn.URL.join(route).route, endpoint="defgears")

            for td_a in soup.select("td a")[:200]:
                defgear, basic_info, stats = Defgear(), {}, defaultdict(list)
                thumbnail, *ele_overlay = td_a.select("img")

                defgear.thumbnail = cn.URL.join(thumbnail.get("data-src")).route
                defgear.id = extract_id(defgear.thumbnail)
                defgear.name = td_a.select_one("p").get_text()
                defgear.element_overlay_img = (
                    cn.URL.join(ele_overlay[0].get("data-src")).route
                    if len(ele_overlay) > 0
                    else None
                )

                # checks if gear exists in database, and skips if found
                matches = defgears_table.search(where("id") == defgear.id)
                if len(matches) > 0:
                    print(f"[STATUS]: found {defgear.id}, skipping...")
                    continue

                details_page_soup = soupify(cn.URL.join(td_a.get("href")).route, endpoint="defgears")

                defgear.image = cn.URL.join(
                    details_page_soup.select_one(".detail__img-block > img").attrs[
                        "data-src"
                    ]
                ).route

                print(f"[STATUS]: scraping {defgear.name}")
                for title_bar in details_page_soup.select(".title_bar"):
                    match title_bar.select_one(".title_bar--text").text.strip():
                        case cn.BASIC_INFO:
                            desc_tbl = title_bar.find_next_sibling()

                            labels = [
                                label.get_text() for label in desc_tbl.select("dt")
                            ]
                            values = [
                                value.get_text() for value in desc_tbl.select("dd")
                            ]

                            for label, value in zip(labels, values):
                                basic_info[label.lower().replace(" ", "_")] = (
                                    parse_int_or(value, value)
                                )

                            defgear.basic_info = BasicInfo(**basic_info)

                        case cn.STATS:
                            stats_table = title_bar.find_next_sibling()
                            for column in stats_table.select("dl")[1:]:
                                values = [
                                    parse_int_or(value.get_text())
                                    for value in column.select("dd")[1:]
                                ]
                                stats["ATK"].append(values[0])
                                stats["MATK"].append(values[1])
                                stats["DEF"].append(values[2])
                                stats["MDEF"].append(values[3])

                            defgear.stats = Stats(**stats)

                        case cn.SKILL:
                            skill_table = title_bar.find_next_sibling()
                            name, effect = skill_table.select("dd")
                            defgear.skill = Skill(
                                name=name.get_text(),
                                effect=effect.get_text()
                            )

                        case cn.REFORGE_INFO:
                            desc_terms = ["Before Reforging", "After Reforging"]
                            items = extract_items(
                                cn.URL, [title_bar.find_next_sibling()], desc_terms
                            )

                            defgear.reforge_info = ReforgeInfo(
                                before_reforging=items[desc_terms[0]],
                                after_reforging=items[desc_terms[1]],
                            )

                        case cn.AWAKENING_INFO:
                            desc_terms = ["Before Awakening", "After Awakening"]
                            items = extract_items(
                                cn.URL,
                                details_page_soup.select("dl.detail__reincarnation"),
                                desc_terms,
                            )

                            defgear.awakening_info = AwakeningInfo(
                                before_awakening=items[desc_terms[0]],
                                after_awakening=items[desc_terms[1]],
                            )

                            titles = details_page_soup.select("div.sp_evo_title")
                            for title in titles:
                                match title.text.strip():
                                    case cn.AWAKENING_MATERIALS_GEAR:
                                        content = title.find_next_sibling().select("td:not(.no_boder)")
                                        print("len: ", len(content))
                                        defgear.awakening_gears = []

                                        for element in content:
                                            gear_image, *overlay = element.select("img")
                                            defgear.awakening_gears.append(
                                                Item(
                                                    id=extract_id(  # pyright: ignore
                                                        gear_image.get("data-src")
                                                    ),
                                                    name=element.select_one("p").get_text(),
                                                    image=cn.URL.join(
                                                        gear_image.get("data-src")
                                                    ).route,
                                                    element_overlay=None
                                                    if len(overlay) <= 0
                                                    else cn.URL.join(
                                                        overlay[0].get("data-src")
                                                    ).route,
                                                )
                                            )

                                    case cn.AWAKENING_MATERIALS_ITEMS:
                                        items = title.find_next_sibling().select("td:not(.no_boder)")
                                        defgear.awakening_items = []

                                        for item in items:
                                            defgear.awakening_items.append(
                                                Item(
                                                    id=extract_id(  # pyright: ignore
                                                        item.select_one("img").attrs["data-src"]
                                                    ),
                                                    name=item.select_one("p").get_text(),
                                                    image=cn.URL.join(
                                                        item.select_one("img").attrs["data-src"]
                                                    ).route,
                                                    element_overlay=None
                                                    if len(overlay) <= 0
                                                    else cn.URL.join(
                                                        overlay[0].get("data-src")
                                                    ).route,
                                                )
                                            )

                        case cn.REFORGE_MATERIALS:
                            items = title_bar.find_next_sibling().select("dd")
                            defgear.reforge_materials = []

                            for item in items:
                                gear_image, *overlay = item.select("img")
                                defgear.reforge_materials.append(
                                    Item(
                                        id=extract_id( # pyright: ignore
                                            item.select_one("a").attrs["href"]
                                        ),
                                        name=item.select_one("p").get_text(),
                                        image=cn.URL.join(
                                            gear_image.get("data-src")
                                        ).route,
                                        element_overlay=None
                                        if len(overlay) <= 0
                                        else cn.URL.join(
                                            overlay[0].get("data-src")
                                        ).route,
                                    )
                                )
                # print(defgear)
                defgears_table.insert(Document(defgear.asdict(), doc_id=defgear.id))
                bump_version("defgears")

    def _abilities(self):
        pass

    def _furnitures(self):
        pass

    def _monsters(self):
        rarity_routes = [
            "/en/equip_list/4_1.html",
            "/en/equip_list/4_2.html",
            "/en/equip_list/4_3.html",
            "/en/equip_list/4_4.html",
            "/en/equip_list/4_5.html",
        ]

        monster_table =  databases["monsters"]

        for route in rarity_routes:
            soup = soupify(cn.URL.join(route).route, endpoint="monsters")

            for td_a in soup.select("td a")[:200]:
                monster, basic_info, stats = Monster(), {}, defaultdict(list)
                thumbnail, *ele_overlay = td_a.select("img")

                monster.thumbnail = cn.URL.join(thumbnail.get("data-src")).route
                monster.id = extract_id(monster.thumbnail)
                monster.name = td_a.select_one("p").get_text()
                monster.element_overlay_img = (
                    cn.URL.join(ele_overlay[0].get("data-src")).route
                    if len(ele_overlay) > 0
                    else None
                )

                # checks if gear exists in database, and skips if found
                matches = monster_table.search(where("id") == monster.id)
                if len(matches) > 0:
                    print(f"[STATUS]: found {monster.name}, skipping...")
                    continue

                # details_page_soup = soupify(cn.URL.join(td_a.get("href")).route)

                details_page_soup = soupify(
                    cn.URL.join(td_a.get("href")).route,
                    endpoint="monsters",
                )

                # details_page_soup = soupify(
                #     "https://jam-capture-unisonleague-ww.ateamid.com/en/equip_detail/1916106.html",
                #     endpoint="monsters",
                # )

                # details_page_soup = soupify(
                #     "https://jam-capture-unisonleague-ww.ateamid.com/en/equip_detail/4415110.html",
                #     endpoint="monsters",
                # )

                # details_page_soup = soupify(
                #     "https://jam-capture-unisonleague-ww.ateamid.com/en/equip_detail/4415002.html",
                #     endpoint="monsters",
                # )

                # details_page_soup = soupify(
                #     "https://jam-capture-unisonleague-ww.ateamid.com/en/equip_detail/4415316.html",
                #     endpoint="monsters",
                # )

                # details_page_soup = soupify(
                #     "https://jam-capture-unisonleague-ww.ateamid.com/en/equip_detail/4415019.html",
                #     endpoint="monsters",
                # )

                monster.image = cn.URL.join(
                    details_page_soup.select_one(".detail__img-block > img").attrs[
                        "data-src"
                    ]
                ).route

                print(f"[STATUS]: scraping {monster.name}")

                for title_bar in details_page_soup.select(".title_bar"):
                    match title_bar.select_one(".title_bar--text").text.strip():
                        case cn.BASIC_INFO:
                            basic_info_table = title_bar.find_next_sibling()

                            labels = [
                                label.get_text()
                                for label in basic_info_table.select("dt")
                            ]
                            values = [
                                value.get_text()
                                for value in basic_info_table.select("dd")
                            ]

                            for label, value in zip(labels, values):
                                basic_info[label.lower().replace(" ", "_")] = (
                                    parse_int_or(value, value)
                                )

                            monster.basic_info = MonsterBasicInfo(**basic_info)

                        case cn.STATS:
                            stats_desc_list = title_bar.find_next_sibling()
                            desc_lists = [dl for dl in stats_desc_list.select("dl")]
                            keys = [
                                key.get_text() for key in desc_lists[0].select("dd")[1:]
                            ]

                            for dl in desc_lists[1:]:
                                for idx, dd in enumerate(dl.select("dd")[1:]):
                                    key = (
                                        keys[idx].lower()
                                        if keys[idx] in ["Stats1", "Stats2"]
                                        else keys[idx]
                                    )
                                    stats[key].append(parse_int_or(dd.get_text()))

                            monster.stats = (
                                Stats(**stats)
                                if "stats1" not in stats
                                else MonsterStats(**stats)
                            )

                        case cn.SKILL:
                            skill_table = title_bar.find_next_sibling()
                            name, effect = skill_table.select("dd")
                            monster.skill = Skill(
                                name=name.get_text(),
                                effect=effect.get_text()
                            )

                        case cn.PASSIVE_SKILL:
                            skill_table = title_bar.find_next_sibling()
                            name, effect = skill_table.select("dd")
                            monster.passive_skill = Skill(
                                name=name.get_text(),
                                effect=effect.get_text()
                            )

                        case cn.BURST_SKILLS:
                            skill_table = title_bar.find_next_sibling()
                            name, effect = skill_table.select("dd")
                            monster.burst_skills = Skill(
                                name=name.get_text(),
                                effect=effect.get_text()
                            )

                        case cn.REFORGE_INFO:
                            desc_terms = ["Before Reforging", "After Reforging"]
                            items = extract_items(
                                cn.URL, [title_bar.find_next_sibling()], desc_terms
                            )

                            monster.reforge_info = ReforgeInfo(
                                before_reforging=items[desc_terms[0]],
                                after_reforging=items[desc_terms[1]],
                            )

                        case cn.HIDDEN_POTENTIAL:
                            hidden_potential_table = title_bar.find_next_sibling()
                            dts, dds = [i.get_text() for i in hidden_potential_table.select("dt")], [i.get_text() for i in hidden_potential_table.select("dd")]
                            potential = {}

                            for (dt, dd) in zip(dts, dds):
                                potential[dt.lower().replace(" ", "_")] = dd

                            monster.hidden_potential = HiddenPotential(**potential)

                        case cn.AWAKENING_INFO:
                            desc_terms = ["Before Awakening", "After Awakening"]
                            items = extract_items(
                                cn.URL,
                                details_page_soup.select("dl.detail__reincarnation"),
                                desc_terms,
                            )

                            monster.awakening_info = AwakeningInfo(
                                before_awakening=items[desc_terms[0]],
                                after_awakening=items[desc_terms[1]],
                            )

                            titles = details_page_soup.select("div.sp_evo_title")
                            for title in titles:
                                match title.text.strip():
                                    case cn.AWAKENING_MATERIALS_GEAR:
                                        gears = title.find_next_sibling().select("td:not(.no_boder)")
                                        monster.materials_needed_gear = []

                                        for element in gears:
                                            gear_image, *overlay = element.select("img")
                                            monster.materials_needed_gear.append(
                                                Item(
                                                    id=extract_id(  # pyright: ignore
                                                        gear_image.get("data-src")
                                                    ),
                                                    name=element.select_one("p").get_text(),
                                                    image=cn.URL.join(
                                                        gear_image.get("data-src")
                                                    ).route,
                                                    element_overlay=None
                                                    if len(overlay) <= 0
                                                    else cn.URL.join(
                                                        overlay[0].get("data-src")
                                                    ).route,
                                                )
                                            )

                                    case cn.AWAKENING_MATERIALS_ITEMS:
                                        items = title.find_next_sibling().select("td:not(.no_boder)")
                                        monster.materials_needed_item = []

                                        for item in items:
                                            monster.materials_needed_item.append(
                                                Item(
                                                    id=extract_id(  # pyright: ignore
                                                        item.select_one("img").attrs["data-src"]
                                                    ),
                                                    name=item.select_one("p").get_text(),
                                                    image=cn.URL.join(
                                                        item.select_one("img").attrs["data-src"]
                                                    ).route,
                                                    element_overlay=None
                                                    if len(overlay) <= 0
                                                    else cn.URL.join(
                                                        overlay[0].get("data-src")
                                                    ).route,
                                                )
                                            )

                        case cn.ENLIGHTENING_INFO:
                            desc_terms = ["Before Enlightening", "After Enlightening"]
                            items = extract_items(
                                cn.URL,
                                details_page_soup.select("dl.detail__reincarnation"),
                                desc_terms,
                            )

                            monster.enlightening_info = EnlighteningInfo(
                                before_enlightening=items[desc_terms[0]],
                                after_enlightening=items[desc_terms[1]],
                            )

                            titles = details_page_soup.select("div.sp_evo_title")
                            for title in titles:
                                match title.text.strip():
                                    case cn.AWAKENING_MATERIALS_GEAR:
                                        gears = title.find_next_sibling().select("td:not(.no_boder)")
                                        monster.materials_needed_gear = []

                                        for element in gears:
                                            gear_image, *overlay = element.select("img")
                                            monster.materials_needed_gear.append(
                                                Item(
                                                    id=extract_id(  # pyright: ignore
                                                        gear_image.get("data-src")
                                                    ),
                                                    name=element.select_one("p").get_text(),
                                                    image=cn.URL.join(
                                                        gear_image.get("data-src")
                                                    ).route,
                                                    element_overlay=None
                                                    if len(overlay) <= 0
                                                    else cn.URL.join(
                                                        overlay[0].get("data-src")
                                                    ).route,
                                                )
                                            )

                                    case cn.AWAKENING_MATERIALS_ITEMS:
                                        items = title.find_next_sibling().select("td:not(.no_boder)")
                                        monster.materials_needed_item = []

                                        for item in items:
                                            monster.materials_needed_item.append(
                                                Item(
                                                    id=extract_id(  # pyright: ignore
                                                        item.select_one("img").attrs["data-src"]
                                                    ),
                                                    name=item.select_one("p").get_text(),
                                                    image=cn.URL.join(
                                                        item.select_one("img").attrs["data-src"]
                                                    ).route,
                                                    element_overlay=None
                                                    if len(overlay) <= 0
                                                    else cn.URL.join(
                                                        overlay[0].get("data-src")
                                                    ).route,
                                                )
                                            )

                monster_table.insert(Document(monster.asdict(), doc_id=monster.id))
                bump_version("monsters")



def main():
    scraper = Scraper()
