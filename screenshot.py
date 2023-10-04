import time
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageDraw
import keyboard
import pyscreenshot as ImageGrab
import os
import subprocess

class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot App")
        self.root.geometry("300x150")

        self.frame = ttk.Frame(root)
        self.frame.pack(padx=20, pady=20)

        self.save_path = tk.StringVar()
        self.save_path.set("./Screenshots/")

        self.dragging = False
        self.start_x = None
        self.start_y = None

        self.init_ui()

    def init_ui(self):
        ttk.Label(self.frame, text="Save Location:").grid(row=0, column=0)
        ttk.Entry(self.frame, textvariable=self.save_path, width=30).grid(row=0, column=1)
        ttk.Button(self.frame, text="Browse", command=self.browse_save_path).grid(row=0, column=2)

        ttk.Button(self.frame, text="Capture Full Screen", command=self.capture_full_screen).grid(row=1, column=1)
        ttk.Button(self.frame, text="Capture Region", command=self.capture_region).grid(row=2, column=1)

        self.capture_with_hotkey()

        # Bind mouse events
        self.root.bind("<ButtonPress-1>", self.on_mouse_click)
        self.root.bind("<B1-Motion>", self.on_mouse_drag)
        self.root.bind("<ButtonRelease-1>", self.on_mouse_release)

    def browse_save_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_path.set(folder)

    def capture_full_screen(self):
        timestamp = int(time.time())
        file_path = f"{self.save_path.get()}/{timestamp}.png"
        screenshot = ImageGrab.grab()
        screenshot.save(file_path)
        self.open_image(file_path)

    def capture_region(self):
        print("Click and drag to select the region to capture.")
        print("Release the mouse button when done.")

    def on_mouse_click(self, event):
        if not self.dragging:
            self.start_x = event.x_root
            self.start_y = event.y_root
            self.dragging = True

    def on_mouse_drag(self, event):
        if self.dragging:
            x, y = event.x_root, event.y_root
            self.draw_selection_rectangle(self.start_x, self.start_y, x, y)

    def on_mouse_release(self, event):
        if self.dragging:
            # Capture the selected region
            x1, y1 = self.start_x, self.start_y
            x2, y2 = event.x_root, event.y_root

            # Convert coordinates to local window space
            x1_win = self.root.winfo_pointerx() - self.root.winfo_rootx()
            y1_win = self.root.winfo_pointery() - self.root.winfo_rooty()
            x2_win = x1_win + x2 - x1
            y2_win = y1_win + y2 - y1

            # Ensure x1 < x2 and y1 < y2
            if x1_win >= x2_win or y1_win >= y2_win:
                self.dragging = False
                return

            screenshot = ImageGrab.grab(bbox=(x1_win, y1_win, x2_win, y2_win))

            save_or_crop = tk.messagebox.askquestion("Save or Crop",
                                                     "Do you want to save the selected region or crop it?")
            if save_or_crop == "yes":
                timestamp = int(time.time())
                file_path = f"{self.save_path.get()}/{timestamp}_region.png"
                screenshot.save(file_path)
                self.open_image(file_path)
            else:
                self.show_cropped_region(screenshot)

            self.dragging = False

    def show_cropped_region(self, screenshot):
        screenshot.show()

    def draw_selection_rectangle(self, x1, y1, x2, y2):

        screenshot = ImageGrab.grab().convert("RGBA")

        overlay = Image.new("RGBA", screenshot.size)

        draw = ImageDraw.Draw(overlay)
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2, fill=None)

        screenshot = Image.alpha_composite(screenshot, overlay)
        screenshot.show()

    def capture_with_hotkey(self):
        hotkey = "ctrl+alt+s"
        keyboard.add_hotkey(hotkey, self.capture_full_screen)
        ttk.Label(self.frame, text=f"Hotkey ({hotkey}) to Capture Full Screen").grid(row=3, column=1)

    def open_image(self, file_path):
        try:
            if os.name == 'nt':
                os.startfile(file_path)
            elif os.name == 'posix':
                subprocess.Popen(['xdg-open', file_path])
        except Exception as e:
            print(f"Failed to open the image: {str(e)}")

def main():
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
