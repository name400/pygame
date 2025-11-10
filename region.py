import random

class Region:
    def __init__(self, name, bg_path, monsters, bosses, weakness):
        self.name = name
        self.bg_path = bg_path
        self.monsters = monsters   # 일반 몬스터 템플릿 리스트(dict)
        self.bosses = bosses       # 보스 템플릿 리스트(dict)
        self.weakness = weakness   # 지역 약점(플레이어 속성과 일치 시 추가 보정)

FOREST = Region(
    "숲", "assets/bg_forest.png",
    monsters=[
        {"name":"슬라임","hp":60,"atk":12,"exp":30,"gold":12,"element":"beast"},
        {"name":"늑대","hp":62,"atk":13,"exp":31,"gold":13,"element":"beast"},
        {"name":"버섯","hp":58,"atk":11,"exp":33,"gold":11,"element":"fungus"},
    ],
    bosses=[
        {"name":"대왕 늑대","hp":180,"atk":24,"exp":150,"gold":60,"element":"beast"},
    ],
    weakness="fire"
)

DESERT = Region(
    "사막", "assets/bg_desert.png",
    monsters=[
        {"name":"전갈","hp":61,"atk":12,"exp":32,"gold":12,"element":"insect"},
        {"name":"고대 골렘","hp":66,"atk":14,"exp":36,"gold":15,"element":"machine"},  # 번개 상성 대상
        {"name":"모래뱀","hp":62,"atk":11,"exp":31,"gold":11,"element":"beast"},
    ],
    bosses=[
        {"name":"사막의 여왕","hp":182,"atk":23,"exp":152,"gold":62,"element":"undead"},
    ],
    weakness="lightning"   # ⚡ 새 속성 배치
)

SNOW = Region(
    "설원", "assets/bg_snow.png",
    monsters=[
        {"name":"설늑대","hp":59,"atk":12,"exp":31,"gold":12,"element":"beast"},
        {"name":"얼음정령","hp":60,"atk":14,"exp":32,"gold":13,"element":"spirit"},
        {"name":"수룡 새끼","hp":61,"atk":12,"exp":33,"gold":12,"element":"water"},  # 번개 상성 대상
    ],
    bosses=[
        {"name":"빙결 거인","hp":179,"atk":25,"exp":149,"gold":61,"element":"giant"},
    ],
    weakness="fire"
)

SWAMP = Region(
    "늪지", "assets/bg_swamp.png",
    monsters=[
        {"name":"거머리","hp":58,"atk":12,"exp":35,"gold":11,"element":"beast"},
        {"name":"독개구리","hp":60,"atk":13,"exp":30,"gold":12,"element":"poison"},
        {"name":"물 정령","hp":62,"atk":11,"exp":34,"gold":13,"element":"water"},  # 번개 상성 대상
    ],
    bosses=[
        {"name":"맹독의 군주","hp":181,"atk":24,"exp":151,"gold":59,"element":"poison"},
    ],
    weakness="lightning"
)

VOLCANO = Region(
    "화산", "assets/bg_volcano.png",
    monsters=[
        {"name":"화염도마뱀","hp":61,"atk":13,"exp":31,"gold":12,"element":"fire"},
        {"name":"용암정령","hp":60,"atk":12,"exp":30,"gold":13,"element":"fire"},
        {"name":"숯 괴물","hp":59,"atk":11,"exp":30,"gold":11,"element":"earth"},  # 대지 상성 대상
    ],
    bosses=[
        {"name":"화염의 군주","hp":183,"atk":23,"exp":153,"gold":62,"element":"fire"},
    ],
    weakness="earth"      # 🪨 새 속성 배치
)

REGIONS = [FOREST, DESERT, SNOW, SWAMP, VOLCANO]

def choose_region_random():
    return random.choice(REGIONS)
