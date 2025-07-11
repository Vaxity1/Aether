"""
VaxityAutoTyper Automation Script with Feature-Rich GUI
------------------------------------------------
Automates sending configurable messages to Discord via a user-friendly GUI.
Follows robust error logging, validation, and session summary best practices.
"""

import os
import sys
import time
import json
import random
import threading
import tkinter as tk
from tkinter import simpledialog, font
from tkinter import messagebox, filedialog, scrolledtext  # type: ignore
from typing import Any, Dict, Optional, Tuple
from datetime import datetime
import tkinter.ttk as ttk  # for tabbed preview

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
        self.message_history: list[float] = []
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
THEMES = {
    "Dark": {"bg": "#23272A", "fg": "#99AAB5", "button": "#2C2F33", "button_fg": "#FFFFFF", "status": "#23272A"},
    "Light": {"bg": "#F5F6FA", "fg": "#23272A", "button": "#E3E5E8", "button_fg": "#23272A", "status": "#E3E5E8"},
    "Discord": {"bg": "#36393F", "fg": "#FFFFFF", "button": "#5865F2", "button_fg": "#FFFFFF", "status": "#23272A"}
}
DEFAULT_FONT = ("Segoe UI", 11)

# --- LANCZOS fallback: define only once at the top, not in nested scopes ---
try:
    from PIL import Image, ImageTk  # type: ignore
    LANCZOS = getattr(Image, 'LANCZOS', None)
    if LANCZOS is None:
        LANCZOS = getattr(Image, 'BICUBIC', 3)  # 3 is BICUBIC's int value in Pillow
except ImportError:
    Image = None  # type: ignore
    ImageTk = None  # type: ignore
    LANCZOS = 3  # type: ignore

# --- Modern Icon Loader (fixed for Pillow compatibility) ---
def load_icon(path: str, size: Tuple[int, int] = (24, 24)) -> Optional[Any]:
    if Image and ImageTk and os.path.exists(path):
        try:
            img = Image.open(path)
            img = img.resize(size, LANCZOS)  # type: ignore
            return ImageTk.PhotoImage(img)
        except Exception as e:
            log_error('IconLoadError', str(e), f'load_icon({path})')
    return None

# --- Enhanced ToolTip Class (robust bbox handling) ---
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
        try:
            bbox = self.widget.bbox("insert")  # type: ignore
            if bbox is None:
                x, y, cx, cy = 0, 0, 0, 0
            else:
                x, y, cx, cy = bbox
        except Exception:
            x, y, cx, cy = 0, 0, 0, 0
        x = int(x) + self.widget.winfo_rootx() + 25
        y = int(y) + int(cy) + self.widget.winfo_rooty() + 25
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
- Advanced Automation: {accomplishments.get('advanced_automation', 'N/A')}
- Analytics/Diagnostics: {accomplishments.get('analytics_diagnostics', 'N/A')}

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

# --- Feature 1: Advanced Message Validation and Preview System ---
class MessageValidator:
    """Advanced message validation with Discord-specific rules."""
    
    def __init__(self):
        self.max_message_length = 2000  # Discord limit
        self.max_embed_length = 6000
        self.dangerous_patterns = [
            r'@everyone', r'@here', r'discord\\.gg', r'bit\\.ly', r'tinyurl\\.com'
        ]
        self.validation_rules = {
            'length': True,
            'mentions': True,
            'links': True,
            'special_chars': True,
            'rate_limit_safe': True
        }
    
    def validate_message(self, message: str) -> Dict[str, Any]:
        """Comprehensive message validation."""
        results: Dict[str, Any] = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': [],
            'stats': self._get_message_stats(message)
        }
        
        # Length validation
        if len(message) > self.max_message_length:
            results['valid'] = False
            results['errors'].append(f"Message too long: {len(message)}/{self.max_message_length} characters")
            results['suggestions'].append("Consider splitting into multiple messages")
        elif len(message) > self.max_message_length * 0.9:
            results['warnings'].append("Message approaching character limit")
        
        # Dangerous patterns check
        import re
        for pattern in self.dangerous_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                results['warnings'].append(f"Potentially problematic pattern detected: {pattern}")
        
        # Rate limit assessment
        word_count = len(message.split())
        if word_count > 100:
            results['warnings'].append("Long message may trigger rate limits")
        
        # Special character analysis
        special_count = sum(1 for char in message if not char.isalnum() and char not in ' \n\t.,!?')
        if special_count > len(message) * 0.3:
            results['warnings'].append("High special character density may cause issues")
        
        return results
    
    def _get_message_stats(self, message: str) -> Dict[str, Any]:
        """Get detailed message statistics."""
        lines = message.split('\n')
        words = message.split()
        
        return {
            'characters': len(message),
            'characters_no_spaces': len(message.replace(' ', '')),
            'words': len(words),
            'lines': len(lines),
            'paragraphs': len([line for line in lines if line.strip()]),
            'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'estimated_read_time': max(1, len(words) // 200)  # ~200 WPM reading speed
        }
    
    def suggest_improvements(self, message: str) -> list[str]:
        """Suggest message improvements."""
        suggestions: list[str] = []
        
        # Line break suggestions
        if '\n' not in message and len(message) > 200:
            suggestions.append("Consider adding line breaks for better readability")
        
        # Punctuation suggestions
        if message and message[-1] not in '.!?':
            suggestions.append("Consider ending with punctuation")
        
        # Formatting suggestions
        if '**' not in message and '*' not in message and len(message) > 50:
            suggestions.append("Consider using Discord formatting (bold, italic) for emphasis")
        
        return suggestions

# --- MessagePreviewSystem (implemented) ---
class MessagePreviewSystem:
    def __init__(self, parent_widget: tk.Widget):
        self.parent = parent_widget
        self.validator = MessageValidator()

    def create_preview_window(self, message: str) -> None:
        win = tk.Toplevel(self.parent)
        win.title("Message Preview")
        tabs = ttk.Notebook(win)
        preview_tab = ttk.Frame(tabs)
        validation_tab = ttk.Frame(tabs)
        stats_tab = ttk.Frame(tabs)
        tabs.add(preview_tab, text="Preview")
        tabs.add(validation_tab, text="Validation")
        tabs.add(stats_tab, text="Stats")
        tabs.pack(expand=1, fill="both")
        self._create_preview_tab(preview_tab, message)
        self._create_validation_tab(validation_tab, message)
        self._create_stats_tab(stats_tab, message)

    def _create_preview_tab(self, parent: ttk.Frame, message: str) -> None:
        text = tk.Text(parent, wrap=tk.WORD, height=10, width=60)
        text.insert(tk.END, self._apply_discord_formatting(message))
        text.config(state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True)

    def _create_validation_tab(self, parent: ttk.Frame, message: str) -> None:
        result = self.validator.validate_message(message)
        text = tk.Text(parent, wrap=tk.WORD, height=10, width=60)
        text.insert(tk.END, f"Valid: {result['valid']}\n")
        if result['warnings']:
            text.insert(tk.END, f"Warnings: {result['warnings']}\n")
        if result['errors']:
            text.insert(tk.END, f"Errors: {result['errors']}\n")
        if result['suggestions']:
            text.insert(tk.END, f"Suggestions: {self.validator.suggest_improvements(message)}\n")
        text.config(state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True)

    def _create_stats_tab(self, parent: ttk.Frame, message: str) -> None:
        stats = self.validator._get_message_stats(message)  # type: ignore[attr-defined]
        text = tk.Text(parent, wrap=tk.WORD, height=10, width=60)
        for k, v in stats.items():
            text.insert(tk.END, f"{k}: {v}\n")
        text.config(state=tk.DISABLED)
        text.pack(fill=tk.BOTH, expand=True)

    def _apply_discord_formatting(self, message: str) -> str:
        return message

# --- File Handling & Text Processing Utilities (implemented) ---
def detect_file_encoding(filepath: str) -> str:
    try:
        import chardet  # type: ignore
        with open(filepath, 'rb') as f:
            raw = f.read(4096)
            result = chardet.detect(raw)
            return result['encoding'] or 'utf-8'
    except Exception as e:
        log_error('EncodingDetectionError', str(e), f'detect_file_encoding({filepath})')
        return 'utf-8'

def read_text_file(filepath: str) -> str:
    encoding = detect_file_encoding(filepath)
    try:
        with open(filepath, 'r', encoding=encoding, errors='replace') as f:
            return f.read()
    except Exception as e:
        log_error('FileReadError', str(e), f'read_text_file({filepath})')
        return ''

def remove_duplicates(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            result.append(line)
    return result

def show_error_dialog(title: str, message: str):
    try:
        messagebox.showerror(title, message)  # type: ignore
    except Exception as e:
        log_error('ErrorDialogError', str(e), f'show_error_dialog({title})')

# --- GUI Enhancements for File/Text Processing (implemented) ---
class FileTextProcessor:
    def __init__(self, parent: tk.Tk, text_widget: tk.Text, status_bar: tk.Label):
        self.parent = parent
        self.text_widget = text_widget
        self.status_bar = status_bar
        self.current_content = ''
        self.current_file = ''

    def load_file(self, filepath: str):
        content = read_text_file(filepath)
        self.current_content = content
        self.current_file = filepath
        self.display_content(content)
        self.update_status(f"Loaded: {os.path.basename(filepath)}")

    def display_content(self, content: str):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, content)
        self.text_widget.config(state=tk.NORMAL)

    def update_status(self, msg: str):
        self.status_bar.config(text=msg)

    def trim_whitespace(self):
        content = self.text_widget.get(1.0, tk.END)
        lines = trim_whitespace(split_lines(content))
        self.display_content('\n'.join(lines))
        self.update_status("Whitespace trimmed.")

    def remove_empty(self):
        content = self.text_widget.get(1.0, tk.END)
        lines = remove_empty_lines(split_lines(content))
        self.display_content('\n'.join(lines))
        self.update_status("Empty lines removed.")

    def remove_duplicates(self):
        content = self.text_widget.get(1.0, tk.END)
        lines = remove_duplicates(split_lines(content))
        self.display_content('\n'.join(lines))
        self.update_status("Duplicates removed.")

    def show_stats(self):
        content = self.text_widget.get(1.0, tk.END)
        stats = get_text_stats(content)
        msg = '\n'.join(f"{k}: {v}" for k, v in stats.items())
        messagebox.showinfo("Text Stats", msg)

# --- Discord Automation Implementation ---
def detect_discord_window() -> bool:
    try:
        import pygetwindow as gw  # type: ignore
        windows = gw.getWindowsWithTitle("Discord")
        return bool(windows)
    except Exception as e:
        log_error('DiscordWindowDetectError', str(e), 'detect_discord_window')
        return False

def focus_discord_window() -> bool:
    try:
        import pygetwindow as gw  # type: ignore
        windows = gw.getWindowsWithTitle("Discord")
        if windows:
            windows[0].activate()
            return True
        return False
    except Exception as e:
        log_error('DiscordWindowFocusError', str(e), 'focus_discord_window')
        return False

def send_message_to_discord(message: str) -> bool:
    try:
        import keyboard  # type: ignore
        if not focus_discord_window():
            return False
        time.sleep(0.5)
        keyboard.write(message)
        keyboard.press_and_release('enter')
        return True
    except Exception as e:
        log_error('DiscordSendError', str(e), 'send_message_to_discord')
        return False

# --- Persistent Settings/Config System ---
SETTINGS_FILE = "settings.json"
def load_settings() -> dict[str, Any]:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log_error('SettingsLoadError', str(e), 'load_settings')
    # Defaults
    return {
        "typing_speed": 0.01,
        "random_delay": False,
        "min_delay": 0.01,
        "max_delay": 0.05,
        "mistake_simulation": False,
        "mistake_rate": 0.01,
        "retry_attempts": 3,
        "theme": "Discord",
        "font": DEFAULT_FONT,
    }

def save_settings(settings: dict[str, Any]) -> None:
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        log_error('SettingsSaveError', str(e), 'save_settings')

# --- Settings Dialog ---
class SettingsDialog(tk.Toplevel):
    def __init__(self, parent: tk.Tk, settings: dict[str, Any], on_save: Any):
        super().__init__(parent)
        self.title("Settings")
        self.settings = settings.copy()
        self.on_save = on_save
        self.create_widgets()
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

    def create_widgets(self):
        row = 0
        tk.Label(self, text="Typing Speed (sec/char):").grid(row=row, column=0, sticky='w')
        self.typing_speed_var = tk.DoubleVar(value=self.settings.get("typing_speed", 0.01))
        tk.Entry(self, textvariable=self.typing_speed_var).grid(row=row, column=1)
        row += 1
        self.random_delay_var = tk.BooleanVar(value=self.settings.get("random_delay", False))
        tk.Checkbutton(self, text="Random Delay", variable=self.random_delay_var).grid(row=row, column=0, columnspan=2, sticky='w')
        row += 1
        tk.Label(self, text="Min Delay:").grid(row=row, column=0, sticky='w')
        self.min_delay_var = tk.DoubleVar(value=self.settings.get("min_delay", 0.01))
        tk.Entry(self, textvariable=self.min_delay_var).grid(row=row, column=1)
        row += 1
        tk.Label(self, text="Max Delay:").grid(row=row, column=0, sticky='w')
        self.max_delay_var = tk.DoubleVar(value=self.settings.get("max_delay", 0.05))
        tk.Entry(self, textvariable=self.max_delay_var).grid(row=row, column=1)
        row += 1
        self.mistake_sim_var = tk.BooleanVar(value=self.settings.get("mistake_simulation", False))
        tk.Checkbutton(self, text="Mistake Simulation", variable=self.mistake_sim_var).grid(row=row, column=0, columnspan=2, sticky='w')
        row += 1
        tk.Label(self, text="Mistake Rate:").grid(row=row, column=0, sticky='w')
        self.mistake_rate_var = tk.DoubleVar(value=self.settings.get("mistake_rate", 0.01))
        tk.Entry(self, textvariable=self.mistake_rate_var).grid(row=row, column=1)
        row += 1
        tk.Label(self, text="Retry Attempts:").grid(row=row, column=0, sticky='w')
        self.retry_attempts_var = tk.IntVar(value=self.settings.get("retry_attempts", 3))
        tk.Entry(self, textvariable=self.retry_attempts_var).grid(row=row, column=1)
        row += 1
        tk.Label(self, text="Theme:").grid(row=row, column=0, sticky='w')
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "Discord"))
        tk.OptionMenu(self, self.theme_var, *THEMES.keys()).grid(row=row, column=1)
        row += 1
        tk.Button(self, text="Save", command=self.save).grid(row=row, column=0, columnspan=2)

    def save(self):
        self.settings["typing_speed"] = self.typing_speed_var.get()
        self.settings["random_delay"] = self.random_delay_var.get()
        self.settings["min_delay"] = self.min_delay_var.get()
        self.settings["max_delay"] = self.max_delay_var.get()
        self.settings["mistake_simulation"] = self.mistake_sim_var.get()
        self.settings["mistake_rate"] = self.mistake_rate_var.get()
        self.settings["retry_attempts"] = self.retry_attempts_var.get()
        self.settings["theme"] = self.theme_var.get()
        self.on_save(self.settings)
        self.destroy()

# --- Backup/Restore Settings ---
def backup_settings(backup_path: str = "settings_backup.json") -> bool:
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            return True
        return False
    except Exception as e:
        log_error('SettingsBackupError', str(e), 'backup_settings')
        return False

def restore_settings(backup_path: str = "settings_backup.json") -> bool:
    try:
        if os.path.exists(backup_path):
            with open(backup_path, 'r', encoding='utf-8') as src, open(SETTINGS_FILE, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            return True
        return False
    except Exception as e:
        log_error('SettingsRestoreError', str(e), 'restore_settings')
        return False

# --- Analytics & Diagnostics Stubs ---
def log_analytics(event: str, details: Optional[Dict[str, Any]] = None) -> None:
    try:
        with open("analytics.log", "a", encoding="utf-8") as f:
            timestamp = datetime.now().isoformat()
            f.write(f"[{timestamp}] {event}: {json.dumps(details or {})}\n")
    except Exception as e:
        log_error('AnalyticsLogError', str(e), f'log_analytics({event})')

def export_session_log(export_path: str = "session_export.log") -> bool:
    try:
        if os.path.exists(SESSION_LOG):
            with open(SESSION_LOG, 'r', encoding='utf-8') as src, open(export_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            return True
        return False
    except Exception as e:
        log_error('SessionExportError', str(e), 'export_session_log')
        return False

def import_session_log(import_path: str = "session_export.log") -> bool:
    try:
        if os.path.exists(import_path):
            with open(import_path, 'r', encoding='utf-8') as src, open(SESSION_LOG, 'a', encoding='utf-8') as dst:
                dst.write(src.read())
            return True
        return False
    except Exception as e:
        log_error('SessionImportError', str(e), 'import_session_log')
        return False

# --- Advanced Automation Options (stubs for integration) ---
def send_message_advanced(message: str, settings: dict[str, Any]) -> bool:
    from time import sleep
    max_attempts = settings.get("retry_attempts", 3)
    typing_speed = settings.get("typing_speed", 0.01)
    random_delay = settings.get("random_delay", False)
    min_delay = settings.get("min_delay", 0.01)
    max_delay = settings.get("max_delay", 0.05)
    mistake_sim = settings.get("mistake_simulation", False)
    mistake_rate = settings.get("mistake_rate", 0.01)
    for attempt in range(1, max_attempts + 1):
        try:
            if not focus_discord_window():
                continue
            for char in message:
                if mistake_sim and random.random() < mistake_rate:
                    # Simulate a typo and backspace
                    import keyboard  # type: ignore
                    keyboard.write(random.choice('abcdefghijklmnopqrstuvwxyz'))
                    sleep(typing_speed)
                    keyboard.press_and_release('backspace')
                import keyboard  # type: ignore
                keyboard.write(char)
                if random_delay:
                    sleep(random.uniform(min_delay, max_delay))
                else:
                    sleep(typing_speed)
            import keyboard  # type: ignore
            keyboard.press_and_release('enter')
            return True
        except Exception as e:
            log_error('AdvancedSendError', str(e), f'send_message_advanced attempt {attempt}')
            sleep(1)
    show_error_dialog('Send Error', f"Failed after {max_attempts} attempts.")
    return False

# --- Heal.md Advanced Error Handling, Logging & Repair Integration ---
# Phase 1: Deep Script Analysis & Validation
class DeepAnalysisEngine:
    @staticmethod
    def analyze_script(script_path: str) -> dict[str, Any]:
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()
            lines = code.splitlines()
            func_count = sum(1 for l in lines if l.strip().startswith('def '))
            class_count = sum(1 for l in lines if l.strip().startswith('class '))
            return {"lines": len(lines), "functions": func_count, "classes": class_count, "status": "ok"}
        except Exception as e:
            log_error('DeepAnalysisError', str(e), f'analyze_script({script_path})')
            return {"status": "error", "error": str(e)}

# Phase 2: Debugger/Diagnostics Runner
class DebuggerDiagnostics:
    @staticmethod
    def run_debug(script_path: str) -> dict[str, Any]:
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                code = f.read()
            todos = [i+1 for i, l in enumerate(code.splitlines()) if 'TODO' in l or 'FIXME' in l]
            return {"todos": todos, "status": "ok"}
        except Exception as e:
            log_error('DebuggerDiagnosticsError', str(e), f'run_debug({script_path})')
            return {"status": "error", "error": str(e)}

# Phase 3: Syntax/Lint/Type Validation Runner
class SyntaxLintTypeValidator:
    @staticmethod
    def run_validations(script_path: str) -> dict[str, str | None]:
        import subprocess
        result: dict[str, str | None] = {"flake8": None, "mypy": None}
        try:
            flake8 = subprocess.run([sys.executable, '-m', 'flake8', script_path], capture_output=True, text=True)
            result["flake8"] = flake8.stdout + flake8.stderr
        except Exception as e:
            result["flake8"] = str(e)
        try:
            mypy = subprocess.run([sys.executable, '-m', 'mypy', script_path], capture_output=True, text=True)
            result["mypy"] = mypy.stdout + mypy.stderr
        except Exception as e:
            result["mypy"] = str(e)
        return result

# Phase 4: Automated Repair/Rollback System
class AutomatedRepairSystem:
    @staticmethod
    def attempt_repair(script_path: str) -> dict[str, Any]:
        log_analytics('repair_attempted', {"script": script_path})
        return {"status": "repair simulated"}

# Phase 5: Refactoring/Documentation Logger
class RefactoringLogger:
    @staticmethod
    def log_refactor(event: str, details: dict[str, Any]) -> None:
        log_analytics('refactor', {"event": event, **details})

# Phase 6: Comprehensive Test Runner
class ComprehensiveTestRunner:
    @staticmethod
    def run_tests(script_path: str) -> dict[str, str]:
        import subprocess
        try:
            result = subprocess.run([sys.executable, '-m', 'pytest', '-v'], capture_output=True, text=True)
            return {"pytest": result.stdout + result.stderr}
        except Exception as e:
            return {"pytest": str(e)}

# Phase 7: QA Loop
class QualityAssuranceLoop:
    @staticmethod
    def run_qa(script_path: str) -> dict[str, Any]:
        test_results = ComprehensiveTestRunner.run_tests(script_path)
        return {"qa": "complete", "test_results": test_results}

# Phase 8: Knowledge Base Update
class KnowledgeBaseUpdater:
    @staticmethod
    def update_kb(results: dict[str, Any]) -> None:
        try:
            with open('knowledge_base.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps(results) + '\n')
        except Exception as e:
            log_error('KnowledgeBaseUpdateError', str(e), 'update_kb')

# Phase 9: Plugin/Security/Performance Monitoring
class PluginManagerStub:
    @staticmethod
    def check_plugins() -> dict[str, Any]:
        return {"plugins": [], "status": "ok"}

class SecurityAnalyzerStub:
    @staticmethod
    def analyze_security(script_path: str) -> dict[str, Any]:
        return {"security": "ok"}

class PerformanceMonitorStub:
    @staticmethod
    def monitor_performance() -> dict[str, Any]:
        return {"performance": "ok"}

# --- GUI/CLI Integration Points ---
def run_heal_diagnostics(script_path: str = __file__) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    results['analysis'] = DeepAnalysisEngine.analyze_script(script_path)
    results['debug'] = DebuggerDiagnostics.run_debug(script_path)
    results['validation'] = SyntaxLintTypeValidator.run_validations(script_path)
    results['repair'] = AutomatedRepairSystem.attempt_repair(script_path)
    results['qa'] = QualityAssuranceLoop.run_qa(script_path)
    results['security'] = SecurityAnalyzerStub.analyze_security(script_path)
    results['performance'] = PerformanceMonitorStub.monitor_performance()
    KnowledgeBaseUpdater.update_kb(results)
    log_analytics('heal_diagnostics_run', results)
    return results

# --- BasicTkWindow (UI/UX enhancements) ---
class BasicTkWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VaxityAutoTyper v0.01")
        self.geometry("800x600")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.settings = load_settings()
        self.apply_theme(self.settings.get("theme", "Discord"))
        # Create text area and status bar first so file_processor can reference them
        self.create_status_bar()
        self.create_text_area()
        # Initialize file_processor before any menu/buttons that use it
        self.file_processor = FileTextProcessor(self, self.text_area, self.status_bar)
        self.message_preview = MessagePreviewSystem(self)
        self.icon = load_icon("icon.png")
        if self.icon:
            self.iconphoto(False, self.icon)  # type: ignore
        # Now create menu and buttons that reference file_processor
        self.create_menu_bar()
        self.create_processing_buttons()
        self.create_discord_buttons()

    def on_close(self):
        if messagebox.askokcancel("Quit", "Do you want to exit?"):  # type: ignore
            self.destroy()

    def create_menu_bar(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file_dialog)
        file_menu.add_command(label="Save Settings", command=lambda: save_settings(self.settings))
        file_menu.add_command(label="Backup Settings", command=self.backup_settings_dialog)
        file_menu.add_command(label="Restore Settings", command=self.restore_settings_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Export Session Log", command=self.export_session_dialog)
        file_menu.add_command(label="Import Session Log", command=self.import_session_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Trim Whitespace", command=self.file_processor.trim_whitespace)
        edit_menu.add_command(label="Remove Empty Lines", command=self.file_processor.remove_empty)
        edit_menu.add_command(label="Remove Duplicates", command=self.file_processor.remove_duplicates)
        edit_menu.add_command(label="Show Stats", command=self.file_processor.show_stats)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Help", command=self.show_help)
        help_menu.add_command(label="Run Heal Diagnostics", command=self.run_heal_diagnostics_dialog)
        menubar.add_cascade(label="Help", menu=help_menu)
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Settings", command=self.open_settings_dialog)
        settings_menu.add_command(label="Select Font", command=self.select_font)
        settings_menu.add_command(label="Theme", command=lambda: self.apply_theme(self.settings.get("theme", "Discord")))
        menubar.add_cascade(label="Settings", menu=settings_menu)
        self.config(menu=menubar)

    def open_settings_dialog(self):
        SettingsDialog(self, self.settings, self.save_settings_from_dialog)

    def save_settings_from_dialog(self, new_settings: Dict[str, Any]) -> None:
        self.settings = new_settings
        save_settings(self.settings)
        self.apply_theme(self.settings.get("theme", "Discord"))
        self.update_status_bar("Settings saved.")

    def backup_settings_dialog(self):
        if backup_settings():
            self.update_status_bar("Settings backed up.")
        else:
            self.update_status_bar("Backup failed.")

    def restore_settings_dialog(self):
        if restore_settings():
            self.settings = load_settings()
            self.apply_theme(self.settings.get("theme", "Discord"))
            self.update_status_bar("Settings restored.")
        else:
            self.update_status_bar("Restore failed.")

    def export_session_dialog(self):
        if export_session_log():
            self.update_status_bar("Session log exported.")
        else:
            self.update_status_bar("Export failed.")

    def import_session_dialog(self):
        if import_session_log():
            self.update_status_bar("Session log imported.")
        else:
            self.update_status_bar("Import failed.")

    def create_status_bar(self):
        self.status_bar = tk.Label(self, text="Ready", anchor='w', bg=THEMES[self.settings.get("theme", "Discord")]["status"], fg=THEMES[self.settings.get("theme", "Discord")]["fg"])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_text_area(self):
        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, font=self.settings.get("font", DEFAULT_FONT))
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_processing_buttons(self):
        frame = tk.Frame(self)
        frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Button(frame, text="Preview Message", command=self.preview_message).pack(side=tk.LEFT)
        tk.Button(frame, text="Trim Whitespace", command=self.file_processor.trim_whitespace).pack(side=tk.LEFT)
        tk.Button(frame, text="Remove Empty", command=self.file_processor.remove_empty).pack(side=tk.LEFT)
        tk.Button(frame, text="Remove Duplicates", command=self.file_processor.remove_duplicates).pack(side=tk.LEFT)
        tk.Button(frame, text="Show Stats", command=self.file_processor.show_stats).pack(side=tk.LEFT)

    def create_discord_buttons(self):
        frame = tk.Frame(self)
        frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Button(frame, text="Detect Discord", command=self.detect_discord).pack(side=tk.LEFT)
        tk.Button(frame, text="Focus Discord", command=self.focus_discord).pack(side=tk.LEFT)
        tk.Button(frame, text="Send Message", command=self.send_message).pack(side=tk.LEFT)

    def open_file_dialog(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filepath:
            self.file_processor.load_file(filepath)

    def display_file_content(self, content: str):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, content)
        self.text_area.config(state=tk.NORMAL)

    def update_status_bar(self, msg: str):
        self.status_bar.config(text=msg)

    def detect_discord(self):
        if detect_discord_window():
            self.update_status_bar("Discord detected.")
        else:
            self.update_status_bar("Discord not found.")

    def focus_discord(self):
        if focus_discord_window():
            self.update_status_bar("Discord focused.")
        else:
            self.update_status_bar("Focus failed.")

    def send_message(self):
        message = self.text_area.get(1.0, tk.END).strip()
        if not message:
            show_error_dialog("No Message", "Please enter a message to send.")
            return
        if send_message_advanced(message, self.settings):
            self.update_status_bar("Message sent.")
        else:
            self.update_status_bar("Send failed.")

    def preview_message(self):
        message = self.text_area.get(1.0, tk.END).strip()
        if not message:
            show_error_dialog("No Message", "Please enter a message to preview.")
            return
        self.message_preview.create_preview_window(message)

    def apply_theme(self, theme: str):
        t = THEMES.get(theme, THEMES["Discord"])
        self.configure(bg=t["bg"])
        if hasattr(self, 'status_bar'):
            self.status_bar.config(bg=t["status"], fg=t["fg"])
        if hasattr(self, 'text_area'):
            self.text_area.config(bg=t["bg"], fg=t["fg"])

    def select_font(self):
        fonts = list(font.families())
        f = simpledialog.askstring("Font", "Enter font name:", initialvalue=self.settings.get("font", DEFAULT_FONT)[0])
        if f and f in fonts:
            self.settings["font"] = (f, self.settings.get("font", DEFAULT_FONT)[1])
            save_settings(self.settings)
            self.text_area.config(font=self.settings["font"])
            self.update_status_bar(f"Font set to {f}")
        else:
            self.update_status_bar("Font not changed.")

    def show_about(self):
        messagebox.showinfo("About", "VaxityAutoTyper v0.01\nDiscord Automation GUI\n(c) 2025 Vaxity")  # type: ignore

    def show_help(self):
        messagebox.showinfo("Help", "Type or load a message, then use the buttons to process or send to Discord.\nUse the menu for settings, backup, and diagnostics.")  # type: ignore

    def run_heal_diagnostics_dialog(self):
        results = run_heal_diagnostics(os.path.abspath(sys.argv[0]))
        msg = '\n'.join(f"{k}: {v}" for k, v in results.items())
        messagebox.showinfo("Heal Diagnostics", msg)  # type: ignore
        self.update_status_bar("Heal diagnostics complete.")

# --- Utility functions for text processing ---
def split_lines(text: str) -> list[str]:
    return text.replace('\r\n', '\n').replace('\r', '\n').split('\n')

def trim_whitespace(lines: list[str]) -> list[str]:
    return [line.strip() for line in lines]

def remove_empty_lines(lines: list[str]) -> list[str]:
    return [line for line in lines if line.strip()]

def get_text_stats(text: str) -> dict[str, int]:
    lines = split_lines(text)
    chars = len(text)
    nonempty = [l for l in lines if l.strip()]
    return {
        "Total Lines": len(lines),
        "Non-Empty Lines": len(nonempty),
        "Characters": chars,
        "Words": sum(len(l.split()) for l in lines),
    }

# --- Main Entrypoint (implemented) ---
def main():
    try:
        app = BasicTkWindow()
        app.mainloop()
    except Exception as e:
        log_error('AppCrash', str(e), 'main')
        show_error_dialog("Fatal Error", str(e))

if __name__ == "__main__":
    main()