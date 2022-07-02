import click
from trimesh import Trimesh

from mesh_generating_utils import create_backplate, create_mesh


@click.command()
@click.argument("image_path")
@click.option("-f", "--flat", is_flag=True, default=False)
@click.option("-i", "--invert", is_flag=True, default=False)
@click.option("-mx", "--max_height", default=255)
def create_models(image_path: str, invert: bool, flat: bool, max_height: int) -> None:
    pixels_mesh: Trimesh = create_mesh(image_path, invert, flat, max_height)
    pixels_mesh.export("pixels.stl")

    # backplate_mesh: Trimesh = create_mesh()


if __name__ == "__main__":
    create_models()
