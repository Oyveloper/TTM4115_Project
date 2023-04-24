from ast import List
from typing import Callable
from appJar import gui


class Frame:
    def __init__(self, setup: Callable):
        self.setup = setup


class GUIHelper:
    def __init__(self):
        self.app = gui()

    def add_frames(self, frames: List[Frame]):
        with self.app.frameStack("frames"):
            for frame in frames:
                with self.app.frame():
                    (frame.setup)()

    def start(self):
        self.app.go()
