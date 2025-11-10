import pygame

# =====[ 기본 판매 아이템 템플릿 ]=====
BASE_SHOP_ITEMS = [
    {"name":"회복 포션(+50)", "type":"consumable", "heal":50, "cost":15, "desc":"HP 50 회복"},
    {"name":"소형 포션(+25)", "type":"consumable", "heal":25, "cost":8,  "desc":"HP 25 회복"},
    {"name":"브론즈 소드",     "type":"weapon", "slot":"weapon","atk":5, "cost":30, "desc":"+5 ATK"},
    {"name":"가죽 갑옷",       "type":"armor",  "slot":"armor", "def":3, "cost":30, "desc":"+3 DEF"},
    {"name":"루비 반지",       "type":"accessory","slot":"accessory","hp":20,"cost":35,"desc":"+20 MaxHP"},

    # ---- 룬: 무기와 분리 (별도 슬롯 "rune") ----
    {"name":"불의 룬",    "type":"rune", "slot":"rune", "element":"fire",      "cost":40, "desc":"무기 속성: 불"},
    {"name":"얼음의 룬",  "type":"rune", "slot":"rune", "element":"ice",       "cost":40, "desc":"무기 속성: 얼음"},
    {"name":"번개의 룬",  "type":"rune", "slot":"rune", "element":"lightning", "cost":40, "desc":"무기 속성: 번개"},
    {"name":"대지의 룬",  "type":"rune", "slot":"rune", "element":"earth",     "cost":40, "desc":"무기 속성: 대지"},
    {"name":"독의 룬",    "type":"rune", "slot":"rune", "element":"poison",    "cost":40, "desc":"무기 속성: 독"},
]

EXIT_ITEM = {"name":"그만두기", "type":"exit", "cost":0}

# =====[ 티어 정의 ]=====
# (최소 레벨, 티어명, 스탯/가격 배수)
TIERS = [
    (0,  "브론즈",   1.00),
    (10, "실버",     1.20),
    (20, "골드",     1.40),
    (30, "플래티넘", 1.60),
    (40, "다이아",   1.80),
    (50, "미스릴",   2.00),
    (60, "오리하르콘",2.20),
]

TIER_WORDS = ["브론즈","실버","골드","플래티넘","다이아","미스릴","오리하르콘"]

def get_tier_for_level(level: int):
    """플레이어 레벨에 맞는 (티어명, 배수, 티어인덱스) 반환"""
    tier_name, mult = TIERS[0][1], TIERS[0][2]
    tier_idx = 0
    for i, (min_lv, name, m) in enumerate(TIERS):
        if level >= min_lv:
            tier_name, mult, tier_idx = name, m, i
        else:
            break
    return tier_name, mult, tier_idx

def strip_tier_words(base_name: str) -> str:
    """아이템 이름 앞의 티어 단어 제거(예: '브론즈 소드' -> '소드')"""
    for w in TIER_WORDS:
        if base_name.startswith(w + " "):
            return base_name[len(w)+1:]
    return base_name

def scaled_item(item: dict, tier_name: str, mult: float, tier_idx: int) -> dict:
    """템플릿 아이템을 티어/배수에 맞춰 스케일 & 이름 변경"""
    it = item.copy()

    # 이름 처리
    base = strip_tier_words(it["name"])
    if it.get("type") == "rune" or "룬" in it["name"]:
        it["name"] = f"{tier_name} {it['name']}"
    else:
        it["name"] = f"{tier_name} {base}"

    # 공통: 가격 스케일
    if "cost" in it:
        it["cost"] = max(1, int(round(it["cost"] * mult)))

    # 타입별 스케일
    t = it.get("type")
    if t == "weapon" and it.get("slot") == "weapon":
        if it.get("atk", 0) > 0:
            it["atk"] = max(1, int(round(it["atk"] * mult)))
            it["desc"] = f"+{it['atk']} ATK"

    elif t == "armor" and it.get("slot") == "armor":
        if "def" in it:
            it["def"] = max(1, int(round(it["def"] * mult)))
            it["desc"] = f"+{it['def']} DEF"

    elif t == "accessory" and it.get("slot") == "accessory":
        if "hp" in it:
            it["hp"] = max(1, int(round(it["hp"] * mult)))
            it["desc"] = f"+{it['hp']} MaxHP"

    elif t == "consumable":
        if "heal" in it:
            it["heal"] = max(1, int(round(it["heal"] * mult)))
            it["desc"] = f"HP {it['heal']} 회복"

    elif t == "rune" and it.get("slot") == "rune":
        # 룬: 속성 부여 + 추가 피해 % (티어에 따라 증가)
        bonus = 10 + 5 * tier_idx  # 10%, 15%, 20%, ...
        it["element_bonus"] = bonus
        elem_map = {
            "fire":"불", "ice":"얼음", "lightning":"번개",
            "earth":"대지", "poison":"독"
        }
        elem_kor = elem_map.get(it.get("element"), "속성")
        it["desc"] = f"무기 속성: {elem_kor}, 추가 피해 +{bonus}%"

    return it

def build_shop_items_for_level(player_level: int):
    """플레이어 레벨에 따라 스케일된 상점 아이템 목록 생성"""
    tier_name, mult, tier_idx = get_tier_for_level(player_level)
    scaled = [scaled_item(it, tier_name, mult, tier_idx) for it in BASE_SHOP_ITEMS]
    scaled.append(EXIT_ITEM)  # 마지막에 '그만두기'
    return scaled

def open_shop(screen, font, player):
    idx = 0
    running = True

    # ✅ 상점 진입 시점의 플레이어 레벨을 기준으로 아이템 스냅샷 생성
    SHOP_ITEMS = build_shop_items_for_level(getattr(player, "level", 1))

    while running:
        screen.fill((25, 15, 10))
        screen.blit(font.render("🏪 상점: ↑/↓ 선택, ENTER 구매, ESC 나가기", True, (255,255,255)), (60, 100))
        screen.blit(font.render(f"Gold: {player.gold}", True, (255,220,120)), (60, 140))

        for i, it in enumerate(SHOP_ITEMS):
            mark = "▶ " if i == idx else "  "
            name = it["name"]
            cost = it["cost"]
            desc = it.get("desc","")
            color = (255,255,255) if i != idx else (120,255,120)
            y = 200 + i*34
            screen.blit(font.render(f"{mark}{name} - {cost}G  {desc}", True, color), (60, y))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    idx = (idx + 1) % len(SHOP_ITEMS)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    idx = (idx - 1) % len(SHOP_ITEMS)
                elif event.key == pygame.K_ESCAPE:
                    return
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    chosen = SHOP_ITEMS[idx]
                    if chosen["type"] == "exit":
                        return
                    if player.gold >= chosen["cost"]:
                        player.gold -= chosen["cost"]
                        item_copy = {k:v for k,v in chosen.items() if k not in ("cost",)}
                        player.add_item(item_copy)
                    else:
                        pass
