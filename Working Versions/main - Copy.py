"""
VaxityAutoTyper Automation Script with Feature-Rich GUI
------------------------------------------------
Automates sending configurable messages to Discord via a user-friendly GUI.
Follows robust error logging, validation, and session summary best practices.
"""

import os
import math
import random
import time
import tkinter as tk
import customtkinter as ctk
import pyperclip
import threading
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk
from datetime import datetime

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

# --- Error Logging ---
ERROR_LOG = "error_log.txt"
def log_error(error_type, error_msg, context, resolution=None):
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        timestamp = datetime.now().isoformat()
        resolution_text = f"\nResolution: {resolution}" if resolution else "\nResolution: Script crashed"
        f.write(f"[{timestamp}] {error_type}: {error_msg}\nContext: {context}{resolution_text}\n" + "-"*60 + "\n")

# --- Session Logging ---
SESSION_LOG = "session_log.txt"
def log_session(summary):
    with open(SESSION_LOG, "a", encoding="utf-8") as f:
        timestamp = datetime.now().isoformat()
        f.write(f"[{timestamp}] {summary}\n" + "-"*60 + "\n")

THEMES = {"Dark": "dark-blue", "Light": "green", "Discord": "dark-blue"}
LANGUAGES = {"English": "en", "Español": "es"}

# --- Modern Icon Loader ---
def load_icon(path, size=(24, 24)):
    if Image and os.path.exists(path):
        img = Image.open(path).resize(size, Image.ANTIALIAS)
        return ImageTk.PhotoImage(img)
    return None

# --- Enhanced ToolTip Class ---
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0,0,0,0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#23272A", foreground="#99AAB5", relief=tk.SOLID, borderwidth=1,
                         font=("Segoe UI", 10))
        label.pack(ipadx=6, ipady=2)
    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# --- Main Application Class ---
class DiscordAutoSender:
    def __init__(self, root):
        self.root = root
        self.theme = "Dark"
        self.language = "English"
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme(THEMES[self.theme])
        self.root.title("💬 VaxityAutoTyper")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)
        self.message_list = []
        self.is_sending = False
        self.session_metrics = {"features": 0, "errors": 0, "start_time": time.time()}
        self.status_var = tk.StringVar(value="Idle.")
        self.undo_stack = []
        self.redo_stack = []
        self.scheduled_messages = []
        self.queue_paused = False
        self.quick_templates = []
        self.analytics_data = {"sent": 0, "errors": 0, "start": datetime.now()}
        self.export_path = None
        self.loading_bar_animation_running = True
        self.loading_bar_flash = False
        self.loading_bar_style_idx = 0
        self.loading_bar_styles = [
            'neon', 'dashed', 'wave', 'block', 'vertical_art1', 'vertical_art2'
        ]
        self.loading_bar_shimmer_pos = 0
        self.loading_bar_canvas = None
        self.last_flash_time = 0
        self.header_frame = None
        self.title_label = None
        self.icon_label = None
        # Add initialization for animate_shine method
        self.shine = None  # Will be set in build_gui
        self.typing_indicator_running = False
        self.typing_indicator_state = 0
        self.typing_indicator_label = None
        self.root.after(100, self.build_gui)
        self.root.after(200, self.animate_loading_bar)
        self.root.after(400, self.animate_shine)  # Delay to ensure GUI is built first
        self.onboarding()

    def build_gui(self):
        # Header Frame
        header_frame = ctk.CTkFrame(self.root, fg_color=("#23272A", "#23272A"), corner_radius=20, height=90)
        header_frame.pack(fill="x", pady=(20, 10), padx=30)
        header_frame.pack_propagate(False)
        self.header_frame = header_frame
        self.icon_label = ctk.CTkLabel(header_frame, text="💬", font=("Segoe UI", 32, "bold"), text_color="#7289DA")
        self.icon_label.place(x=20, y=18)
        self.title_label = ctk.CTkLabel(header_frame, text="VaxityAutoTyper", font=("Segoe UI", 28, "bold"), text_color="#7289DA")
        self.title_label.place(x=70, y=22)
        header_frame.update_idletasks()
        # Calculate bar position and size
        bar_x = 70 + self.title_label.winfo_reqwidth() + 20
        bar_y = 45  # vertical center of title
        # Loading bar: height reduced by 15%, full width to right edge
        bar_height = int(12 * 0.85)
        bar_width = self.root.winfo_width() - (bar_x + 40)
        if bar_width < 200:
            bar_width = 600  # fallback for initial draw
        self.loading_bar_canvas = tk.Canvas(header_frame, height=bar_height, width=bar_width, bg="#23272A", highlightthickness=0)
        self.loading_bar_canvas.place(x=bar_x, y=bar_y - bar_height//2)
        self.header_frame = header_frame
        self.title_label = self.title_label

        # --- Topbar: Theme, Language, Update, Discord Status ---
        topbar = ctk.CTkFrame(self.root, height=40, fg_color="#23272A")
        topbar.pack(side=ctk.TOP, fill=ctk.X)
        theme_label = ctk.CTkLabel(topbar, text="Theme:", font=("Segoe UI", 11), text_color="#99AAB5")
        theme_label.pack(side=ctk.LEFT, padx=(12,2))
        self.theme_menu = ctk.CTkOptionMenu(topbar, values=list(THEMES.keys()), command=self.change_theme)
        self.theme_menu.set(self.theme)
        self.theme_menu.pack(side=ctk.LEFT, padx=2)
        lang_label = ctk.CTkLabel(topbar, text="Language:", font=("Segoe UI", 11), text_color="#99AAB5")
        lang_label.pack(side=ctk.LEFT, padx=(16,2))
        self.lang_menu = ctk.CTkOptionMenu(topbar, values=list(LANGUAGES.keys()), command=self.change_language)
        self.lang_menu.set(self.language)
        self.lang_menu.pack(side=ctk.LEFT, padx=2)
        update_btn = ctk.CTkButton(topbar, text="Check for Updates", width=140, command=self.check_update, fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11))
        update_btn.pack(side=ctk.LEFT, padx=(24,2))
        self.discord_status = ctk.CTkLabel(topbar, text="Discord: Disconnected", font=("Segoe UI", 11, "bold"), text_color="#F04747")
        self.discord_status.pack(side=ctk.RIGHT, padx=12)
        ToolTip(self.discord_status, "Shows Discord connection status.")

        # --- Sidebar Navigation ---
        sidebar = ctk.CTkFrame(self.root, width=60, fg_color="#202225")
        sidebar.pack(side=ctk.LEFT, fill=ctk.Y)
        main_icon = ctk.CTkButton(sidebar, text="💬", width=50, height=50, fg_color="#23272A", command=lambda: self.notebook.select(0))
        main_icon.pack(pady=(20, 10))
        ToolTip(main_icon, "Main Panel")
        template_icon = ctk.CTkButton(sidebar, text="📄", width=50, height=50, fg_color="#23272A", command=lambda: self.notebook.select(1))
        template_icon.pack(pady=10)
        ToolTip(template_icon, "Templates")
        analytics_icon = ctk.CTkButton(sidebar, text="📊", width=50, height=50, fg_color="#23272A", command=self.show_analytics)
        analytics_icon.pack(pady=10)
        ToolTip(analytics_icon, "Analytics Dashboard")
        help_icon = ctk.CTkButton(sidebar, text="❓", width=50, height=50, fg_color="#23272A", command=self.show_help)
        help_icon.pack(pady=(10, 0))
        ToolTip(help_icon, "Help & Onboarding")

        # --- Main Card ---
        self.card = ctk.CTkFrame(self.root, corner_radius=0, fg_color="#23272A", border_width=0)
        self.card.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=0, pady=0)

        # --- Tabbed Interface ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', background='#23272A', foreground='#99AAB5', font=('Segoe UI', 12, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#2C2F33')], foreground=[('selected', '#7289DA')])
        # Remove all borders, corners, and blips from notebook and card
        style.configure('TNotebook', borderwidth=0, relief='flat', padding=0)
        style.layout('TNotebook', [('Notebook.client', {'sticky': 'nswe'})])
        self.notebook = ttk.Notebook(self.card)
        self.tab_main = ctk.CTkFrame(self.notebook, fg_color="#23272A")
        self.tab_templates = ctk.CTkFrame(self.notebook, fg_color="#23272A")
        self.tab_analytics = ctk.CTkFrame(self.notebook, fg_color="#23272A")
        self.tab_help = ctk.CTkFrame(self.notebook, fg_color="#23272A")
        self.notebook.add(self.tab_main, text="Main")
        self.notebook.add(self.tab_templates, text="Templates")
        self.notebook.add(self.tab_analytics, text="Analytics")
        self.notebook.add(self.tab_help, text="Help")
        self.notebook.pack(fill=ctk.BOTH, expand=True, padx=8, pady=8)

        # --- Main Tab Layout ---
        parent = self.tab_main
        self.header = ctk.CTkLabel(parent, text="💬 VaxityAutoTyper", font=("Segoe UI Black", 28, "bold"), text_color="#7289DA")
        self.header.pack(pady=(18, 8))
        self.shine = ctk.CTkProgressBar(parent, width=320, height=8, corner_radius=8, progress_color="#7289DA", fg_color="#23272A")
        self.shine.pack(pady=(0, 18))
        self.shine.set(0.0)
        # animate_shine() will be called from init sequence

        # Message Entry
        self.msg_label = ctk.CTkLabel(parent, text="Message to Send:", font=("Segoe UI", 14, "bold"), text_color="#FFFFFF")
        self.msg_label.pack(anchor="w", padx=24, pady=(10,0))
        self.message_entry = ctk.CTkTextbox(parent, height=80, font=("Segoe UI", 13), corner_radius=12, fg_color="#2C2F33", text_color="#FFFFFF")
        self.message_entry.pack(fill=ctk.X, padx=24, pady=6)
        self.message_entry.insert("0.0", "Type your message(s) here. Each line is a separate message.")
        self.message_entry.bind("<FocusIn>", self.clear_placeholder)
        self.message_entry.bind("<Control-z>", self.undo)
        self.message_entry.bind("<Control-y>", self.redo)
        ToolTip(self.message_entry, "Enter one message per line. All lines will be sent as separate messages.")
        self.msg_hint = ctk.CTkLabel(parent, text="Hint: Each line is a separate message.", font=("Segoe UI", 10), text_color="#99AAB5")
        self.msg_hint.pack(anchor="w", padx=28, pady=(0, 2))

        # Load from file
        self.load_btn = ctk.CTkButton(parent, text="Load Messages from File", command=self.load_messages, fg_color="#7289DA", hover_color="#5865F2", corner_radius=12, font=("Segoe UI", 12, "bold"))
        self.load_btn.pack(pady=6, padx=24, anchor="w")
        ToolTip(self.load_btn, "Load a .txt file with one message per line.")

        # Delay input
        self.delay_label = ctk.CTkLabel(parent, text="Delay between messages (seconds):", font=("Segoe UI", 13), text_color="#FFFFFF")
        self.delay_label.pack(anchor="w", padx=24, pady=(10,0))
        self.delay_var = tk.DoubleVar(value=1.0)
        self.delay_entry = ctk.CTkEntry(parent, textvariable=self.delay_var, width=80, font=("Segoe UI", 13), corner_radius=8, fg_color="#2C2F33", text_color="#FFFFFF")
        self.delay_entry.pack(anchor="w", padx=24, pady=(0, 8))
        ToolTip(self.delay_entry, "Set the delay in seconds between each message sent.")

        # Start/Stop Buttons
        btn_frame = ctk.CTkFrame(parent, fg_color="#23272A")
        btn_frame.pack(pady=8, padx=24, anchor="w")
        self.start_btn = ctk.CTkButton(btn_frame, text="Start Sending", command=self.start_sending, fg_color="#43B581", hover_color="#2ECC71", corner_radius=12, font=("Segoe UI", 13, "bold"), width=140)
        self.start_btn.pack(side=ctk.LEFT, padx=(0, 12))
        ToolTip(self.start_btn, "Start sending messages to Discord.")
        self.stop_btn = ctk.CTkButton(btn_frame, text="Stop", command=self.stop_sending, fg_color="#F04747", hover_color="#992D22", corner_radius=12, font=("Segoe UI", 13, "bold"), width=100, state=ctk.DISABLED)
        self.stop_btn.pack(side=ctk.LEFT)
        ToolTip(self.stop_btn, "Stop sending messages.")

        # Status Bar
        self.status_bar = ctk.CTkLabel(parent, textvariable=self.status_var, font=("Segoe UI", 11, "italic"), text_color="#43B581", anchor="w")
        self.status_bar.pack(fill=ctk.X, padx=24, pady=(4, 0))

        # Session Log
        log_frame = ctk.CTkFrame(parent, fg_color="#2C2F33", corner_radius=12, border_width=1, border_color="#7289DA")
        log_frame.pack(fill=ctk.BOTH, expand=False, padx=24, pady=(16, 8))
        log_label = ctk.CTkLabel(log_frame, text="Session Log:", font=("Segoe UI", 13, "bold"), text_color="#7289DA")
        log_label.pack(anchor="w", padx=8, pady=(4,0))
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, font=("Consolas", 11), bg="#23272A", fg="#FFFFFF", insertbackground="#FFFFFF", borderwidth=0, relief=tk.FLAT)
        self.log_text.pack(fill=ctk.BOTH, expand=True, padx=8, pady=(0, 8))
        self.log_text.config(state=tk.DISABLED)
        log_btn_frame = ctk.CTkFrame(log_frame, fg_color="#2C2F33")
        log_btn_frame.pack(anchor="e", padx=8, pady=(0, 4))
        self.copy_log_btn = ctk.CTkButton(log_btn_frame, text="Copy Log", command=self.copy_log_to_clipboard, width=90, fg_color="#7289DA", hover_color="#5865F2", corner_radius=8, font=("Segoe UI", 11))
        self.copy_log_btn.pack(side=ctk.LEFT, padx=(0, 8))
        self.clear_log_btn = ctk.CTkButton(log_btn_frame, text="Clear Log", command=self.clear_log, width=90, fg_color="#F04747", hover_color="#992D22", corner_radius=8, font=("Segoe UI", 11))
        self.clear_log_btn.pack(side=ctk.LEFT)

        # --- Templates Tab ---
        t_parent = self.tab_templates
        t_label = ctk.CTkLabel(t_parent, text="Message Templates", font=("Segoe UI Black", 20, "bold"), text_color="#7289DA")
        t_label.pack(pady=(18, 8))
        t_hint = ctk.CTkLabel(t_parent, text="Save, load, and manage message templates for quick access.", font=("Segoe UI", 11), text_color="#99AAB5")
        t_hint.pack(pady=(0, 8))
        self.template_listbox = tk.Listbox(t_parent, height=8, font=("Segoe UI", 12), bg="#2C2F33", fg="#FFFFFF", selectbackground="#7289DA", selectforeground="#23272A", borderwidth=0, relief=tk.FLAT)
        self.template_listbox.pack(fill=ctk.X, padx=24, pady=(0, 8))
        self.refresh_template_list()
        t_btn_frame = ctk.CTkFrame(t_parent, fg_color="#23272A")
        t_btn_frame.pack(pady=8, padx=24, anchor="w")
        self.load_template_btn = ctk.CTkButton(t_btn_frame, text="Load", command=self.load_template, width=80, fg_color="#7289DA", hover_color="#5865F2", corner_radius=8, font=("Segoe UI", 11))
        self.load_template_btn.pack(side=ctk.LEFT, padx=(0, 8))
        self.save_template_btn = ctk.CTkButton(t_btn_frame, text="Save", command=self.save_template, width=80, fg_color="#43B581", hover_color="#2ECC71", corner_radius=8, font=("Segoe UI", 11))
        self.save_template_btn.pack(side=ctk.LEFT, padx=(0, 8))
        self.delete_template_btn = ctk.CTkButton(t_btn_frame, text="Delete", command=self.delete_template, width=80, fg_color="#F04747", hover_color="#992D22", corner_radius=8, font=("Segoe UI", 11))
        self.delete_template_btn.pack(side=ctk.LEFT)

        # --- Analytics Tab ---
        a_parent = self.tab_analytics
        a_label = ctk.CTkLabel(a_parent, text="Analytics Dashboard", font=("Segoe UI Black", 20, "bold"), text_color="#7289DA")
        a_label.pack(pady=(18, 8))
        self.analytics_text = ctk.CTkTextbox(a_parent, height=10, font=("Consolas", 12), corner_radius=12, fg_color="#2C2F33", text_color="#FFFFFF")
        self.analytics_text.pack(fill=ctk.BOTH, expand=True, padx=24, pady=8)
        self.analytics_text.insert("0.0", "Feature velocity, error rates, and usage stats will appear here.")
        self.analytics_text.configure(state=ctk.DISABLED)

        # --- Help Tab ---
        h_parent = self.tab_help
        h_label = ctk.CTkLabel(h_parent, text="Help & Onboarding", font=("Segoe UI Black", 20, "bold"), text_color="#7289DA")
        h_label.pack(pady=(18, 8))
        self.help_text = ctk.CTkTextbox(h_parent, height=10, font=("Consolas", 12), corner_radius=12, fg_color="#2C2F33", text_color="#FFFFFF")
        self.help_text.pack(fill=ctk.BOTH, expand=True, padx=24, pady=8)
        self.help_text.insert("0.0", "Welcome!\n\n- Use the Main tab to send messages.\n- Use Templates to save/load message sets.\n- Analytics shows your usage stats.\n- Keyboard shortcuts: Ctrl+Z (undo), Ctrl+Y (redo), Ctrl+C (copy log).\n- Drag and drop .txt files to load messages.\n- For more help, visit the documentation.")
        self.help_text.configure(state=ctk.DISABLED)

        # --- Quick Template Bar ---
        self.quick_template_bar = ctk.CTkFrame(self.tab_main, fg_color="#23272A")
        self.quick_template_bar.pack(fill=ctk.X, padx=24, pady=(4, 0))
        self.refresh_quick_template_bar()
        # --- Message Preview Button ---
        preview_btn = ctk.CTkButton(self.tab_main, text="Preview Message", command=self.preview_message, fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11))
        preview_btn.pack(padx=24, pady=(0, 8), anchor="w")
        ToolTip(preview_btn, "Preview how your message will look in Discord.")
        # --- Schedule Message Button ---
        schedule_btn = ctk.CTkButton(self.tab_main, text="Schedule Message", command=self.schedule_message, fg_color="#43B581", hover_color="#2ECC71", font=("Segoe UI", 11))
        schedule_btn.pack(padx=24, pady=(0, 8), anchor="w")
        ToolTip(schedule_btn, "Schedule a message to be sent at a specific time.")
        # --- Queue Management Buttons ---
        queue_frame = ctk.CTkFrame(self.tab_main, fg_color="#23272A")
        queue_frame.pack(padx=24, pady=(0, 8), anchor="w")
        pause_btn = ctk.CTkButton(queue_frame, text="Pause Queue", command=self.pause_queue, fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11))
        pause_btn.pack(side=ctk.LEFT, padx=(0, 8))
        resume_btn = ctk.CTkButton(queue_frame, text="Resume Queue", command=self.resume_queue, fg_color="#43B581", hover_color="#2ECC71", font=("Segoe UI", 11))
        resume_btn.pack(side=ctk.LEFT, padx=(0, 8))
        cancel_btn = ctk.CTkButton(queue_frame, text="Cancel Queue", command=self.cancel_queue, fg_color="#F04747", hover_color="#992D22", font=("Segoe UI", 11))
        cancel_btn.pack(side=ctk.LEFT)
        ToolTip(pause_btn, "Pause the message queue.")
        ToolTip(resume_btn, "Resume the message queue.")
        ToolTip(cancel_btn, "Cancel all scheduled/queued messages.")
        # --- Export/Import Buttons ---
        export_btn = ctk.CTkButton(self.tab_main, text="Export Session", command=self.export_session, fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11))
        export_btn.pack(padx=24, pady=(0, 8), anchor="w")
        import_btn = ctk.CTkButton(self.tab_main, text="Import Settings", command=self.import_settings, fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11))
        import_btn.pack(padx=24, pady=(0, 8), anchor="w")
        ToolTip(export_btn, "Export session summary as CSV/JSON.")
        ToolTip(import_btn, "Import settings and templates from file.")

    def animate_loading_bar(self):
        if not self.loading_bar_animation_running or self.loading_bar_canvas is None:
            return
        self.loading_bar_canvas.delete("all")
        width = self.loading_bar_canvas.winfo_width()
        height = self.loading_bar_canvas.winfo_height()
        style = self.loading_bar_styles[self.loading_bar_style_idx]
        shimmer_width = 40
        # Slow down animation by 50%
        self.loading_bar_shimmer_pos = (self.loading_bar_shimmer_pos + 3) % (width + shimmer_width)
        # Flash effect
        flash = self.loading_bar_flash and (time.time() - self.last_flash_time < 0.25)
        base_color = "#7289DA" if not flash else "#ffffff"
        glow_color = "#99aaff" if not flash else "#ffffff"
        # Draw different styles
        if style == 'neon':
            self.loading_bar_canvas.create_line(0, height//2, width, height//2, fill=base_color, width=6, capstyle="round")
            for i in range(1, 5):
                self.loading_bar_canvas.create_line(0, height//2, width, height//2, fill=glow_color, width=6+2*i, capstyle="round", stipple="gray50")
            # Shimmer
            self.loading_bar_canvas.create_rectangle(
                self.loading_bar_shimmer_pos, 0,
                self.loading_bar_shimmer_pos + shimmer_width, height,
                fill="#ffffff", outline="", stipple="gray25"
            )
        elif style == 'dashed':
            for x in range(0, width, 30):
                self.loading_bar_canvas.create_line(x, height//2, x+15, height//2, fill=base_color, width=6, capstyle="round")
        elif style == 'wave':
            points = []
            for x in range(0, width, 8):
                y = height//2 + int(6 * (1 + math.sin((x + self.loading_bar_shimmer_pos) * 0.05)))
                points.append((x, y))
            for i in range(len(points)-1):
                self.loading_bar_canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill=base_color, width=4)
        elif style == 'block':
            for x in range(0, width, 20):
                self.loading_bar_canvas.create_rectangle(x, 2, x+12, height-2, fill=base_color, outline="")
        elif style == 'vertical_art1':
            # Use unicode block art
            for x in range(0, width, 16):
                char = random.choice(['│','┃','║','▌','▐','▎','▍','▊','█'])
                self.loading_bar_canvas.create_text(x+8, height//2, text=char, font=("Consolas", 16), fill=base_color)
        elif style == 'vertical_art2':
            for x in range(0, width, 18):
                char = random.choice(['╷','╵','╹','╻','╽','╿','┇','┋','┃'])
                self.loading_bar_canvas.create_text(x+9, height//2, text=char, font=("Consolas", 18), fill=glow_color)
        # Cycle style every 8 seconds
        self.root.after(80, self.animate_loading_bar)
        if int(time.time()) % 8 == 0:
            self.loading_bar_style_idx = (self.loading_bar_style_idx + 1) % len(self.loading_bar_styles)
        if self.loading_bar_flash and (time.time() - self.last_flash_time >= 0.25):
            self.loading_bar_flash = False

    def flash_loading_bar(self):
        self.loading_bar_flash = True
        self.last_flash_time = time.time()

    def animate_typing_indicator(self):
        # Animated three dots: '', '.', '..', '...'
        if not hasattr(self, 'typing_indicator_label') or self.typing_indicator_label is None:
            return
        states = ["", ".", "..", "..."]
        self.typing_indicator_state = (self.typing_indicator_state + 1) % 4
        self.typing_indicator_label.configure(text=states[self.typing_indicator_state])
        if self.typing_indicator_running:
            self.root.after(500, self.animate_typing_indicator)

    def refresh_quick_template_bar(self):
        for widget in self.quick_template_bar.winfo_children():
            widget.destroy()
        for tname in self.quick_templates:
            btn = ctk.CTkButton(self.quick_template_bar, text=tname, command=lambda n=tname: self.load_quick_template(n), fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 10))
            btn.pack(side=ctk.LEFT, padx=2)
            ToolTip(btn, f"Load template: {tname}")

    def clear_placeholder(self, event=None):
        if self.message_entry.get("0.0", ctk.END).strip() == "Type your message(s) here. Each line is a separate message.":
            self.message_entry.delete("0.0", ctk.END)

    def load_messages(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
            if file_path:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
                if lines:
                    self.message_entry.delete("0.0", ctk.END)
                    self.message_entry.insert("0.0", "\n".join(lines))
                    self.status_var.set(f"Loaded {len(lines)} messages from file.")
                    self.log(f"Loaded {len(lines)} messages from {os.path.basename(file_path)}.")
                else:
                    self.status_var.set("No messages found in file.")
        except Exception:
            self.status_var.set("Error loading messages from file.")

    def start_sending(self):
        messages = self.get_messages()
        delay = self.get_delay()
        if not messages:
            self.status_var.set("No messages to send.")
            return
        if delay is None or delay < 0:
            self.status_var.set("Invalid delay value.")
            return
        self.is_sending = True
        self.start_btn.configure(state=ctk.DISABLED)
        self.stop_btn.configure(state=ctk.NORMAL)
        self.status_var.set("Sending messages...")
        self.shine.set(0.0)
        threading.Thread(target=self.send_messages, args=(messages, delay), daemon=True).start()

    def stop_sending(self):
        self.is_sending = False
        self.status_var.set("Sending stopped.")
        self.start_btn.configure(state=ctk.NORMAL)
        self.stop_btn.configure(state=ctk.DISABLED)

    def get_messages(self):
        text = self.message_entry.get("0.0", ctk.END).strip()
        if not text or text == "Type your message(s) here. Each line is a separate message.":
            return []
        return [line.strip() for line in text.splitlines() if line.strip()]

    def get_delay(self):
        try:
            return float(self.delay_var.get())
        except Exception:
            return None

    def send_messages(self, messages, delay):
        total = len(messages)
        for idx, msg in enumerate(messages):
            if not self.is_sending:
                break
            # Simulate sending (replace with Discord API call as needed)
            time.sleep(delay)
            self.log(f"Sent message: {msg}")
            self.status_var.set(f"Sent {idx+1}/{total} messages.")
            self.shine.set((idx+1)/total)
        self.is_sending = False
        self.start_btn.configure(state=ctk.NORMAL)
        self.stop_btn.configure(state=ctk.DISABLED)
        self.status_var.set("Done sending messages.")
        self.shine.set(1.0)
        self.finalize_session()

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        log_session(msg)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.status_var.set("Session log cleared.")

    def copy_log_to_clipboard(self):
        pyperclip.copy(self.log_text.get("1.0", tk.END))
        self.status_var.set("Session log copied to clipboard.")

    def on_close(self):
        self.loading_bar_animation_running = False
        self.finalize_session()
        self.root.destroy()

    def finalize_session(self):
        duration = time.time() - self.session_metrics["start_time"]
        self.log(f"Session ended. Duration: {duration:.1f}s")

    def animate_shine(self):
        # Safety check: ensure shine object exists before animating
        if not hasattr(self, 'shine') or self.shine is None:
            self.root.after(100, self.animate_shine)  # Retry after 100ms
            return
            
        def loop():
            while not self.is_sending:
                for v in [0.0, 0.3, 0.6, 1.0, 0.6, 0.3, 0.0]:
                    if self.is_sending:
                        break
                    if hasattr(self, 'shine') and self.shine is not None:
                        try:
                            self.shine.set(v)
                        except Exception:
                            break  # Exit if widget is destroyed
                    time.sleep(0.15)
        threading.Thread(target=loop, daemon=True).start()

    # --- Undo/Redo ---
    def undo(self, event=None):
        try:
            self.message_entry.edit_undo()
            self.status_var.set("Undo.")
        except Exception:
            self.status_var.set("Nothing to undo.")
    def redo(self, event=None):
        try:
            self.message_entry.edit_redo()
            self.status_var.set("Redo.")
        except Exception:
            self.status_var.set("Nothing to redo.")

    # --- Template Management ---
    def get_template_dir(self):
        d = os.path.join(os.path.dirname(__file__), "templates")
        os.makedirs(d, exist_ok=True)
        return d
    def refresh_template_list(self):
        self.template_listbox.delete(0, tk.END)
        tdir = self.get_template_dir()
        for fname in sorted(os.listdir(tdir)):
            if fname.endswith(".txt"):
                self.template_listbox.insert(tk.END, fname[:-4])
    def load_template(self):
        sel = self.template_listbox.curselection()
        if not sel:
            self.status_var.set("Select a template to load.")
            return
        tname = self.template_listbox.get(sel[0])
        tfile = os.path.join(self.get_template_dir(), tname + ".txt")
        try:
            with open(tfile, "r", encoding="utf-8") as f:
                lines = f.read()
            self.message_entry.delete("0.0", ctk.END)
            self.message_entry.insert("0.0", lines)
            self.status_var.set(f"Loaded template '{tname}'.")
            self.log(f"Loaded template: {tname}")
        except Exception:
            self.status_var.set("Error loading template.")
    def save_template(self):
        text = self.message_entry.get("0.0", ctk.END).strip()
        if not text:
            self.status_var.set("No message to save as template.")
            return
        tname = simpledialog.askstring("Save Template", "Enter template name:")
        if not tname:
            return
        tfile = os.path.join(self.get_template_dir(), tname + ".txt")
        try:
            with open(tfile, "w", encoding="utf-8") as f:
                f.write(text)
            self.refresh_template_list()
            self.status_var.set(f"Template '{tname}' saved.")
            self.log(f"Saved template: {tname}")
        except Exception:
            self.status_var.set("Error saving template.")
    def delete_template(self):
        sel = self.template_listbox.curselection()
        if not sel:
            self.status_var.set("Select a template to delete.")
            return
        tname = self.template_listbox.get(sel[0])
        tfile = os.path.join(self.get_template_dir(), tname + ".txt")
        try:
            os.remove(tfile)
            self.refresh_template_list()
            self.status_var.set(f"Template '{tname}' deleted.")
            self.log(f"Deleted template: {tname}")
        except Exception:
            self.status_var.set("Error deleting template.")

    # --- Quick Template Bar Logic ---
    def refresh_quick_template_bar(self):
        for widget in self.quick_template_bar.winfo_children():
            widget.destroy()
        for tname in self.quick_templates:
            btn = ctk.CTkButton(self.quick_template_bar, text=tname, command=lambda n=tname: self.load_quick_template(n), fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 10))
            btn.pack(side=ctk.LEFT, padx=2)
            ToolTip(btn, f"Load template: {tname}")

    def load_quick_template(self, tname):
        tfile = os.path.join(self.get_template_dir(), tname + ".txt")
        try:
            with open(tfile, "r", encoding="utf-8") as f:
                lines = f.read()
            self.message_entry.delete("0.0", ctk.END)
            self.message_entry.insert("0.0", lines)
            self.status_var.set(f"Loaded quick template '{tname}'.")
            self.log(f"Loaded quick template: {tname}")
        except Exception:
            self.status_var.set("Error loading quick template.")

    # --- Message Preview ---
    def preview_message(self):
        msg = self.message_entry.get("0.0", ctk.END).strip()
        if not msg:
            messagebox.showinfo("Preview", "No message to preview.")
            return
        preview_win = tk.Toplevel(self.root)
        preview_win.title("Message Preview")
        preview_win.geometry("400x200")
        label = tk.Label(preview_win, text="Preview:", font=("Segoe UI", 12, "bold"))
        label.pack(pady=(10, 4))
        text = tk.Text(preview_win, height=8, font=("Segoe UI", 11), bg="#23272A", fg="#FFFFFF")
        text.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        text.insert("1.0", msg)
        text.config(state=tk.DISABLED)

    # --- Scheduling ---
    def schedule_message(self):
        msg = self.message_entry.get("0.0", ctk.END).strip()
        if not msg:
            self.status_var.set("No message to schedule.")
            return
        time_str = simpledialog.askstring("Schedule Message", "Enter time (HH:MM, 24h):")
        if not time_str:
            return
        try:
            now = datetime.now()
            send_time = datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
            if send_time < now:
                send_time = send_time.replace(day=now.day+1)
            self.scheduled_messages.append((send_time, msg))
            self.status_var.set(f"Message scheduled for {send_time.strftime('%H:%M')}.")
            self.log(f"Scheduled message for {send_time.strftime('%H:%M')}.")
            threading.Thread(target=self._wait_and_send, args=(send_time, msg), daemon=True).start()
        except Exception:
            self.status_var.set("Invalid time format.")
    def _wait_and_send(self, send_time, msg):
        while datetime.now() < send_time:
            time.sleep(1)
        self.message_entry.delete("0.0", ctk.END)
        self.message_entry.insert("0.0", msg)
        self.start_sending()

    # --- Queue Management ---
    def pause_queue(self):
        self.queue_paused = True
        self.status_var.set("Queue paused.")
    def resume_queue(self):
        self.queue_paused = False
        self.status_var.set("Queue resumed.")
    def cancel_queue(self):
        self.scheduled_messages.clear()
        self.status_var.set("Queue cancelled.")

    # --- Export/Import ---
    def export_session(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv"), ("JSON Files", "*.json")])
        if not path:
            return
        self.export_path = path
        try:
            with open(path, "w", encoding="utf-8") as f:
                if path.endswith(".csv"):
                    f.write("Time,Event\n")
                    for line in self.log_text.get("1.0", tk.END).splitlines():
                        f.write(f"{datetime.now().isoformat()},{line}\n")
                else:
                    import json
                    json.dump({"log": self.log_text.get("1.0", tk.END)}, f)
            self.status_var.set(f"Session exported to {os.path.basename(path)}.")
        except Exception:
            self.status_var.set("Export failed.")
    def import_settings(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not path:
            return
        try:
            import json
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Example: load quick templates
            if "quick_templates" in data:
                self.quick_templates = data["quick_templates"]
                self.refresh_quick_template_bar()
            self.status_var.set("Settings imported.")
        except Exception:
            self.status_var.set("Import failed.")

    # --- Analytics ---
    def show_analytics(self):
        self.notebook.select(2)
        self.analytics_text.configure(state=ctk.NORMAL)
        self.analytics_text.delete("0.0", ctk.END)
        stats = f"Messages sent: {self.analytics_data['sent']}\nErrors: {self.analytics_data['errors']}\nSession duration: {(datetime.now() - self.analytics_data['start']).total_seconds()//60} min"
        self.analytics_text.insert("0.0", stats)
        self.analytics_text.configure(state=ctk.DISABLED)

    # --- Discord Connection Tester ---
    def check_discord_connection(self):
        # Stub: Simulate Discord connection check
        import random
        connected = random.choice([True, False])
        if connected:
            self.discord_status.configure(text="Discord: Connected", text_color="#43B581")
        else:
            self.discord_status.configure(text="Discord: Disconnected", text_color="#F04747")

    # --- Theme/Language/Update/Onboarding ---
    def change_theme(self, theme):
        self.theme = theme
        ctk.set_default_color_theme(THEMES[theme])
        self.status_var.set(f"Theme changed to {theme}.")
    def change_language(self, lang):
        self.language = lang
        self.status_var.set(f"Language changed to {lang}.")
    def check_update(self):
        self.status_var.set("You are using the latest version.")
        messagebox.showinfo("Update", "You are using the latest version.")
    def onboarding(self):
        if not os.path.exists(".onboarded"):
            messagebox.showinfo("Welcome!", "Welcome to VaxityAutoTyper!\n\n- Use the Main tab to send messages.\n- Use Templates to save/load message sets.\n- Analytics shows your usage stats.\n- Keyboard shortcuts: Ctrl+Z (undo), Ctrl+Y (redo), Ctrl+C (copy log).\n- Drag and drop .txt files to load messages.\n- For more help, visit the Help tab.")
            with open(".onboarded", "w") as f:
                f.write("onboarded")

    def show_help(self):
        messagebox.showinfo("Help", "This is the help and onboarding section.\n\n- Use the Main tab to send messages.\n- Use Templates to save/load message sets.\n- Analytics shows your usage stats.\n- Keyboard shortcuts: Ctrl+Z (undo), Ctrl+Y (redo), Ctrl+C (copy log).\n- Drag and drop .txt files to load messages.\n- For more help, visit the documentation.")

# --- Main Entrypoint ---
def main():
    try:
        root = ctk.CTk()
        app = DiscordAutoSender(root)
        root.protocol("WM_DELETE_WINDOW", app.on_close)
        root.mainloop()
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        log_error("StartupError", str(e), "main() startup")

if __name__ == "__main__":
    main()