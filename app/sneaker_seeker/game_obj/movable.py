from sneaker_seeker.common_types import Location, SpeedVec


class Movable:

    def __init__(self, location: dict = None, speed: dict = None) -> None:
        self.location: Location = Location(**location) if location else Location()
        self.speed: SpeedVec = SpeedVec(**speed) if speed else SpeedVec()

    def move(self, dt: float):
        self.location.x += self.speed.vx * dt
        self.location.y += self.speed.vy * dt


