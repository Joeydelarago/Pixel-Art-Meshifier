from typing import List, Tuple
import numpy as np
import trimesh as tm
from PIL import Image, ImageOps
from trimesh.base import Trimesh

from mesh_builder import MeshBuilder


#  Factor of original height, where original height is between 0 - 255
HEIGHT_SCALE_FACTOR = .1
BACKPLATE_HEIGHT = 10

def load_image(filename: str):
    image_array_grayscale: np.array = []
    with Image.open(filename) as image:
            image_array = np.asarray(image).tolist()
            image_array_grayscale = np.asarray(image.convert('L'))  
    
    #  Flip so image is not mirrored in output
    image_array_grayscale = np.flip(image_array_grayscale, 0) 
    
    #  Flip 0 -> 255 black -> white scaling so dark pixels have higher values
    #  Also scale values down
    scaler = lambda p: (255 - p) * HEIGHT_SCALE_FACTOR
    image_array_grayscale = scaler(image_array_grayscale)
    
    #  Add BACKPLATE height to give solid backplate on model (minimum pixel height will be BACKPLATE HEIGHT)
    backplate_modifier = lambda p: p + BACKPLATE_HEIGHT
    image_array_grayscale = backplate_modifier(image_array_grayscale)
    
    
    return image_array_grayscale

def image_to_faces(image_array: np.array) -> List[List[int]]: 
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
            fz = 0 if y <= 0 else image_array[y - 1, x] / 25
            bz = 0 if y >= height - 1 else image_array[y + 1, x] / 25
            lz = 0 if x <= 0 else image_array[y, x - 1] / 25
            rz = 0 if x >= width - 1 else image_array[y, x + 1] / 25
            tris.extend(create_pixel_tris(x, y, image_array[y][x] / 25, fz, bz, lz, rz))
    
    # Create back plate        
    tris.append([[0, 0, 0], [0, height, 0], [width, height, 0]])
    tris.append([[0, 0, 0], [width, height, 0], [width, 0, 0]])
    
    return tris   


def create_pixel_tris(x, y, z, fz, bz, lz, rz) -> List[List[int]]:
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
    if fz != z:
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
    
    
    if bz != z:
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
    
    if lz != z:
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
    
    if rz != z:
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
    
    
    return tris

def create_trimesh(faces: List[List[int]]) -> Trimesh:
    # faces: List[[x, y, z]]
    builder = MeshBuilder()
    for face in faces:
        builder.add_face(face) 
    return builder.get_trimesh()
    

if __name__ == "__main__":
    filename= "pokemon_oak.png"
    grayscale_image = load_image(filename)
    faces = image_to_faces(grayscale_image)
    mesh = create_trimesh(faces)
    # print(mesh.fill_holes())
    # mesh = mesh.slice_plane([0, 0, 1], [0, 0, 1], True)
    mesh.show()
    mesh.export("test.stl")
    