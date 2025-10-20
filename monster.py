import random

class Monster:
    def __init__(self, name, hp, atk, exp, gold):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.exp = exp
        self.gold = gold

    def attack(self):
        return random.randint(self.atk - 2, self.atk + 2)
