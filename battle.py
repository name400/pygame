# battle.py (REPLACE)
import pygame, random, sys
from monster import Monster

def _scale_stat(base, run_count, stage, boss=False):
    val = int(base * (1 + 0.05 * run_count) * (1 + 0.08 * (stage - 1)))
    if boss: val = int(val * 1.6)
    return max(1, val)

def _open_skill_menu(screen, font, player):
    # 보유 스킬 리스트와 현재 쿨 표시, 숫자키 선택
    skills = player.skill_display_list()  # [(sid,name,cd), ...]
    if not skills: return None
    running = True; idx = 0

    while running:
        screen.fill((22,22,26))
        screen.blit(font.render("스킬 사용 (↑/↓, ENTER 선택, ESC 취소)", True, (255,255,255)), (60, 80))
        for i,(sid,name,cd) in enumerate(skills):
            mark = "▶ " if i == idx else "  "
            ready = "(사용가능)" if cd == 0 else f"(쿨 {cd})"
            color = (120,255,200) if (i==idx and cd==0) else ((220,220,220) if cd==0 else (180,180,180))
            screen.blit(font.render(f"{mark}{name} {ready}", True, color), (80, 160 + i*36))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w): idx = (idx - 1) % len(skills)
                elif event.key in (pygame.K_DOWN, pygame.K_s): idx = (idx + 1) % len(skills)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sid = skills[idx][0]
                    if player.can_use(sid):
                        return sid
                elif event.key == pygame.K_ESCAPE:
                    return None

def start_battle(screen, font, player, region, run_count, stage, flee_rate, boss=False):
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
    monster_stunned = False

    while running:
        screen.fill((20,20,20))
        info1 = f"적: {m.name} HP {m.hp} | 플레이어 HP {player.hp}/{player.max_hp}"
        info2 = "[1] 공격  [2] 도망  [3] 스킬"
        screen.blit(font.render(info1, True, (255,255,0)), (60, 80))
        screen.blit(font.render(info2, True, (200,200,200)), (60, 120))

        for i, text in enumerate(log[-7:]):
            screen.blit(font.render(text, True, (255,255,255)), (60, 420 + i*26))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    # 라운드 시작: 디버프/버프/쿨타임 감소
                    player.apply_debuffs_each_round(lambda t: log.append(t))
                    if player.hp <= 0:
                        log.append("💀 디버프로 쓰러졌다..."); pygame.display.flip(); pygame.time.delay(1200)
                        return "lose"

                    # 상성(지역 약점 == 플레이어 무기 속성)
                    dmg = player.attack()
                    if region.weakness == player.element:
                        dmg = int(dmg * 1.25); log.append("🔥 지역 상성! 추가 피해 +25%")

                    m.hp -= dmg; log.append(f"당신의 공격! {m.name}에게 {dmg} 데미지!")
                    if m.hp <= 0:
                        bonus = 50 if boss else 0
                        log.append(f"{m.name} 처치! EXP +{m.exp}, GOLD +{m.gold + bonus}")
                        player.gain_exp(m.exp, m.gold + bonus)
                        pygame.display.flip(); pygame.time.delay(900)
                        player.tick_debuffs_after_battle()
                        return "win"

                    # 몬스터 반격 (기절 시 스킵)
                    if monster_stunned:
                        log.append("⚡ 적이 기절하여 행동하지 못했다!")
                        monster_stunned = False
                    else:
                        incoming = m.attack()
                        real, dodged = player.receive_attack(incoming)
                        if dodged: log.append(f"{m.name}의 공격! 회피 성공!")
                        else:      log.append(f"{m.name}의 공격! {incoming} → 방어/가드 후 {real} 데미지!")
                        if player.hp <= 0:
                            log.append("💀 패배했습니다..."); pygame.display.flip(); pygame.time.delay(1200)
                            return "lose"

                elif event.key == pygame.K_2:
                    if random.random() < flee_rate and not boss:
                        log.append("성공적으로 도망쳤다!")
                        pygame.display.flip(); pygame.time.delay(600)
                        player.tick_debuffs_after_battle()
                        return "run"
                    else:
                        log.append("도망 실패! 반격을 당한다!")
                        incoming = m.attack()
                        real, dodged = player.receive_attack(incoming)
                        if dodged: log.append(f"{m.name}의 공격! 회피 성공!")
                        else:      log.append(f"{m.name}의 공격! {incoming} → 방어/가드 후 {real} 데미지!")
                        if player.hp <= 0:
                            log.append("💀 패배했습니다..."); pygame.display.flip(); pygame.time.delay(1200)
                            return "lose"

                elif event.key == pygame.K_3:
                    # --- 스킬 사용 ---
                    sid = _open_skill_menu(screen, font, player)
                    if sid:
                        # 라운드 시작 처리
                        player.apply_debuffs_each_round(lambda t: log.append(t))
                        if player.hp <= 0:
                            log.append("💀 디버프로 쓰러졌다..."); pygame.display.flip(); pygame.time.delay(1200)
                            return "lose"

                        dmg, stun, extra = player.cast_skill(sid, m)
                        for t in extra: log.append(t)

                        # 속성 상성은 '스킬도 공격성 스킬이면' 적용하도록 간단 처리
                        if dmg > 0 and region.weakness == player.element:
                            add = int(dmg * 0.25); dmg += add
                            log.append(f"🔥 지역 상성! 추가 피해 +{add}")

                        if dmg > 0:
                            m.hp -= dmg; log.append(f"스킬 피해! {m.name}에게 {dmg} 데미지!")
                        if stun:
                            monster_stunned = True

                        if m.hp <= 0:
                            bonus = 50 if boss else 0
                            log.append(f"{m.name} 처치! EXP +{m.exp}, GOLD +{m.gold + bonus}")
                            player.gain_exp(m.exp, m.gold + bonus)
                            pygame.display.flip(); pygame.time.delay(900)
                            player.tick_debuffs_after_battle()
                            return "win"

                        # 적 턴 (기절이면 스킵)
                        if monster_stunned:
                            log.append("⚡ 적이 기절하여 행동하지 못했다!")
                            monster_stunned = False
                        else:
                            incoming = m.attack()
                            real, dodged = player.receive_attack(incoming)
                            if dodged: log.append(f"{m.name}의 공격! 회피 성공!")
                            else:      log.append(f"{m.name}의 공격! {incoming} → 방어/가드 후 {real} 데미지!")
                            if player.hp <= 0:
                                log.append("💀 패배했습니다..."); pygame.display.flip(); pygame.time.delay(1200)
                                return "lose"

        clock.tick(30)
