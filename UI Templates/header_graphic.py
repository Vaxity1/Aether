"""
Header Graphic from VaxityAutoTyper (formerly Discord Automation Script)
Extracted for standalone use.
"""
import tkinter as tk
import customtkinter as ctk

class HeaderGraphic:
    def __init__(self, parent, title="VaxityAutoTyper"):
        self.frame = ctk.CTkFrame(parent, fg_color=("#23272A", "#23272A"), corner_radius=20, height=90)
        self.frame.pack(fill="x", pady=(20, 10), padx=30)
        self.frame.pack_propagate(False)
        self.icon_label = ctk.CTkLabel(self.frame, text="💬", font=("Segoe UI", 32, "bold"), text_color="#7289DA")
        self.icon_label.place(x=20, y=18)
        self.title_label = ctk.CTkLabel(self.frame, text=title, font=("Segoe UI", 28, "bold"), text_color="#7289DA")
        self.title_label.place(x=70, y=22)
        self.frame.update_idletasks()

    def get_frame(self):
        return self.frame
