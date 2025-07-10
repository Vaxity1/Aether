"""
Discord Automation Script with Feature-Rich GUI (Animated Chat Bubbles Version)
------------------------------------------------
This version replaces the loading bar with animated chat bubbles moving left to right.
"""

import tkinter as tk
import customtkinter as ctk
import time

class DiscordAutoSenderBubbles:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Automation Script - Chat Bubbles")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.bubble_animation_running = True
        self.bubble_canvas = None
        self.bubbles = []
        self.build_gui()
        self.animate_bubbles()
        self.onboarding()

    def build_gui(self):
        # Header Frame
        header_frame = ctk.CTkFrame(self.root, fg_color=("#23272A", "#23272A"), corner_radius=20, height=90)
        header_frame.pack(fill="x", pady=(20, 10), padx=30)
        header_frame.pack_propagate(False)
        icon_label = ctk.CTkLabel(header_frame, text="💬", font=("Segoe UI", 32, "bold"), text_color="#7289DA")
        icon_label.pack(side="left", padx=(20, 10), pady=10)
        title_label = ctk.CTkLabel(header_frame, text="Discord Automation Script", font=("Segoe UI", 28, "bold"), text_color="#7289DA")
        title_label.pack(side="left", pady=10)
        # Animated Chat Bubbles Loading Bar
        self.bubble_canvas = tk.Canvas(header_frame, height=30, width=120, bg="#23272A", highlightthickness=0)
        self.bubble_canvas.pack(side="left", padx=(20, 0), pady=10)
        self.init_bubbles()
        # ...rest of GUI...

    def init_bubbles(self):
        # Initialize 3 chat bubbles at the bottom of the canvas
        self.bubbles = [
            {'x': 20, 'y': 25, 'r': 7, 'color': '#7289DA', 'delay': 0},
            {'x': 60, 'y': 25, 'r': 7, 'color': '#7289DA', 'delay': 200},
            {'x': 100, 'y': 25, 'r': 7, 'color': '#7289DA', 'delay': 400},
        ]

    def animate_bubbles(self):
        if not self.bubble_animation_running or self.bubble_canvas is None:
            return
        self.bubble_canvas.delete("all")
        now = int(time.time() * 1000) % 1200
        for bubble in self.bubbles:
            # Animate each bubble rising and fading
            phase = ((now + bubble['delay']) % 1200) / 1200
            y = 25 - 10 * (1 - abs(0.5 - phase) * 2)  # Up and down
            # For neomorphic effect, add a soft shadow
            self.bubble_canvas.create_oval(
                bubble['x'] - bubble['r'] + 2, y - bubble['r'] + 2,
                bubble['x'] + bubble['r'] + 2, y + bubble['r'] + 2,
                fill="#1a1d20", outline="")
            self.bubble_canvas.create_oval(
                bubble['x'] - bubble['r'], y - bubble['r'],
                bubble['x'] + bubble['r'], y + bubble['r'],
                fill=bubble['color'], outline="")
        self.root.after(60, self.animate_bubbles)

    def onboarding(self):
        pass  # Placeholder for onboarding logic

    def on_close(self):
        self.bubble_animation_running = False
        self.root.destroy()

def main():
    root = ctk.CTk()
    app = DiscordAutoSenderBubbles(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
