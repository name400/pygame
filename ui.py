import pygame

def draw_ui(screen, player, font):
    # HP 바
    pygame.draw.rect(screen, (80, 80, 80), (20, 20, 200, 20))
    hp_ratio = player.hp / player.max_hp
    pygame.draw.rect(screen, (255, 0, 0), (20, 20, 200 * hp_ratio, 20))

    # 텍스트
    txt = font.render(
        f"Lv.{player.level} HP:{player.hp}/{player.max_hp}  Gold:{player.gold}  EXP:{player.exp}/100",
        True,
        (255, 255, 255)
    )
    screen.blit(txt, (20, 50))
    screen.blit(font.render("[SPACE] 전투 시작", True, (200, 200, 200)), (20, 550))
