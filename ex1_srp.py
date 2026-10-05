class Car:
    def move(self):
        self.position += self.speed

class RaceLogger:
    def __init__(self):
        self.entries = []

    def record(self, tick, racers):
        for r in racers:
            self.entries.append((tick, r.name, r.position))

    def save(self, path):
        with open(path, "w") as f:
            for tick, name, pos in self.entries:
                f.write(f"{tick},{name},{pos}\n")

logger = RaceLogger()
track.run(racers, on_tick=logger.record)
logger.save("log.txt")