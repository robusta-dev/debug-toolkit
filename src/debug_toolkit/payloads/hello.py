from pathlib import Path


def entrypoint(output_path: Path):
    with open(output_path, "w") as output_file:
        output_file.write("HELLO WORLD")
