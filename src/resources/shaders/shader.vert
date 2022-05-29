#version 330

in vec3 in_position;
out float colour_intensity;
uniform mat4 transform;

void main() {
    gl_Position = transform * vec4(in_position, 1.0);
    colour_intensity = in_position[2];
}