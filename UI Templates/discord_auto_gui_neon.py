"""
Discord Automation Script GUI - Neon Glow Underline Version
Neomorphic, professional, clean design with neon-glow underline loading bar under header.
"""
import tkinter as tk
import customtkinter as ctk
import threading
import time

class DiscordAutoSenderNeon:
    def __init__(self, root):
        self.root = root
        self.root.title("Discord Automation Script - Neon Glow")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.neon_animation_running = True
        self.neon_canvas = None
        self.neon_shimmer_pos = 0
        self.build_gui()
        self.animate_neon_underline()
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
        # Neon Glow Underline Loading Bar
        self.neon_canvas = tk.Canvas(header_frame, height=12, width=180, bg="#23272A", highlightthickness=0)
        self.neon_canvas.pack(side="left", padx=(20, 0), pady=10)
        # ...rest of GUI...

    def animate_neon_underline(self):
        if not self.neon_animation_running or self.neon_canvas is None:
            return
        self.neon_canvas.delete("all")
        # Draw neon underline with animated shimmer
        width = 180
        height = 12
        base_color = "#7289DA"
        glow_color = "#99aaff"
        shimmer_width = 40
        self.neon_shimmer_pos = (self.neon_shimmer_pos + 6) % (width + shimmer_width)
        # Draw base neon line
        self.neon_canvas.create_line(0, height//2, width, height//2, fill=base_color, width=6, capstyle="round")
        # Draw glow
        for i in range(1, 5):
            self.neon_canvas.create_line(0, height//2, width, height//2, fill=glow_color, width=6+2*i, capstyle="round", stipple="gray50")
        # Draw shimmer
        self.neon_canvas.create_rectangle(
            self.neon_shimmer_pos, 0,
            self.neon_shimmer_pos + shimmer_width, height,
            fill="#ffffff", outline="", stipple="gray25"
        )
        self.root.after(40, self.animate_neon_underline)

    def onboarding(self):
        pass  # Placeholder for onboarding logic

    def on_close(self):
        self.neon_animation_running = False
        self.root.destroy()

def main():
    root = ctk.CTk()
    app = DiscordAutoSenderNeon(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
