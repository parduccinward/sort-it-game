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
        self.configure(bg="#FFF6E5")  # Fondo cálido tipo pastel
        self.level_number = level_number
        self.images = images
        self.correct_order = correct_order
        self.on_level_complete = on_level_complete

        self.selected_order: List[int] = []

        self.setup_ui()

    def setup_ui(self):
        # Título de nivel
        label = tk.Label(
            self,
            text=f"Nivel {self.level_number}",
            font=("Comic Sans MS", 24, "bold"),
            bg="#FFF6E5",
            fg="#5D5D5D",
        )
        label.pack(pady=10)

        # Mezclar imágenes para mostrar
        self.shuffled_indices = list(range(len(self.images)))
        random.shuffle(self.shuffled_indices)

        # Contenedor para imágenes
        self.buttons_frame = tk.Frame(self, bg="#FFF6E5")
        self.buttons_frame.pack(pady=10)

        self.image_buttons = []
        for idx in self.shuffled_indices:
            btn = tk.Button(
                self.buttons_frame,
                image=self.images[idx],
                command=lambda i=idx: self.image_clicked(i),
                borderwidth=2,
                relief=tk.RAISED,
                bg="#FFF6E5",
                activebackground="#FFE0B2",
            )
            btn.pack(side=tk.LEFT, padx=10)
            self.image_buttons.append(btn)

        # Texto de selección
        self.selection_label = tk.Label(
            self,
            text="Selecciona el orden:",
            font=("Comic Sans MS", 16),
            bg="#FFF6E5",
            fg="#5D5D5D",
        )
        self.selection_label.pack(pady=10)

        # Vista previa del orden
        self.selected_order_frame = tk.Frame(self, bg="#FFF6E5")
        self.selected_order_frame.pack(pady=5)

    def image_clicked(self, image_idx):
        if len(self.selected_order) >= len(self.images):
            return

        logging.info(f"Imagen seleccionada: {image_idx}")
        self.selected_order.append(image_idx)
        self.update_selected_order_view()

        if len(self.selected_order) == len(self.images):
            self.after(
                500, self.validate_order
            )  # Dar un respiro de 0.5s antes de validar

    def update_selected_order_view(self):
        for widget in self.selected_order_frame.winfo_children():
            widget.destroy()

        for idx in self.selected_order:
            lbl = tk.Label(
                self.selected_order_frame,
                image=self.images[idx],
                borderwidth=2,
                relief=tk.SUNKEN,
                bg="#FFF6E5",
            )
            lbl.pack(side=tk.LEFT, padx=5)

    def validate_order(self):
        logging.info(f"Validando orden: {self.selected_order} vs {self.correct_order}")

        if self.selected_order == self.correct_order:
            messagebox.showinfo("¡Muy bien!", "🎉 ¡Has ordenado correctamente!")
            self.on_level_complete(self.level_number)
            self.destroy()
        else:
            messagebox.showerror("Inténtalo de nuevo", "❌ El orden no es correcto.")
            self.reset_level()

    def reset_level(self):
        self.selected_order = []
        self.update_selected_order_view()
