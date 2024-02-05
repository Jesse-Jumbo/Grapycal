import tkinter as tk
from tkinter import filedialog

import json
from grapycal import Node
from objectsync.sobject import SObjectSerialized

class JsonLoader(Node):
    '''
    To load json file from your local storage
    Input : json data format 
    Output : json data format
    '''
    category = "numpy/dataloader"
    def create(self):
        super().build_node()
        self.shape.set("simple")
        self.label.set("Json Loader")
        self.output_port = self.add_out_port("Json Outputs")
        self.text = self.add_text_control("0")
        self.button = self.add_button_control("Load")
        self.image_num = 0
        self.files_path = []
        self.button.on_click += self.button_clicked

    def button_clicked(self):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-alpha", 0.0)
        root.attributes("-topmost", True)
        root.focus_force()
        selected_files = filedialog.askopenfilenames(
            parent=root, initialdir="./", filetypes=[("jpeg files", "*.jpg")]
        )
        root.destroy()
        if len(selected_files) == 0:
            return
        self.files_path = selected_files
        self.image_num = len(self.files_path)
        self.text.set(str(self.image_num))

    def double_click(self):
        self.run(self.task)

    def task(self):
        files = []
        for file in self.files_path:
            f = open(file)
            file = json.load(f)
            files.append(file)
        self.output_port.push_data(files)

    def destroy(self) -> SObjectSerialized:
        return super().destroy()
