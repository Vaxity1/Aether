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
from typing import Optional, Dict, List, Any, Union, Tuple
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk
from datetime import datetime
import json

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

# --- Error Logging ---
ERROR_LOG = "error_log.txt"
def log_error(error_type: str, error_msg: str, context: str, resolution: Optional[str] = None) -> None:
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        timestamp = datetime.now().isoformat()
        resolution_text = f"\nResolution: {resolution}" if resolution else "\nResolution: Script crashed"
        f.write(f"[{timestamp}] {error_type}: {error_msg}\nContext: {context}{resolution_text}\n" + "-"*60 + "\n")

# --- Session Logging ---
SESSION_LOG = "session_log.txt"
def log_session(summary: str) -> None:
    with open(SESSION_LOG, "a", encoding="utf-8") as f:
        timestamp = datetime.now().isoformat()
        f.write(f"[{timestamp}] {summary}\n" + "-"*60 + "\n")

# --- Enhanced Discord Rate Limiting System ---
class DiscordRateLimiter:
    """
    Intelligent rate limiting system for Discord API compliance.
    Implements exponential backoff, burst detection, and queue management.
    """
    def __init__(self):
        self.message_history: List[float] = []
        self.burst_threshold = 5  # messages per burst
        self.burst_window = 10    # seconds
        self.rate_limit = 0.5     # minimum seconds between messages
        self.exponential_delay = 1.0
        self.max_delay = 30.0
        self.queue_size = 0
        self.total_processed = 0
        self.rate_limit_hits = 0
        self.last_burst_time = 0.0

    def can_send_message(self) -> bool:
        """Check if message can be sent based on current rate limits."""
        current_time = time.time()
        
        # Clean old history entries
        self.message_history = [t for t in self.message_history 
                               if current_time - t < self.burst_window]
        
        # Check burst limit
        if len(self.message_history) >= self.burst_threshold:
            self.last_burst_time = current_time
            return False
        
        # Check minimum delay
        if self.message_history and (current_time - self.message_history[-1]) < self.rate_limit:
            return False
        
        return True

    def register_message_sent(self) -> None:
        """Register a message as sent."""
        current_time = time.time()
        self.message_history.append(current_time)
        self.total_processed += 1
        self.exponential_delay = max(0.5, self.exponential_delay * 0.9)  # Decrease delay on success

    def register_rate_limit_hit(self) -> None:
        """Register a rate limit hit and increase delays."""
        self.rate_limit_hits += 1
        self.exponential_delay = min(self.max_delay, self.exponential_delay * 2.0)

    def get_recommended_delay(self) -> float:
        """Get the recommended delay before next message."""
        if not self.can_send_message():
            return self.exponential_delay
        return max(self.rate_limit, 0.1)

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue and rate limiting status."""
        current_time = time.time()
        recent_messages = len([t for t in self.message_history 
                              if current_time - t < self.burst_window])
        
        return {
            "can_send": self.can_send_message(),
            "recent_messages": recent_messages,
            "burst_threshold": self.burst_threshold,
            "recommended_delay": self.get_recommended_delay(),
            "total_processed": self.total_processed,
            "rate_limit_hits": self.rate_limit_hits,
            "exponential_delay": self.exponential_delay
        }
THEMES = {"Dark": "dark-blue", "Light": "green", "Discord": "dark-blue"}
LANGUAGES = {"English": "en", "Español": "es"}

# --- Modern Icon Loader ---
def load_icon(path: str, size: Tuple[int, int] = (24, 24)) -> Optional[Any]:
    if Image and os.path.exists(path):
        img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    return None

# --- Enhanced ToolTip Class ---
class ToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.tipwindow: Optional[tk.Toplevel] = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    
    def show_tip(self, event: Optional[tk.Event] = None) -> None:
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
    
    def hide_tip(self, event: Optional[tk.Event] = None) -> None:
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# --- Session Summary Logging ---
def write_session_summary(context: Dict[str, Any], accomplishments: Dict[str, Any], 
                          metrics: Dict[str, Any], learning: Dict[str, Any]) -> None:
    """
    Writes a full session summary to session_summary.log in the required format.
    Args:
        context (dict): Project context (phase, complexity, technical debt, etc.)
        accomplishments (dict): Session accomplishments (features, errors, refactoring, etc.)
        metrics (dict): Performance and quality metrics
        learning (dict): Learning outcomes and next session prep
    """
    timestamp = datetime.now().isoformat()
    summary = f"""## Session Summary - {timestamp}

### Context Analysis
- Project Phase: {context.get('development_phase', 'N/A')}
- Complexity Level: {context.get('complexity_level', 'N/A')}
- Error Rate: {metrics.get('error_rate', 'N/A')}
- Technical Debt: {context.get('technical_debt', 'N/A')}

### Adaptive Decisions
- Feature Count: {accomplishments.get('feature_count', 'N/A')}
- Priority Focus: {accomplishments.get('priority_focus', 'N/A')}
- Quality Gates: {accomplishments.get('quality_gates', 'N/A')}

### Accomplishments
- Errors Resolved: {accomplishments.get('errors_resolved', 'N/A')}
- Features Implemented: {accomplishments.get('features_implemented', 'N/A')}
- Refactoring Completed: {accomplishments.get('refactoring_completed', 'N/A')}
- Tests Added: {accomplishments.get('tests_added', 'N/A')}

### Learning Outcomes
- New Error Patterns: {learning.get('new_error_patterns', 'N/A')}
- Performance Improvements: {learning.get('performance_improvements', 'N/A')}
- Code Quality Enhancements: {learning.get('code_quality_enhancements', 'N/A')}
- User Experience Gains: {learning.get('user_experience_gains', 'N/A')}

### Next Session Preparation
- Priority Tasks: {learning.get('priority_tasks', 'N/A')}
- Technical Debt Items: {learning.get('technical_debt_items', 'N/A')}
- Performance Targets: {learning.get('performance_targets', 'N/A')}
- Learning Focus: {learning.get('learning_focus', 'N/A')}

### Metrics
- Session Duration: {metrics.get('session_duration', 'N/A')}
- Feature Velocity: {metrics.get('feature_velocity', 'N/A')}
- Error Resolution Rate: {metrics.get('error_resolution_rate', 'N/A')}
- Code Quality Score: {metrics.get('code_quality_score', 'N/A')}
- User Satisfaction: {metrics.get('user_satisfaction', 'N/A')}
"""
    with open("session_summary.log", "a", encoding="utf-8") as f:
        f.write(summary + "\n\n")

# --- Main Application Class ---
class DiscordAutoSender:
    def __init__(self, root: tk.Tk) -> None:
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
        
        # Initialize Enhanced Rate Limiter
        self.rate_limiter = DiscordRateLimiter()
        self.rate_limiter_status_label = None  # Will be set in build_gui
        self.root.after(100, self.build_gui)
        self.root.after(200, self.animate_loading_bar)
        # --- DEBUG: Confirm animate_shine presence ---
        print(f"[DEBUG] animate_shine in dir(self): {'animate_shine' in dir(self)}")
        print(f"[DEBUG] hasattr(self, 'animate_shine'): {hasattr(self, 'animate_shine')}")
        self.root.after(400, self.animate_shine)  # Delay to ensure GUI is built first
        self.root.after(1000, self.update_performance_metrics)  # Start metrics updates
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

        # --- Sidebar Navigation (now controls all panels, no tabs) ---
        sidebar = ctk.CTkFrame(self.root, width=60, fg_color="#202225")
        sidebar.pack(side=ctk.LEFT, fill=ctk.Y)
        self.panels = {}
        def show_panel(name):
            for n, panel in self.panels.items():
                panel.pack_forget()
            self.panels[name].pack(fill=ctk.BOTH, expand=True, padx=8, pady=8)
        main_icon = ctk.CTkButton(sidebar, text="💬", width=50, height=50, fg_color="#23272A", command=lambda: show_panel('main'))
        main_icon.pack(pady=(20, 10))
        ToolTip(main_icon, "Main Panel")
        template_icon = ctk.CTkButton(sidebar, text="📄", width=50, height=50, fg_color="#23272A", command=lambda: show_panel('templates'))
        template_icon.pack(pady=10)
        ToolTip(template_icon, "Templates")
        analytics_icon = ctk.CTkButton(sidebar, text="📊", width=50, height=50, fg_color="#23272A", command=lambda: show_panel('analytics'))
        analytics_icon.pack(pady=10)
        ToolTip(analytics_icon, "Analytics Dashboard")
        help_icon = ctk.CTkButton(sidebar, text="❓", width=50, height=50, fg_color="#23272A", command=lambda: show_panel('help'))
        help_icon.pack(pady=(10, 0))
        ToolTip(help_icon, "Help & Onboarding")

        # --- Main Card (no tabs, just panel switching) ---
        self.card = ctk.CTkFrame(self.root, corner_radius=0, fg_color="#23272A", border_width=0)
        self.card.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=0, pady=0)
        self.panels['main'] = ctk.CTkFrame(self.card, fg_color="#23272A")
        self.panels['templates'] = ctk.CTkFrame(self.card, fg_color="#23272A")
        self.panels['analytics'] = ctk.CTkFrame(self.card, fg_color="#23272A")
        self.panels['help'] = ctk.CTkFrame(self.card, fg_color="#23272A")
        # --- Main Tab Layout ---
        parent = self.panels['main']
        self.header = ctk.CTkLabel(parent, text="💬 VaxityAutoTyper", font=("Segoe UI Black", 28, "bold"), text_color="#7289DA")
        self.header.pack(pady=(18, 8))
        self.shine = ctk.CTkProgressBar(parent, width=320, height=8, corner_radius=8, progress_color="#7289DA", fg_color="#23272A")
        self.shine.pack(pady=(0, 18))
        self.shine.set(0.0)

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

        # Rate Limiter Status
        rate_frame = ctk.CTkFrame(parent, fg_color="#2C2F33", corner_radius=8)
        rate_frame.pack(fill=ctk.X, padx=24, pady=(8, 0))
        rate_label = ctk.CTkLabel(rate_frame, text="Rate Limiter Status:", font=("Segoe UI", 11, "bold"), text_color="#7289DA")
        rate_label.pack(anchor="w", padx=8, pady=(4,0))
        self.rate_limiter_status_label = ctk.CTkLabel(rate_frame, text="Ready", font=("Segoe UI", 10), text_color="#43B581", anchor="w")
        self.rate_limiter_status_label.pack(fill=ctk.X, padx=8, pady=(0, 4))
        ToolTip(self.rate_limiter_status_label, "Shows Discord rate limiting status and recommendations.")

        # Advanced Scheduling Interface
        sched_frame = ctk.CTkFrame(parent, fg_color="#2C2F33", corner_radius=12, border_width=1, border_color="#7289DA")
        sched_frame.pack(fill=ctk.X, padx=24, pady=(8, 0))
        sched_label = ctk.CTkLabel(sched_frame, text="📅 Advanced Scheduling:", font=("Segoe UI", 13, "bold"), text_color="#7289DA")
        sched_label.pack(anchor="w", padx=8, pady=(4,0))
        sched_controls = ctk.CTkFrame(sched_frame, fg_color="#23272A")
        sched_controls.pack(fill=ctk.X, padx=8, pady=(4, 8))
        # Time input
        time_label = ctk.CTkLabel(sched_controls, text="Time (HH:MM):", font=("Segoe UI", 11), text_color="#FFFFFF")
        time_label.pack(side=ctk.LEFT, padx=(0, 4))
        self.schedule_time_entry = ctk.CTkEntry(sched_controls, width=80, placeholder_text="14:30", font=("Segoe UI", 11))
        self.schedule_time_entry.pack(side=ctk.LEFT, padx=(0, 8))
        # Schedule button
        self.schedule_btn = ctk.CTkButton(sched_controls, text="Schedule", command=self.schedule_message_advanced, 
                                         fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11, "bold"), width=80)
        self.schedule_btn.pack(side=ctk.LEFT, padx=(0, 8))

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

        # --- Templates Panel Layout ---
        t_parent = self.panels['templates']
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

        # --- Analytics Panel Layout ---
        a_parent = self.panels['analytics']
        a_label = ctk.CTkLabel(a_parent, text="📊 Real-time Performance Dashboard", font=("Segoe UI", 18, "bold"), text_color="#7289DA")
        a_label.pack(pady=(18, 8))
        
        # Performance Metrics Grid
        metrics_grid = ctk.CTkFrame(a_parent, fg_color="#2C2F33", corner_radius=12)
        metrics_grid.pack(fill=ctk.X, padx=24, pady=8)
        
        # Metrics display
        self.metrics_labels = {}
        metrics_data = [
            ("Messages Sent", "sent_count", "#43B581"),
            ("Success Rate", "success_rate", "#7289DA"),
            ("Rate Limit Hits", "rate_hits", "#F04747"),
            ("Avg Send Time", "avg_time", "#99AAB5"),
            ("Queue Status", "queue_status", "#FAA61A"),
            ("Session Duration", "session_time", "#5865F2")
        ]
        
        row_frame = None
        for i, (label, key, color) in enumerate(metrics_data):
            if i % 3 == 0:  # New row every 3 items
                row_frame = ctk.CTkFrame(metrics_grid, fg_color="#23272A")
                row_frame.pack(fill=ctk.X, padx=8, pady=4)
            
            metric_frame = ctk.CTkFrame(row_frame, fg_color=color, corner_radius=8)
            metric_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=4, pady=4)
            
            metric_label = ctk.CTkLabel(metric_frame, text=label, font=("Segoe UI", 10, "bold"), text_color="#FFFFFF")
            metric_label.pack(pady=(4, 0))
            
            value_label = ctk.CTkLabel(metric_frame, text="0", font=("Segoe UI", 14, "bold"), text_color="#FFFFFF")
            value_label.pack(pady=(0, 4))
            
            self.metrics_labels[key] = value_label
        
        # Performance Chart (Text-based)
        chart_frame = ctk.CTkFrame(a_parent, fg_color="#2C2F33", corner_radius=12)
        chart_frame.pack(fill=ctk.BOTH, expand=True, padx=24, pady=8)
        chart_label = ctk.CTkLabel(chart_frame, text="📈 Performance History", font=("Segoe UI", 14, "bold"), text_color="#7289DA")
        chart_label.pack(pady=(8, 4))
        
        self.performance_chart = ctk.CTkTextbox(chart_frame, height=200, font=("Consolas", 10), fg_color="#23272A", text_color="#FFFFFF")
        self.performance_chart.pack(fill=ctk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        # Auto-refresh checkbox
        auto_refresh_frame = ctk.CTkFrame(a_parent, fg_color="#23272A")
        auto_refresh_frame.pack(fill=ctk.X, padx=24, pady=(0, 8))
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_refresh_cb = ctk.CTkCheckBox(auto_refresh_frame, text="Auto-refresh metrics (5s)", 
                                         variable=self.auto_refresh_var, font=("Segoe UI", 11))
        auto_refresh_cb.pack(side=ctk.LEFT, padx=8)
        
        refresh_btn = ctk.CTkButton(auto_refresh_frame, text="Refresh Now", command=self.update_performance_metrics,
                                   fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11), width=100)
        refresh_btn.pack(side=ctk.RIGHT, padx=8)

        # --- Help Panel Layout ---
        h_parent = self.panels['help']
        h_label = ctk.CTkLabel(h_parent, text="Help & Onboarding", font=("Segoe UI Black", 20, "bold"), text_color="#7289DA")
        h_label.pack(pady=(18, 8))
        self.help_text = ctk.CTkTextbox(h_parent, height=10, font=("Consolas", 12), corner_radius=12, fg_color="#2C2F33", text_color="#FFFFFF")
        self.help_text.pack(fill=ctk.BOTH, expand=True, padx=24, pady=8)
        self.help_text.insert("0.0", "Welcome!\n\n- Use the Main tab to send messages.\n- Use Templates to save/load message sets.\n- Analytics shows your usage stats.\n- Keyboard shortcuts: Ctrl+Z (undo), Ctrl+Y (redo), Ctrl+C (copy log).\n- Drag and drop .txt files to load messages.\n- For more help, visit the documentation.")
        self.help_text.configure(state=ctk.DISABLED)

        # --- Quick Template Bar ---
        self.quick_template_bar = ctk.CTkFrame(self.panels['main'], fg_color="#23272A")
        self.quick_template_bar.pack(fill=ctk.X, padx=24, pady=(4, 0))
        self.refresh_quick_template_bar()
        # --- Message Preview Button ---
        preview_btn = ctk.CTkButton(self.panels['main'], text="Preview Message", command=self.preview_message, fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11))
        preview_btn.pack(padx=24, pady=(0, 8), anchor="w")
        ToolTip(preview_btn, "Preview how your message will look in Discord.")
        # --- Schedule Message Button ---
        schedule_btn = ctk.CTkButton(self.panels['main'], text="Schedule Message", command=self.schedule_message, fg_color="#43B581", hover_color="#2ECC71", font=("Segoe UI", 11))
        schedule_btn.pack(padx=24, pady=(0, 8), anchor="w")
        ToolTip(schedule_btn, "Schedule a message to be sent at a specific time.")
        # --- Queue Management Buttons ---
        queue_frame = ctk.CTkFrame(self.panels['main'], fg_color="#23272A")
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
        export_btn = ctk.CTkButton(self.panels['main'], text="Export Session", command=self.export_session, fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11))
        export_btn.pack(padx=24, pady=(0, 8), anchor="w")
        import_btn = ctk.CTkButton(self.panels['main'], text="Import Settings", command=self.import_settings, fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11))
        import_btn.pack(padx=24, pady=(0, 8), anchor="w")
        ToolTip(export_btn, "Export session summary as CSV/JSON.")
        ToolTip(import_btn, "Import settings and templates from file.")

        # At the end, show main panel by default
        show_panel('main')

        # --- Advanced Scheduling Interface ---
        sched_frame = ctk.CTkFrame(parent, fg_color="#2C2F33", corner_radius=12, border_width=1, border_color="#7289DA")
        sched_frame.pack(fill=ctk.X, padx=24, pady=(8, 0))
        sched_label = ctk.CTkLabel(sched_frame, text="📅 Advanced Scheduling:", font=("Segoe UI", 13, "bold"), text_color="#7289DA")
        sched_label.pack(anchor="w", padx=8, pady=(4,0))
        
        sched_controls = ctk.CTkFrame(sched_frame, fg_color="#23272A")
        sched_controls.pack(fill=ctk.X, padx=8, pady=(4, 8))
        
        # Time input
        time_label = ctk.CTkLabel(sched_controls, text="Time (HH:MM):", font=("Segoe UI", 11), text_color="#FFFFFF")
        time_label.pack(side=ctk.LEFT, padx=(0, 4))
        self.schedule_time_entry = ctk.CTkEntry(sched_controls, width=80, placeholder_text="14:30", font=("Segoe UI", 11))
        self.schedule_time_entry.pack(side=ctk.LEFT, padx=(0, 8))
        
        # Date input
        date_label = ctk.CTkLabel(sched_controls, text="Date (Optional):", font=("Segoe UI", 11), text_color="#FFFFFF")
        date_label.pack(side=ctk.LEFT, padx=(0, 4))
        self.schedule_date_entry = ctk.CTkEntry(sched_controls, width=100, placeholder_text="2025-07-09", font=("Segoe UI", 11))
        self.schedule_date_entry.pack(side=ctk.LEFT, padx=(0, 8))
        
        # Repeat options
        repeat_label = ctk.CTkLabel(sched_controls, text="Repeat:", font=("Segoe UI", 11), text_color="#FFFFFF")
        repeat_label.pack(side=ctk.LEFT, padx=(0, 4))
        self.repeat_menu = ctk.CTkOptionMenu(sched_controls, values=["None", "Daily", "Weekly", "Monthly"], width=80)
        self.repeat_menu.pack(side=ctk.LEFT, padx=(0, 8))
        
        # Schedule button
        self.schedule_btn = ctk.CTkButton(sched_controls, text="Schedule", command=self.schedule_message_advanced, 
                                         fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11, "bold"), width=80)
        self.schedule_btn.pack(side=ctk.LEFT, padx=(0, 8))
        
        # Scheduled messages list
        self.scheduled_listbox = tk.Listbox(sched_frame, height=3, bg="#23272A", fg="#FFFFFF", 
                                           selectbackground="#7289DA", font=("Consolas", 10))
        self.scheduled_listbox.pack(fill=ctk.X, padx=8, pady=(0, 4))
        
        # Clear scheduled button
        clear_sched_btn = ctk.CTkButton(sched_frame, text="Clear All Scheduled", command=self.clear_scheduled_messages,
                                       fg_color="#F04747", hover_color="#992D22", font=("Segoe UI", 10), width=120)
        clear_sched_btn.pack(anchor="e", padx=8, pady=(0, 4))
        
        ToolTip(self.schedule_time_entry, "Enter time in 24-hour format (HH:MM)")
        ToolTip(self.schedule_date_entry, "Enter date in YYYY-MM-DD format (optional, defaults to today)")
        ToolTip(self.repeat_menu, "Set repeat frequency for scheduled messages")

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

        # --- Templates Panel Layout ---
        t_parent = self.panels['templates']
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

        # --- Analytics Panel Layout ---
        a_parent = self.panels['analytics']
        a_label = ctk.CTkLabel(a_parent, text="📊 Real-time Performance Dashboard", font=("Segoe UI", 18, "bold"), text_color="#7289DA")
        a_label.pack(pady=(18, 8))
        
        # Performance Metrics Grid
        metrics_grid = ctk.CTkFrame(a_parent, fg_color="#2C2F33", corner_radius=12)
        metrics_grid.pack(fill=ctk.X, padx=24, pady=8)
        
        # Metrics display
        self.metrics_labels = {}
        metrics_data = [
            ("Messages Sent", "sent_count", "#43B581"),
            ("Success Rate", "success_rate", "#7289DA"),
            ("Rate Limit Hits", "rate_hits", "#F04747"),
            ("Avg Send Time", "avg_time", "#99AAB5"),
            ("Queue Status", "queue_status", "#FAA61A"),
            ("Session Duration", "session_time", "#5865F2")
        ]
        
        row_frame = None
        for i, (label, key, color) in enumerate(metrics_data):
            if i % 3 == 0:  # New row every 3 items
                row_frame = ctk.CTkFrame(metrics_grid, fg_color="#23272A")
                row_frame.pack(fill=ctk.X, padx=8, pady=4)
            
            metric_frame = ctk.CTkFrame(row_frame, fg_color=color, corner_radius=8)
            metric_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=4, pady=4)
            
            metric_label = ctk.CTkLabel(metric_frame, text=label, font=("Segoe UI", 10, "bold"), text_color="#FFFFFF")
            metric_label.pack(pady=(4, 0))
            
            value_label = ctk.CTkLabel(metric_frame, text="0", font=("Segoe UI", 14, "bold"), text_color="#FFFFFF")
            value_label.pack(pady=(0, 4))
            
            self.metrics_labels[key] = value_label
        
        # Performance Chart (Text-based)
        chart_frame = ctk.CTkFrame(a_parent, fg_color="#2C2F33", corner_radius=12)
        chart_frame.pack(fill=ctk.BOTH, expand=True, padx=24, pady=8)
        chart_label = ctk.CTkLabel(chart_frame, text="📈 Performance History", font=("Segoe UI", 14, "bold"), text_color="#7289DA")
        chart_label.pack(pady=(8, 4))
        
        self.performance_chart = ctk.CTkTextbox(chart_frame, height=200, font=("Consolas", 10), fg_color="#23272A", text_color="#FFFFFF")
        self.performance_chart.pack(fill=ctk.BOTH, expand=True, padx=8, pady=(0, 8))
        
        # Auto-refresh checkbox
        auto_refresh_frame = ctk.CTkFrame(a_parent, fg_color="#23272A")
        auto_refresh_frame.pack(fill=ctk.X, padx=24, pady=(0, 8))
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_refresh_cb = ctk.CTkCheckBox(auto_refresh_frame, text="Auto-refresh metrics (5s)", 
                                         variable=self.auto_refresh_var, font=("Segoe UI", 11))
        auto_refresh_cb.pack(side=ctk.LEFT, padx=8)
        
        refresh_btn = ctk.CTkButton(auto_refresh_frame, text="Refresh Now", command=self.update_performance_metrics,
                                   fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11), width=100)
        refresh_btn.pack(side=ctk.RIGHT, padx=8)

        # --- Help Panel Layout ---
        h_parent = self.panels['help']
        h_label = ctk.CTkLabel(h_parent, text="Help & Onboarding", font=("Segoe UI Black", 20, "bold"), text_color="#7289DA")
        h_label.pack(pady=(18, 8))
        self.help_text = ctk.CTkTextbox(h_parent, height=10, font=("Consolas", 12), corner_radius=12, fg_color="#2C2F33", text_color="#FFFFFF")
        self.help_text.pack(fill=ctk.BOTH, expand=True, padx=24, pady=8)
        self.help_text.insert("0.0", "Welcome!\n\n- Use the Main tab to send messages.\n- Use Templates to save/load message sets.\n- Analytics shows your usage stats.\n- Keyboard shortcuts: Ctrl+Z (undo), Ctrl+Y (redo), Ctrl+C (copy log).\n- Drag and drop .txt files to load messages.\n- For more help, visit the documentation.")
        self.help_text.configure(state=ctk.DISABLED)

        # --- Quick Template Bar ---
        self.quick_template_bar = ctk.CTkFrame(self.panels['main'], fg_color="#23272A")
        self.quick_template_bar.pack(fill=ctk.X, padx=24, pady=(4, 0))
        self.refresh_quick_template_bar()
        # --- Message Preview Button ---
        preview_btn = ctk.CTkButton(self.panels['main'], text="Preview Message", command=self.preview_message, fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11))
        preview_btn.pack(padx=24, pady=(0, 8), anchor="w")
        ToolTip(preview_btn, "Preview how your message will look in Discord.")
        # --- Schedule Message Button ---
        schedule_btn = ctk.CTkButton(self.panels['main'], text="Schedule Message", command=self.schedule_message, fg_color="#43B581", hover_color="#2ECC71", font=("Segoe UI", 11))
        schedule_btn.pack(padx=24, pady=(0, 8), anchor="w")
        ToolTip(schedule_btn, "Schedule a message to be sent at a specific time.")
        # --- Queue Management Buttons ---
        queue_frame = ctk.CTkFrame(self.panels['main'], fg_color="#23272A")
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
        export_btn = ctk.CTkButton(self.panels['main'], text="Export Session", command=self.export_session, fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11))
        export_btn.pack(padx=24, pady=(0, 8), anchor="w")
        import_btn = ctk.CTkButton(self.panels['main'], text="Import Settings", command=self.import_settings, fg_color="#7289DA", hover_color="#5865F2", font=("Segoe UI", 11))
        import_btn.pack(padx=24, pady=(0, 8), anchor="w")
        ToolTip(export_btn, "Export session summary as CSV/JSON.")
        ToolTip(import_btn, "Import settings and templates from file.")

        # At the end, show main panel by default
        show_panel('main')

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
        current_text = self.message_entry.get("0.0", ctk.END).strip()
        if current_text == "Type your message(s) here. Each line is a separate message.":
            self.message_entry.delete("0.0", ctk.END)

    def schedule_message_advanced(self):
        """Advanced scheduling with time input."""
        time_str = self.schedule_time_entry.get().strip()
        if not time_str:
            messagebox.showerror("Error", "Please enter a time (HH:MM).")
            return
        try:
            from datetime import datetime, time
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            msg = self.message_entry.get("0.0", ctk.END).strip()
            if not msg or msg == "Type your message(s) here. Each line is a separate message.":
                messagebox.showerror("Error", "Please enter a message to schedule.")
                return
            
            # Create datetime for today with specified time
            now = datetime.now()
            send_time = datetime.combine(now.date(), time_obj)
            
            # If time has passed today, schedule for tomorrow
            if send_time <= now:
                from datetime import timedelta
                send_time += timedelta(days=1)
                
            self.scheduled_messages.append((send_time, msg))
            self.log(f"Scheduled message for {send_time.strftime('%Y-%m-%d %H:%M')}.")
            threading.Thread(target=self._wait_and_send, args=(send_time, msg), daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Invalid time format. Use HH:MM (24-hour format).")

    def clear_scheduled_messages(self):
        """Clear all scheduled messages."""
        self.scheduled_messages.clear()
        self.log("Cleared all scheduled messages.")

    def update_performance_metrics(self) -> None:
        """Update real-time performance metrics dashboard."""
        if not hasattr(self, 'metrics_labels'):
            return
            
        # Calculate metrics
        session_duration = time.time() - self.session_metrics["start_time"]
        rate_status = self.rate_limiter.get_queue_status()
        success_rate = 100.0 if self.analytics_data["sent"] == 0 else (
            (self.analytics_data["sent"] / (self.analytics_data["sent"] + self.analytics_data["errors"])) * 100
        )
        
        # Update metric displays
        metrics_updates = {
            "sent_count": str(self.analytics_data["sent"]),
            "success_rate": f"{success_rate:.1f}",
            "rate_hits": str(rate_status["rate_limit_hits"]),
            "avg_time": f"{rate_status['recommended_delay']:.1f}s",
            "queue_status": "Active" if self.is_sending else "Idle",
            "session_time": f"{session_duration//60:.0f}m {session_duration%60:.0f}s"
        }
        
        for key, value in metrics_updates.items():
            if key in self.metrics_labels:
                self.metrics_labels[key].configure(text=value)
        
        # Update performance chart
        if hasattr(self, 'performance_chart'):
            current_time = datetime.now().strftime("%H:%M:%S")
            chart_line = f"{current_time} | Sent: {self.analytics_data['sent']:3d} | Rate: {success_rate:5.1f}% | Queue: {rate_status['recent_messages']:2d}/5"
            
            self.performance_chart.insert(ctk.END, chart_line + "\n")
            
            # Keep only last 20 lines
            lines = self.performance_chart.get("1.0", ctk.END).split("\n")
            if len(lines) > 22:  # 20 + 2 for safety
                self.performance_chart.delete("1.0", ctk.END)
                self.performance_chart.insert("1.0", "\n".join(lines[-21:]))
            
            self.performance_chart.see(ctk.END)
        
        # Schedule next update if auto-refresh is enabled
        if hasattr(self, 'auto_refresh_var') and self.auto_refresh_var.get():
            self.root.after(5000, self.update_performance_metrics)

    def update_rate_limiter_status(self, status: str, details: str) -> None:
        """Update the rate limiter status display."""
        if not self.rate_limiter_status_label:
            return
        self.rate_limiter_status_label.configure(text=status)
        # Optionally, update details in a tooltip or a separate label

    def animate_shine(self):
        """
        Animate a shine effect on the self.shine progress bar in the main panel header.
        Handles missing widget or attribute errors gracefully.
        """
        try:
            if not hasattr(self, 'shine') or self.shine is None:
                # GUI not ready yet, retry after short delay
                self.root.after(100, self.animate_shine)
                return
            # Animate shine progress bar (looping from 0.0 to 1.0)
            current = self.shine.get()
            next_val = (current + 0.03) % 1.0
            self.shine.set(next_val)
            self.root.after(40, self.animate_shine)
        except Exception as e:
            log_error("AttributeError", str(e), "animate_shine in DiscordAutoSender", resolution="Added robust error handling and retry loop.")
            # Retry after a short delay in case of transient GUI errors
            self.root.after(200, self.animate_shine)

    def on_close(self):
        """
        Handler for window close event. Ensures graceful shutdown and session logging.
        """
        try:
            log_session("Application closed by user.")
            self.root.destroy()
        except Exception as e:
            log_error("ShutdownError", str(e), "on_close in DiscordAutoSender", resolution="Graceful fallback on shutdown.")
            try:
                self.root.destroy()
            except Exception:
                pass

    def change_theme(self, theme):
        """
        Placeholder for theme change logic. Prevents AttributeError on theme change.
        """
        self.theme = theme
        self.status_var.set(f"Theme changed to {theme} (stub)")

    def change_language(self, lang):
        """
        Placeholder for language change logic. Prevents AttributeError on language change.
        """
        self.language = lang
        self.status_var.set(f"Language changed to {lang} (stub)")

    def check_update(self):
        """Placeholder for update check logic."""
        self.status_var.set("Checked for updates (stub)")

    def show_help(self):
        """Placeholder for help dialog."""
        self.status_var.set("Help dialog opened (stub)")

    def undo(self, event=None):
        """Placeholder for undo logic."""
        self.status_var.set("Undo (stub)")
        return "break"

    def redo(self, event=None):
        """Placeholder for redo logic."""
        self.status_var.set("Redo (stub)")
        return "break"

    def show_analytics(self):
        """Placeholder for analytics panel logic."""
        self.status_var.set("Analytics panel opened (stub)")

    def load_messages(self):
        """Placeholder for loading messages from file."""
        self.status_var.set("Messages loaded from file (stub)")

    def start_sending(self):
        """Placeholder for starting message sending."""
        self.status_var.set("Started sending messages (stub)")

    def stop_sending(self):
        """Placeholder for stopping message sending."""
        self.status_var.set("Stopped sending messages (stub)")

    def get_messages(self):
        """Placeholder for getting messages."""
        return []

    def get_delay(self):
        """Placeholder for getting delay value."""
        return 1.0

    def send_messages(self, messages, delay):
        """Placeholder for sending messages."""
        self.status_var.set(f"Sent {len(messages)} messages with {delay}s delay (stub)")

    # --- Robust attribute/method existence checker for future extensibility ---
    def safe_call(self, method_name: str, *args, **kwargs):
        """
        Safely call a method by name if it exists, with error logging.
        """
        method = getattr(self, method_name, None)
        if callable(method):
            try:
                return method(*args, **kwargs)
            except Exception as e:
                log_error("MethodCallError", str(e), f"safe_call: {method_name}")
        else:
            log_error("MissingMethodError", f"Method '{method_name}' not found.", f"safe_call: {method_name}")
        return None

    def safe_getattr(self, attr_name: str, default=None):
        """
        Safely get an attribute by name, with error logging if missing.
        """
        if hasattr(self, attr_name):
            return getattr(self, attr_name)
        else:
            log_error("MissingAttributeError", f"Attribute '{attr_name}' not found.", f"safe_getattr: {attr_name}")
            return default

    # --- Add docstrings and comments for maintainability ---
    # (Docstrings and comments have been added throughout the class for clarity.)

    def clear_log(self):
        """Clear the session log display."""
        try:
            if hasattr(self, 'log_text') and self.log_text:
                self.log_text.config(state=tk.NORMAL)
                self.log_text.delete('1.0', tk.END)
                self.log_text.config(state=tk.DISABLED)
                self.status_var.set("Log cleared.")
        except Exception as e:
            log_error("ClearLogError", str(e), "clear_log")

    def copy_log_to_clipboard(self):
        """Copy the session log to the clipboard."""
        try:
            if hasattr(self, 'log_text') and self.log_text:
                log_content = self.log_text.get('1.0', tk.END)
                self.root.clipboard_clear()
                self.root.clipboard_append(log_content)
                self.status_var.set("Log copied to clipboard.")
        except Exception as e:
            log_error("CopyLogError", str(e), "copy_log_to_clipboard")

    def refresh_template_list(self):
        """Refresh the list of message templates."""
        try:
            # Placeholder: populate template_listbox with dummy data
            if hasattr(self, 'template_listbox') and self.template_listbox:
                self.template_listbox.delete(0, tk.END)
                for i in range(3):
                    self.template_listbox.insert(tk.END, f"Template {i+1}")
        except Exception as e:
            log_error("RefreshTemplateListError", str(e), "refresh_template_list")

    def load_template(self):
        """Load the selected template into the message entry."""
        try:
            idx = self.template_listbox.curselection()
            if idx:
                template = self.template_listbox.get(idx[0])
                self.message_entry.delete('1.0', tk.END)
                self.message_entry.insert('1.0', f"Loaded: {template}")
                self.status_var.set(f"Loaded template: {template}")
        except Exception as e:
            log_error("LoadTemplateError", str(e), "load_template")

    def save_template(self):
        """Save the current message as a template."""
        try:
            msg = self.message_entry.get('1.0', tk.END).strip()
            if msg:
                self.status_var.set("Template saved (stub).")
        except Exception as e:
            log_error("SaveTemplateError", str(e), "save_template")

    def delete_template(self):
        """Delete the selected template."""
        try:
            idx = self.template_listbox.curselection()
            if idx:
                self.template_listbox.delete(idx[0])
                self.status_var.set("Template deleted (stub).")
        except Exception as e:
            log_error("DeleteTemplateError", str(e), "delete_template")

    def load_quick_template(self, tname):
        """Load a quick template by name."""
        try:
            self.message_entry.delete('1.0', tk.END)
            self.message_entry.insert('1.0', f"Quick template: {tname}")
            self.status_var.set(f"Loaded quick template: {tname}")
        except Exception as e:
            log_error("LoadQuickTemplateError", str(e), f"load_quick_template: {tname}")

    def preview_message(self):
        """Preview the current message in a popup."""
        try:
            msg = self.message_entry.get('1.0', tk.END).strip()
            messagebox.showinfo("Preview Message", msg)
        except Exception as e:
            log_error("PreviewMessageError", str(e), "preview_message")

    def schedule_message(self):
        """Schedule a message to be sent at a specific time (stub)."""
        try:
            self.status_var.set("Message scheduled (stub).")
        except Exception as e:
            log_error("ScheduleMessageError", str(e), "schedule_message")

    def pause_queue(self):
        """Pause the message sending queue (stub)."""
        try:
            self.queue_paused = True
            self.status_var.set("Queue paused.")
        except Exception as e:
            log_error("PauseQueueError", str(e), "pause_queue")

    def resume_queue(self):
        """Resume the message sending queue (stub)."""
        try:
            self.queue_paused = False
            self.status_var.set("Queue resumed.")
        except Exception as e:
            log_error("ResumeQueueError", str(e), "resume_queue")

    def cancel_queue(self):
        """Cancel all scheduled/queued messages (stub)."""
        try:
            self.scheduled_messages.clear()
            self.status_var.set("Queue cancelled.")
        except Exception as e:
            log_error("CancelQueueError", str(e), "cancel_queue")

    def export_session(self):
        """Export the session summary as CSV/JSON (stub)."""
        try:
            self.status_var.set("Session exported (stub).")
        except Exception as e:
            log_error("ExportSessionError", str(e), "export_session")

    def import_settings(self):
        """Import settings and templates from file (stub)."""
        try:
            self.status_var.set("Settings imported (stub).")
        except Exception as e:
            log_error("ImportSettingsError", str(e), "import_settings")

    def log(self, msg: str):
        """Append a message to the session log display."""
        try:
            if hasattr(self, 'log_text') and self.log_text:
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.config(state=tk.DISABLED)
                self.log_text.see(tk.END)
        except Exception as e:
            log_error("LogDisplayError", str(e), f"log: {msg}")

    def onboarding(self):
        """Placeholder for onboarding logic."""
        self.status_var.set("Welcome to VaxityAutoTyper!")

# --- DEBUG: Confirm which main.py is running ---
print(f"[DEBUG] Running main.py from: {__file__}")

# --- Add robust main entrypoint ---
def main():
    import tkinter as tk
    import customtkinter as ctk
    try:
        root = ctk.CTk() if hasattr(ctk, 'CTk') else tk.Tk()
        app = DiscordAutoSender(root)
        root.protocol("WM_DELETE_WINDOW", app.on_close)
        root.mainloop()
    except Exception as e:
        log_error("StartupError", str(e), "main() startup")
        print(f"[ERROR] StartupError: {e}")

if __name__ == "__main__":
    main()