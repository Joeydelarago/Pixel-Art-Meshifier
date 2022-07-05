from typing import List
from trimesh.base import Trimesh


class MeshBuilder:
    def __init__(self, backplate_depth: int = 1):
        self.vi = 0
        self.faces = []
        self.vertices = []
        self.backplate_depth = backplate_depth

    def show_trimesh(self):
        mesh = self.get_trimesh()
        mesh.show()

    def get_trimesh(self) -> Trimesh:
        self.remove_duplicate_vertices()
        mesh = Trimesh(vertices=self.vertices, faces=self.faces)
        return mesh

    def add_face(self, vertices: List[List[int]]):
        face = []
        for vertex in vertices:
            if vertex in self.vertices:
                face.append(self.vertices.index(vertex))
            else:
                self.vertices.append(vertex)
                face.append(self.vi) 
                self.vi += 1
            
        self.faces.append(face)  

    def remove_duplicate_vertices(self):
        print("vertex count:", len(self.vertices))
        new_faces = []
        new_vertices = []
        new_vi = {}
        index = 0
        for vertex in self.vertices:
            if str(vertex) not in new_vi:
                new_vertices.append(vertex)
                new_vi[str(vertex)] = index
                index += 1

        for face in self.faces:
            new_faces.append([new_vi[str(self.vertices[vi])] for vi in face])

        self.faces = new_faces
        self.vertices = new_vertices
        print("vertex count:", len(self.vertices))
