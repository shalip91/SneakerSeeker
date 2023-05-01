from pathlib import Path
from typing import Union, Tuple, Optional

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from sneaker_seeker.game_obj.player import Player
from sneaker_seeker.visualization.visualizer import Visualizer
from sneaker_seeker.game_obj.sneaker import Sneaker
from sneaker_seeker.game_obj.seeker import Seeker
from sneaker_seeker.game_obj.roi import ROI
from sneaker_seeker.game_obj.dkiz import DKIZ


def circle_dkiz_updater(dkiz_patch: matplotlib.patches, dkiz: DKIZ) -> None:
    dkiz_patch[0].set_center((dkiz.location.x, dkiz.location.y))
    dkiz_patch[1].set_data([dkiz.l_frontal_line.location.x, dkiz.r_frontal_line.location.x],
                           [dkiz.l_frontal_line.location.y, dkiz.r_frontal_line.location.y])


def circle_dkiz_creator(ax: plt.Axes, dkiz: DKIZ, appearance: dict) -> Tuple[matplotlib.patches.Circle, plt.Line2D]:
    circle = ax.add_patch(matplotlib.patches.Circle(xy=(dkiz.location.x, dkiz.location.y),
                                                    **dkiz.dimensions, **appearance["inner_circle"]))
    line_x_data = [dkiz.l_frontal_line.location.x, dkiz.r_frontal_line.location.x]
    line_y_data = [dkiz.l_frontal_line.location.y, dkiz.r_frontal_line.location.y]
    line: list[plt.Line2D] = ax.plot(line_x_data, line_y_data, **appearance["frontal_line"])
    return circle, line[0]


PlayerCanvasObj = Tuple[matplotlib.patches.Wedge, plt.Line2D, plt.Line2D]
DKIZCanvasObj = Tuple[Union[matplotlib.patches.Circle, any], plt.Line2D]
ROICanvasObj = matplotlib.patches.Rectangle
CanvasObj = Union[PlayerCanvasObj, DKIZCanvasObj, ROICanvasObj]


class Canvas(Visualizer):
    __dkiz_shape_creator: dict[str, callable] = {"circle": circle_dkiz_creator}
    __dkiz_shape_updater: dict[str, callable] = {"circle": circle_dkiz_updater}

    def __init__(self, height: int, width: int, margin: int, name: str, x_label: str, y_label: str, fig_size: dict,
                 object_appearance: dict, frame_format: str = "jpg") -> None:
        self.height = height
        self.width = width
        self.fig, self.ax = self.__make_fig(**fig_size)
        self.margin = margin
        self.name = name
        self.frame_format = frame_format
        self.x_label = x_label
        self.y_label = y_label
        self.object_appearance: dict = object_appearance
        self.objects: dict[int, CanvasObj] = {}
        self.__init()

    @staticmethod
    def __make_fig(width: int, height: int) -> Union[any, plt.Axes]:
        fig = plt.figure(figsize=(width, height))
        return fig, fig.add_subplot(1, 1, 1)

    def __init(self) -> None:
        self.ax.cla()
        self.fig.suptitle(self.name)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.set_xlim([-self.margin, self.width + self.margin])
        self.ax.set_ylim([-self.margin, self.height + self.margin])
        self.ax.set_aspect("auto", adjustable="box", anchor="C")

    def save(self, path: Path) -> None:
        self.fig.savefig(f"{path}.{self.frame_format}",
                         format="jpeg" if self.frame_format == "jpg" else self.frame_format)

    def __make_player(self, player: Union[Sneaker, Seeker], appearance: dict) -> PlayerCanvasObj:
        wedge = self.ax.add_patch(
            matplotlib.patches.Wedge(center=(player.location.x, player.location.y), r=player.los,
                                     theta1=(player.observation_direction - player.fov / 2),
                                     theta2=(player.observation_direction + player.fov / 2),
                                     **appearance["wedge"]))
        triangle: list[plt.Line2D] = self.ax.plot(player.location.x, player.location.y,
                                                  marker=(3, 0, player.speed.angle - 90),  # directed triangle
                                                  **appearance["triangle"])
        line: list[plt.Line2D] = self.ax.plot(player.location.x, player.location.y,
                                              marker=(2, 0, player.speed.angle - 90),  # directed line
                                              **appearance["line"])
        return wedge, triangle[0], line[0]

    @staticmethod
    def __update_player(player_canvas_obj: PlayerCanvasObj, player: Union[Sneaker, Seeker], appearance: dict) -> None:
        player_canvas_obj[0].set_center((player.location.x, player.location.y))
        player_canvas_obj[0].set_theta1(player.observation_direction - player.fov / 2)
        player_canvas_obj[0].set_theta2(player.observation_direction + player.fov / 2)
        player_canvas_obj[0].set_facecolor(appearance["wedge"]["facecolor"])
        player_canvas_obj[0].set_alpha(appearance["wedge"]["alpha"])
        player_canvas_obj[1].set_data([player.location.x], [player.location.y])
        player_canvas_obj[1].set_marker((3, 0, player.speed.angle - 90))  # set triangle angle
        player_canvas_obj[1].set_color(appearance["triangle"]["color"])
        player_canvas_obj[1].set_alpha(appearance["triangle"]["alpha"])
        player_canvas_obj[2].set_data([player.location.x], [player.location.y])
        player_canvas_obj[2].set_marker((2, 0, player.speed.angle - 90))  # set line angle
        player_canvas_obj[2].set_color(appearance["line"]["color"])
        player_canvas_obj[2].set_alpha(appearance["line"]["alpha"])

    def __print_player_to_canvas(self, player_canvas_obj: PlayerCanvasObj, player: Union[Sneaker, Seeker],
                                 appearance: dict) -> None:
        if player_canvas_obj is None:
            self.objects[player.id] = self.__make_player(player, appearance)
        else:
            Canvas.__update_player(player_canvas_obj=player_canvas_obj, player=player, appearance=appearance)

    def make_seeker(self, seeker: Seeker) -> None:
        seeker_canvas_obj: Optional[PlayerCanvasObj] = self.objects.get(seeker.id)
        appearance = self.object_appearance["seeker"]
        self.__print_player_to_canvas(seeker_canvas_obj, seeker, appearance)

    def make_sneaker(self, sneaker: Sneaker) -> None:
        sneaker_canvas_obj: Optional[PlayerCanvasObj] = self.objects.get(sneaker.id)
        appearance = self.object_appearance["sneaker"][sneaker.state.lower()]
        self.__print_player_to_canvas(sneaker_canvas_obj, sneaker, appearance)

    def make_ROI(self, roi: ROI) -> None:
        self.ax.add_patch(matplotlib.patches.Rectangle(xy=(roi.location.x, roi.location.y),
                                                       width=roi.width,
                                                       height=roi.height,
                                                       **self.object_appearance["roi"]))

    def make_DKIZ(self, dkiz: DKIZ) -> None:
        dkiz_canvas_obj: Union[matplotlib.patches.Circle, any] = self.objects.get(dkiz.id)
        if dkiz_canvas_obj is None:  # create new object
            self.objects[dkiz.id] = Canvas.__dkiz_shape_creator[dkiz.type](ax=self.ax, dkiz=dkiz,
                                                                           appearance=self.object_appearance["dkiz"])
        else:  # update existing object
            Canvas.__dkiz_shape_updater[dkiz.type](dkiz_canvas_obj, dkiz)

    def time_stamp(self, curr_time) -> None:
        self.ax.set_title(f"time[sec]: {curr_time / 1000:.1f}")

    def remove_player(self, player: Player) -> None:
        player_canvas_obj: Optional[PlayerCanvasObj] = self.objects.get(player.id)
        player_canvas_obj[0].remove()
        player_canvas_obj[1].remove()
        player_canvas_obj[2].remove()




