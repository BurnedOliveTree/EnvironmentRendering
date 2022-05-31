#version 330

in float colour_intensity;
in vec3 v_position;
out vec4 f_color;
uniform vec3 colour;
uniform int z_scale;
uniform sampler2D snow_texture;
uniform sampler2D stone_texture;
uniform sampler2D grass_texture;

void main()
{
    if (v_position[2] < 20){
        f_color = texture(grass_texture, vec2(v_position[0]/1000, v_position[1]/1000)) + vec4((colour_intensity / z_scale) * colour, 1.0);
    }
    else if(v_position[2] < 35){
        f_color = texture(stone_texture, vec2(v_position[0]/1000, v_position[1]/1000)) + vec4((colour_intensity / z_scale) * colour, 1.0);
    }
    else {
//        f_color = vec4((colour_intensity / z_scale) * colour, 1.0);
        f_color = texture(snow_texture, vec2(v_position[0]/1000, v_position[1]/1000)) + vec4((colour_intensity / z_scale) * colour, 1.0);

    }
}
//        f_color = vec4((colour_intensity / z_scale) * colour, 1.0) + texture(stone_texture, vec2(v_position[0], v_position[1]));
