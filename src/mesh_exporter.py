from trimesh.base import Trimesh
from trimesh.exchange import threemf

class MeshExporter():
    def __init__(self):
        pass
    
    def export_stl(self, mesh: Trimesh, filename: str) -> None:
        mesh.export(filename)
 