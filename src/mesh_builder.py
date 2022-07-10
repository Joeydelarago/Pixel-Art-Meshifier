from typing import List
from trimesh.base import Trimesh


class MeshBuilder:
    def __init__(self, backplate_depth: int = 1):
        self.vi = 0
        self.faces = []
        self.vertices = []
        self.vertex_to_vi = {}
        self.backplate_depth = backplate_depth

    def show_trimesh(self):
        mesh = self.get_trimesh()
        mesh.show()

    def get_trimesh(self) -> Trimesh:
        mesh = Trimesh(vertices=self.vertices, faces=self.faces)
        return mesh

    def add_face(self, vertices: List[List[int]]):
        face = [self.add_vertex(vertex) for vertex in vertices]
        self.faces.append(face)

    def add_vertex(self, vertex: List[int]) -> int:
        # Adds a vertex and returns it's index
        # If the vertex already exists, returns the index of the existing vertex
        if not str(vertex) in self.vertex_to_vi:
            self.vertex_to_vi[str(vertex)] = self.vi
            self.vertices.append(vertex)
            self.vi += 1
            return self.vi - 1
        else:
            return self.vertex_to_vi[str(vertex)]
