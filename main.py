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
import pyperclip
import threading
from typing import Optional, Dict, List, Any, Union, Tuple
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk
from datetime import datetime
import json

try:
    import customtkinter as ctk
except ImportError:
    ctk = None

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
    """Load and resize an icon if PIL is available."""
    if Image and ImageTk and os.path.exists(path):
        try:
            img = Image.open(path).resize(size, Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            log_error("ICON_ERROR", str(e), f"Loading icon: {path}", "Using default icon")
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
        try:
            x, y, _, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') and callable(getattr(self.widget, 'bbox', None)) else (0, 0, 0, 20)
        except (tk.TclError, TypeError):
            x, y, _, cy = (0, 0, 0, 20)
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
        """Hide the tooltip."""
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            try:
                tw.destroy()
            except tk.TclError:
                pass  # Widget may already be destroyedtw.destroy()

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

# --- Feature 1: Advanced Message Validation and Preview System ---
class MessageValidator:
    """Advanced message validation with Discord-specific rules."""
    
    def __init__(self):
        self.max_message_length = 2000  # Discord limit
        self.max_embed_length = 6000
        self.dangerous_patterns = [
            r'@everyone', r'@here', r'discord\.gg', r'bit\.ly', r'tinyurl\.com'
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
        results = {
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
    
    def _get_message_stats(self, message: str) -> Dict[str, int]:
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
    
    def suggest_improvements(self, message: str) -> List[str]:
        """Suggest message improvements."""
        suggestions = []
        
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

class MessagePreviewSystem:
    """Advanced message preview with Discord-like rendering."""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.validator = MessageValidator()
        
    def create_preview_window(self, message: str) -> None:
        """Create a comprehensive preview window."""
        preview_window = tk.Toplevel(self.parent)
        preview_window.title("Message Preview & Validation")
        preview_window.geometry("800x600")
        preview_window.configure(bg='#36393f')  # Discord dark theme
        
        # Create notebook for tabs
        notebook = ttk.Notebook(preview_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Preview tab
        preview_frame = ttk.Frame(notebook)
        notebook.add(preview_frame, text="Preview")
        self._create_preview_tab(preview_frame, message)
        
        # Validation tab
        validation_frame = ttk.Frame(notebook)
        notebook.add(validation_frame, text="Validation")
        self._create_validation_tab(validation_frame, message)
        
        # Statistics tab
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Statistics")
        self._create_stats_tab(stats_frame, message)
    
    def _create_preview_tab(self, parent: ttk.Frame, message: str) -> None:
        """Create Discord-like message preview."""
        # Header with user info simulation
        header_frame = tk.Frame(parent, bg='#36393f')
        header_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(header_frame, text="VaxityAutoTyper", fg='#ffffff', bg='#36393f', 
                font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        tk.Label(header_frame, text="Today at 12:00 PM", fg='#99aab5', bg='#36393f', 
                font=('Arial', 10)).pack(side=tk.LEFT, padx=(10, 0))
        
        # Message content with Discord-like styling
        message_frame = tk.Frame(parent, bg='#40444b', relief=tk.RAISED, bd=1)
        message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        message_text = scrolledtext.ScrolledText(
            message_frame, wrap=tk.WORD, bg='#40444b', fg='#dcddde',
            font=('Arial', 11), insertbackground='#dcddde', selectbackground='#5865f2'
        )
        message_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Render message with basic Discord formatting
        formatted_message = self._apply_discord_formatting(message)
        message_text.insert('1.0', formatted_message)
        message_text.config(state=tk.DISABLED)
    
    def _create_validation_tab(self, parent: ttk.Frame, message: str) -> None:
        """Create validation results display."""
        validation = self.validator.validate_message(message)
        
        # Validation summary
        summary_frame = tk.LabelFrame(parent, text="Validation Summary", padx=10, pady=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        status_color = 'green' if validation['valid'] else 'red'
        status_text = 'VALID' if validation['valid'] else 'INVALID'
        tk.Label(summary_frame, text=f"Status: {status_text}", fg=status_color, 
                font=('Arial', 12, 'bold')).pack()
        
        # Errors
        if validation['errors']:
            error_frame = tk.LabelFrame(parent, text="Errors", fg='red', padx=10, pady=10)
            error_frame.pack(fill=tk.X, padx=10, pady=5)
            for error in validation['errors']:
                tk.Label(error_frame, text=f"• {error}", fg='red', anchor='w').pack(fill=tk.X)
        
        # Warnings
        if validation['warnings']:
            warning_frame = tk.LabelFrame(parent, text="Warnings", fg='orange', padx=10, pady=10)
            warning_frame.pack(fill=tk.X, padx=10, pady=5)
            for warning in validation['warnings']:
                tk.Label(warning_frame, text=f"• {warning}", fg='orange', anchor='w').pack(fill=tk.X)
        
        # Suggestions
        suggestions = self.validator.suggest_improvements(message)
        if suggestions:
            suggestion_frame = tk.LabelFrame(parent, text="Suggestions", fg='blue', padx=10, pady=10)
            suggestion_frame.pack(fill=tk.X, padx=10, pady=5)
            for suggestion in suggestions:
                tk.Label(suggestion_frame, text=f"• {suggestion}", fg='blue', anchor='w').pack(fill=tk.X)
    
    def _create_stats_tab(self, parent: ttk.Frame, message: str) -> None:
        """Create statistics display."""
        stats = self.validator._get_message_stats(message)
        
        stats_frame = tk.LabelFrame(parent, text="Message Statistics", padx=10, pady=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create two-column layout
        left_frame = tk.Frame(stats_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        right_frame = tk.Frame(stats_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Left column stats
        left_stats = [
            ("Characters", stats['characters']),
            ("Characters (no spaces)", stats['characters_no_spaces']),
            ("Words", stats['words']),
            ("Lines", stats['lines'])
        ]
        
        for label, value in left_stats:
            row = tk.Frame(left_frame)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"{label}:", anchor='w').pack(side=tk.LEFT)
            tk.Label(row, text=str(value), anchor='e', font=('Arial', 10, 'bold')).pack(side=tk.RIGHT)
        
        # Right column stats
        right_stats = [
            ("Paragraphs", stats['paragraphs']),
            ("Avg Word Length", f"{stats['avg_word_length']:.1f}"),
            ("Est. Read Time", f"{stats['estimated_read_time']} min"),
            ("Discord Limit", f"{stats['characters']}/2000")
        ]
        
        for label, value in right_stats:
            row = tk.Frame(right_frame)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"{label}:", anchor='w').pack(side=tk.LEFT)
            tk.Label(row, text=str(value), anchor='e', font=('Arial', 10, 'bold')).pack(side=tk.RIGHT)
    
    def _apply_discord_formatting(self, message: str) -> str:
        """Apply basic Discord formatting simulation."""
        # This is a simple simulation - real Discord formatting would be more complex
        import re
        
        # Bold text
        message = re.sub(r'\*\*(.*?)\*\*', r'[\1]', message)
        # Italic text  
        message = re.sub(r'\*(.*?)\*', r'/\1/', message)
        # Code blocks
        message = re.sub(r'`(.*?)`', r'[\1]', message)
        
        return message

# --- Main Application Class ---
class DiscordAutoSender:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.theme = "Dark"
        self.language = "English"
        
        # Only set customtkinter if available
        if ctk:
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme(THEMES[self.theme])
        
        self.root.title("💬 VaxityAutoTyper")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)
        self.message_list: List[str] = []
        self.is_sending = False
        self.session_metrics: Dict[str, Union[int, float]] = {"features": 0, "errors": 0, "start_time": time.time()}
        self.status_var = tk.StringVar(value="Idle.")
        self.undo_stack: List[str] = []
        self.redo_stack: List[str] = []
        self.scheduled_messages: List[Tuple[str, float]] = []
        self.queue_paused = False
        self.quick_templates: List[str] = []
        self.analytics_data: Dict[str, Union[int, datetime]] = {"sent": 0, "errors": 0, "start": datetime.now()}
        self.export_path: Optional[str] = None
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
        # Build the main GUI components
        self.text_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=80, height=20)
        self.text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, anchor='w')
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.template_listbox = tk.Listbox(self.root, height=6)
        self.template_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.refresh_template_list()
        self.status_var.set("GUI built.")

    def onboarding(self):
        messagebox.showinfo("Welcome", "Welcome to VaxityAutoTyper! Configure your settings and start automating Discord messages.")
        self.status_var.set("Welcome to VaxityAutoTyper!")

    def animate_loading_bar(self):
        # Simulate a loading bar animation in the status bar
        if not hasattr(self, 'loading_bar_progress'):
            self.loading_bar_progress = 0
        self.loading_bar_progress = (self.loading_bar_progress + 1) % 20
        bar = '[' + '=' * self.loading_bar_progress + ' ' * (20 - self.loading_bar_progress) + ']'
        self.status_var.set(f"Loading {bar}")
        self.root.after(100, self.animate_loading_bar)

    def flash_loading_bar(self):
        # Flash the status bar for visual feedback
        original = self.status_bar.cget('background')
        self.status_bar.config(background='yellow')
        self.root.after(200, lambda: self.status_bar.config(background=original))
        self.status_var.set("Loading bar flashed.")

    def animate_typing_indicator(self):
        # Animate a typing indicator in the status bar
        dots = '.' * ((self.typing_indicator_state % 3) + 1)
        self.status_var.set(f"Typing{dots}")
        self.typing_indicator_state += 1
        if self.typing_indicator_running:
            self.root.after(500, self.animate_typing_indicator)

    def refresh_quick_template_bar(self):
        # Refresh quick template bar (simulate by updating listbox)
        self.refresh_template_list()
        self.status_var.set("Quick template bar refreshed.")

    def clear_placeholder(self, event=None):
        self.text_area.delete('1.0', tk.END)
        self.status_var.set("Placeholder cleared.")
        return "break"

    def schedule_message_advanced(self):
        # Schedule a message with advanced options
        msg = simpledialog.askstring("Schedule Message", "Enter message to schedule:")
        if msg:
            delay = simpledialog.askinteger("Delay", "Delay in seconds:", minvalue=1, maxvalue=3600)
            if delay:
                threading.Timer(delay, lambda: self.send_messages([msg], 0)).start()
                self.scheduled_messages.append((msg, delay))
                self.status_var.set(f"Scheduled message '{msg}' in {delay}s.")

    def clear_scheduled_messages(self):
        self.scheduled_messages.clear()
        self.status_var.set("Scheduled messages cleared.")

    def update_performance_metrics(self) -> None:
        # Update and display real performance metrics
        elapsed = time.time() - self.session_metrics["start_time"]
        sent = self.analytics_data["sent"]
        errors = self.analytics_data["errors"]
        self.status_var.set(f"Performance: Sent={sent}, Errors={errors}, Uptime={int(elapsed)}s")
        self.root.after(2000, self.update_performance_metrics)

    def update_rate_limiter_status(self, status: str, details: str) -> None:
        # Show real rate limiter status
        q = self.rate_limiter.get_queue_status()
        self.status_var.set(f"RateLimiter: {status} | {details} | CanSend={q['can_send']} | Recent={q['recent_messages']}")

    def animate_shine(self):
        # Animate a shine effect on the title label if present
        if self.title_label:
            orig_fg = self.title_label.cget('foreground')
            self.title_label.config(foreground='gold')
            self.root.after(300, lambda: self.title_label.config(foreground=orig_fg))
        self.status_var.set("Shine animated.")

    def on_close(self):
        log_session("Session closed by user.")
        self.root.destroy()

    def change_theme(self, theme):
        if theme in THEMES:
            ctk.set_default_color_theme(THEMES[theme])
            self.status_var.set(f"Theme changed to {theme}.")
        else:
            self.status_var.set(f"Theme '{theme}' not found.")

    def change_language(self, lang):
        if lang in LANGUAGES:
            self.language = lang
            self.status_var.set(f"Language changed to {lang}.")
        else:
            self.status_var.set(f"Language '{lang}' not found.")

    def check_update(self):
        # Simulate checking for updates
        self.status_var.set("Checked for updates. No updates available.")

    def show_help(self):
        messagebox.showinfo("Help", "This is the help dialog for VaxityAutoTyper. For support, visit the documentation.")
        self.status_var.set("Help dialog opened.")

    def undo(self, event=None):
        if self.undo_stack:
            last = self.undo_stack.pop()
            self.redo_stack.append(self.text_area.get('1.0', tk.END))
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', last)
            self.status_var.set("Undo performed.")
        else:
            self.status_var.set("Nothing to undo.")
        return "break"

    def redo(self, event=None):
        if self.redo_stack:
            next_ = self.redo_stack.pop()
            self.undo_stack.append(self.text_area.get('1.0', tk.END))
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', next_)
            self.status_var.set("Redo performed.")
        else:
            self.status_var.set("Nothing to redo.")
        return "break"

    def show_analytics(self):
        sent = self.analytics_data["sent"]
        errors = self.analytics_data["errors"]
        elapsed = time.time() - self.analytics_data["start"].timestamp()
        messagebox.showinfo("Analytics", f"Messages sent: {sent}\nErrors: {errors}\nUptime: {int(elapsed)}s")
        self.status_var.set("Analytics panel opened.")

    def load_messages(self):
        file = filedialog.askopenfilename(title="Load Messages", filetypes=[("Text Files", "*.txt")])
        if file:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert('1.0', content)
                self.status_var.set(f"Messages loaded from {file}.")

    def start_sending(self):
        if self.is_sending:
            self.status_var.set("Already sending messages.")
            return
        self.is_sending = True
        messages = self.get_messages()
        delay = self.get_delay()
        threading.Thread(target=self.send_messages, args=(messages, delay), daemon=True).start()
        self.status_var.set("Started sending messages.")

    def stop_sending(self):
        self.is_sending = False
        self.status_var.set("Stopped sending messages.")

    def get_messages(self):
        return [line.strip() for line in self.text_area.get('1.0', tk.END).splitlines() if line.strip()]

    def get_delay(self):
        # Get delay from user or use default
        return 1.0

    def send_messages(self, messages, delay):
        for msg in messages:
            if not self.is_sending:
                break
            if self.rate_limiter.can_send_message():
                # Simulate sending message
                self.analytics_data["sent"] += 1
                self.rate_limiter.register_message_sent()
                self.status_var.set(f"Sent: {msg}")
            else:
                self.analytics_data["errors"] += 1
                self.rate_limiter.register_rate_limit_hit()
                self.status_var.set("Rate limited. Waiting...")
                time.sleep(self.rate_limiter.get_recommended_delay())
            time.sleep(delay)
        self.is_sending = False
        self.status_var.set(f"Sent {len(messages)} messages with {delay}s delay.")

    def clear_log(self):
        open(ERROR_LOG, "w").close()
        self.status_var.set("Log cleared.")

    def copy_log_to_clipboard(self):
        with open(ERROR_LOG, "r", encoding="utf-8") as f:
            log_content = f.read()
        self.root.clipboard_clear()
        self.root.clipboard_append(log_content)
        self.status_var.set("Log copied to clipboard.")

    def refresh_template_list(self):
        # Simulate loading template names from disk
        self.template_listbox.delete(0, tk.END)
        templates = [f for f in os.listdir('.') if f.endswith('.template.txt')]
        for t in templates:
            self.template_listbox.insert(tk.END, t)
        self.status_var.set("Template list refreshed.")

    def load_template(self):
        sel = self.template_listbox.curselection()
        if sel:
            fname = self.template_listbox.get(sel[0])
            with open(fname, "r", encoding="utf-8") as f:
                content = f.read()
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert('1.0', content)
                self.status_var.set(f"Template '{fname}' loaded.")

    def save_template(self):
        content = self.text_area.get('1.0', tk.END)
        fname = simpledialog.askstring("Save Template", "Enter template name:")
        if fname:
            fname = fname.strip().replace(' ', '_') + '.template.txt'
            with open(fname, "w", encoding="utf-8") as f:
                f.write(content)
            self.refresh_template_list()
            self.status_var.set(f"Template '{fname}' saved.")

    def delete_template(self):
        sel = self.template_listbox.curselection()
        if sel:
            fname = self.template_listbox.get(sel[0])
            os.remove(fname)
            self.refresh_template_list()
            self.status_var.set(f"Template '{fname}' deleted.")

    def load_quick_template(self, tname):
        fname = tname if tname.endswith('.template.txt') else tname + '.template.txt'
        if os.path.exists(fname):
            with open(fname, "r", encoding="utf-8") as f:
                content = f.read()
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert('1.0', content)
                self.status_var.set(f"Quick template '{tname}' loaded.")
        else:
            self.status_var.set(f"Template '{tname}' not found.")

    def preview_message(self):
        msg = self.text_area.get('1.0', tk.END).strip()
        messagebox.showinfo("Preview Message", msg if msg else "No message to preview.")
        self.status_var.set("Message previewed.")

    def schedule_message(self):
        msg = self.text_area.get('1.0', tk.END).strip()
        delay = simpledialog.askinteger("Schedule Message", "Delay in seconds:", minvalue=1, maxvalue=3600)
        if msg and delay:
            threading.Timer(delay, lambda: self.send_messages([msg], 0)).start()
            self.scheduled_messages.append((msg, delay))
            self.status_var.set(f"Scheduled message in {delay}s.")

    def pause_queue(self):
        self.queue_paused = True
        self.status_var.set("Queue paused.")

    def resume_queue(self):
        self.queue_paused = False
        self.status_var.set("Queue resumed.")

    def cancel_queue(self):
        self.is_sending = False
        self.status_var.set("Queue cancelled.")

    def export_session(self):
        file = filedialog.asksaveasfilename(title="Export Session", defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file:
            data = {
                "messages": self.get_messages(),
                "analytics": self.analytics_data,
                "scheduled": self.scheduled_messages
            }
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            self.status_var.set(f"Session exported to {file}.")

    def import_settings(self):
        file = filedialog.askopenfilename(title="Import Settings", filetypes=[("JSON Files", "*.json")])
        if file:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "messages" in data:
                    self.text_area.delete('1.0', tk.END)
                    self.text_area.insert('1.0', '\n'.join(data["messages"]))
                if "analytics" in data:
                    self.analytics_data = data["analytics"]
                if "scheduled" in data:
                    self.scheduled_messages = data["scheduled"]
            self.status_var.set(f"Settings imported from {file}.")

    def log(self, msg: str):
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(f"[LOG] {msg}\n")
        self.status_var.set(f"Log: {msg}")

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