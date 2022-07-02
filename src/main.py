import click
from trimesh import Trimesh

from mesh_generating_utils import create_backplate, create_mesh


@click.command()
@click.argument("image_path")
@click.argument("output_path", default="pixels.stl")
@click.option("-f", "--flat", is_flag=True, default=False)
@click.option("-i", "--invert", is_flag=True, default=False)
@click.option("-mx", "--max_height", default=255)
@click.option("-b", "--backplate", is_flag=True, default=False)
def create_models(image_path: str, output_path: str, invert: bool, flat: bool, max_height: int, backplate: bool) -> None:
    pixels_mesh: Trimesh = create_mesh(image_path, invert, flat, max_height, False)
    pixels_mesh.export(output_path)

    if backplate:
        backplate_mesh: Trimesh = create_mesh(image_path, False, True, 1, True)
        backplate_mesh.export("backplate.stl")


if __name__ == "__main__":
    create_models()
