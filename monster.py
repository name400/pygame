import random

class Monster:
    def __init__(self, name, hp, atk, exp, gold, element="neutral"):
        self.name = name
        self.hp = hp
        self.atk = atk
        self.exp = exp
        self.gold = gold
        self.element = element

    def attack(self):
        return random.randint(max(1, self.atk - 2), self.atk + 2)
