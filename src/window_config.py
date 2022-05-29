from csv import reader
from pathlib import Path
from moderngl import DEPTH_TEST, TRIANGLE_STRIP
from moderngl_window import WindowConfig
from numpy import array, pi
from pyrr import Matrix44

import config
from shaders.shader_utils import get_shaders


class HeightMapWindowConfig(WindowConfig):
    gl_version = config.GL_VERSION
    title = config.WINDOW_TITLE
    resource_dir = (Path(__file__).parent / 'resources').resolve()
    x_scale = 1
    y_scale = 1
    z_scale = 40

    def __init__(self, **kwargs):
        super(HeightMapWindowConfig, self).__init__(**kwargs)

        shaders = get_shaders(self.argv.shader_path)
        self.program = self.ctx.program(vertex_shader=shaders[self.argv.shader_name].vertex_shader,
                                        fragment_shader=shaders[self.argv.shader_name].fragment_shader)
        self.read_height_map()
        self.generate()
        self.transform = self.program['transform']
        self.colour = self.program['colour']
        self.z_scale = self.program['z_scale']
    
    def read_height_map(self):
        result = []
        with open(HeightMapWindowConfig.resource_dir / (self.argv.map_name + '.csv')) as csv_file:
            csv_reader = reader(csv_file, delimiter=',')
            for y, row in enumerate(csv_reader):
                result.append(array([array((
                    float(x) * HeightMapWindowConfig.x_scale,
                    float(y) * HeightMapWindowConfig.y_scale,
                    float(z) * HeightMapWindowConfig.z_scale)) for x, z in enumerate(row)]))
        self.height_map = array(result)
        self.size = self.height_map.shape
        self.size = (self.size[0], self.size[1], HeightMapWindowConfig.z_scale)
    
    def generate(self):
        vertices = []
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                vertices.append(self.height_map[y][x])
        
        indices = []
        for y in range(self.size[1] - 1):
            for x in range(self.size[0] - 1):
                indices.append(x + y * self.size[0])
                indices.append(x + 1 + y * self.size[0])
                indices.append(x + (y + 1) * self.size[0])
                indices.append(x + 1 + (y + 1) * self.size[0])
                indices.append(x + (y + 1) * self.size[0])
                indices.append(x + 1 + y * self.size[0])
            indices.append(-1)

        vbo = self.ctx.buffer(array(vertices).astype('float32').tobytes())
        ibo = self.ctx.buffer(array(indices).astype('int32').tobytes())
        self.vao = self.ctx.vertex_array(self.program, vbo, 'in_position', index_buffer=ibo)

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('--shader_path', type=str, required=True, help='Path to the directory with shaders')
        parser.add_argument('--shader_name', type=str, required=True, help='Name of the shader to look for in the shader_path directory')
        parser.add_argument('--map_name', type=str, required=True, help='Name of the map to load')

    def render(self, time: float, frame_time: float):
        self.ctx.clear(0.8, 0.8, 0.8, 0.0)
        self.ctx.enable(DEPTH_TEST)

        def calc_transform(trans_vec: tuple, scale_vec: tuple = (1.0, 1.0, 1.0), rotate_val: float = 0):
            projection = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 1000.0)
            look_at = Matrix44.look_at(
                (-self.size[0] / 2, -self.size[1] / 2, 160), # TODO replace magic number 160
                (self.size[0] / 2, self.size[1] / 2, 0.0),
                (0.0, 0.0, 1.0),
            )
            return projection * look_at\
                   * Matrix44.from_z_rotation(rotate_val * 2 * pi)\
                   * Matrix44.from_translation(trans_vec)\
                   * Matrix44.from_scale(scale_vec)

        self.colour.value = (0.5, 0.25, 0.0)
        self.z_scale.value = HeightMapWindowConfig.z_scale
        self.transform.write(calc_transform((0.0, 0.0, 5.0)).astype('float32'))
        self.vao.render(TRIANGLE_STRIP)
