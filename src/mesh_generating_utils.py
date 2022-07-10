import logging
import math
import numpy as np

from typing import List
from PIL import Image
from trimesh.base import Trimesh

from mesh_builder import MeshBuilder


MAX_SIZE = 288


def load_image(filename: str, invert: bool = True, flat: bool = False, max_height: int = 25,
               fill: bool = False) -> np.array:
    with Image.open(filename) as image:
        if image.width > MAX_SIZE or image.height > MAX_SIZE:
            image.thumbnail([MAX_SIZE, MAX_SIZE], Image.NEAREST)

        image_array_grayscale = np.asarray(image.convert('L'))

    #  Flip so image is not mirrored in output
    image_array_grayscale = np.flip(image_array_grayscale, 0)

    #  Flip 0 -> 255 black -> white scaling so dark pixels have higher values
    if invert:
        scaler = lambda p: np.round((255 - p))
        image_array_grayscale = scaler(image_array_grayscale)

    if max_height:
        scaler = lambda p: np.round(max_height * (p / 255))
        image_array_grayscale = scaler(image_array_grayscale)

    if flat:
        image_array_grayscale[image_array_grayscale > 0] = max_height

    if fill:
        image_array_grayscale = np.full((len(image_array_grayscale[0]), len(image_array_grayscale)), max_height)
    return image_array_grayscale


def create_pixel_tris(x, y, z, fz, bz, lz, rz) -> List[List[int]]:
    # x, y, z top left coords of the pixel
    # fz, bz, lz, rz front, back, left and right pixel z values
    # returns List[[x, y, z]]
    tris = []

    #  Top A
    top_A = []
    top_A.append([x, y, z])
    top_A.append([x + 1, y, z])
    top_A.append([x, y + 1, z])

    #  Top B
    top_B = []
    top_B.append([x + 1, y + 1, z])
    top_B.append([x, y + 1, z])
    top_B.append([x + 1, y, z])

    tris.append(top_A)
    tris.append(top_B)

    # If the height of this pixel and the pixel in front are the same they dont need a wall along the z axis
    if fz < z:
        #  Front A
        front_A = []
        front_A.append([x, y, z])
        front_A.append([x, y, fz])
        front_A.append([x + 1, y, z])

        #  Front B
        front_B = []
        front_B.append([x, y, fz])
        front_B.append([x + 1, y, fz])
        front_B.append([x + 1, y, z])

        tris.append(front_A)
        tris.append(front_B)

    if bz < z:
        #  Bottom A
        bottom_A = []
        bottom_A.append([x, y + 1, z])
        bottom_A.append([x + 1, y + 1, z])
        bottom_A.append([x, y + 1, bz])

        #  Bottom B
        bottom_B = []
        bottom_B.append([x, y + 1, bz])
        bottom_B.append([x + 1, y + 1, z])
        bottom_B.append([x + 1, y + 1, bz])

        tris.append(bottom_A)
        tris.append(bottom_B)

    if lz < z:
        #  Left A
        left_A = []
        left_A.append([x, y, z])
        left_A.append([x, y + 1, z])
        left_A.append([x, y, lz])

        #  Left B
        left_B = []
        left_B.append([x, y, lz])
        left_B.append([x, y + 1, z])
        left_B.append([x, y + 1, lz])

        tris.append(left_A)
        tris.append(left_B)

    if rz < z:
        #  Right A
        right_A = []
        right_A.append([x + 1, y, z])
        right_A.append([x + 1, y, rz])
        right_A.append([x + 1, y + 1, z])

        #  Right B
        right_B = []
        right_B.append([x + 1, y, rz])
        right_B.append([x + 1, y + 1, rz])
        right_B.append([x + 1, y + 1, z])

        tris.append(right_A)
        tris.append(right_B)

    #  Bottom A
    bottom_A = []
    bottom_A.append([x, y, 0])
    bottom_A.append([x, y + 1, 0])
    bottom_A.append([x + 1, y, 0])

    #  Bottam B
    bottom_B = []
    bottom_B.append([x + 1, y + 1, 0])
    bottom_B.append([x + 1, y, 0])
    bottom_B.append([x, y + 1, 0])

    tris.append(bottom_A)
    tris.append(bottom_B)

    return tris


def image_to_faces(image_array: np.array) -> List[List[int]]:
    tris = []

    width = len(image_array[0])
    height = len(image_array)

    #  Create top faces and connecting sides of extruded pixel
    for y in range(height):
        logging.info("Progress: ", int((y / len(image_array)) * 100), "%")
        for x in range(width):
            # fz is the height of the pixel above
            # bz is the height of the pixel below
            # rz is the height of the pixel to the right etc

            z = image_array[y][x]

            # Skip 0 values so we only extrude pixel that are not white
            if z == 0:
                continue

            fz = 0 if y <= 0 else image_array[y - 1, x]
            bz = 0 if y >= height - 1 else image_array[y + 1, x]
            lz = 0 if x <= 0 else image_array[y, x - 1]
            rz = 0 if x >= width - 1 else image_array[y, x + 1]
            tris.extend(create_pixel_tris(x, y, z, fz, bz, lz, rz))

    return tris


def create_mesh(image_path: str, invert: bool, flat: bool, max_height: int, fill: bool) -> Trimesh:
    grayscale_image = load_image(image_path, invert, flat, max_height, fill)
    faces = image_to_faces(grayscale_image)
    logging.info("Creating mesh")

    builder = MeshBuilder()
    for face in faces:
        builder.add_face(face)

    logging.info("Finished creating mesh")

    return builder.get_trimesh()
