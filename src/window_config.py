from pathlib import Path

from csv import reader
import moderngl
from moderngl_window import WindowConfig
from moderngl_window import geometry
from pyrr import Matrix44
import numpy as np

import config
from shaders.shader_utils import get_shaders


class HeightMapWindowConfig(WindowConfig):
    gl_version = config.GL_VERSION
    title = config.WINDOW_TITLE
    resource_dir = (Path(__file__).parent / 'resources').resolve()

    def __init__(self, **kwargs):
        super(HeightMapWindowConfig, self).__init__(**kwargs)

        shaders = get_shaders(self.argv.shader_path)
        self.program = self.ctx.program(vertex_shader=shaders[self.argv.shader_name].vertex_shader,
                                        fragment_shader=shaders[self.argv.shader_name].fragment_shader)
        self.read_height_map()
        self.generate()
        self.transform = self.program['transform']
        self.colour = self.program['colour']
    
    def read_height_map(self):
        result = []
        with open(HeightMapWindowConfig.resource_dir / (self.argv.map_name + '.csv')) as csv_file:
            csv_reader = reader(csv_file, delimiter=',')
            for row in csv_reader:
                result.append(np.array([float(value) for value in row]))
        self.height_map = np.array(result)
    
    def generate(self):
        vbo = self.ctx.buffer(self.height_map.astype('float32').tobytes())
        self.vao = self.ctx.simple_vertex_array(self.program, vbo, 'in_position')
        # fbo = self.ctx.simple_framebuffer((512, 512))

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('--shader_path', type=str, required=True, help='Path to the directory with shaders')
        parser.add_argument('--shader_name', type=str, required=True, help='Name of the shader to look for in the shader_path directory')
        parser.add_argument('--map_name', type=str, required=True, help='Name of the map to load')

    def render(self, time: float, frame_time: float):
        self.ctx.clear(0.8, 0.8, 0.8, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST)

        def calc_transform(trans_vec: tuple, scale_vec: tuple = (1.0, 1.0, 1.0), rotate_val: float = 0):
            projection = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 1000.0)
            look_at = Matrix44.look_at(
                (-20.0, -15.0, 5.0),
                (0.0, 0.0, 1.0),
                (0.0, 0.0, 1.0),
            )
            return projection * look_at\
                   * Matrix44.from_translation(trans_vec)\
                   * Matrix44.from_x_rotation(rotate_val * 2 * np.pi)\
                   * Matrix44.from_scale(scale_vec)

        self.colour.value = (1.0, 0.0, 0.0)
        self.transform.write(calc_transform((0.0, 0.0, 5.0)).astype('float32'))
        self.vao.render(moderngl.TRIANGLE_STRIP)
