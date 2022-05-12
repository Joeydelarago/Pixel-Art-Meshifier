from typing import List
from trimesh.base import Trimesh
import numpy as np

class MeshBuilder():
    def __init__(self, backplate_depth: int = 1):
        self.vi = 0
        self.faces = []
        self.vertices = []
        self.backplate_depth = backplate_depth
        
    def show_trimesh(self):
        mesh = Trimesh(vertices=self.vertices, faces=self.faces)
        mesh.show()
        
    def get_trimesh(self) -> Trimesh:
        mesh = Trimesh(vertices=self.vertices, faces=self.faces) 
        print("vertex count:", len(mesh.vertices))
        mesh.merge_vertices() 
        print("vertex count:", len(mesh.vertices))
        return mesh
        
    def add_face(self, vertices: List[List[int]]): 
        self.vertices.extend(vertices)  
        self.faces.append([self.vi, self.vi+1, self.vi+2])
        self.vi += 3