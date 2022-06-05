import click
from mesh_exporter import MeshExporter

from mesh_generator import MeshGenerator


@click.command()
@click.argument("image_path")
def create_models(image_path: str) -> None:
    generator = MeshGenerator()
    grayscale_image = generator.load_image(image_path)
    faces = generator.image_to_faces(grayscale_image)
    pixels = generator.create_pixels_trimesh(faces)
    backplate = generator.create_backplate(grayscale_image)
    
    exporter = MeshExporter()
    exporter.export_stl(pixels, "pixels.stl")
    exporter.export_stl(backplate, "backplate.stl")
    
if __name__ == "__main__":
    create_models()