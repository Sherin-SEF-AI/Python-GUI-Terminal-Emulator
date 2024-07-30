import customtkinter as ctk
from tkinter import filedialog, messagebox, Scrollbar, Text, Toplevel
import subprocess
import time

class TerminalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Terminal GUI")

        # Initialize theme
        self.current_theme = "light"
        self.command_history = []
        self.history_index = 0

        # Create a frame for the main layout
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(expand=True, fill='both')

        # Create a frame for the terminal output
        self.terminal_frame = ctk.CTkFrame(self.main_frame, fg_color="#2E2E2E")  # Use fg_color for background
        self.terminal_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Create a scrolled text widget for the terminal output
        self.terminal_output = Text(self.terminal_frame, wrap="word", state='disabled', bg="#1e1e1e", fg="white", insertbackground="white", font=("Arial", 12))
        self.terminal_output.pack(expand=True, fill='both', side=ctk.LEFT)
        self.terminal_output_scrollbar = Scrollbar(self.terminal_frame, command=self.terminal_output.yview)
        self.terminal_output['yscrollcommand'] = self.terminal_output_scrollbar.set
        self.terminal_output_scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)

        # Create a frame for the buttons
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="#2E2E2E")  # Use fg_color for background
        self.button_frame.grid(row=0, column=1, sticky='ns', padx=10, pady=10)
        self.button_frame.grid_rowconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(0, weight=1)

        # Create an entry widget for command input
        self.entry_frame = ctk.CTkFrame(self.button_frame)
        self.entry_frame.pack(fill='x', padx=5, pady=5)

        self.command_entry = ctk.CTkEntry(self.entry_frame, width=300, font=("Arial", 12))
        self.command_entry.pack(side=ctk.LEFT, padx=5, pady=5, expand=True, fill='x')
        self.command_entry.bind('<Return>', self.execute_command)
        self.command_entry.bind('<Up>', self.show_previous_command)
        self.command_entry.bind('<Down>', self.show_next_command)
        self.command_entry.bind('<KeyRelease>', self.suggest_commands)

        # Create a dropdown for frequently used commands
        self.common_commands = [
            "ls", "pwd", "echo Hello, World!", "date", "uname -a", "whoami", "df -h",
            "free -m", "uptime", "ps aux", "netstat -tuln", "top", "grep --help",
            "ping -c 4 google.com", "cat /proc/cpuinfo", "cat /proc/meminfo",
            "tar -cvf archive.tar.gz /path/to/directory", "chmod 755 filename", "curl -O http://example.com/file"
        ]
        self.dropdown_var = ctk.StringVar(value=self.common_commands[0])
        self.dropdown = ctk.CTkOptionMenu(self.entry_frame, variable=self.dropdown_var, values=self.common_commands, command=self.suggest_commands)
        self.dropdown.pack(side=ctk.LEFT, padx=5, pady=5)

        # Create buttons with user-friendly sizes
        self.create_buttons(self.button_frame)

        # Create a frame for additional controls
        self.control_frame = ctk.CTkFrame(root)
        self.control_frame.pack(fill='x', side=ctk.BOTTOM, padx=10, pady=5)

        # Create a status bar
        self.status_bar = ctk.CTkLabel(self.control_frame, text="Ready", anchor='w', font=("Arial", 12))
        self.status_bar.pack(side=ctk.BOTTOM, fill='x', padx=10, pady=5)

        # Set initial theme
        self.set_theme(self.current_theme)

    def set_theme(self, theme):
        """Apply the specified theme to the application."""
        if theme == "dark":
            ctk.set_appearance_mode("dark")
            self.terminal_frame.configure(fg_color="#2E2E2E")
            self.terminal_output.configure(bg="#1e1e1e", fg="white", insertbackground="white")
        else:
            ctk.set_appearance_mode("light")
            self.terminal_frame.configure(fg_color="#FFFFFF")
            self.terminal_output.configure(bg="#FFFFFF", fg="black", insertbackground="black")

    def create_buttons(self, parent):
        buttons = [
            ("Enter", self.execute_command_button),
            ("Clear Entry", self.clear_entry),
            ("Clear Terminal", self.clear_terminal),
            ("Save Output", self.save_output),
            ("Load Session", self.load_session),
            ("Toggle Theme", self.toggle_theme),
            ("About", self.show_about),
            ("Help", self.show_help),
            ("Search Output", self.search_output)
        ]
        for text, command in buttons:
            button = ctk.CTkButton(parent, text=text, command=command, width=120, height=40, font=("Arial", 12))  # Adjusted size
            button.pack(padx=5, pady=5, fill='x')

    def execute_command(self, event=None):
        command = self.command_entry.get()
        if command:
            if command.startswith("sudo"):
                self.execute_sudo_command(command)
            else:
                self.execute_non_sudo_command(command)

    def execute_sudo_command(self, command):
        """Execute a command with sudo privileges."""
        def on_submit():
            password = password_entry.get()
            try:
                result = subprocess.run(f"echo {password} | sudo -S {command[5:]}", shell=True, text=True, capture_output=True)
                self.append_output(result.stdout, 'green')
                if result.stderr:
                    self.append_output(result.stderr, 'red')
                self.set_status("Command executed with sudo")
            except Exception as e:
                self.append_output(str(e), 'red')
                self.set_status("Error executing sudo command")
            password_window.destroy()

        password_window = Toplevel(self.root)
        password_window.title("Sudo Authentication")
        password_window.grab_set()

        password_label = ctk.CTkLabel(password_window, text="Enter sudo password:")
        password_label.pack(padx=10, pady=5)

        password_entry = ctk.CTkEntry(password_window, show='*', width=300)
        password_entry.pack(padx=10, pady=5)

        submit_button = ctk.CTkButton(password_window, text="Submit", command=on_submit)
        submit_button.pack(padx=10, pady=10)

    def execute_non_sudo_command(self, command):
        """Execute a command without sudo."""
        self.command_history.append(command)
        self.update_history_dropdown()
        self.history_index = len(self.command_history)
        self.append_output(f"$ {command}\n", 'white')
        self.set_status("Running...")
        start_time = time.time()
        try:
            # Run the command using subprocess
            result = subprocess.run(command, shell=True, text=True, capture_output=True)
            end_time = time.time()
            execution_time = end_time - start_time
            self.append_output(result.stdout, 'green')
            if result.stderr:
                self.append_output(result.stderr, 'red')
            self.set_status(f"Command executed in {execution_time:.2f} seconds")
        except Exception as e:
            self.append_output(str(e), 'red')
            self.set_status("Error")
        self.command_entry.delete(0, ctk.END)
        self.command_entry.focus_set()  # Ensure entry is focused for new command input
        self.suggest_commands(None)  # Reset dropdown suggestions

    def execute_command_button(self):
        self.execute_command()

    def clear_entry(self):
        self.command_entry.delete(0, ctk.END)
        self.set_status("Entry cleared")

    def append_output(self, text, color='white'):
        self.terminal_output.configure(state='normal')
        self.terminal_output.insert('end', text)
        self.terminal_output.tag_add(color, 'end-1c linestart', 'end')
        self.terminal_output.tag_config(color, foreground=color)
        self.terminal_output.configure(state='disabled')
        self.terminal_output.yview(ctk.END)

    def show_previous_command(self, event):
        if self.command_history:
            self.history_index = max(0, self.history_index - 1)
            self.command_entry.delete(0, ctk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])

    def show_next_command(self, event):
        if self.command_history:
            self.history_index = min(len(self.command_history), self.history_index + 1)
            if self.history_index < len(self.command_history):
                self.command_entry.delete(0, ctk.END)
                self.command_entry.insert(0, self.command_history[self.history_index])
            else:
                self.command_entry.delete(0, ctk.END)

    def clear_terminal(self):
        self.terminal_output.configure(state='normal')
        self.terminal_output.delete('1.0', ctk.END)
        self.terminal_output.configure(state='disabled')
        self.set_status("Terminal cleared")

    def save_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(self.terminal_output.get('1.0', ctk.END))
                messagebox.showinfo("Save Output", "Output saved successfully.")
                self.set_status("Output saved")
            except Exception as e:
                messagebox.showerror("Save Output", f"Error saving output: {e}")
                self.set_status("Error saving output")

    def toggle_theme(self):
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"
        self.set_theme(self.current_theme)

    def show_about(self):
        messagebox.showinfo("About", "Python Terminal GUI\nVersion 1.0\n\nCreated by Your Name")

    def show_help(self):
        help_text = (
            "Available Commands:\n"
            " - ls: List directory contents\n"
            " - pwd: Print working directory\n"
            " - echo Hello, World!: Print text\n"
            " - date: Display current date and time\n"
            " - uname -a: Show system information\n"
            " - whoami: Display current user\n"
            " - df -h: Display disk space usage\n"
            " - free -m: Show memory usage\n"
            " - uptime: Show system uptime\n"
            " - ps aux: List running processes\n"
            " - netstat -tuln: Show network connections\n"
            " - top: Display system resource usage\n"
            " - grep --help: Show help for grep command\n"
            " - ping -c 4 google.com: Ping a remote host\n"
            " - cat /proc/cpuinfo: Show CPU info\n"
            " - cat /proc/meminfo: Show memory info\n"
            "Press 'Enter' to execute a command. Use the dropdown to select common commands."
        )
        messagebox.showinfo("Help", help_text)

    def search_output(self):
        search_window = Toplevel(self.root)
        search_window.title("Search Output")

        search_label = ctk.CTkLabel(search_window, text="Search Term:")
        search_label.pack(padx=10, pady=5)

        search_entry = ctk.CTkEntry(search_window, width=300)
        search_entry.pack(padx=10, pady=5)
        
        def search_command():
            search_term = search_entry.get()
            self.terminal_output.tag_remove('search', '1.0', ctk.END)
            if search_term:
                start_idx = '1.0'
                while True:
                    start_idx = self.terminal_output.search(search_term, start_idx, nocase=True, stopindex=ctk.END)
                    if not start_idx:
                        break
                    end_idx = f"{start_idx}+{len(search_term)}c"
                    self.terminal_output.tag_add('search', start_idx, end_idx)
                    start_idx = end_idx
                self.terminal_output.tag_config('search', background='yellow', foreground='black')
        
        search_button = ctk.CTkButton(search_window, text="Search", command=search_command)
        search_button.pack(padx=10, pady=10)

    def load_session(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.clear_terminal()
                    self.terminal_output.configure(state='normal')
                    self.terminal_output.insert('1.0', file.read())
                    self.terminal_output.configure(state='disabled')
                messagebox.showinfo("Load Session", "Session loaded successfully.")
                self.set_status("Session loaded")
            except Exception as e:
                messagebox.showerror("Load Session", f"Error loading session: {e}")
                self.set_status("Error loading session")

    def update_history_dropdown(self):
        self.dropdown.configure(values=self.command_history)

    def set_status(self, text):
        self.status_bar.configure(text=text)
    
    def suggest_commands(self, event):
        typed = self.command_entry.get()
        if typed:
            suggestions = [cmd for cmd in self.common_commands if cmd.startswith(typed)]
            if suggestions:
                self.dropdown.configure(values=suggestions)
            else:
                self.dropdown.configure(values=self.common_commands)
        else:
            self.dropdown.configure(values=self.common_commands)

if __name__ == "__main__":
    root = ctk.CTk()
    app = TerminalGUI(root)
    root.mainloop()

