install:
	python3 -m venv ./venv
	./venv/bin/python3 -m pip install -r requirements.txt

run:
	./venv/bin/python3 src/main.py --shader_path ./src/resources/shaders --shader_name shader --map_name heightmap --textures_path ./src/resources/textures --snow_texture_file snow.png --stone_texture_file stone.jpg  --grass_texture_file grass.jpg
