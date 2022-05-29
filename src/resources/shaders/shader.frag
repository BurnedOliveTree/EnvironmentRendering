#version 330

in float colour_intensity;
out vec4 f_color;
uniform vec3 colour;
uniform int z_scale;

void main()
{
    f_color = vec4((colour_intensity / z_scale) * colour, 1.0);
}
