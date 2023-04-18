from abc import ABC, abstractmethod
from sneaker_seeker.game_obj.player import Player


class PathPlanner(ABC):
    @abstractmethod
    def set_path(self, player: Player):
        pass

