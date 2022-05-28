install:
	python3 -m venv ./venv
	./venv/bin/python3 -m pip install -r requirements.txt

run:
	./venv/bin/python3 src/main.py --shader_path ./src/resources --shader_name shader
