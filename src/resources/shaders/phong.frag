#version 330

in vec3 v_position, v_normal;
float ambient_strength, diffuse_strength, specular_strength, object_shininess;
vec3 ambient_light_color, diffuse_light_color, specular_light_color, light_pos;
vec3 object_diffuse_color, object_specular_color;
out vec4 f_color;

in float colour_intensity;
uniform vec3 colour;
uniform int z_scale;
uniform sampler2D snow_texture;
uniform sampler2D stone_texture;
uniform sampler2D grass_texture;

void main() {
  // Ustawienie połyskliwości i kolorów obiektu
  object_shininess = 30;
  object_diffuse_color = vec3(0.7, 0, 0);
  object_specular_color = vec3(1, 1, 1);

  // Ustawienie kolorów światła
  ambient_light_color = vec3(0.1, 0.1, 0.1);
  diffuse_light_color = vec3(1, 1, 1);
  specular_light_color = vec3(1, 1, 1);

  // Ustawienie pozycji światła
  light_pos = vec3(-5, 7, 3);

  // Obliczenie znormalizowanego wektora normalnego danego wierzchołka
  vec3 normal_direction = normalize(v_normal);

  // Obliczenie znormalizowanego wektora z danego wierzchołka w kierunku źródła
  // światła
  vec3 light_direction = normalize(light_pos - v_position);

  // Obliczenie iloczynu skalarnego wektora normalnego i wektora w kierunku
  // źródła światła, który wyznacza znaczenie, jakie ma oświetlenie diffuse na
  // dany wierzchołek. Jeśli kąt między tymi wektorami jest większy niż 90
  // stopni, znaczenie to jest ustawiane na 0.
  float diffuse_impact = max(dot(normal_direction, light_direction), 0);
  float specular_impact = 0;

  if (diffuse_impact > 0) {

    // Obliczenie wektora z pozycji widoku do wierzchołka (współrzędne
    // wierzchołka są odpowiednio przesuwane w vertex shaderze, więc nie trzeba
    // ich odejmować od współrzędnych punktu widoku)
    vec3 look_direction = normalize(-v_position);

    // Obliczenie wektora światła odbitego od powierzhni obiektu
    vec3 reflect_direction = reflect(-light_direction, normal_direction);

    // Obliczenie iloczynu skalarnego pomiędzy wektorem odbicia światła, a
    // wektorem pozycji widoku i podniesienie go do potęgi wartości
    // połyskliwości obiektu, co wyznacza znaczenie, jakie ma oświetlenie
    // specular na dany wierzchołek. Ponownie, jeśli kąt pomiędzy tymi wektorami
    // jest większy niż 90 stopni, znaczenie jest ustawiane na 0.
    specular_impact =
        pow(max(dot(reflect_direction, look_direction), 0), object_shininess);
  }
  // Ustawienie mocy każdego z rodzajów światła
  ambient_strength = 0.1;
  diffuse_strength = 1;
  specular_strength = 0.8;

  vec3 ambient, diffuse, specular;
  // Obliczenie wartości każdej ze składowych koloru danego fragmentu
  ambient = ambient_strength * ambient_light_color;
  diffuse = diffuse_strength * diffuse_impact * diffuse_light_color *
            object_diffuse_color;
  specular = specular_strength * specular_impact * specular_light_color *
             object_specular_color;

  // Ustawienie koloru fragmentu na sumę składowych kolorów ambient, diffuse i
  // specular
    if (v_position[2] < 20){
        f_color = texture(grass_texture, vec2(v_position[0]/1000, v_position[1]/1000)) + vec4((colour_intensity / z_scale) * colour * (ambient + diffuse + specular), 1.0);
    }
    else if(v_position[2] < 35){
        f_color = texture(stone_texture, vec2(v_position[0]/1000, v_position[1]/1000)) + vec4((colour_intensity / z_scale) * colour * (ambient + diffuse + specular), 1.0);
    }
    else {
//        f_color = vec4((colour_intensity / z_scale) * colour, 1.0);
        f_color = texture(snow_texture, vec2(v_position[0]/1000 + v_normal[0], v_position[1]/1000)) + vec4((colour_intensity / z_scale) * colour * (ambient + diffuse + specular), 1.0);

    }

//   f_color = vec4((ambient + diffuse + specular), 1);

}
