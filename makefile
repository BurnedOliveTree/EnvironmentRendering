all:
	make install
	make run

install:
	python3.9 -m venv ./venv
	./venv/bin/python3.9 -m pip install -r requirements.txt

run:
	./venv/bin/python3.9 src/main.py --map_name heightmap --textures_path src/resources/textures --snow_texture_file snow.png --stone_texture_file stone.jpg --grass_texture_file grass.jpg --water_texture_file water.jpg --shader_path src/resources/shaders --shader_name phong
