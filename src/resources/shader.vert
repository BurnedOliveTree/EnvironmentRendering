#version 330

in vec3 in_position;
uniform mat4 transform;

void main() {
    gl_Position = transform * vec4(in_position, 1.0);
}