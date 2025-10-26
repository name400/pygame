# job_ui.py
import pygame

JOBS = [
    ("Warrior", "전사",  "+40 HP, +5 ATK"),
    ("Rogue",   "도적",  "+10 HP, +8 ATK (치명타/회피 특화)"),
    ("Mage",    "마법사", "-10 HP, +12 ATK (마법 특화)"),
    ("Tanker",  "탱커",  "+80 HP, +2 ATK (방어 특화)"),
]

def choose_job(screen, font, player):
    idx = 0
    running = True
    while running:
        screen.fill((16,16,20))
        title = font.render("전직: 레벨 10 달성! 직업을 선택하세요 (↑/↓, ENTER)", True, (255,255,255))
        screen.blit(title, (60, 80))

        for i, (key, name, desc) in enumerate(JOBS):
            mark = "▶ " if i == idx else "  "
            color = (120,255,120) if i == idx else (220,220,220)
            screen.blit(font.render(f"{mark}{name} - {desc}", True, color), (80, 160 + i*36))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    idx = (idx - 1) % len(JOBS)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    idx = (idx + 1) % len(JOBS)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    code = JOBS[idx][0]
                    player.unlock_job(code)
                    return
                elif event.key == pygame.K_ESCAPE:
                    return

def choose_first_skill(screen, font, player):
    # 직업별 3개 중 1개를 고르는 화면
    skills = player.skill_progression[player.job]  # [('id','표시명','설명'),...]
    idx = 0
    running = True
    while running:
        screen.fill((16,18,22))
        title = font.render(f"{player.job_kr()} 전직 완료! 첫 스킬을 선택하세요 (↑/↓, ENTER)", True, (255,255,255))
        screen.blit(title, (60, 80))

        for i, (sid, name, desc) in enumerate(skills[:3]):  # 초기에 3개 후보
            mark = "▶ " if i == idx else "  "
            color = (120,255,200) if i == idx else (220,220,220)
            screen.blit(font.render(f"{mark}{name}", True, color), (80, 160 + i*40))
            screen.blit(font.render(f"   {desc}", True, (180,180,180)), (100, 190 + i*40))

        hint = font.render("선택된 스킬은 즉시 습득됩니다. (최초 1개, 이후 5레벨마다 자동 추가)", True, (200,200,200))
        screen.blit(hint, (60, 320))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    idx = (idx - 1) % 3
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    idx = (idx + 1) % 3
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sid = skills[idx][0]
                    player.learn_skill(sid)   # 첫 스킬 확정
                    player.pending_first_skill = False
                    return
                elif event.key == pygame.K_ESCAPE:
                    return
