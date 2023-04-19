import pytest
from sneaker_seeker.common_types.physical_specs import PhysicalSpecs
from sneaker_seeker.common_types.point2d import Point2D
from sneaker_seeker.common_types.speed_vec import SpeedVec
from sneaker_seeker.game_obj.player import Player


@pytest.fixture
def player():
    return Player(
        physical_specs={"cruise_speed": 50, "max_speed": 100, "max_speed_time": 20},
        point={"x": 0, "y": 0},
        observation_direction=0,
        los=1000,
        fov=60,
        speed={"_magnitude": 10, "_direction": 0}
    )


def test_player_creation(player):
    assert player.id > 0
    assert isinstance(player.physical_specs, PhysicalSpecs)
    assert isinstance(player.location, Point2D)
    assert isinstance(player.speed, SpeedVec)
    assert player.speed.magnitude == 10
    assert player.speed.direction == 0


def test_player_move(player):
    player.move(1)
    assert player.location.x == 10
    assert player.location.y == 0