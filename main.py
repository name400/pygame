import pygame, sys, random
from player import Player
from battle import battle
from ui import draw_ui

# --- 초기화 ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("⚔️ PyRPG")
clock = pygame.time.Clock()
font = pygame.font.SysFont("malgungothic", 24)
count = 0

# --- 객체 생성 ---
player = Player(400, 300)

# --- 색상 ---
BG_COLOR = (25, 25, 40)
PLAYER_COLOR = (0, 200, 255)

# --- 메인 루프 ---
while True:
    screen.fill(BG_COLOR)
    keys = pygame.key.get_pressed()

    player.move(keys)

    # 플레이어 표시
    pygame.draw.circle(screen, PLAYER_COLOR, (player.x, player.y), 15)

    # UI 표시
    draw_ui(screen, player, font)

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and random.random() < 0.6:
                count+=1
                battle(screen, font, player,count)

    pygame.display.flip()
    clock.tick(60)
