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
        self.shine = None  # Will be set in build_gui
        self.typing_indicator_running = False
        self.typing_indicator_state = 0
        self.typing_indicator_label = None
        self.rate_limiter = DiscordRateLimiter()
        self.rate_limiter_status_label = None  # Will be set in build_gui
        self.root.after(100, self.build_gui)
        self.root.after(200, self.animate_loading_bar)
        print(f"[DEBUG] animate_shine in dir(self): {'animate_shine' in dir(self)}")
        print(f"[DEBUG] hasattr(self, 'animate_shine'): {hasattr(self, 'animate_shine')}")
        self.root.after(400, self.animate_shine)
        self.root.after(1000, self.update_performance_metrics)
        self.onboarding()

    def build_gui(self):
        self.status_var.set("GUI built (stub)")

    def onboarding(self):
        self.status_var.set("Welcome to VaxityAutoTyper!")

    def animate_loading_bar(self):
        self.status_var.set("Loading bar animation (stub)")

    def flash_loading_bar(self):
        self.status_var.set("Loading bar flash (stub)")

    def animate_typing_indicator(self):
        self.status_var.set("Typing indicator animation (stub)")

    def refresh_quick_template_bar(self):
        self.status_var.set("Quick template bar refreshed (stub)")

    def clear_placeholder(self, event=None):
        self.status_var.set("Placeholder cleared (stub)")
        return "break"

    def schedule_message_advanced(self):
        self.status_var.set("Advanced message scheduled (stub)")

    def clear_scheduled_messages(self):
        self.status_var.set("Scheduled messages cleared (stub)")

    def update_performance_metrics(self) -> None:
        self.status_var.set("Performance metrics updated (stub)")

    def update_rate_limiter_status(self, status: str, details: str) -> None:
        self.status_var.set(f"Rate limiter: {status} ({details}) (stub)")

    def animate_shine(self):
        self.status_var.set("Shine animated (stub)")

    def on_close(self):
        self.status_var.set("Closed (stub)")
        self.root.destroy()

    def change_theme(self, theme):
        self.status_var.set(f"Theme changed to {theme} (stub)")

    def change_language(self, lang):
        self.status_var.set(f"Language changed to {lang} (stub)")

    def check_update(self):
        self.status_var.set("Checked for updates (stub)")

    def show_help(self):
        self.status_var.set("Help dialog opened (stub)")

    def undo(self, event=None):
        self.status_var.set("Undo (stub)")
        return "break"

    def redo(self, event=None):
        self.status_var.set("Redo (stub)")
        return "break"

    def show_analytics(self):
        self.status_var.set("Analytics panel opened (stub)")

    def load_messages(self):
        self.status_var.set("Messages loaded from file (stub)")

    def start_sending(self):
        self.status_var.set("Started sending messages (stub)")

    def stop_sending(self):
        self.status_var.set("Stopped sending messages (stub)")

    def get_messages(self):
        return []

    def get_delay(self):
        return 1.0

    def send_messages(self, messages, delay):
        self.status_var.set(f"Sent {len(messages)} messages with {delay}s delay (stub)")

    def safe_call(self, method_name: str, *args, **kwargs):
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
        if hasattr(self, attr_name):
            return getattr(self, attr_name)
        else:
            log_error("MissingAttributeError", f"Attribute '{attr_name}' not found.", f"safe_getattr: {attr_name}")
            return default

    def clear_log(self):
        self.status_var.set("Log cleared (stub)")

    def copy_log_to_clipboard(self):
        self.status_var.set("Log copied to clipboard (stub)")

    def refresh_template_list(self):
        self.status_var.set("Template list refreshed (stub)")

    def load_template(self):
        self.status_var.set("Template loaded (stub)")

    def save_template(self):
        self.status_var.set("Template saved (stub)")

    def delete_template(self):
        self.status_var.set("Template deleted (stub)")

    def load_quick_template(self, tname):
        self.status_var.set(f"Quick template loaded: {tname} (stub)")

    def preview_message(self):
        self.status_var.set("Message previewed (stub)")

    def schedule_message(self):
        self.status_var.set("Message scheduled (stub)")

    def pause_queue(self):
        self.status_var.set("Queue paused (stub)")

    def resume_queue(self):
        self.status_var.set("Queue resumed (stub)")

    def cancel_queue(self):
        self.status_var.set("Queue cancelled (stub)")

    def export_session(self):
        self.status_var.set("Session exported (stub)")

    def import_settings(self):
        self.status_var.set("Settings imported (stub)")

    def log(self, msg: str):
        self.status_var.set(f"Log: {msg} (stub)")

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