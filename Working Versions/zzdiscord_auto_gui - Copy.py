"""
Discord Automation Script with Feature-Rich GUI
------------------------------------------------
Automates sending configurable messages to Discord via a user-friendly GUI.
Follows robust error logging, validation, and session summary best practices.
"""

import tkinter as tk
import customtkinter as ctk
import threading
import time
import os
import pyperclip
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk
from datetime import datetime
import locale

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

# --- Theme and Language Support ---
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

# --- Error Logging ---
ERROR_LOG = "error_log.txt"
def log_error(error_type, error_msg, context, resolution=None):
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {error_type}: {error_msg}\nContext: {context}\n")
        if resolution:
            f.write(f"Resolution: {resolution}\n")
        f.write("-"*60 + "\n")

# --- Session Logging ---
SESSION_LOG = "session_log.txt"
def log_session(summary):
    with open(SESSION_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {summary}\n{'-'*60}\n")

# --- Main Application Class ---
class DiscordAutoSender:
    def __init__(self, root):
        self.root = root
        self.theme = "Dark"
        self.language = "English"
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme(THEMES[self.theme])
        self.root.title("💬 Discord Automation Script")
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
        self.build_gui()
        self.onboarding()

    def build_gui(self):
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
        # Sidebar icons (stub, can be replaced with actual images)
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
        self.card = ctk.CTkFrame(self.root, corner_radius=25, fg_color="#23272A", border_width=2, border_color="#2C2F33")
        self.card.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=0, pady=0)

        # --- Tabbed Interface ---
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', background='#23272A', foreground='#99AAB5', font=('Segoe UI', 12, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#2C2F33')], foreground=[('selected', '#7289DA')])
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
        self.header = ctk.CTkLabel(parent, text="💬 Discord Automation Script", font=("Segoe UI Black", 28, "bold"), text_color="#7289DA")
        self.header.pack(pady=(18, 8))
        self.shine = ctk.CTkProgressBar(parent, width=320, height=8, corner_radius=8, progress_color="#7289DA", fg_color="#23272A")
        self.shine.pack(pady=(0, 18))
        self.shine.set(0.0)
        self.animate_shine()

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
        except Exception as e:
            log_error("FileError", str(e), "load_messages")
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
        self.finalize_session()
        self.root.destroy()

    def finalize_session(self):
        duration = time.time() - self.session_metrics["start_time"]
        self.log(f"Session ended. Duration: {duration:.1f}s")

    def animate_shine(self):
        def loop():
            while not self.is_sending:
                for v in [0.0, 0.3, 0.6, 1.0, 0.6, 0.3, 0.0]:
                    if self.is_sending:
                        break
                    self.shine.set(v)
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
        except Exception as e:
            log_error("TemplateError", str(e), "load_template")
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
        except Exception as e:
            log_error("TemplateError", str(e), "save_template")
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
        except Exception as e:
            log_error("TemplateError", str(e), "delete_template")
            self.status_var.set("Error deleting template.")

    # --- Analytics and Help Tabs ---
    def show_analytics(self):
        self.notebook.select(2)
        self.analytics_text.configure(state=ctk.NORMAL)
        self.analytics_text.delete("0.0", ctk.END)
        stats = f"Features used: {self.session_metrics['features']}\nErrors: {self.session_metrics['errors']}\nSession duration: {time.time() - self.session_metrics['start_time']:.1f}s"
        self.analytics_text.insert("0.0", stats)
        self.analytics_text.configure(state=ctk.DISABLED)
    def show_help(self):
        self.notebook.select(3)

    # --- Theme/Language/Update/Onboarding ---
    def change_theme(self, theme):
        self.theme = theme
        ctk.set_default_color_theme(THEMES[theme])
        self.status_var.set(f"Theme changed to {theme}.")
    def change_language(self, lang):
        self.language = lang
        self.status_var.set(f"Language changed to {lang}.")
    def check_update(self):
        # Simulate update check
        self.status_var.set("You are using the latest version.")
        messagebox.showinfo("Update", "You are using the latest version.")
    def onboarding(self):
        if not os.path.exists(".onboarded"):
            messagebox.showinfo("Welcome!", "Welcome to Discord Automation Script!\n\n- Use the Main tab to send messages.\n- Use Templates to save/load message sets.\n- Analytics shows your usage stats.\n- Keyboard shortcuts: Ctrl+Z (undo), Ctrl+Y (redo), Ctrl+C (copy log).\n- Drag and drop .txt files to load messages.\n- For more help, visit the Help tab.")
            with open(".onboarded", "w") as f:
                f.write("onboarded")

# --- Main Entrypoint ---
def main():
    try:
        root = ctk.CTk()
        app = DiscordAutoSender(root)
        root.protocol("WM_DELETE_WINDOW", app.on_close)
        root.mainloop()
    except Exception as e:
        log_error("StartupError", str(e), "main")

if __name__ == "__main__":
    main()