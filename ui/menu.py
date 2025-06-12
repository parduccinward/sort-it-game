import tkinter as tk
import logging
from typing import Callable, List


class MenuUI(tk.Tk):
    MAX_LEVELS = 20
    BUTTON_WIDTH = 20
    BUTTON_HEIGHT = 6
    GRID_COLUMNS = 5

    # Paleta pastel para los botones, colores más suaves pero variados
    LEVEL_COLORS = [
        "#FFA07A",  # light salmon
        "#87CEFA",  # light sky blue
        "#90EE90",  # light green
        "#FFB6C1",  # light pink
        "#FFDAB9",  # peach puff
        "#D8BFD8",  # thistle (lila pastel)
        "#AFEEEE",  # pale turquoise
        "#FFDEAD",  # navajo white
        "#98FB98",  # pale green
        "#F0E68C",  # khaki
    ]

    LEVEL_EMOJIS = ["🎈", "🚀", "🌟", "🍭", "🐱", "🐶", "🌈", "🍎", "🎉", "⚡"]

    def __init__(self, controller, start_level_callback: Callable[[int], None]):
        super().__init__()
        self.title("🎮 Menu Juego para Ordenar 🎉")
        self.controller = controller
        self.start_level_callback = start_level_callback

        # Fondo amarillo pastel suave
        self.configure(bg="#FFF9E3")

        self.level_buttons: List[tk.Button] = []

        self.create_widgets()

    def create_widgets(self) -> None:
        unlocked_levels = self.controller.get_unlocked_levels()
        logging.info(f"Unlocked levels: {unlocked_levels}")

        for level in range(1, self.MAX_LEVELS + 1):
            self.create_level_button(level, level in unlocked_levels)

    def create_level_button(self, level: int, is_unlocked: bool) -> None:
        emoji = self.LEVEL_EMOJIS[(level - 1) % len(self.LEVEL_EMOJIS)]
        btn_text = f"{emoji} Level {level} {emoji}"
        btn = tk.Button(
            self,
            text=btn_text,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            font=("Comic Sans MS", 18, "bold"),
            relief=tk.RAISED,
            bd=5,
            fg="#222222",  # texto oscuro para buen contraste
            activeforeground="#222222",
            wraplength=140,
            justify=tk.CENTER,
            cursor="hand2",
        )

        bg_color = self.LEVEL_COLORS[(level - 1) % len(self.LEVEL_COLORS)]

        if is_unlocked:
            btn.config(
                state=tk.NORMAL,
                bg=bg_color,
                activebackground=self._darker_color(bg_color, 0.85),
                command=lambda lvl=level: self.on_level_selected(lvl),
            )
            btn.bind("<Enter>", lambda e, b=btn, c=bg_color: b.config(bg=self._darker_color(c, 0.9)))
            btn.bind("<Leave>", lambda e, b=btn, c=bg_color: b.config(bg=c))
        else:
            btn.config(state=tk.DISABLED, bg="#DDD", fg="#888")

        # Posición en la grilla
        row = (level - 1) // self.GRID_COLUMNS
        column = (level - 1) % self.GRID_COLUMNS
        btn.grid(row=row, column=column, padx=10, pady=10)

        self.level_buttons.append(btn)

    def _darker_color(self, hex_color: str, factor: float) -> str:
        """Devuelve un color más oscuro aplicando factor (0..1) a un color hex pastel."""
        hex_color = hex_color.lstrip("#")
        rgb = [int(hex_color[i : i + 2], 16) for i in (0, 2, 4)]
        darker = [max(0, int(c * factor)) for c in rgb]
        return "#%02x%02x%02x" % tuple(darker)

    def on_level_selected(self, level: int) -> None:
        logging.info(f"Level {level} selected. Starting level...")
        if callable(self.start_level_callback):
            self.start_level_callback(level)
