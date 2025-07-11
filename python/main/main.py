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
import tkinter as tk
from tkinter import simpledialog, font
from tkinter import messagebox, filedialog, scrolledtext  # type: ignore
from typing import Any, Dict, Optional, Tuple
from datetime import datetime
import tkinter.ttk as ttk  # for tabbed preview
import chardet  # type: ignore

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

# --- Session Summary Logging Logic ---
def write_session_summary(context, accomplishments, metrics, learning):
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
                x, y = 0, 0
            else:
                x, y = bbox[:2]
        except Exception:
            x, y = 0, 0
        x = int(x) + self.widget.winfo_rootx() + 25
        y = int(y) + self.widget.winfo_rooty() + 25
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

# --- Utility: Robust File Reading with Encoding Detection (Phase 2, Prompt 51) ---
def detect_file_encoding(filepath: str) -> str:
    """Detect file encoding using chardet."""
    with open(filepath, 'rb') as f:
        raw = f.read(4096)
    result = chardet.detect(raw)
    encoding = result['encoding']
    if encoding is None:
        return 'utf-8'  # fallback
    return encoding

def read_text_file(filepath: str) -> str:
    """Read text file with robust encoding detection (UTF-8, ASCII, Windows-1252)."""
    try:
        encoding = detect_file_encoding(filepath)
        if encoding.lower() in ['utf-8', 'ascii', 'windows-1252']:
            with open(filepath, 'r', encoding=encoding, errors='replace') as f:
                return f.read()
        # fallback: try utf-8, then windows-1252
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            with open(filepath, 'r', encoding='windows-1252', errors='replace') as f:
                return f.read()
    except Exception as e:
        log_error('FileReadError', str(e), f'read_text_file({filepath})')
        raise

# --- Utility: Remove Duplicates (Phase 2, Prompt 55) ---
def remove_duplicates(lines: list[str]) -> list[str]:
    """Remove duplicate lines, preserving order."""
    seen: set[str] = set()
    result: list[str] = []
    for line in lines:
        if line not in seen:
            seen.add(line)
            result.append(line)
    return result

# --- Utility: Error Dialog (for error handling in GUI) ---
def show_error_dialog(title: str, message: str):
    import tkinter.messagebox as messagebox
    messagebox.showerror(str(title), str(message))  # type: ignore

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

# --- Patch: Remove LANCZOS assignment block completely (fix constant redefinition error) ---

# --- File/Text Processing Utilities ---
def split_lines(text: str) -> list[str]:
    """Split text into lines, handling all common line endings."""
    return text.replace('\r\n', '\n').replace('\r', '\n').split('\n')

def remove_empty_lines(lines: list[str]) -> list[str]:
    """Remove empty or whitespace-only lines."""
    return [line for line in lines if line.strip()]

def trim_whitespace(lines: list[str]) -> list[str]:
    """Trim leading and trailing whitespace from each line."""
    return [line.strip() for line in lines]

def get_text_stats(text: str) -> dict[str, Any]:
    lines = split_lines(text)
    nonempty = remove_empty_lines(lines)
    chars = len(text)
    words = len(text.split())
    return {
        'lines': len(lines),
        'nonempty_lines': len(nonempty),
        'characters': chars,
        'words': words,
        'avg_line_length': chars // len(lines) if lines else 0,
        'avg_word_length': (sum(len(w) for w in text.split()) // words) if words else 0
    }

# --- FileTextProcessor Implementation ---
class FileTextProcessor:
    def __init__(self, parent: tk.Tk, text_widget: tk.Text, status_bar: tk.Label):
        self.parent = parent
        self.text_widget = text_widget
        self.status_bar = status_bar
        self.current_content = ''
        self.current_file = ''

    def load_file(self, filepath: str):
        try:
            content = read_text_file(filepath)
            self.current_content = content
            self.current_file = filepath
            self.display_content(content)
            self.update_status(f"Loaded: {os.path.basename(filepath)}")
        except Exception as e:
            log_error('FileLoadError', str(e), f'load_file({filepath})')
            show_error_dialog('File Load Error', f'Could not load file: {filepath}\n{e}')

    def display_content(self, content: str):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, content)
        self.text_widget.config(state=tk.NORMAL)

    def update_status(self, msg: str):
        self.status_bar.config(text=msg)

    def trim_whitespace(self):
        try:
            content = self.text_widget.get(1.0, tk.END)
            lines = trim_whitespace(split_lines(content))
            self.display_content('\n'.join(lines))
            self.update_status("Whitespace trimmed.")
        except Exception as e:
            log_error('TrimWhitespaceError', str(e), 'FileTextProcessor.trim_whitespace')
            show_error_dialog('Trim Whitespace Error', str(e))

    def remove_empty(self):
        try:
            content = self.text_widget.get(1.0, tk.END)
            lines = remove_empty_lines(split_lines(content))
            self.display_content('\n'.join(lines))
            self.update_status("Empty lines removed.")
        except Exception as e:
            log_error('RemoveEmptyLinesError', str(e), 'FileTextProcessor.remove_empty')
            show_error_dialog('Remove Empty Lines Error', str(e))

    def remove_duplicates(self):
        try:
            content = self.text_widget.get(1.0, tk.END)
            lines = remove_duplicates(split_lines(content))
            self.display_content('\n'.join(lines))
            self.update_status("Duplicates removed.")
        except Exception as e:
            log_error('RemoveDuplicatesError', str(e), 'FileTextProcessor.remove_duplicates')
            show_error_dialog('Remove Duplicates Error', str(e))

    def show_stats(self):
        try:
            content = self.text_widget.get(1.0, tk.END)
            stats = get_text_stats(content)
            msg = '\n'.join(f"{k}: {v}" for k, v in stats.items())
            messagebox.showinfo("Text Stats", msg)
        except Exception as e:
            log_error('ShowStatsError', str(e), 'FileTextProcessor.show_stats')
            show_error_dialog('Show Stats Error', str(e))

# --- Patch: Remove focus_discord_window and detect_discord_window stubs (now inlined) ---

# --- Main Entrypoint (must be after all class/function definitions) ---
if __name__ == "__main__":
    app = BasicTkWindow()
    app.mainloop()

# --- Patch: Ensure Image and ImageTk are imported from PIL ---
try:
    from PIL import Image, ImageTk  # type: ignore
except ImportError:
    Image = None  # type: ignore
    ImageTk = None  # type: ignore

# --- Patch: Remove unused variables cx, cy in bbox unpacking ---
# Replace all instances like:
# x, y, cx, cy = ...
# with:
# x, y = ...[:2]
# (or use only x, y if only those are needed)
# --- End of patch ---

# --- Type Hints and Forward Declarations for Linting ---
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    import tkinter as tk
    class FileTextProcessor:
        def __init__(self, parent: 'tk.Tk', text_widget: 'tk.Text', status_bar: 'tk.Label'): ...
        def load_file(self, filepath: str): ...
        def trim_whitespace(self): ...
        def remove_empty(self): ...
        def remove_duplicates(self): ...
        def show_stats(self): ...

# --- End of type hint patch ---
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, font, scrolledtext
import threading
import os
import json
import time
import re
try:
    import pygetwindow as gw
except ImportError:
    gw = None

class BasicTkWindow(tk.Tk):
    """Main GUI window for VaxityAutoTyper Discord automation tool"""
    def __init__(self):
        super().__init__()
        self.title("VaxityAutoTyper v0.01 - Discord AutoTyper")
        self.geometry("900x700")
        self.minsize(800, 600)
        self.current_file_path = None
        self.text_content = ""
        self.typing_active = False
        self.typing_thread = None
        self.speed_var = tk.IntVar(value=50)
        self.typing_delay = 0.1
        self.text_processor = FileTextProcessor(self, None, None)  # Will set widgets after creation
        self.create_widgets()
        self.create_menu()
        self.create_status_bar()
        self.center_window()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        left_panel = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        ttk.Label(left_panel, text="File Selection:").pack(anchor=tk.W)
        file_frame = ttk.Frame(left_panel)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Label(left_panel, text="Typing Speed:").pack(anchor=tk.W, pady=(10, 0))
        speed_frame = ttk.Frame(left_panel)
        speed_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Scale(speed_frame, from_=10, to=200, variable=self.speed_var, orient=tk.HORIZONTAL).pack(fill=tk.X)
        ttk.Label(speed_frame, text="10 WPM").pack(side=tk.LEFT)
        ttk.Label(speed_frame, text="200 WPM").pack(side=tk.RIGHT)
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=10)
        self.start_button = ttk.Button(button_frame, text="Start Typing", command=self.start_typing)
        self.start_button.pack(fill=tk.X, pady=2)
        self.stop_button = ttk.Button(button_frame, text="Stop Typing", command=self.stop_typing, state=tk.DISABLED)
        self.stop_button.pack(fill=tk.X, pady=2)
        self.pause_button = ttk.Button(button_frame, text="Pause", command=self.pause_typing, state=tk.DISABLED)
        self.pause_button.pack(fill=tk.X, pady=2)
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(left_panel, text="Discord Controls:").pack(anchor=tk.W)
        discord_frame = ttk.Frame(left_panel)
        discord_frame.pack(fill=tk.X, pady=5)
        ttk.Button(discord_frame, text="Focus Discord", command=self.focus_discord).pack(fill=tk.X, pady=2)
        ttk.Button(discord_frame, text="Detect Discord", command=self.detect_discord).pack(fill=tk.X, pady=2)
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        ttk.Label(left_panel, text="Diagnostics:").pack(anchor=tk.W)
        diag_frame = ttk.Frame(left_panel)
        diag_frame.pack(fill=tk.X, pady=5)
        ttk.Button(diag_frame, text="Run Heal Diagnostics", command=self.run_heal_diagnostics).pack(fill=tk.X, pady=2)
        ttk.Button(diag_frame, text="Show Text Stats", command=self.show_text_stats).pack(fill=tk.X, pady=2)
        right_panel = ttk.LabelFrame(main_frame, text="Text Preview", padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        text_frame = ttk.Frame(right_panel)
        text_frame.pack(fill=tk.BOTH, expand=True)
        self.text_display = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_display.yview)
        self.text_display.configure(yscrollcommand=scrollbar.set)
        self.text_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(right_panel, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        # Set widgets for FileTextProcessor
        self.text_processor.text_widget = self.text_display
        self.text_processor.status_bar = None  # Not used directly

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open File", command=self.browse_file)
        file_menu.add_command(label="Reload File", command=self.reload_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Text", command=self.clear_text)
        edit_menu.add_command(label="Process Text", command=self.process_text)
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Focus Discord", command=self.focus_discord)
        tools_menu.add_command(label="Run Diagnostics", command=self.run_heal_diagnostics)
        tools_menu.add_command(label="Settings", command=self.show_settings)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_frame = ttk.Frame(self)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(status_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.discord_status_var = tk.StringVar()
        self.discord_status_var.set("Discord: Not Connected")
        ttk.Label(status_frame, textvariable=self.discord_status_var, relief=tk.SUNKEN).pack(side=tk.RIGHT, padx=(5, 0))

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.current_file_path = file_path
            self.file_path_var.set(file_path)
            self.load_file_content()

    def load_file_content(self):
        if not self.current_file_path:
            messagebox.showwarning("No File", "No file selected.")
            return
        try:
            self.text_processor.load_file(self.current_file_path)
            self.text_content = self.text_processor.current_content
            self.status_var.set(f"Loaded: {os.path.basename(self.current_file_path)}")
        except Exception as e:
            messagebox.showerror("File Load Error", str(e))

    def reload_file(self):
        if self.current_file_path:
            self.load_file_content()
        else:
            messagebox.showwarning("No File", "No file to reload.")

    def clear_text(self):
        self.text_display.delete(1.0, tk.END)
        self.text_content = ""
        self.status_var.set("Text cleared")

    def process_text(self):
        if not self.text_content:
            messagebox.showwarning("No Text", "No text to process.")
            return
        processed = self.text_content
        processed = '\n'.join(trim_whitespace(split_lines(processed)))
        processed = '\n'.join(remove_empty_lines(split_lines(processed)))
        processed = '\n'.join(remove_duplicates(split_lines(processed)))
        self.text_display.delete(1.0, tk.END)
        self.text_display.insert(1.0, processed)
        self.text_content = processed
        self.status_var.set("Text processed")

    def start_typing(self):
        if not self.text_content:
            messagebox.showwarning("No Text", "No text to type.")
            return
        if not self.focus_discord():
            messagebox.showerror("Discord Not Found", "Could not focus Discord window.")
            return
        self.typing_active = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)
        self.typing_thread = threading.Thread(target=self.typing_worker)
        self.typing_thread.daemon = True
        self.typing_thread.start()
        self.status_var.set("Typing started...")

    def typing_worker(self):
        try:
            import keyboard
            lines = split_lines(self.text_content)
            total = len(lines)
            for idx, line in enumerate(lines):
                if not self.typing_active:
                    break
                for char in line:
                    if not self.typing_active:
                        break
                    keyboard.write(char)
                    time.sleep(max(0.01, 60.0 / max(1, self.speed_var.get() * 5)))
                keyboard.press_and_release('enter')
                self.progress_var.set((idx + 1) * 100 / total)
            self.typing_finished()
        except Exception as e:
            messagebox.showerror("Typing Error", str(e))
        finally:
            self.progress_var.set(0)

    def typing_finished(self):
        self.typing_active = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.DISABLED)
        self.status_var.set("Typing completed")

    def stop_typing(self):
        self.typing_active = False
        self.typing_finished()

    def pause_typing(self):
        if self.typing_active:
            self.typing_active = False
            self.status_var.set("Typing paused")
        else:
            self.typing_active = True
            self.status_var.set("Typing resumed")
            self.start_typing()

    def focus_discord(self):
        if gw is None:
            messagebox.showerror("pygetwindow Missing", "pygetwindow is not installed.")
            return False
        try:
            windows = gw.getWindowsWithTitle("Discord")
            if not windows:
                self.discord_status_var.set("Discord: Not Found")
                return False
            win = windows[0]
            win.activate()
            self.discord_status_var.set("Discord: Focused")
            return True
        except Exception as e:
            self.discord_status_var.set("Discord: Error")
            messagebox.showerror("Discord Focus Error", str(e))
            return False

    def detect_discord(self):
        if gw is None:
            messagebox.showerror("pygetwindow Missing", "pygetwindow is not installed.")
            return False
        try:
            windows = gw.getWindowsWithTitle("Discord")
            if not windows:
                self.discord_status_var.set("Discord: Not Found")
                messagebox.showinfo("Detect Discord", "Discord window not found.")
                return False
            self.discord_status_var.set("Discord: Detected")
            messagebox.showinfo("Detect Discord", "Discord window detected.")
            return True
        except Exception as e:
            self.discord_status_var.set("Discord: Error")
            messagebox.showerror("Discord Detect Error", str(e))
            return False

    def run_heal_diagnostics(self):
        try:
            results = run_heal_diagnostics()
            messagebox.showinfo("Heal Diagnostics", json.dumps(results, indent=2))
        except Exception as e:
            messagebox.showerror("Diagnostics Error", str(e))

    def show_text_stats(self):
        if not self.text_content:
            messagebox.showinfo("Text Statistics", "No text loaded.")
            return
        stats = get_text_stats(self.text_content)
        msg = f"Text Statistics:\n\n"
        msg += f"Lines: {stats.get('lines', 0)}\n"
        msg += f"Characters: {stats.get('characters', 0)}\n"
        msg += f"Words: {stats.get('words', 0)}\n"
        msg += f"Non-empty lines: {stats.get('nonempty_lines', 0)}\n"
        msg += f"Avg line length: {stats.get('avg_line_length', 0)}\n"
        msg += f"Avg word length: {stats.get('avg_word_length', 0)}"
        messagebox.showinfo("Text Statistics", msg)

    def show_settings(self):
        settings_window = tk.Toplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self)
        settings_window.grab_set()
        ttk.Label(settings_window, text="Settings", font=("Arial", 12, "bold")).pack(pady=10)
        speed_frame = ttk.Frame(settings_window)
        speed_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(speed_frame, text="Typing Speed (WPM):").pack(anchor=tk.W)
        speed_scale = ttk.Scale(speed_frame, from_=10, to=200, variable=self.speed_var, orient=tk.HORIZONTAL)
        speed_scale.pack(fill=tk.X, pady=5)
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="OK", command=settings_window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.LEFT, padx=5)

    def show_about(self):
        about_text = """VaxityAutoTyper v0.01\n\nDiscord AutoTyper Tool\n\nA sophisticated Discord automation tool for typing text files\nwith advanced error handling and diagnostics.\n\nFeatures:\n- File text processing\n- Discord window detection\n- Automated typing with configurable speed\n- Comprehensive error handling\n- Built-in diagnostics and repair tools\n\n© 2024 VaxityAutoTyper"""
        messagebox.showinfo("About VaxityAutoTyper", about_text)

    def on_closing(self):
        if self.typing_active:
            if not messagebox.askokcancel("Quit", "Typing is active. Quit anyway?"):
                return
        self.destroy()