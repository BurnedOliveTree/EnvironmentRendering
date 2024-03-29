import debug_tools
from terrain import Terrain
import constants
import json
import argparse
import export_tools


if __name__ == "__main__":
    # get input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_path", default=constants.DEFAULT_CONFIG_PATH, type=str)
    parser.add_argument("--resolution", required=False, type=int, nargs="+")
    parser.add_argument("--octave_multiplier", required=False, type=float, nargs="+")
    parser.add_argument("--output_path", default=constants.DEFAULT_OUTPUT_PATH, type=str)
    parser.add_argument("--seed", default=constants.DEFAULT_SEED, type=int)
    parser.add_argument('--grid', dest='grid', action='store_true')
    parser.add_argument('--no_grid', dest='grid', action='store_false')
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.set_defaults(debug=False)
    parser.set_defaults(grid=False)
    args = parser.parse_args()

    with open(args.config_path) as json_file:
        world_conf = json.load(json_file)

    terrain = Terrain(config=world_conf, seed=args.seed, shape=args.resolution,
                      octave_multiplier=args.octave_multiplier)
    color_map = terrain.get_color_map()
    height_map = terrain.height_map
    moisture_map = terrain.moisture_map
    export_tools.export_to_file(height_map, "heightmap.csv")
    export_tools.export_to_file(moisture_map, "moisturemap.csv")

    img = export_tools.create_image_from_color_map(color_map, args.grid)
    img.save(args.output_path)


    if args.debug:
        debug_tools.plot2d(terrain.height_map)
        debug_tools.plot2d(terrain.moisture_map, cmap='gray')
