#version 330

out vec4 f_color;
uniform vec3 colour;

void main()
{
    f_color = vec4(colour, 1.0);
}
