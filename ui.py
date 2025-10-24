import pygame

def draw_ui(screen, player, font, stage, region_name, flee_rate):
    # HP 바
    pygame.draw.rect(screen, (80, 80, 80), (20, 20, 220, 20))
    hp_ratio = player.hp / player.max_hp
    pygame.draw.rect(screen, (255, 0, 0), (20, 20, 220 * hp_ratio, 20))

    line1 = f"Stage {stage}  Region:{region_name}  Lv.{player.level}  Gold:{player.gold}"
    line2 = f"HP:{player.hp}/{player.max_hp}  EXP:{player.exp}/100  ATK:{player.atk}  DEF:{player.defence}"
    line3 = f"Element:{player.element}  Flee:{int(flee_rate*100)}%  [SPACE] 전투  [I] 인벤토리"

    screen.blit(font.render(line1, True, (255, 255, 255)), (20, 50))
    screen.blit(font.render(line2, True, (255, 255, 255)), (20, 80))
    screen.blit(font.render(line3, True, (210, 210, 210)), (20, 110))

    # 디버프 표시
    active = [f"{k}:{v}" for k, v in player.debuffs.items() if v > 0]
    if active:
        screen.blit(font.render("Debuffs: " + ", ".join(active), True, (255, 200, 80)), (20, 140))
