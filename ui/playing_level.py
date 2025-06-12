import tkinter as tk
from tkinter import messagebox
import random
import logging
from typing import List, Callable

class PlayingLevelUI(tk.Toplevel):
    def __init__(
        self,
        master,
        level_number: int,
        images: List[tk.PhotoImage],
        correct_order: List[int],
        on_level_complete: Callable[[int], None],
    ):
        super().__init__(master)
        self.title(f"Nivel {level_number}")
        self.level_number = level_number
        self.images = images
        self.correct_order = correct_order  # list de índices de imágenes en orden correcto, ej [0,1,2]
        self.on_level_complete = on_level_complete

        self.selected_order: List[int] = []

        self.setup_ui()

    def setup_ui(self):
        # Mostrar número de nivel
        label = tk.Label(self, text=f"Nivel {self.level_number}", font=("Comic Sans MS", 24, "bold"))
        label.pack(pady=10)

        # Mezclar imágenes para mostrar
        self.shuffled_indices = list(range(len(self.images)))
        random.shuffle(self.shuffled_indices)

        # Contenedor para botones de imágenes
        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(pady=10)

        self.image_buttons = []
        for idx in self.shuffled_indices:
            btn = tk.Button(
                self.buttons_frame,
                image=self.images[idx],
                command=lambda i=idx: self.image_clicked(i),
                borderwidth=2,
                relief=tk.RAISED,
            )
            btn.pack(side=tk.LEFT, padx=10)
            self.image_buttons.append(btn)

        # Contenedor para mostrar orden seleccionado
        self.selection_label = tk.Label(self, text="Selecciona el orden:", font=("Comic Sans MS", 16))
        self.selection_label.pack(pady=10)

        self.selected_order_frame = tk.Frame(self)
        self.selected_order_frame.pack(pady=5)

        # Botón para validar selección
        self.validate_btn = tk.Button(self, text="Validar Orden", command=self.validate_order, state=tk.DISABLED)
        self.validate_btn.pack(pady=10)

    def image_clicked(self, image_idx):
        if len(self.selected_order) >= len(self.images):
            return  # Ya seleccionó las 3 imágenes

        logging.info(f"Imagen seleccionada: {image_idx}")
        self.selected_order.append(image_idx)
        self.update_selected_order_view()

        if len(self.selected_order) == len(self.images):
            self.validate_btn.config(state=tk.NORMAL)

    def update_selected_order_view(self):
        # Limpiar contenedor
        for widget in self.selected_order_frame.winfo_children():
            widget.destroy()

        # Mostrar las imágenes seleccionadas en orden
        for idx in self.selected_order:
            lbl = tk.Label(self.selected_order_frame, image=self.images[idx], borderwidth=2, relief=tk.SUNKEN)
            lbl.pack(side=tk.LEFT, padx=5)

    def validate_order(self):
        logging.info(f"Validando orden: {self.selected_order} vs {self.correct_order}")

        if self.selected_order == self.correct_order:
            messagebox.showinfo("¡Muy bien!", "🎉 ¡Has ordenado correctamente!")
            self.on_level_complete(self.level_number)
            self.destroy()  # Cerrar ventana nivel
        else:
            messagebox.showerror("Inténtalo de nuevo", "❌ El orden no es correcto.")
            self.reset_level()

    def reset_level(self):
        self.selected_order = []
        self.update_selected_order_view()
        self.validate_btn.config(state=tk.DISABLED)
