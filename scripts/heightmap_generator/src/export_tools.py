from PIL import Image
import numpy as np
import constants


def create_image_from_color_map(color_map, grid=False):
    """A function that returns color_map converted to pillow image

    Keyword arguments:
    color_map -- 3d numpy color array (dtype=np.uint8)
    grid -- output image has a grid that separates pixels
    """
    # match x coordinate to horizontal photo dimension and y to vertical
    color_map = np.swapaxes(color_map, 0, 1)

    if grid:
        freq = constants.GRID_PIXEL_FREQUENCY
        old_shape = color_map.shape
        new_shape = freq * old_shape[0] + 1, freq * old_shape[1] + 1, old_shape[2]
        tmp_color_map = np.zeros(new_shape, dtype=np.uint8)
        for x in range(new_shape[0] - 1):
            for y in range(new_shape[1] - 1):
                if x % freq == 0 or y % freq == 0:
                    tmp_color_map[x][y] = constants.GRID_COLOR
                else:
                    tmp_color_map[x][y] = color_map[x // freq][y // freq]
        for x in range(new_shape[0]):
            tmp_color_map[x][new_shape[1] - 1] = constants.GRID_COLOR
        for y in range(new_shape[1]):
            tmp_color_map[new_shape[0] - 1][y] = constants.GRID_COLOR
        color_map = tmp_color_map
    img = Image.fromarray(color_map, 'RGB')
    return img


def export_to_file(export_map, path="./output.heightmap"):
    """
    map -- 2d numpy array
    path -- save path
    """

    np.savetxt(path, export_map, delimiter=",", fmt="%.7f")