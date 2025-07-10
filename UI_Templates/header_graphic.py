# header_graphic.py
# Standalone header graphic for VaxityAutoTyper GUI
# This file was extracted from main.py

import tkinter as tk
from typing import Optional, Any

class HeaderGraphic(tk.Canvas):
    def __init__(self, master: Optional[tk.Widget] = None, width: int = 400, height: int = 80, **kwargs: Any) -> None:
        super().__init__(master, width=width, height=height, bg='black', highlightthickness=0, **kwargs)
        self.width = width
        self.height = height
        self.draw_graphic()

    def draw_graphic(self):
        # Example: Modern neon header with glow and gradient
        self.create_rectangle(0, 0, self.width, self.height, fill='#181A20', outline='')
        # Neon glow effect
        for i in range(10):
            self.create_oval(30-i, 20-i, 370+i, 60+i, outline=f'#00fff{9-i}', width=2, fill='')
        # Main neon text
        self.create_text(self.width//2, self.height//2, text="VaxityAutoTyper", font=("Segoe UI", 28, "bold"), fill="#00fff7", anchor="center")
        # Subtle accent lines
        self.create_line(40, 70, 360, 70, fill="#00fff7", width=2, stipple="gray50")
        self.create_line(40, 10, 360, 10, fill="#00fff7", width=1, stipple="gray25")
