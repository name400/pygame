import pygame

# 판매 아이템 템플릿
SHOP_ITEMS = [
    {"name":"회복 포션(+50)", "type":"consumable", "heal":50, "cost":15, "desc":"HP 50 회복"},
    {"name":"소형 포션(+25)", "type":"consumable", "heal":25, "cost":8,  "desc":"HP 25 회복"},
    {"name":"브론즈 소드",     "type":"weapon", "slot":"weapon","atk":5, "cost":30, "desc":"+5 ATK"},
    {"name":"가죽 갑옷",       "type":"armor",  "slot":"armor", "def":3, "cost":30, "desc":"+3 DEF"},
    {"name":"루비 반지",       "type":"accessory","slot":"accessory","hp":20,"cost":35,"desc":"+20 MaxHP"},
    {"name":"불의 룬",         "type":"weapon", "slot":"weapon","atk":0,"element":"fire","cost":40,"desc":"무기 속성: 불"},
    {"name":"얼음의 룬",       "type":"weapon", "slot":"weapon","atk":0,"element":"ice","cost":40,"desc":"무기 속성: 얼음"},
    {"name":"그만두기",        "type":"exit", "cost":0}
]

def open_shop(screen, font, player):
    idx = 0
    running = True
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
            screen.blit(font.render(f"{mark}{name} - {cost}G  {desc}", True, color), (60, 200 + i*34))

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
                        # 구매한 아이템을 인벤토리에 추가(룬도 아이템으로 처리 → 장착 시 속성 변경)
                        item_copy = {k:v for k,v in chosen.items() if k not in ("cost",)}
                        player.add_item(item_copy)
                    else:
                        # 잔액 부족 시 간단 알림(생략)
                        pass
