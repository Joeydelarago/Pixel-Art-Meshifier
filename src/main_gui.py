#!/usr/bin/env python
import io
import os
import sys
from typing import List

import PySimpleGUI as sg
from PIL import Image, ImageTk, ImageOps
from PIL.Image import Dither

from mesh_generating_utils import create_mesh


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainGui:
    def __init__(self):
        self.pixels_mesh = None
        self.image_path = None
        self.display_image = sg.Image(data=self.get_img_data(resource_path("resources/placeholder.png"), first=True))

        self.window = sg.Window("Pixel Meshifier",
                                self.build_layout(),
                                default_element_size=(12, 1),
                                default_button_element_size=(12, 1))
        self.main_loop()

    def main_loop(self) -> None:
        while True:
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, "Exit"):
                break
            print(event, values)

            if event == "About...":
                self.window.disappear()
                sg.popup("About this program",
                         "Version 1.0",
                         "Author: Joey de l'Arago",
                         "GitHub: https://github.com/Joeydelarago", grab_anywhere=True)
                self.window.reappear()

            elif event == "-LOAD-" or event == "Open     Ctrl-O":
                input_path = sg.popup_get_file("Choose your file",
                                               keep_on_top=True,
                                               file_types=(("PNG Files", "*.png"), ("JPG Files", "*.jpg")))

                if not input_path:
                    continue

                self.image_path = input_path
                self.display_image.update(data=self.get_img_data(input_path, first=True))


            elif event == "-SAVE-" or event == "Save       Ctrl-S":
                if self.image_path is None:
                    sg.popup("Please load an image first")
                    continue

                output_path = sg.popup_get_file("Choose your file",
                                                keep_on_top=True,
                                                save_as=True,
                                                file_types=(("STL Files", "*.stl"), ("All Files", "*.*")))

                if not output_path:
                    continue

                backplate = self.window.Element("Backplate").Get()
                invert = self.window.Element("Invert").Get()
                flat = self.window.Element("Flat").Get()
                steps = values["Steps"]

                self.pixels_mesh = create_mesh(self.image_path, invert, flat, steps, backplate)
                self.pixels_mesh.export(output_path)

        self.window.close()

    def build_layout(self) -> List[List[sg.Element]]:
        sg.theme("LightGray")
        sg.set_options(element_padding=(0, 0))

        menu_layout = [["&File", ["&Open     Ctrl-O", "&Save       Ctrl-S", "E&xit"]],
                       ["&Help", "&About..."], ]

        l_column = sg.Column(
            [
                [sg.Menu(menu_layout, tearoff=False, pad=(200, 1))],
                [sg.Text("Options", font=("Helvetica", 16), size=(10, 1), pad=((0, 0), (0, 6)))],
                [sg.Checkbox("Backplate", key="Backplate", pad=((0, 0), (0, 4)), default=False,
                             tooltip="Export a backplate that fills the image")],
                [sg.Checkbox("Invert", key="Invert", pad=((0, 0), (0, 4)), default=False,
                             tooltip="Make darker pixels thicker rather than thinner")],
                [sg.Checkbox("Flat", key="Flat", pad=((0, 0), (0, 4)), default=False,
                             tooltip="Flatten all pixels to a single height")],
                [sg.Text("Steps: ", size=(5, 1), pad=((0, 10), (11, 0))),
                 sg.Slider(key="Steps", range=(1, 32), orientation="h", size=(20, 10), default_value=5)],
            ],
            vertical_alignment="top",
            size=(200, 400)
        )

        r_column = sg.Column(
            [
                [self.display_image],
                [sg.Button("Save", key="-SAVE-", expand_x=True), sg.Button("Load", key="-LOAD-", expand_x=True)],
            ]
        )

        layout = [
            [l_column, r_column]
        ]

        return layout

    def get_img_data(self, image_path: str, maxsize=(500, 500), first=False):
        """ Generate image data using PIL """
        img = Image.open(image_path)
        img = ImageOps.contain(img, maxsize, Dither.NONE)
        if first:
            bio = io.BytesIO()
            img.save(bio, format="PNG")
            del img
            return bio.getvalue()
        return ImageTk.PhotoImage(img)


if __name__ == "__main__":
    gui = MainGui()
