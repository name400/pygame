import pygame, sys
import random
from player import Player
from battle import start_battle
from ui import draw_ui
from region import choose_region_random
from shop import open_shop
from event import run_event
from inventory_ui import open_inventory

# --- 초기화 ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("⚔️ PyRPG+")
clock = pygame.time.Clock()
font = pygame.font.SysFont("malgungothic", 24)

# --- 상태 ---
player = Player(400, 300)

# 지역 랜덤 선택
region = choose_region_random()

def game_over_screen(screen, font, WIDTH=800, HEIGHT=600):
    import pygame
    screen.fill((0, 0, 0))
    title = font.render("GAME OVER", True, (255, 80, 80))
    hint  = font.render("[R] 재시작   [Q] 종료", True, (220, 220, 220))
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 40))
    screen.blit(hint,  (WIDTH//2 - hint.get_width()//2,  HEIGHT//2 + 10))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "restart"
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    return "quit"

def load_bg(path, fallback=(25,25,40)):
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, (WIDTH, HEIGHT))
    except:
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill(fallback)
        return surf

bg = load_bg(region.bg_path)

stage = 1
run_count = 0
done_in_stage = 0

def calc_flee_rate():
    return min(0.9, 0.6 + 0.02 * player.level)

def stage_is_boss(s):
    # 보스 웨이브: 5의 배수 스테이지
    return s % 5 == 0

def battles_per_stage(s):
    # 보스 스테이지는 1회, 일반은 3회
    return 1 if stage_is_boss(s) else 3

# --- 메인 루프 ---
while True:
    keys = pygame.key.get_pressed()
    screen.blit(bg, (0, 0))

    # 이동 & 플레이어 표시
    player.move(keys)
    pygame.draw.circle(screen, (0, 200, 255), (player.x, player.y), 15)

    # UI
    draw_ui(screen, player, font, stage, region.name, calc_flee_rate())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # 전투 시작
                run_count += 1
                outcome = start_battle(
                    screen, font, player,
                    region, run_count, stage,
                    flee_rate=calc_flee_rate(),
                    boss=stage_is_boss(stage)
                )
                
                if outcome == "lose":
                    choice = game_over_screen(screen, font, WIDTH, HEIGHT)
                    if choice == "restart":
                        # 전체 상태 리셋
                        player = Player(400, 300)
                        region = choose_region_random()
                        bg = load_bg(region.bg_path)
                        stage = 1
                        run_count = 0
                        done_in_stage = 0
                    else:
                        pygame.quit()
                        sys.exit()
                else:
                    if outcome in ("win","run"):
                        done_in_stage+=1

                if done_in_stage >= battles_per_stage(stage):
                    done_in_stage = 0
                    stage += 1

                    # 스테이지 종료 보상/상호작용
                    if stage_is_boss(stage-1):
                        # 보스 스테이지 직후에는 상점
                        open_shop(screen, font, player)
                    else:
                        # 그 외엔 랜덤하게 이벤트 또는 상점(50%)
                        if random.random() < 0.5:
                            run_event(screen, font, player)
                        else:
                            open_shop(screen, font, player)

                    # 매 스테이지마다 지역을 랜덤 교체
                    region = choose_region_random()
                    bg = load_bg(region.bg_path)

            elif event.key in (pygame.K_i,):
                open_inventory(screen, font, player)

    pygame.display.flip()
    clock.tick(60)
