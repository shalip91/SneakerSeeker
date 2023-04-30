import random

from sneaker_seeker.path_planner.path_planner import PathPlanner
from sneaker_seeker.game_obj.roi import ROI
from sneaker_seeker.game_obj.player import Player
from sneaker_seeker.common_types.vec2d import Vec2D
from sneaker_seeker.utilities import utils


class PathPlannerStraightLine(PathPlanner):
    def __init__(self, roi: ROI, **_ignore) -> None:
        self.roi = roi
        self.tracked_players = {}

    def set_path(self, player: Player) -> None:
        # set the player's speed only once using tracked_players dict.
        if player.id not in self.tracked_players.keys():
            self.tracked_players[player.id] = player.id
            if player.speed.magnitude == 0:
                player.speed = Vec2D.from_polar(magnitude=player.physical_specs.max_speed,
                                                angle=random.uniform(0, 360))
                player.observation_direction = utils.calc_angle(y=player.speed.y, x=player.speed.x)
