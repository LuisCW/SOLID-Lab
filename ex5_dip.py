class Race:
    def __init__(self, racers, track=None):
        self.racers = racers
        self.track = track or Track(length=30)

    def start(self):
        return self.track.run(self.racers)

class RocketSled(Vehicle): ...  

Race([SportsCar("Flash"), DeliveryVan("Eddie")]).start()
Race([RocketSled("Rocky"), Drone("Buzz")]).start()