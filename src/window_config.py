import struct
from csv import reader
from pathlib import Path

import numpy as np
from moderngl import DEPTH_TEST, TRIANGLE_STRIP
from moderngl_window import WindowConfig
from numpy import array, pi
from pyrr import Matrix44
from PIL import Image
import os
import config
from shaders.shader_utils import get_shaders


class HeightMapWindowConfig(WindowConfig):
    gl_version = config.GL_VERSION
    title = config.WINDOW_TITLE
    resource_dir = (Path(__file__).parent / 'resources').resolve()
    xy_scale = 1
    z_scale = 40
    texture_scale = 1000
    def __init__(self, **kwargs):
        super(HeightMapWindowConfig, self).__init__(**kwargs)

        shaders = get_shaders(self.argv.shader_path)
        self.program = self.ctx.program(vertex_shader=shaders[self.argv.shader_name].vertex_shader,
                                        fragment_shader=shaders[self.argv.shader_name].fragment_shader)
        self.read_height_map()
        self.load_textures()
        self.generate()
        self.transform = self.program['transform']
        self.colour = self.program['colour']
        self.texture_scale = self.program['texture_scale']

    def load_textures(self):
        self.program['snow_texture'] = 0
        self.program['grass_texture'] = 1
        self.program['stone_texture'] = 2

        snow_img = Image.open(os.path.join(self.argv.textures_path, self.argv.snow_texture_file))
        snow_texture = self.ctx.texture(snow_img.size, 4, snow_img.tobytes(), alignment=4)
        snow_texture.use(location=0)
        stone_img = Image.open(os.path.join(self.argv.textures_path, self.argv.stone_texture_file))
        stone_texture = self.ctx.texture(stone_img.size, 3, stone_img.tobytes(), alignment=4)
        stone_texture.use(location=2)
        grass_img = Image.open(os.path.join(self.argv.textures_path, self.argv.grass_texture_file))
        grass_texture = self.ctx.texture(grass_img.size, 3, grass_img.tobytes(), alignment=4)
        grass_texture.use(location=1)

    def read_height_map(self):
        result = []
        with open(HeightMapWindowConfig.resource_dir / (self.argv.map_name + '.csv')) as csv_file:
            csv_reader = reader(csv_file, delimiter=',')
            for y, row in enumerate(csv_reader):
                result.append(array([array((
                    float(x) * HeightMapWindowConfig.xy_scale,
                    float(y) * HeightMapWindowConfig.xy_scale,
                    float(z) * HeightMapWindowConfig.z_scale)) for x, z in enumerate(row)]))
        self.height_map = array(result)
        self.size = self.height_map.shape
        self.size = (self.size[0], self.size[1], HeightMapWindowConfig.z_scale)

    def generate(self):
        vertices = []
        vertices_and_normals = []
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                vertices.append(self.height_map[y][x])
                vertices_and_normals.append([*self.height_map[y][x], 0, 0, 0])

        indices = []
        print("calculating normals...")

        def create_triangles(v1_i, v2_i, v3_i):
            indices.append(v1_i)
            indices.append(v2_i)
            indices.append(v3_i)
            edge1 = vertices[v2_i] - vertices[v1_i]
            edge2 = vertices[v3_i] - vertices[v1_i]
            cross = np.cross(edge1, edge2)
            for i in range(3):
                vertices_and_normals[v1_i][3+i] += cross[i]
                vertices_and_normals[v2_i][3+i] += cross[i]
                vertices_and_normals[v3_i][3+i] += cross[i]

        for y in range(self.size[1] - 1):
            # normals.append([])
            for x in range(self.size[0] - 1):
                # first triangle
                v1_i = x + y * self.size[0]
                v2_i = x + 1 + y * self.size[0]
                v3_i = x + (y + 1) * self.size[0]
                create_triangles(v1_i, v2_i, v3_i)

                # second triangle
                v1_i = x + 1 + (y + 1) * self.size[0]
                v2_i = x + (y + 1) * self.size[0]
                v3_i = x + 1 + y * self.size[0]
                create_triangles(v1_i, v2_i, v3_i)

            indices.append(-1)

        print("done")
        vbo = self.ctx.buffer(array(vertices_and_normals).astype('float32').tobytes())
        ibo = self.ctx.buffer(array(indices).astype('int32').tobytes())
        self.vao = self.ctx.vertex_array(self.program, [
            (vbo, '3f 3f', 'in_position', 'in_normal'),
        ],
                                         index_buffer=ibo,
                                         index_element_size=4)

    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('--shader_path', type=str, required=True, help='Path to the directory with shaders')
        parser.add_argument('--shader_name', type=str, required=True,
                            help='Name of the shader to look for in the shader_path directory')
        parser.add_argument('--map_name', type=str, required=True, help='Name of the map to load')
        parser.add_argument('--textures_path', type=str, required=True, help='Path to the directory with texutres')
        parser.add_argument('--snow_texture_file', type=str, required=True,
                            help='Filename (with extension) of snow texture')
        parser.add_argument('--stone_texture_file', type=str, required=True,
                            help='Filename (with extension) of stone texture')
        parser.add_argument('--grass_texture_file', type=str, required=True,
                            help='Filename (with extension) of grass texture')

    def render(self, time: float, frame_time: float):
        self.ctx.clear(0.8, 0.8, 0.8, 0.0)
        self.ctx.enable(DEPTH_TEST)

        def calc_transform(trans_vec: tuple,
                           scale_vec: tuple = (1.0, 1.0, 1.0),
                           rotate_val: float = 0):  # todo add time to rotate val
            projection = Matrix44.perspective_projection(45.0, self.aspect_ratio, 0.1, 1000.0)
            look_at = Matrix44.look_at(
                (-self.size[0] / 2, -self.size[1] / 2, 160),  # TODO replace magic number 160
                (self.size[0] / 2, self.size[1] / 2, 0.0),
                (0.0, 0.0, 1.0),
            )
            return projection * look_at \
                   * Matrix44.from_z_rotation(rotate_val * 2 * pi) \
                   * Matrix44.from_translation(trans_vec) \
                   * Matrix44.from_scale(scale_vec)

        self.colour.value = (0.72, 0.68, 0.66)
        self.texture_scale.value = HeightMapWindowConfig.texture_scale
        self.transform.write(calc_transform((0.0, 0.0, 5.0)).astype('float32'))
        self.vao.render(TRIANGLE_STRIP)
