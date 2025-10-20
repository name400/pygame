import random

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.hp = 100
        self.max_hp = 100
        self.atk = 10
        self.exp = 0
        self.gold = 0
        self.level = 1

    def move(self, keys):
        if keys[97] or keys[276]:  # a or ←
            self.x -= self.speed
        if keys[100] or keys[275]:  # d or →
            self.x += self.speed
        if keys[119] or keys[273]:  # w or ↑
            self.y -= self.speed
        if keys[115] or keys[274]:  # s or ↓
            self.y += self.speed

    def attack(self):
        return random.randint(self.atk - 3, self.atk + 3)

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)

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
        print(f"🎉 레벨업! Lv.{self.level}")
