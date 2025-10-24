import pygame, random, sys
from monster import Monster

def _scale_stat(base, run_count, stage, boss=False):
    # 전투 횟수/스테이지에 따른 성장, 보스는 추가 배수
    val = int(base * (1 + 0.05 * run_count) * (1 + 0.08 * (stage - 1)))
    if boss:
        val = int(val * 1.6)  # 보스 보정
    return max(1, val)

def start_battle(screen, font, player, region, run_count, stage, flee_rate, boss=False):
    # 템플릿 선택
    tpl = random.choice(region.bosses if boss else region.monsters)
    m = Monster(
        name=("Boss " if boss else "") + tpl["name"],
        hp=_scale_stat(tpl["hp"], run_count, stage, boss),
        atk=_scale_stat(tpl["atk"], run_count, stage, boss),
        exp=_scale_stat(tpl["exp"], run_count, stage, boss),
        gold=_scale_stat(tpl["gold"], run_count, stage, boss),
        element=tpl.get("element","neutral")
    )

    log = [f"{region.name}의 {m.name}이(가) 나타났다! (속성:{m.element})"]
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill((20,20,20))
        info1 = f"적: {m.name} HP {m.hp} | 플레이어 HP {player.hp}/{player.max_hp}"
        info2 = "[1] 공격  [2] 도망"
        screen.blit(font.render(info1, True, (255,255,0)), (60, 80))
        screen.blit(font.render(info2, True, (200,200,200)), (60, 120))

        for i, text in enumerate(log[-6:]):
            screen.blit(font.render(text, True, (255, 255, 255)), (60, 420 + i*26))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    # 라운드 시작 디버프
                    player.apply_debuffs_each_round(lambda t: log.append(t))
                    if player.hp <= 0:
                        log.append("💀 디버프로 쓰러졌다...")
                        pygame.display.flip(); pygame.time.delay(1200)
                        return "lose"

                    # 상성 적용(지역 약점 == 플레이어 무기 속성)
                    dmg = player.attack()
                    if region.weakness == player.element:
                        dmg = int(dmg * 1.25)
                        log.append("🔥 지역 상성! 추가 피해 +25%")
                    m.hp -= dmg
                    log.append(f"당신의 공격! {m.name}에게 {dmg} 데미지!")

                    if m.hp <= 0:
                        bonus = 0
                        if boss:
                            bonus = 50  # 보스 추가 보상(골드/경험)
                        log.append(f"{m.name} 처치 성공! EXP +{m.exp}, GOLD +{m.gold + bonus}")
                        player.gain_exp(m.exp, m.gold + bonus)
                        pygame.display.flip(); pygame.time.delay(900)
                        player.tick_debuffs_after_battle()
                        return "win"

                    # 몬스터 반격
                    incoming = m.attack()
                    real = player.take_damage(incoming)
                    log.append(f"{m.name}의 공격! {incoming} → 방어 후 {real} 데미지!")
                    if player.hp <= 0:
                        log.append("💀 패배했습니다...")
                        pygame.display.flip(); pygame.time.delay(1200)
                        return "lose"

                elif event.key == pygame.K_2:
                    if random.random() < flee_rate and not boss:  # 보스전은 도망 금지(원하면 허용해도 됨)
                        log.append("성공적으로 도망쳤다!")
                        pygame.display.flip(); pygame.time.delay(600)
                        player.tick_debuffs_after_battle()
                        return "run"
                    else:
                        log.append("도망 실패! 반격을 당한다!")
                        incoming = m.attack()
                        real = player.take_damage(incoming)
                        log.append(f"{m.name}의 공격! {incoming} → 방어 후 {real} 데미지!")
                        if player.hp <= 0:
                            log.append("💀 패배했습니다...")
                            pygame.display.flip(); pygame.time.delay(1200)
                            return "lose"
        clock.tick(30)
