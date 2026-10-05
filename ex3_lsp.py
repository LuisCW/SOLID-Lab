class UnreliableCar(Vehicle):
    def move(self):
        if random.random() < 0.3:
            return            
        self.position += 5