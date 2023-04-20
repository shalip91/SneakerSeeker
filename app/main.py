import subprocess

from sneaker_seeker import utils
from sneaker_seeker.path_planner.path_planner_factory import PathPlannerFactory
from sneaker_seeker.game_obj.seeker import Seeker
from sneaker_seeker.game_obj.sneaker import Sneaker
from sneaker_seeker.game_obj.DKIZ import DKIZ
from sneaker_seeker.game_obj.ROI import ROI
from sneaker_seeker.visualization.canvas import Canvas
from sneaker_seeker.simulation.simulator import Simulator

SCENARIO_NAME = "scenario01"
SAVE_FRAME_EVERY_N_STEP = 10
VID_SPEEDUP_FACTOR = 10
SCALE_WORLD_FACTOR = 1


def scale_world(scenario: dict, scale_factor):
    for name in ["world", "ROI"]:
        for k in scenario[name].keys():
            scenario[name][k] *= scale_factor
    for name, sub_name in [["canvas", "fig_size"]]:
        for k in scenario[name][sub_name].keys():
            scenario[name][sub_name][k] *= scale_factor


@utils.my_timer
# @utils.my_profiler
def main() -> None:
    config = utils.read_json("config.json")
    scenario = utils.read_json(f"scenarios/{SCENARIO_NAME}.json")
    out_path = utils.make_output_path(outputdir=config["outputdir"], scenario_name=SCENARIO_NAME,
                                      empty_output_path=True)

    scale_world(scenario, SCALE_WORLD_FACTOR)

    game_objects = {
        "roi": ROI(**scenario["ROI"]),  # Region Of Interest of the game of seeking
        "dkiz": DKIZ(**scenario["sneaker"]["deployment"]["DKIZ"]),  # this the Dynamic Keep-In Zone for the Sneakers.
        "visualizer": Canvas(frame_format=config["frame_format"], **scenario["world"], **scenario["canvas"]),
        "sneakers": [Sneaker(**scenario["sneaker"]["common_data"]) for _ in range(scenario["sneaker"]["num"])],
        "seekers": [Seeker(**scenario["seeker"]["common_data"]) for _ in range(scenario["seeker"]["num"])]
    }

    path_planners = {Seeker: PathPlannerFactory.create(scenario["seeker"]["path_planner"], **game_objects),
                     Sneaker: PathPlannerFactory.create(scenario["sneaker"]["path_planner"], **game_objects)}

    simulator = Simulator(out_path=out_path, scenario=scenario, path_planners=path_planners, **game_objects)
    simulator.run(save_frame_every_n_step=SAVE_FRAME_EVERY_N_STEP)

    utils.make_video(frames_dir=out_path, frames_format=config["frame_format"], video_name=f"{SCENARIO_NAME}.avi",
                     fps=(VID_SPEEDUP_FACTOR * utils.real_time_fps(scenario['time_step_ms'], SAVE_FRAME_EVERY_N_STEP)))


if __name__ == "__main__":
    main()
    video_file = f"./{SCENARIO_NAME}.avi"
    subprocess.run(['start', video_file], shell=True)
