# ui.py
import pygame

def draw_ui(screen, player, font, stage, region_name, flee_rate):
    # 1) 반투명 HUD 영역
    hud = pygame.Surface((800, 160), pygame.SRCALPHA)  # 너비/높이는 화면에 맞게
    # 화산은 붉은 배경이라 살짝 더 어두운 바, 그 외는 일반 어두운 바
    bar_color = (0, 0, 0, 170) if region_name != "화산" else (0, 0, 0, 190)
    hud.fill(bar_color)
    screen.blit(hud, (0, 0))

    # 2) 텍스트 색(모든 지역에서 흰색 고정 가능)
    txt  = (255, 255, 255)
    hint = (220, 220, 220)

    # 3) HP 바 + 텍스트
    pygame.draw.rect(screen, (60, 60, 60), (20, 20, 220, 20), border_radius=4)
    hp_ratio = player.hp / player.max_hp
    pygame.draw.rect(screen, (220, 60, 60), (20, 20, int(220 * hp_ratio), 20), border_radius=4)

    line1 = f"Stage {stage}  Region:{region_name}  Lv.{player.level}  Gold:{player.gold}"
    job_text = player.job_kr() if player.job else "-"
    line2 = f"HP:{player.hp}/{player.max_hp}  EXP:{player.exp}/100  ATK:{player.atk}  DEF:{player.defence}  Job:{job_text}"
    line3 = f"Element:{player.element}  Flee:{int(flee_rate*100)}%  [SPACE] 전투  [I] 인벤토리  [3] 스킬(전투중)"

    screen.blit(font.render(line1, True, txt),  (20, 50))
    screen.blit(font.render(line2, True, txt),  (20, 80))
    screen.blit(font.render(line3, True, hint), (20, 110))

    # 디버프/스킬
    active_debuffs = [f"{k}:{v}" for k, v in player.debuffs.items() if v > 0]
    if active_debuffs:
        screen.blit(font.render("Debuffs: " + ", ".join(active_debuffs), True, (255, 200, 80)), (20, 140))

    if player.skills:
        names = {sid:name for (sid, name, _) in player.skill_progression[player.job]}
        disp = [f"{names.get(sid, sid)}({player.skill_cooldowns.get(sid, 0)})" for sid in player.skills]
        screen.blit(font.render("Skills: " + ", ".join(disp), True, (180, 230, 255)), (20, 170))
