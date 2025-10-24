import random

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5

        # 기본 능력치(장비 전/후 적용을 위해 base와 현재값 분리할 수도 있지만
        # 간단화를 위해 현재값만 사용하고 equip/unequip 시 가감)
        self.max_hp = 100
        self.hp = 100
        self.atk = 15
        self.defence = 5

        self.exp = 0
        self.gold = 0
        self.level = 1

        # 상태/버프
        self.debuffs = {}               # 예: {"poison": 3, "weaken": 2}
        self.element = "physical"       # 무기 속성(상점에서 룬 구매로 변경)

        # 인벤토리/장비
        self.inventory = []             # 아이템 dict들의 리스트
        self.equipment = {              # 장비 슬롯
            "weapon": None,
            "armor": None,
            "accessory": None
        }

    # 이동
    def move(self, keys):
        if keys[97] or keys[276]:  # a or ←
            self.x -= self.speed
        if keys[100] or keys[275]:  # d or →
            self.x += self.speed
        if keys[119] or keys[273]:  # w or ↑
            self.y -= self.speed
        if keys[115] or keys[274]:  # s or ↓
            self.y += self.speed

    # 실효 공격력(약화 디버프 고려)
    def effective_atk(self):
        base = self.atk
        if self.debuffs.get("weaken", 0) > 0:
            base -= 3
        return max(1, base)

    def attack(self):
        a = self.effective_atk()
        return random.randint(max(1, a - 3), a + 3)

    def take_damage(self, incoming):
        # 방어 적용, 최소 1
        real = max(1, incoming - self.defence)
        self.hp = max(0, self.hp - real)
        return real

    def gain_exp(self, exp, gold):
        self.exp += exp
        self.gold += gold
        if self.exp >= 100:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp = 0
        self.atk += 3
        self.max_hp += 20
        self.hp = self.max_hp
        self.defence += 1
        print(f"🎉 레벨업! Lv.{self.level}")

    # 라운드 시작 시 디버프 틱 처리
    def apply_debuffs_each_round(self, log_append):
        if self.debuffs.get("poison", 0) > 0:
            self.hp = max(0, self.hp - 5)
            self.debuffs["poison"] -= 1
            log_append("🧪 중독 피해로 5 데미지!")

    def tick_debuffs_after_battle(self):
        # 전투 단위 유지 디버프가 있으면 여기서 감소시키는 로직 추가 가능
        pass

    def add_debuff(self, name, turns):
        self.debuffs[name] = self.debuffs.get(name, 0) + turns

    # -------- 인벤토리/장비 기능 --------
    def add_item(self, item: dict):
        """item 예시:
        무기: {'name':'브론즈 소드','type':'weapon','slot':'weapon','atk':+5,'desc':'...'}
        방어구: {'name':'가죽 갑옷','type':'armor','slot':'armor','def':+3}
        장신구: {'name':'루비 반지','type':'accessory','slot':'accessory','hp':+20}
        소모품: {'name':'포션','type':'consumable','heal':50}
        """
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
        # 기존 장비가 있으면 먼저 해제
        if self.equipment.get(slot):
            self.unequip(slot, log_append)

        # 능력치 적용
        if "atk" in item: self.atk += item["atk"]
        if "def" in item: self.defence += item["def"]
        if "hp"  in item:
            self.max_hp += item["hp"]
            self.hp = min(self.max_hp, self.hp)

        if item.get("element"):
            self.element = item["element"]

        self.equipment[slot] = item
        if log_append: log_append(f"🔧 장착: {item['name']}")
        # 장착 시 인벤토리에서 제거
        self.inventory.pop(idx)

    def unequip(self, slot, log_append=None):
        eq = self.equipment.get(slot)
        if not eq: return
        # 능력치 롤백
        if "atk" in eq: self.atk -= eq["atk"]
        if "def" in eq: self.defence -= eq["def"]
        if "hp"  in eq:
            self.max_hp -= eq["hp"]
            self.hp = min(self.hp, self.max_hp)

        # 속성 롤백은 단순화(무기 해제해도 기존 속성 유지)
        self.add_item(eq)
        self.equipment[slot] = None
        if log_append: log_append(f"🔧 해제: {eq['name']}")
