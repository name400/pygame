# battle.py (REPLACE)
import pygame, random, sys
from monster import Monster

# --- 속성 상성 테이블 ---
# 번개 → 물/기계, 대지 → 화산/바위(=fire/earth), 독 → 야만/인간형/거인
ELEM_EFFECTIVE = {
    "lightning": {"water", "machine"},
    "earth":     {"fire", "earth"},
    "poison":    {"beast", "human", "giant"},
}

# === 난이도/보상 스케일 (최종) ===
def _scale_stat(base, run_count, stage, boss=False, kind="other"):
    """
    kind: "hp" | "atk" | "exp" | "gold" | "other"
    - HP/ATK: 현재 비율 유지(너가 OK라 한 구간)
    - EXP/GOLD: 후반부 급증 억제
    - Boss: 더 약하게 (HP/ATK 1.15배, 보상은 거의 추가 없음)
    """
    stage_idx = max(0, stage - 1)
    run_idx   = min(run_count, 10)

    if kind in ("hp", "atk", "other"):
        stage_mult = 1.0 + 0.04 * stage_idx
        run_mult   = 1.0 + 0.02 * run_idx
    elif kind == "exp":
        early = min(stage_idx, 9)
        late  = max(stage_idx - 9, 0)
        stage_mult = (1.0 + 0.02 * early) * (1.0 + 0.005 * late)
        run_mult   = 1.0 + 0.01 * run_idx
    elif kind == "gold":
        early = min(stage_idx, 9)
        late  = max(stage_idx - 9, 0)
        stage_mult = (1.0 + 0.015 * early) * (1.0 + 0.005 * late)
        run_mult   = 1.0 + 0.01 * run_idx

    val = int(base * stage_mult * run_mult)

    if kind == "exp":
        val = int(val * 0.90)   # EXP 전체 10% 하향
    if kind == "gold":
        val = int(val * 0.85)   # GOLD 전체 15% 하향

    if boss:
        if kind in ("hp", "atk"):
            val = int(val * 1.15)   # 보스 더 약하게
        elif kind in ("exp", "gold"):
            val = int(val * 1.05)   # 보상 거의 안 올림

    return max(1, val)

# --- 스킬 메뉴 ---
def _open_skill_menu(screen, font, player):
    skills = player.skill_display_list()
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
                    if player.can_use(sid): return sid
                elif event.key == pygame.K_ESCAPE: return None

# ---- 룬 보너스 / 속성 보정 ----
def _get_rune_bonus_pct(player):
    r = player.equipment.get("rune")
    return int(r.get("element_bonus", 0)) if r else 0

def _apply_element_modifiers(player, region, monster, base_dmg, log):
    dmg = base_dmg
    if dmg <= 0: return 0

    # 1) 지역 약점 +25%
    if region.weakness == player.element:
        add = int(dmg * 0.25); dmg += add
        log.append(f"🔥 지역 약점 적중! 추가 피해 +{add} (+25%)")

    # 2) 속성 상성 +20%
    eff = ELEM_EFFECTIVE.get(player.element, set())
    if monster.element in eff:
        add = int(dmg * 0.20); dmg += add
        log.append(f"⚡ 속성 상성! ({player.element}→{monster.element}) +{add} (+20%)")

    # 3) 룬 자체 보너스
    rune_pct = _get_rune_bonus_pct(player)
    if rune_pct:
        add = int(dmg * (rune_pct / 100.0)); dmg += add
        log.append(f"🔷 룬 보너스 +{rune_pct}%: +{add}")

    return max(0, dmg)

# ---- 보스 드랍 ----
def _stage_mult(stage):
    # 보스 드랍 스케일 완만 (5스테이지 단위, +8%)
    boss_idx = max(1, stage // 5)
    return 1.0 + 0.08 * (boss_idx - 1)

def _scale_drop(item, mult):
    it = item.copy()
    if "atk" in it: it["atk"] = max(1, int(it["atk"] * mult))
    if "def" in it: it["def"] = max(1, int(it["def"] * mult))
    if "hp"  in it: it["hp"]  = max(1, int(it["hp"]  * mult))
    if it.get("type") == "rune":
        base = it.get("element_bonus", 20)
        it["element_bonus"] = int(base * mult)
    return it

def _boss_drop_for_region(region, stage):
    m = _stage_mult(stage)
    pool_map = {
        "숲": [
            {"type":"weapon","slot":"weapon","name":"숲의 대검","atk":12,"desc":"+ATK"},
            {"type":"accessory","slot":"accessory","name":"숲의 펜던트","hp":30,"desc":"+MaxHP"},
            {"type":"rune","slot":"rune","name":"숲의 심장 룬","element":region.weakness,"element_bonus":20,"desc":"지역의 정수"},
        ],
        "사막": [
            {"type":"weapon","slot":"weapon","name":"사막의 커틀러스","atk":13,"desc":"+ATK"},
            {"type":"accessory","slot":"accessory","name":"모래의 문장","hp":28,"desc":"+MaxHP"},
            {"type":"rune","slot":"rune","name":"사막의 폭풍 룬","element":region.weakness,"element_bonus":20,"desc":"지역의 정수"},
        ],
        "설원": [
            {"type":"weapon","slot":"weapon","name":"빙결 도끼","atk":14,"desc":"+ATK"},
            {"type":"accessory","slot":"accessory","name":"서리의 인장","hp":32,"desc":"+MaxHP"},
            {"type":"rune","slot":"rune","name":"서리의 룬","element":region.weakness,"element_bonus":20,"desc":"지역의 정수"},
        ],
        "늪지": [
            {"type":"weapon","slot":"weapon","name":"늪의 미늘창","atk":13,"desc":"+ATK"},
            {"type":"accessory","slot":"accessory","name":"맹독의 인장","hp":29,"desc":"+MaxHP"},
            {"type":"rune","slot":"rune","name":"늪의 맹독 룬","element":region.weakness,"element_bonus":20,"desc":"지역의 정수"},
        ],
        "화산": [
            {"type":"weapon","slot":"weapon","name":"용암 검","atk":15,"desc":"+ATK"},
            {"type":"accessory","slot":"accessory","name":"화염의 문장","hp":35,"desc":"+MaxHP"},
            {"type":"rune","slot":"rune","name":"화염의 핵 룬","element":region.weakness,"element_bonus":20,"desc":"지역의 정수"},
        ],
    }
    pool = pool_map.get(region.name, [
        {"type":"weapon","slot":"weapon","name":"미지의 검","atk":12,"desc":"+ATK"},
        {"type":"accessory","slot":"accessory","name":"미지의 문장","hp":30,"desc":"+MaxHP"},
        {"type":"rune","slot":"rune","name":"미지의 룬","element":region.weakness,"element_bonus":20,"desc":"지역의 정수"},
    ])
    chosen = random.choice(pool)
    return _scale_drop(chosen, m)

def start_battle(screen, font, player, region, run_count, stage, flee_rate, boss=False):
    tpl = random.choice(region.bosses if boss else region.monsters)
    m = Monster(
        name=("Boss " if boss else "") + tpl["name"],
        hp=_scale_stat(tpl["hp"],  run_count, stage, boss, kind="hp"),
        atk=_scale_stat(tpl["atk"], run_count, stage, boss, kind="atk"),
        exp=_scale_stat(tpl["exp"], run_count, stage, boss, kind="exp"),
        gold=_scale_stat(tpl["gold"], run_count, stage, boss, kind="gold"),
        element=tpl.get("element","neutral")
    )

    log = [f"{region.name}의 {m.name}이(가) 나타났다! (적 속성:{m.element}, 내 속성:{player.element})"]
    clock = pygame.time.Clock()
    running = True
    monster_stunned = False

    while running:
        screen.fill((20,20,20))
        info1 = f"적: {m.name} HP {m.hp} | 플레이어 HP {player.hp}/{player.max_hp}"
        info2 = "[1] 공격  [2] 도망  [3] 스킬"
        screen.blit(font.render(info1, True, (255,255,0)), (60, 80))
        screen.blit(font.render(info2, True, (200,200,200)), (60, 120))

        for i, text in enumerate(log[-9:]):
            screen.blit(font.render(text, True, (255,255,255)), (60, 420 + i*26))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1:
                    player.apply_debuffs_each_round(lambda t: log.append(t))
                    if player.hp <= 0:
                        log.append("💀 디버프로 쓰러졌다..."); pygame.display.flip(); pygame.time.delay(1200)
                        return "lose"

                    raw = player.attack()
                    dmg = _apply_element_modifiers(player, region, m, raw, log)
                    m.hp -= dmg
                    log.append(f"당신의 공격! {m.name}에게 {raw} → 최종 {dmg} 데미지!")

                    if m.hp <= 0:
                        bonus = 15 if boss else 0    # 보스 골드 보너스 축소
                        log.append(f"{m.name} 처치! EXP +{m.exp}, GOLD +{m.gold + bonus}")
                        player.gain_exp(m.exp, m.gold + bonus)

                        if boss:
                            drop = _boss_drop_for_region(region, stage)
                            player.add_item(drop)
                            log.append(f"🎁 보스 드랍 획득: {drop['name']}")

                        pygame.display.flip(); pygame.time.delay(900)
                        player.tick_debuffs_after_battle()
                        return "win"

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
                    sid = _open_skill_menu(screen, font, player)
                    if sid:
                        player.apply_debuffs_each_round(lambda t: log.append(t))
                        if player.hp <= 0:
                            log.append("💀 디버프로 쓰러졌다..."); pygame.display.flip(); pygame.time.delay(1200)
                            return "lose"

                        raw_dmg, stun, extra = player.cast_skill(sid, m)
                        for t in extra: log.append(t)

                        if raw_dmg > 0:
                            dmg = _apply_element_modifiers(player, region, m, raw_dmg, log)
                            m.hp -= dmg
                            log.append(f"스킬 피해! {m.name}에게 {raw_dmg} → 최종 {dmg} 데미지!")
                        if stun:
                            monster_stunned = True

                        if m.hp <= 0:
                            bonus = 15 if boss else 0
                            log.append(f"{m.name} 처치! EXP +{m.exp}, GOLD +{m.gold + bonus}")
                            player.gain_exp(m.exp, m.gold + bonus)

                            if boss:
                                drop = _boss_drop_for_region(region, stage)
                                player.add_item(drop)
                                log.append(f"🎁 보스 드랍 획득: {drop['name']}")

                            pygame.display.flip(); pygame.time.delay(900)
                            player.tick_debuffs_after_battle()
                            return "win"

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
