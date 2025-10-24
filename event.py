import pygame, random

def run_event(screen, font, player):
    events = [
        ("회복의 샘",         lambda p: setattr(p, "hp", p.max_hp),                 "🩸 체력이 모두 회복되었다!"),
        ("신비한 상자",       lambda p: setattr(p, "gold", p.gold + random.randint(10, 50)), "💰 금화를 발견했다!"),
        ("독 포자",           lambda p: p.add_debuff("poison", 3),                  "🧪 중독! 3라운드 동안 매 라운드 5피해"),
        ("저주의 그림자",     lambda p: p.add_debuff("weaken", 3),                  "⚠️ 약화! 3라운드 동안 공격력 -3"),
    ]
    name, effect, msg = random.choice(events)
    effect(player)

    screen.fill((20, 20, 30))
    screen.blit(font.render(f"이벤트: {name}", True, (255,255,255)), (100, 250))
    screen.blit(font.render(msg, True, (220,220,120)), (100, 290))
    screen.blit(font.render("아무 키나 눌러 계속...", True, (180,180,180)), (100, 340))
    pygame.display.flip()

    wait = True
    while wait:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                wait = False
