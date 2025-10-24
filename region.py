import random

class Region:
    def __init__(self, name, bg_path, monsters, bosses, weakness):
        self.name = name
        self.bg_path = bg_path
        self.monsters = monsters   # 일반 몬스터 템플릿 리스트(dict)
        self.bosses = bosses       # 보스 템플릿 리스트(dict)
        self.weakness = weakness   # 지역 약점(플레이어 무기 속성과 일치 시 +25% 데미지)

FOREST = Region(
    "숲", "assets/bg_forest.png",
    monsters=[
        {"name":"슬라임","hp":30,"atk":5,"exp":18,"gold":5,"element":"beast"},
        {"name":"늑대","hp":45,"atk":8,"exp":25,"gold":7,"element":"beast"},
        {"name":"버섯","hp":38,"atk":6,"exp":22,"gold":6,"element":"fungus"},
    ],
    bosses=[
        {"name":"대왕 늑대","hp":140,"atk":18,"exp":120,"gold":50,"element":"beast"},
    ],
    weakness="fire"
)

DESERT = Region(
    "사막", "assets/bg_desert.png",
    monsters=[
        {"name":"전갈","hp":50,"atk":9,"exp":35,"gold":9,"element":"insect"},
        {"name":"미라","hp":60,"atk":10,"exp":42,"gold":12,"element":"undead"},
        {"name":"모래뱀","hp":55,"atk":11,"exp":40,"gold":10,"element":"beast"},
    ],
    bosses=[
        {"name":"사막의 여왕","hp":160,"atk":22,"exp":150,"gold":70,"element":"undead"},
    ],
    weakness="ice"
)

SNOW = Region(
    "설원", "assets/bg_snow.png",
    monsters=[
        {"name":"설늑대","hp":65,"atk":12,"exp":50,"gold":14,"element":"beast"},
        {"name":"얼음정령","hp":70,"atk":13,"exp":54,"gold":16,"element":"spirit"},
        {"name":"설거인","hp":85,"atk":14,"exp":65,"gold":20,"element":"giant"},
    ],
    bosses=[
        {"name":"빙결 거인","hp":190,"atk":26,"exp":180,"gold":90,"element":"giant"},
    ],
    weakness="fire"
)

SWAMP = Region(
    "늪지", "assets/bg_swamp.png",
    monsters=[
        {"name":"거머리","hp":55,"atk":9,"exp":36,"gold":9,"element":"beast"},
        {"name":"독개구리","hp":50,"atk":10,"exp":38,"gold":10,"element":"poison"},
        {"name":"늪 정령","hp":60,"atk":11,"exp":44,"gold":12,"element":"spirit"},
    ],
    bosses=[
        {"name":"맹독의 군주","hp":175,"atk":24,"exp":160,"gold":80,"element":"poison"},
    ],
    weakness="fire"
)

VOLCANO = Region(
    "화산", "assets/bg_volcano.png",
    monsters=[
        {"name":"화염도마뱀","hp":70,"atk":13,"exp":56,"gold":16,"element":"fire"},
        {"name":"용암정령","hp":75,"atk":14,"exp":60,"gold":18,"element":"fire"},
        {"name":"숯 괴물","hp":80,"atk":15,"exp":66,"gold":20,"element":"earth"},
    ],
    bosses=[
        {"name":"화염의 군주","hp":210,"atk":30,"exp":220,"gold":120,"element":"fire"},
    ],
    weakness="ice"
)

REGIONS = [FOREST, DESERT, SNOW, SWAMP, VOLCANO]

def choose_region_random():
    return random.choice(REGIONS)
