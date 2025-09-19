import tkinter as tk
from PIL import Image, ImageTk

# Create the main window
root = tk.Tk()
root.title("PNG Image Viewer")

# Use raw string to avoid escape character issues
image_path = r"E:\Engineering Utilities\aepl_python_uds_stack_v0.3_Commn - Backup\src\Accolade Logo Without Background 3.png"

# Load and convert image
image = Image.open(image_path)
tk_image = ImageTk.PhotoImage(image)

# Create a label widget to display the image
label = tk.Label(root, image=tk_image)
label.pack()

# Keep a reference to avoid garbage collection
label.image = tk_image

# Start the GUI event loop
root.mainloop()
