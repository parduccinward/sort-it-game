import logging
import tkinter as tk

def load_images_for_level(level: int) -> list[tk.PhotoImage]:
    """Load 3 images for a given level from assets/images."""
    images = []
    for i in range(3):
        path = f"assets/images/level{level}_img{i+1}.png"
        try:
            img = tk.PhotoImage(file=path)
            images.append(img)
        except Exception as e:
            logging.error(f"Failed to load image {path}: {e}")
    return images