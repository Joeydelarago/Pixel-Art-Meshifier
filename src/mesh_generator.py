import math
import numpy as np

from typing import List
from PIL import Image
from trimesh.base import Trimesh
from trimesh import creation

from mesh_builder import MeshBuilder
from mesh_exporter import MeshExporter


#  Factor of original height, where original height is between 0 - 255
HEIGHT_SCALE_FACTOR = .003
BACKPLATE_HEIGHT = 1.2
MAX_SIZE = 144

class MeshGenerator():
    
    def __init__(self):
        backplate: Trimesh = None
        pixels: Trimesh = None
        image_array: List = []

    def load_image(self, filename: str):
        image_array_grayscale: np.array = []
        with Image.open(filename) as image:
                # image.thumbnail([MAX_SIZE, MAX_SIZE], Image.NEAREST)
                image_array = np.asarray(image).tolist()
                image_array_grayscale = np.asarray(image.convert('L'))  
        
        #  Flip so image is not mirrored in output
        image_array_grayscale = np.flip(image_array_grayscale, 0) 
        
        #  Flip 0 -> 255 black -> white scaling so dark pixels have higher values
        #  Also scale values down
        scaler = lambda p: np.round((255 - p) * HEIGHT_SCALE_FACTOR)
        image_array_grayscale = scaler(image_array_grayscale)
        
        self.image_arry = image_array_grayscale
        return image_array_grayscale

    def image_to_faces(self, image_array: np.array) -> List[List[int]]: 
        tris = []
        
        width = len(image_array[0])
        height = len(image_array)
        
        
        #  Create top faces and connecting sides of extruded pixel
        for y in range(height):
            print("Progress: ", int((y/len(image_array)) * 100), "%")
            for x in range(width):
                # fz is the height of the pixel above
                # bz is the height of the pixel below
                # rz is the height of the pixel to the right etc
                
                z = image_array[y][x]
                
                # Skip 0 values so we only extrude pixel that are not white
                if z == 0:
                    continue
                
                fz = 0 if y <= 0 else image_array[y - 1, x] / 25
                bz = 0 if y >= height - 1 else image_array[y + 1, x] / 25
                lz = 0 if x <= 0 else image_array[y, x - 1] / 25
                rz = 0 if x >= width - 1 else image_array[y, x + 1] / 25
                tris.extend(self.create_pixel_tris(x, y, z, fz, bz, lz, rz))
        
        return tris   

    def create_pixel_tris(self, x, y, z, fz, bz, lz, rz) -> List[List[int]]:
        # x, y, z top left coords of the pixel
        # fz, bz, lz, rz front, back, left and right pixel z values
        # returns List[[x, y, z]] 
        tris = []
        
        #  Top A
        top_A = []
        top_A.append([x     ,y     ,z])
        top_A.append([x + 1 ,y     ,z])
        top_A.append([x     ,y + 1 ,z])
        
        #  Top B 
        top_B = []
        top_B.append([x + 1 ,y + 1 ,z])
        top_B.append([x     ,y + 1 ,z])
        top_B.append([x + 1 ,y     ,z])
        
        tris.append(top_A)
        tris.append(top_B)
        
        #If the height of this pixel and the pixel in front are the same they dont need a wall along the z axis
        if fz < z:
            #  Front A
            front_A = []
            front_A.append([x     ,y     ,z])
            front_A.append([x     ,y     ,fz]) 
            front_A.append([x + 1 ,y     ,z])
            
            #  Front B
            front_B = []
            front_B.append([x     ,y     ,fz])
            front_B.append([x + 1 ,y     ,fz])
            front_B.append([x + 1 ,y     ,z])  

            tris.append(front_A)
            tris.append(front_B)
        
        
        if bz < z:
            #  Bottom A
            bottom_A = []
            bottom_A.append([x     ,y + 1 ,z])
            bottom_A.append([x + 1 ,y + 1 ,z])
            bottom_A.append([x     ,y + 1 ,bz])
            
            #  Bottom B
            bottom_B = []
            bottom_B.append([x     ,y + 1 ,bz])
            bottom_B.append([x + 1 ,y + 1 ,z])
            bottom_B.append([x + 1 ,y + 1 ,bz])
            
            tris.append(bottom_A)
            tris.append(bottom_B)
        
        if lz < z:
            #  Left A
            left_A = []
            left_A.append([x     ,y     ,z])
            left_A.append([x     ,y + 1 ,z])
            left_A.append([x     ,y     ,lz])
            
            #  Left B
            left_B = []
            left_B.append([x     ,y     ,lz])
            left_B.append([x     ,y + 1 ,z])
            left_B.append([x     ,y + 1 ,lz])
            
            tris.append(left_A)
            tris.append(left_B)
        
        if rz < z:
            #  Right A
            right_A = []
            right_A.append([x + 1 ,y     ,z])
            right_A.append([x + 1 ,y     ,rz])
            right_A.append([x + 1 ,y + 1 ,z])
            
            #  Right B
            right_B = []
            right_B.append([x + 1 ,y     ,rz])
            right_B.append([x + 1 ,y + 1 ,rz])
            right_B.append([x + 1 ,y + 1 ,z])
            
            tris.append(right_A)
            tris.append(right_B)
            
        #  Bottom A
        bottom_A = []
        bottom_A.append([x     ,y     ,0])
        bottom_A.append([x     ,y + 1 ,0])
        bottom_A.append([x + 1 ,y     ,0])
        
        #  Bottam B
        bottom_B = []
        bottom_B.append([x + 1 ,y + 1 ,0])
        bottom_B.append([x + 1 ,y     ,0])
        bottom_B.append([x     ,y + 1 ,0])
        
        tris.append(bottom_A)
        tris.append(bottom_B)
        
        
        return tris

    def create_pixels_trimesh(self, faces: List[List[int]]) -> Trimesh:
        # faces: List[[x, y, z]]
        builder = MeshBuilder()
        for face in faces:
            builder.add_face(face) 
        self.pixels = builder.get_trimesh()
        return self.pixels

    def create_backplate(self, grayscale_image: List[List[int]]) -> Trimesh:
        self.backplate = creation.box([len(grayscale_image[0]), len(grayscale_image), BACKPLATE_HEIGHT])
        return self.backplate

    