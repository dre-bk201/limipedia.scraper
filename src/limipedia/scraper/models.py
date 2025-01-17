from typing import Optional, Dict, List, Union
from dataclasses import field


def dataclass(cls):
    """
    modified version of dataclass decorator that adds `asdict` as method to the class
    """
    from dataclasses import dataclass, asdict

    setattr(cls, "asdict", asdict)
    return dataclass(cls)


@dataclass
class Stats:
    ATK: List[Optional[int]]
    MATK: List[Optional[int]]
    DEF: List[Optional[int]]
    MDEF: List[Optional[int]]


@dataclass
class Collaboration:
    name: str
    copyright: str


@dataclass
class BasicInfo:
    rarity: str
    gear_type: str
    gear_cost: int
    element: str
    infusion_count: str
    max_level: int
    collaboration: Optional[Collaboration] = None


@dataclass
class Skill:
    name: str
    effect: str


@dataclass
class Item:
    id: str
    name: str
    image: str
    element_overlay: Optional[str] = None


@dataclass
class AbilityEffect:
    ability: Item
    effect: str
    combo_effect: Optional[int] = None


@dataclass
class ReforgeInfo:
    before_reforging: Optional[Item]
    after_reforging: Optional[Item]


@dataclass
class AwakeningInfo:
    before_awakening: Optional[Item]
    after_awakening: Optional[Item]


@dataclass
class Weapon:
    id: int = -1
    name: str = ""
    thumbnail: str = ""
    image: str = ""
    element_overlay_img: Optional[str] = None
    basic_info: BasicInfo = field(default_factory=dict)
    stats: Stats = field(default_factory=dict)
    skill: Optional[Skill] = None
    reforge_info: ReforgeInfo = field(default_factory=dict)
    ability_effect: Optional[AbilityEffect] = None
    reforge_materials: Optional[List[Item]] = None
    awakening_info: Optional[AwakeningInfo] = None
    awakening_gears: Optional[List[Item]] = None
    awakening_items: Optional[List[Item]] = None


@dataclass
class Defgear:
    id: int = -1
    name: str = ""
    thumbnail: str = ""
    image: str = ""
    element_overlay_img: Optional[str] = None
    basic_info: BasicInfo = field(default_factory=dict)
    stats: Stats = field(default_factory=dict)
    skill: Optional[Skill] = None
    reforge_info: ReforgeInfo = field(default_factory=dict)
    reforge_materials: Optional[List[Item]] = None
    awakening_info: Optional[AwakeningInfo] = None
    awakening_gears: Optional[List[Item]] = None
    awakening_items: Optional[List[Item]] = None


@dataclass
class MonsterStats:
    stats1: List[int]
    stats2: List[int]


@dataclass
class MonsterBasicInfo:
    rarity: str
    gear_type: str
    gear_cost: int
    element: str
    hidden_potential_count: int
    max_level: int
    collaboration: Optional[Collaboration] = None


@dataclass
class Restriction:
    text: str
    caution: Optional[str] = None


@dataclass
class HiddenPotential:
    lv1_effect: str
    lv2_effect: str
    lv3_effect: str
    lv4_effect: str
    lv5_effect: Optional[str] = None
    restrictions: Optional[Restriction] = None


@dataclass
class EnlighteningInfo:
    before_enlightening: Optional[Item]
    after_enlightening: Optional[Item]


# Need to figure out how to parse the caution section of restriction in HiddenPotential
@dataclass
class Monster:
    id: int = -1
    name: str = ""
    thumbnail: str = ""
    image: str = ""
    element_overlay_img: Optional[str] = None
    basic_info: MonsterBasicInfo = field(default_factory=dict)
    stats: Union[MonsterStats, Stats] = field(default_factory=dict)
    skill: Skill = field(default_factory=dict)
    burst_skills: Optional[Skill] = None
    hidden_potential: Optional[HiddenPotential] = None
    passive_skill: Optional[Skill] = None
    reforge_info: ReforgeInfo = field(default_factory=dict)
    reforge_materials: Optional[List[Item]] = None
    enlightening_info: Optional[EnlighteningInfo] = None
    awakening_info: Optional[AwakeningInfo] = None
    materials_needed_gear: Optional[List[Item]] = None
    materials_needed_item: Optional[List[Item]] = None
# in-15307756
