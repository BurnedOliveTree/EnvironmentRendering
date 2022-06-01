#version 330

in vec3 in_position;
in vec3 in_normal;

out vec3 v_position;
out vec3 v_normal;

out float colour_intensity;
uniform mat4 transform;

void main() {
    gl_Position = transform * vec4(in_position, 1.0);
    colour_intensity = in_position[2]/3;
    v_position = in_position;
    v_normal = in_normal;
}