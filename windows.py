import customtkinter
from customtkinter import *
import webbrowser
import os
import requests
from tkinter import messagebox
from difflib import get_close_matches
from datetime import datetime
from pathlib import Path
import time
import platform
import sys
import logging

# ======================
# CONFIGURATION
# ======================
CURRENT_VERSION = "1.4.1"
submitted_name = ""
DB = None
typing_timer = None

# Set up paths and logging
def setup_environment():
    system = platform.system().lower()
    if system == 'windows':
        CONFIG_DIR = Path(os.getenv('PROGRAMDATA')) / "SPF_S"
    elif system == 'darwin':
        CONFIG_DIR = Path.home() / "Library" / "Application Support" / "SPF_S"
    else:
        CONFIG_DIR = Path.home() / ".config" / "SPF_S"
    
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        filename=CONFIG_DIR / 'app.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    return CONFIG_DIR

CONFIG_DIR = setup_environment()
POLICY_ACCEPTED_FILE = CONFIG_DIR / "policy_accepted"
NAME_FILE = CONFIG_DIR / "Name_submitted"
BROWSER_PREF_FILE = CONFIG_DIR / "browser_pref"
ATTEMPTS_FILE = CONFIG_DIR / "attempts.txt"
LOCK_TIME_FILE = CONFIG_DIR / "lock_time.txt"

# ======================
# DATA
# ======================
# ===== PROFILE DATABASE =====
PROFILE_URLS = {}
EASTER_EGGS = {}

def load_data():
    """Load both profiles and Easter eggs from external sources"""
    global PROFILE_URLS, EASTER_EGGS
    
    # 1. Load profiles
    try:
        profile_data = requests.get(
            "PROFILE LIST TXT PLACEHOLDER",
            timeout=5
        ).text
        PROFILE_URLS = eval(f"{{{profile_data}}}") if profile_data else {}
    except:
        PROFILE_URLS = {
            "Error - Click me to learn more": "https://aeos-assets.web.app/SPD/err/"
        }

    # 2. Load Easter eggs (same format)
    try:
        egg_data = requests.get(
            "EASTER EGGS TXT PLACEHOLDER",
            timeout=5
        ).text
        EASTER_EGGS = eval(f"{{{egg_data}}}") if egg_data else {}
    except:
        EASTER_EGGS = {
            "Error - Click me to learn more": "https://aeos-assets.web.app/SPD/err/"
        }

# ACTUALLY CALL THE FUNCTION TO LOAD DATA
load_data()  # This line was missing before!

POLICY_TEXT = """
    | Data Collection |:
    - Name (asked in the initialization of app)
    - Logged Search queries (logged with name,time,the 
        search query, dev team can see.)

    | How do we quickly give you access to Schoology profiles? |:
        -We have a list of peoples names, affiliated with their 
        schoology profiles. With this is what we are able to make 
        schoology profile viewing accesible. if you do not wish for
        your schoology profile to be seen, refer to the "Requests"
        section of the privacy policy
    
    | Requests |:
        - DM @spd_requests to:
            * Review collected data
            * Request deletion of profile
                -if it does exist in the database
                at the time of request.
             * Deletion of previous logged data
   
     | Profile data is |:
        - Already publicly available through school systems
        - Used transformatively for educational efficiency
        - Not creating new privacy exposure
        - Only accessible through schoology (you cannot view them
        without a valid NPS account)

        || TOS ||: 

    | What you may NOT use this tool for:
        -Shipping individuals together in slides
        -Gooning
        -Other non-school apopriate practices.

    | You may not repackage/redistribute |
        -Names found while using this app
        -The app itself
        -Links found while using this app
        -Code found while using this app/
            looking in its files.
        
    If you have a problem with these conditions, please seek
    another schoology database, as these are mandatory, and will
    not be tolereated if broken.

    This is not an official schoology tool nor a
    Northville Public Schools one. This was made by a
    student(s). By using this app, agree that you
    have a valid NPS schoology account, and you have 
    clearance to view NPS schoology profiles.

    """

# ======================
# CORE FUNCTIONALITY
# ======================

def print_name(event=None):
    global submitted_name
    name = OTBE.get().strip()
    if not name:
        messagebox.showwarning("Empty Name", "Please enter your name")
        return
    submitted_name = name
    
    # Save the name to file
    with open(NAME_FILE, "w") as f:
        f.write(submitted_name)
    
    # Remove the name entry widgets
    OTBE.place_forget()
    OTBB.place_forget()
    
    # Now initialize the main app
    initialize_main_app()
    
def set_default_browser(choice):
    global DB
    try:
        browsers = {
            "Chrome": 'chrome',
            "Safari": 'safari',
            "Firefox": 'firefox',
            "Edge": 'edge'
        }
        DB = webbrowser.get(browsers.get(choice))
        with open(BROWSER_PREF_FILE, "w") as f:
            f.write(choice)
        return True
    except webbrowser.Error as e:
        messagebox.showerror("Browser Error", f"Could not set {choice} as default browser: {str(e)}")
        DB = webbrowser.get()
        return False

def load_browser_preference():
    if BROWSER_PREF_FILE.exists():
        with open(BROWSER_PREF_FILE, "r") as f:
            return f.read().strip()
    return "Chrome"

def check_name_file():
    global submitted_name
    if NAME_FILE.exists():
        with open(NAME_FILE, "r") as f:
            submitted_name = f.read().strip()
        return True
    return False

def open_settings():
    settings_window = CTkToplevel(app)
    settings_window.title("Settings")
    settings_window.geometry("400x300")
    
    # Theme toggle
    def change_theme():
        current = customtkinter.get_appearance_mode()
        customtkinter.set_appearance_mode("Dark" if current == "Light" else "Light")
    
    CTkButton(
        settings_window,
        text="Toggle Dark/Light Mode",
        command=change_theme
    ).pack(pady=10)
    
    # Browser selection
    browser_label = CTkLabel(settings_window, text="Default Browser:")
    browser_label.pack()
    
    browser_var = customtkinter.StringVar(value=load_browser_preference())
    browser_dropdown = CTkComboBox(
        settings_window,
        values=["Chrome", "Safari", "Firefox", "Edge"],
        variable=browser_var,
        command=set_default_browser
    )
    browser_dropdown.pack(pady=5)
    
    # Reset button (DANGER ZONE)
    reset_frame = CTkFrame(settings_window, fg_color="transparent")
    reset_frame.pack(pady=20, fill="x", expand=True)
    
    CTkLabel(
        reset_frame,
        text="⚠️ Danger Zone ⚠️",
        text_color="red"
    ).pack()
    
    CTkButton(
        reset_frame,
        text="RESET ALL DATA",
        fg_color="red",
        hover_color="darkred",
        command=lambda: [
            messagebox.showwarning("Warning", "This will delete ALL saved data"),
            reset_application_data()  # We'll define this next
        ]
    ).pack(pady=10)
    
def reset_application_data():
    """Delete all stored preferences"""
    files_to_delete = [
        POLICY_ACCEPTED_FILE,
        NAME_FILE,
        BROWSER_PREF_FILE,
        ATTEMPTS_FILE,
        LOCK_TIME_FILE
    ]
    
    for file in files_to_delete:
        try:
            if file.exists():
                file.unlink()  # Delete the file
        except Exception as e:
            logging.error(f"Failed to delete {file}: {e}")
    
    messagebox.showinfo("Reset Complete", "All data cleared. The app will now restart.")
    app.destroy()
    # Restart the application
    os.execl(sys.executable, sys.executable, *sys.argv)
    
def check_name_file():
    global submitted_name
    if NAME_FILE.exists():
        with open(NAME_FILE, "r") as f:
            submitted_name = f.read().strip()
        return True
    return False
# ======================
# PASSWORD SYSTEM
# ======================
LOCK_DURATION = 3600  # 1 hour in seconds

def show_hint():
    hint_label = CTkLabel(master=password_frame,
                        text="Hint: BDAY-25",
                        font=("Futura", 15))
    hint_label.place(relx=0.5, rely=0.9, anchor="center")
    app.after(5000, lambda: hint_label.place_forget() if hint_label.winfo_exists() else None)

def update_attempts_display():
    if is_locked_out():
        remaining = get_lock_time_remaining()
        hours, remainder = divmod(remaining, 3600)
        minutes, seconds = divmod(remainder, 60)
        Try_count.configure(text=f"LOCKED - Time remaining: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}", 
                          text_color="red")
    else:
        attempts = get_attempts()
        Try_count.configure(text=f"{attempts} attempt(s) remaining",
                          text_color="red" if attempts == 1 else "white")

def get_attempts():
    if ATTEMPTS_FILE.exists():
        try:
            with open(ATTEMPTS_FILE, 'r') as f:
                return int(f.read().strip())
        except:
            pass
    return 3

def save_attempts(attempts):
    with open(ATTEMPTS_FILE, 'w') as f:
        f.write(str(attempts))

def is_locked_out():
    if not LOCK_TIME_FILE.exists():
        return False
    try:
        with open(LOCK_TIME_FILE, 'r') as f:
            return time.time() < float(f.read().strip())
    except:
        return False

def get_lock_time_remaining():
    if not is_locked_out():
        return 0
    with open(LOCK_TIME_FILE, 'r') as f:
        return max(0, float(f.read().strip()) - time.time())

def set_lockout():
    with open(LOCK_TIME_FILE, 'w') as f:
        f.write(str(time.time() + LOCK_DURATION))
    save_attempts(3)
    disable_interface()

def check_password():
    if is_locked_out():
        update_attempts_display()
        return
        
    password = password_entry.get().strip()
    if not password:
        messagebox.showwarning("Empty Password", "Please enter a password")
        return
        
    if password_entry.get().strip() == "kalahari25":
        save_attempts(3)
        if LOCK_TIME_FILE.exists():
            LOCK_TIME_FILE.unlink()
        password_frame.destroy()
        initialize_main_app()  # This will handle name check
    else:
        attempts = get_attempts() - 1
        save_attempts(attempts)
        
        if attempts > 0:
            messagebox.showwarning("Incorrect Password", f"{attempts} attempt(s) remaining")
            password_entry.delete(0, 'end')
            if attempts == 2:
                forgot_password_button.place(relx=0.5, rely=0.7, anchor="center")
        else:
            set_lockout()
            messagebox.showerror("Locked Out", "No attempts remaining. Locked for 1 hour.")
        
        update_attempts_display()

def update_timer():
    if is_locked_out():
        remaining = get_lock_time_remaining()
        if remaining <= 0:
            enable_interface()
            if LOCK_TIME_FILE.exists():
                try:
                    LOCK_TIME_FILE.unlink()
                except:
                    pass
    update_attempts_display()
    app.after(1000, update_timer)

def enable_interface():
    password_entry.configure(state="normal")
    submit_btn.configure(state="normal")
    forgot_password_button.configure(state="normal")

def disable_interface():
    password_entry.configure(state="disabled")
    submit_btn.configure(state="disabled")
    forgot_password_button.configure(state="disabled")

# ======================
# MAIN APPLICATION
# ======================
def update_suggestions(event=None):
    global typing_timer
    
    if typing_timer:
        app.after_cancel(typing_timer)
    
    def delayed_update():
        current_input = entry.get().strip().lower()
        if not current_input:
            if hasattr(app, 'suggestion_frame'):
                app.suggestion_frame.place_forget()
            return
            
        suggestions = get_close_matches(current_input, 
                                      list(PROFILE_URLS.keys()) + list(EASTER_EGGS.keys()), 
                                      n=4, cutoff=0.3)
        
        if suggestions:
            if not hasattr(app, 'suggestion_frame'):
                app.suggestion_frame = CTkFrame(master=app, fg_color="transparent")
            
            app.suggestion_frame.place(relx=0.5, rely=0.6, anchor="n")
            
            for widget in app.suggestion_frame.winfo_children():
                widget.destroy()
                
            CTkLabel(app.suggestion_frame, text="Suggestions:", font=("Futura", 14)).pack(pady=(0, 5))
            
            for i, suggestion in enumerate(suggestions):
                btn = CTkButton(
                    app.suggestion_frame,
                    text=suggestion.title(),
                    font=("Helvetica", 12),
                    width=300,
                    command=lambda s=suggestion: select_suggestion(s),
                    fg_color="#000000",
                    hover_color="#111111",
                    text_color="white"
                )
                btn.pack(pady=2)
                app.after(150 * i, lambda b=btn: fade_in_button(b))
    
    typing_timer = app.after(300, delayed_update)

def fade_in_button(button):
    if not button.winfo_exists():
        return
    
    colors = ["#111111", "#1a1a1a", "#222222", "#2a2a2a", "#333333"]
    for color in colors:
        if not button.winfo_exists():
            return
        try:
            hover_r = min(255, int(color[1:3], 16)+20)
            hover_g = min(255, int(color[3:5], 16)+20)
            hover_b = min(255, int(color[5:7], 16)+20)
            hover_color = f"#{hover_r:02x}{hover_g:02x}{hover_b:02x}"
            
            button.configure(fg_color=color, hover_color=hover_color)
            button.update()
            time.sleep(0.02)
        except:
            return

def select_suggestion(suggestion):
    entry.delete(0, 'end')
    entry.insert(0, suggestion)
    if hasattr(app, 'suggestion_frame'):
        app.suggestion_frame.place_forget()
    print_value()

def print_value(event=None):
    query = entry.get().strip().lower()
    
    # 1. Check Easter eggs first
    if query in EASTER_EGGS:
        webbrowser.open(EASTER_EGGS[query])
        return
    
    # 2. Check main profiles
    if query in PROFILE_URLS:
        webbrowser.open(PROFILE_URLS[query])
    else:
        # 3. Show suggestions
        suggestions = get_close_matches(query, list(PROFILE_URLS.keys()), n=3)
        msg = f"No profile found for '{query}'"
        if suggestions:
            msg += f"\n\nDid you mean:\n" + "\n".join(f"• {s.title()}" for s in suggestions)
        messagebox.showinfo("Not Found", msg)

def initialize_main_app():
    global entry, btn, OTBE, OTBB
    
    # Check if name has been submitted
    if not check_name_file():
        # Show name prompt
        OTBE = CTkEntry(
            master=app,
            placeholder_text="What is your name? (Full name)",
            font=("Helvetica", 20),
            fg_color="transparent",
            width=400
        )
        OTBB = CTkButton(
            master=app,
            text="Submit (one time)",
            font=("Futura", 15),
            command=print_name
        )
        OTBE.place(relx=0.5, rely=0.7, anchor="center")
        OTBB.place(relx=0.5, rely=0.8, anchor="center")
        OTBE.bind("<Return>", print_name)
        return  # Don't show main app yet
    
    # Main application UI (only shown if name exists)
    now = datetime.now()
    target = datetime(now.year, 6, 11, 12, 45)
    days = (target - now).days
    
    # UI elements
    CTkLabel(master=app, 
            text=f"Welcome back, {submitted_name}!", 
            font=("Futura", 20)).place(relx=0.5, rely=0.42, anchor="center")
    
    CTkLabel(master=app, 
            text=f"{days}d until school ends",
            font=("Futura", 15, 'bold'),
            text_color="white").place(relx=0.5, rely=0.9, anchor="center")
    
    CTkLabel(master=app, 
            text="SCHOOLOGY PROFILE DATABASE", 
            font=("Futura", 30, 'bold'), 
            text_color="#3EC2FA").place(relx=0.5, rely=0.35, anchor="center")
    
    CTkLabel(master=app, 
            text=CURRENT_VERSION,
            font=("Futura", 10, 'bold'), 
            text_color="Gray").place(relx=0.97, rely=0.028, anchor="center")
    
    entry = CTkEntry(master=app, 
                    placeholder_text="Who do you want to find?", 
                    font=("Helvetica", 12.5, 'bold'), 
                    width=500, height=30)
    btn = CTkButton(master=app, 
                   text="Search", 
                   font=("Futura", 12.5), 
                   width=150, height=27.5, 
                   command=print_value)
    
    entry.pack(anchor="s", expand=True, pady=10)
    btn.pack(anchor="n", expand=True)
    
    entry.bind("<Return>", print_value)
    entry.bind("<KeyRelease>", update_suggestions)

# ======================
# APPLICATION STARTUP
# ======================
if __name__ == "__main__":
    # Initialize main window
    app = CTk()
    app.title("Schoology Profile Database")
    app.geometry("900x700")
    
    # Add this RIGHT AFTER creating your main app window (app = CTk())
    settings_btn = CTkButton(
    master=app,
    text="⚙️",
    width=30,
    height=30,
    command=open_settings,  # We'll define this next
    fg_color="transparent",
    hover_color="#333333"
)
    settings_btn.place(relx=0.95, rely=0.03, anchor="ne")  # Top-right corner
    
    # Load browser preference
    set_default_browser(load_browser_preference())
    
    # Check privacy policy
    if not POLICY_ACCEPTED_FILE.exists():
        policy_window = CTkToplevel(app)
        policy_window.title("Privacy Policy Agreement")
        policy_window.geometry("600x400")
        policy_window.resizable(False, False)
        policy_window.grab_set_global()
        
        # Policy content
        scroll_frame = CTkScrollableFrame(policy_window, width=550, height=250)
        scroll_frame.pack(pady=10)
        CTkLabel(scroll_frame, text=POLICY_TEXT, font=("Helvetica", 14), justify="left").pack(padx=10, pady=10)
        
        # Buttons
        btn_frame = CTkFrame(policy_window)
        btn_frame.pack(pady=10)
        
        CTkButton(btn_frame, 
                 text="✓ Accept", 
                 command=lambda: [POLICY_ACCEPTED_FILE.touch(), policy_window.destroy()],
                 fg_color="#2AA876").pack(side="left", padx=20)
        
        CTkButton(btn_frame,
                 text="✗ Decline",
                 command=lambda: [policy_window.destroy(), app.quit(), sys.exit(0)],
                 fg_color="#E74C3C").pack(side="right", padx=20)
        
        # Center window
        policy_window.update_idletasks()
        width = policy_window.winfo_width()
        height = policy_window.winfo_height()
        x = (policy_window.winfo_screenwidth() // 2) - (width // 2)
        y = (policy_window.winfo_screenheight() // 2) - (height // 2)
        policy_window.geometry(f'+{x}+{y}')
        
        app.wait_window(policy_window)
    
    # Password protection
    password_frame = CTkFrame(master=app)
    password_frame.pack(fill="both", expand=True)
    
    Try_count = CTkLabel(master=password_frame, font=("Futura", 15, 'bold'))
    Try_count.place(relx=0.5, rely=0.5, anchor="center")
    
    CTkLabel(master=password_frame, 
            text="Enter Access Code:",
            font=("Futura", 20)).pack(pady=20)
    
    password_entry = CTkEntry(master=password_frame, 
                            show="*", 
                            font=("Futura", 15),
                            width=200)
    password_entry.pack(pady=10)
    
    submit_btn = CTkButton(master=password_frame, 
                         text="Submit", 
                         command=check_password,
                         font=("Futura", 15))
    submit_btn.pack(pady=20)
    
    forgot_password_button = CTkButton(master=password_frame,
                                     text="Forgot Password?",
                                     font=("Futura", 15),
                                     command=show_hint)
    
    password_entry.bind("<Return>", lambda event: check_password())
    
    # Start timer and main loop
    update_attempts_display()
    app.after(1000, update_timer)
    app.mainloop()
