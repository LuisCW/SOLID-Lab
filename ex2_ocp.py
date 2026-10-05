import random

class Motorcycle(Vehicle):
    def move(self):
        self.position += random.randint(1, 8)   # rápida pero errática

class Bicycle(Vehicle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticks = 0

    def move(self):
        self.ticks += 1
        self.position += max(1, 4 - self.ticks // 5)   