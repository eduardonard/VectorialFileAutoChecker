from glob import glob

from modules.getShapes import *

########
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD


def handle_drop(event):
    # Get the path of the dropped file
    global file_path
    file_path = event.data

    # Process the file or perform any actions you need
    print("Dropped file:", file_path)
    window.destroy()

# Create the main window
window = TkinterDnD.Tk()

# Set up the window properties
window.title("File Drop GUI")
window.geometry("400x300")

# Create a label
label = tk.Label(window, text="Drag and drop a file here")
label.pack(pady=50)

# Create a frame to handle the drag and drop functionality
frame = tk.Frame(window, bd=2, relief=tk.SUNKEN)
frame.pack(padx=50, pady=20, fill=tk.BOTH, expand=True)

# Enable drag and drop functionality for the frame
frame.drop_target_register(DND_FILES)
frame.dnd_bind('<<Drop>>', handle_drop)

# Start the main event loop
window.mainloop()

cad = glob(file_path)[0]
tagli, pieghe, perforatore, tagliacordone, general, shape_canva = get_id_elems(cad)