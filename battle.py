import pygame, random, sys
from monster import Monster

def battle(screen, font, player,count):
    monsters = [
        Monster("슬라임", 30, 5, 20, 5),
        Monster("고블린", 60, 8, 40, 10),
        Monster("늑대", 90, 12, 60, 20)
    ]
    monster = random.choice(monsters)
    log = [f"{monster.name}이(가) 나타났다!"]

    battling = True
    clock = pygame.time.Clock()

    while battling:
        screen.fill((20, 20, 20))

        # 로그 출력
        for i, text in enumerate(log[-6:]):
            txt = font.render(text, True, (255, 255, 255))
            screen.blit(txt, (50, 400 + i * 30))

        # 몬스터/플레이어 상태 출력
        info = f"{monster.name}: HP {monster.hp} / {player.hp}/{player.max_hp}"
        screen.blit(font.render(info, True, (255, 255, 0)), (50, 80))
        screen.blit(font.render("[1] 공격   [2] 도망", True, (200, 200, 200)), (50, 550))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:  # 공격
                    dmg = player.attack()
                    monster.hp -= dmg
                    log.append(f"당신의 공격! {monster.name}에게 {dmg} 데미지!")
                    if monster.hp <= 0:
                        log.append(f"{monster.name} 처치 성공!")
                        player.gain_exp(monster.exp, monster.gold)
                        pygame.time.delay(1000)
                        battling = False
                        break

                    # 몬스터 반격
                    mdmg = monster.attack()
                    player.take_damage(mdmg)
                    log.append(f"{monster.name}의 공격! {mdmg} 데미지!")

                    if player.hp <= 0:
                        log.append("💀 패배했습니다...")
                        pygame.display.flip()
                        pygame.time.delay(1500)
                        pygame.quit()
                        sys.exit()

                elif event.key == pygame.K_2:  # 도망
                    log.append("당신은 도망쳤다!")
                    pygame.time.delay(1000)
                    battling = False

        clock.tick(30)
