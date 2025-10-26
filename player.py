# player.py (REPLACE)
import random

class Player:
    def __init__(self, x, y):
        self.x = x; self.y = y; self.speed = 5

        # --- 기본 능력치 ---
        self.max_hp = 100; self.hp = 100
        self.atk = 15; self.defence = 5
        self.exp = 0; self.gold = 0; self.level = 1

        # --- 상태/속성 ---
        self.debuffs = {}             # {"poison":3,"weaken":2}
        self.buffs = {}               # {"atk_up":(turns, value), "guard":(turns, value), "evasion":(turns, chance)}
        self.element = "physical"     # 무기/룬 속성

        # --- 인벤토리/장비 ---
        self.inventory = []
        self.equipment = {"weapon":None,"armor":None,"accessory":None}

        # --- 전직/스킬 ---
        self.job = None               # 'Warrior'/'Rogue'/'Mage'/'Tanker'
        self.skills = []              # 습득한 스킬 id 리스트
        self.skill_cooldowns = {}     # {skill_id:remain_turns}
        self.pending_job = False      # 레벨 10 도달 시 True -> job_ui.choose_job 호출
        self.pending_first_skill = False  # 전직 직후 첫 스킬 선택 필요

        # 직업 한글 표시
        self.job_name_map = {"Warrior":"전사","Rogue":"도적","Mage":"마법사","Tanker":"탱커"}

        # 직업별 스킬(스킬 id, 표시명, 설명) - 3개
        self.skill_progression = {
            "Warrior":[
                ("power_slash","파워 슬래시","단일 강타 (ATK ×1.5) [쿨2턴]"),
                ("battle_cry","전장의 포효","3턴 동안 공격력 +20% [쿨4턴]"),
                ("rage_burst","분노 폭발","체력이 낮을수록 데미지 ↑ (최대 2.0배) [쿨4턴]"),
            ],
            "Rogue":[
                ("shadow_slash","그림자 베기","2연속 공격 (각 70%) [쿨2턴]"),
                ("smoke_bomb","연막탄","2턴 동안 회피 50% [쿨5턴]"),
                ("backstab","급소 찌르기","치명 일격 (ATK ×2.2) [쿨4턴]"),
            ],
            "Mage":[
                ("flame_bolt","플레임 볼트","28~42 화염 피해 (고정) [쿨2턴]"),
                ("ice_lance","아이스 랜스","ATK ×1.1 + 방어무시 2 [쿨3턴]"),
                ("mana_shield","마나 실드","2턴 동안 가드 50% [쿨5턴]"),
            ],
            "Tanker":[
                ("iron_wall","철벽 방어","2턴 동안 가드 50% [쿨4턴]"),
                ("shield_bash","방패 가격","ATK ×1.0 + 기절(1턴) [쿨4턴]"),
                ("guardian_oath","수호의 맹세","즉시 HP 20% 회복 [쿨5턴]"),
            ],
        }

        # 스킬별 쿨다운(턴)
        self.skill_cd_map = {
            "power_slash":2, "battle_cry":4, "rage_burst":4,
            "shadow_slash":2, "smoke_bomb":5, "backstab":4,
            "flame_bolt":2, "ice_lance":3, "mana_shield":5,
            "iron_wall":4, "shield_bash":4, "guardian_oath":5,
        }

    # ------------ 이동 ------------
    def move(self, keys):
        if keys[97] or keys[276]: self.x -= self.speed  # a/←
        if keys[100] or keys[275]: self.x += self.speed  # d/→
        if keys[119] or keys[273]: self.y -= self.speed  # w/↑
        if keys[115] or keys[274]: self.y += self.speed  # s/↓

    # ------------ 전투 기초 ------------
    def effective_atk(self):
        base = self.atk
        if self.debuffs.get("weaken", 0) > 0: base -= 3
        atk_up = self.buffs.get("atk_up")   # (turns, +ratio)
        if atk_up: base = int(base * (1.0 + atk_up[1]))
        return max(1, base)

    def attack(self):
        a = self.effective_atk()
        return random.randint(max(1, a - 3), a + 3)

    def receive_attack(self, incoming):
        # 회피
        ev = self.buffs.get("evasion")  # (turns, chance)
        if ev and random.random() < ev[1]:
            return 0, True  # 피해 0, 회피 성공
        # 방어
        real = max(1, incoming - self.defence)
        guard = self.buffs.get("guard")  # (turns, ratio)
        if guard:
            real = max(1, int(real * (1.0 - guard[1])))
        self.hp = max(0, self.hp - real)
        return real, False

    def take_damage(self, incoming):
        # 이전 코드 호환용 (회피 미적용)
        real = max(1, incoming - self.defence)
        self.hp = max(0, self.hp - real)
        return real

    # ------------ 레벨/경험 ------------
    def gain_exp(self, exp, gold):
        self.exp += exp; self.gold += gold
        while self.exp >= 100:
            self.exp -= 100
            self.level_up()

    def level_up(self):
        self.level += 1
        self.atk += 3; self.defence += 1
        self.max_hp += 20; self.hp = self.max_hp
        print(f"🎉 레벨업! Lv.{self.level}")

        # 전직 트리거
        if self.level == 10 and self.job is None:
            self.pending_job = True
            self.pending_first_skill = True  # 전직 직후 첫 스킬 선택 대기

        # 이후 5레벨마다 스킬 자동 추가 (직업이 있고, 아직 배우지 않은 스킬이 있으면)
        if self.job and self.level in (15, 20, 25, 30, 35, 40):
            self.learn_next_skill_auto()

    # ------------ 버프/디버프 턴 처리 ------------
    def apply_debuffs_each_round(self, log_append):
        if self.debuffs.get("poison", 0) > 0:
            self.hp = max(0, self.hp - 5)
            self.debuffs["poison"] -= 1
            log_append("🧪 중독 피해로 5 데미지!")

        # 버프 턴 감소
        expired = []
        for k, v in self.buffs.items():
            turns = v[0] - 1
            self.buffs[k] = (turns, v[1])
            if turns <= 0: expired.append(k)
        for k in expired:
            del self.buffs[k]
            if k == "atk_up": log_append("버프 종료: 공격력 증가 효과가 사라졌다.")
            if k == "guard":  log_append("버프 종료: 가드 효과가 사라졌다.")
            if k == "evasion":log_append("버프 종료: 회피 효과가 사라졌다.")

        # 스킬 쿨다운 감소
        for sid in list(self.skill_cooldowns.keys()):
            if self.skill_cooldowns[sid] > 0:
                self.skill_cooldowns[sid] -= 1

    def tick_debuffs_after_battle(self):
        pass

    def add_debuff(self, name, turns):
        self.debuffs[name] = self.debuffs.get(name, 0) + turns

    # ------------ 전직/스킬 ------------
    def job_kr(self):
        return self.job_name_map.get(self.job, "-")

    def unlock_job(self, code):
        self.job = code
        # 직업 스탯 보정
        if code == "Warrior":
            self.max_hp += 40; self.hp = min(self.max_hp, self.hp + 40)
            self.atk += 5
        elif code == "Rogue":
            self.max_hp += 10; self.hp = min(self.max_hp, self.hp + 10)
            self.atk += 8
        elif code == "Mage":
            self.max_hp -= 10; self.hp = min(self.max_hp, self.hp)
            self.atk += 12
        elif code == "Tanker":
            self.max_hp += 80; self.hp = min(self.max_hp, self.hp + 80)
            self.atk += 2

        self.pending_job = False
        print(f"🛡 전직 완료: {self.job_kr()}")

    def learn_skill(self, skill_id):
        if skill_id not in self.skills:
            self.skills.append(skill_id)
            self.skill_cooldowns.setdefault(skill_id, 0)
            print(f"✨ 스킬 습득: {skill_id}")

    def learn_next_skill_auto(self):
        if not self.job: return
        pool = [sid for (sid,_,_) in self.skill_progression[self.job]]
        remaining = [sid for sid in pool if sid not in self.skills]
        if remaining:
            self.learn_skill(remaining[0])  # 남은 것 중 앞에서부터 1개 자동 습득

    # 배틀에서 사용할 수 있는 스킬 목록(이름/쿨/사용가능)
    def skill_display_list(self):
        out = []
        if not self.job: return out
        # 보유 스킬만
        name_map = {sid:name for (sid,name,_) in self.skill_progression[self.job]}
        for sid in self.skills:
            cd = self.skill_cooldowns.get(sid, 0)
            out.append((sid, name_map.get(sid, sid), cd))
        return out

    def can_use(self, sid):
        return sid in self.skills and self.skill_cooldowns.get(sid, 0) == 0

    def put_cooldown(self, sid):
        self.skill_cooldowns[sid] = self.skill_cd_map.get(sid, 1)

    # ------------ 스킬 효과 ------------
    # 반환값: (damage_dealt, monster_stunned, extra_log_list)
    def cast_skill(self, sid, monster):
        logs = []
        dmg = 0
        stun = False

        if sid == "power_slash":
            base = self.effective_atk()
            dmg = int(base * 1.5) + random.randint(-2, 2)
            logs.append("⚔ 파워 슬래시!")
            self.put_cooldown(sid)

        elif sid == "battle_cry":
            self.buffs["atk_up"] = (3, 0.20)  # 3턴 +20%
            logs.append("📣 전장의 포효! 3턴 동안 공격력 +20%")
            self.put_cooldown(sid)

        elif sid == "rage_burst":
            ratio = 1.0 + (1.0 - (self.hp / max(1, self.max_hp)))  # HP가 낮을수록 1.0~2.0
            base = self.effective_atk()
            dmg = int(base * ratio)
            logs.append(f"🔥 분노 폭발! (배수 {ratio:.2f}배)")
            self.put_cooldown(sid)

        elif sid == "shadow_slash":
            base = self.effective_atk()
            hit1 = int(base * 0.7) + random.randint(-2, 2)
            hit2 = int(base * 0.7) + random.randint(-2, 2)
            dmg = max(1, hit1) + max(1, hit2)
            logs.append("🗡 그림자 베기! 2연타 적중")
            self.put_cooldown(sid)

        elif sid == "smoke_bomb":
            self.buffs["evasion"] = (2, 0.5)  # 2턴 50% 회피
            logs.append("💨 연막탄! 2턴 동안 회피 50%")
            self.put_cooldown(sid)

        elif sid == "backstab":
            base = self.effective_atk()
            dmg = int(base * 2.2) + random.randint(-2, 2)
            logs.append("🗡 급소 찌르기! 치명 일격")
            self.put_cooldown(sid)

        elif sid == "flame_bolt":
            dmg = random.randint(28, 42)  # 고정 화염
            logs.append("🔥 플레임 볼트!")
            self.put_cooldown(sid)

        elif sid == "ice_lance":
            base = self.effective_atk()
            dmg = int(base * 1.1) + 2   # 방어무시 2만큼 보정
            logs.append("❄ 아이스 랜스! (방어무시+2)")
            self.put_cooldown(sid)

        elif sid == "mana_shield":
            self.buffs["guard"] = (2, 0.5)  # 50% 경감
            logs.append("🔷 마나 실드! 2턴 동안 받는 피해 50% 감소")
            self.put_cooldown(sid)

        elif sid == "iron_wall":
            self.buffs["guard"] = (2, 0.5)
            logs.append("🛡 철벽 방어! 2턴 동안 받는 피해 50% 감소")
            self.put_cooldown(sid)

        elif sid == "shield_bash":
            base = self.effective_atk()
            dmg = int(base * 1.0) + random.randint(-2, 2)
            stun = True
            logs.append("🛡 방패 가격! (기절 1턴)")
            self.put_cooldown(sid)

        elif sid == "guardian_oath":
            heal = max(1, int(self.max_hp * 0.2))
            self.hp = min(self.max_hp, self.hp + heal)
            logs.append(f"✨ 수호의 맹세! HP {heal} 회복")
            self.put_cooldown(sid)

        else:
            logs.append("…(알 수 없는 스킬)")
        return max(0, dmg), stun, logs

    # -------- 인벤토리/장비 (기존 호환) --------
    def add_item(self, item: dict):
        self.inventory.append(item)

    def use_consumable(self, idx, log_append=None):
        if idx < 0 or idx >= len(self.inventory): return
        item = self.inventory[idx]
        if item.get("type") != "consumable": return
        heal = item.get("heal", 0)
        self.hp = min(self.max_hp, self.hp + heal)
        if log_append: log_append(f"🧴 {item['name']} 사용! HP +{heal}")
        self.inventory.pop(idx)

    def equip_item(self, idx, log_append=None):
        if idx < 0 or idx >= len(self.inventory): return
        item = self.inventory[idx]
        if item.get("type") not in ("weapon","armor","accessory"): return
        slot = item.get("slot")
        if self.equipment.get(slot):
            self.unequip(slot, log_append)
        if "atk" in item: self.atk += item["atk"]
        if "def" in item: self.defence += item["def"]
        if "hp"  in item:
            self.max_hp += item["hp"]; self.hp = min(self.max_hp, self.hp)
        if item.get("element"): self.element = item["element"]
        self.equipment[slot] = item
        if log_append: log_append(f"🔧 장착: {item['name']}")
        self.inventory.pop(idx)

    def unequip(self, slot, log_append=None):
        eq = self.equipment.get(slot)
        if not eq: return
        if "atk" in eq: self.atk -= eq["atk"]
        if "def" in eq: self.defence -= eq["def"]
        if "hp"  in eq:
            self.max_hp -= eq["hp"]; self.hp = min(self.hp, self.max_hp)
        self.add_item(eq); self.equipment[slot] = None
        if log_append: log_append(f"🔧 해제: {eq['name']}")
