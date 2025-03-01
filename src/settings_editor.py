import os
import argparse
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from config import CONFIG_FILE

def read_ini_preserve_keys(filename):
    """
    Reads an INI file and returns a dictionary mapping section names to an ordered
    dictionary of key/value pairs. This manual parser preserves key capitalization.
    Note: Comments and blank lines are ignored.
    """
    data = {}
    current_section = None
    with open(filename, 'r') as f:
        for line in f:
            stripped = line.strip()
            
            # Skip comments and blank lines
            if not stripped or stripped.startswith(';'):
                continue

            # create section if line is a [section header]
            if stripped.startswith('[') and stripped.endswith(']'):
                current_section = stripped[1:-1]
                data[current_section] = {}

            # add key-value pairs to the current section
            elif '=' in line and current_section is not None:
                key, value = line.split('=', 1)
                key = key.strip()  # Preserve original case
                value = value.strip()
                data[current_section][key] = value
    return data

def write_ini_preserve_keys(filename, data):
    """
    Writes the INI data (a dict mapping section names to dicts of key/value pairs)
    back to a file, preserving comments and blank lines.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    with open(filename, 'w') as f:
        current_section = None
        for line in lines:
            stripped = line.strip()

            # Preserve comments and blank lines
            if not stripped or stripped.startswith(';'):
                f.write(line)
                continue

            # Handle section headers
            if stripped.startswith('[') and stripped.endswith(']'):
                current_section = stripped[1:-1]
                f.write(line)
                continue

            # Handle key=value pairs
            if '=' in line and current_section:
                key, value = line.split('=', 1)
                key = key.strip()  # Preserve original case
                value = value.strip()

                # Update the value if the key exists in the data
                if key in data[current_section]:
                    f.write(f'{key} = {data[current_section][key]}\n')
                else:
                    f.write(f'{key} = {value}\n')
            else:
                # For other lines, just write them as is
                f.write(line)

def parse_args():
    parser = argparse.ArgumentParser(description="ASAP-Cabinet-FE Settings")
    parser.add_argument(
        "INI_FILE_PATH", nargs="?", default=None,
        help="Path to the INI file to be edited. If not provided, the default path is used."
    )
    return parser.parse_args()

class ToolTip:
    """
    A tooltip that appears when the widget is clicked.
    Uses a Text widget to handle long explanations.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Button-1>", self.showtip)  # Bind to click event (left-click)

    def showtip(self, event=None):
        # Create a Toplevel window for the explanation pop-up
        if self.text:
            tipwindow = tk.Toplevel(self.widget)
            tipwindow.wm_overrideredirect(True)  # Removes the window borders

            # Set the window geometry and position it near the widget
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
            tipwindow.wm_geometry(f"+{x}+{y}")

            # Create a Text widget to display the explanation, set word wrapping to true
            text_widget = tk.Text(tipwindow, wrap=tk.WORD, height=10, width=50, font=("tahoma", "8", "normal"))
            text_widget.insert(tk.END, self.text)
            text_widget.config(state=tk.DISABLED)  # Make the Text widget read-only
            text_widget.pack(padx=10, pady=10)

            # Add a close button for the pop-up window
            close_button = ttk.Button(tipwindow, text="Close", command=tipwindow.destroy)
            close_button.pack(pady=5)  # Increase padding around the button

            # Automatically adjust window size to fit the content
            tipwindow.update_idletasks()
            width = text_widget.winfo_width() + 40  # Add padding to width
            height = text_widget.winfo_height() + 60  # Add extra space for the button
            tipwindow.geometry(f"{width}x{height}+{x}+{y}")  # Adjust the window size

class IniEditor:
    '''
    The `IniEditor` class reads the INI file, preserves key capitalization, and displays sections and key-value pairs.
    Users can select sections, edit values, and save changes back to the INI file.
    The class also includes explanations for specific keys, displayed as tooltips when users click on a "?" button next to each key.
    '''
    def __init__(self, master, INI_FILE_PATH):
        self.master = master
        self.INI_FILE_PATH = INI_FILE_PATH
        # Read the INI file using our custom parser to preserve key capitalization
        self.ini_data = read_ini_preserve_keys(self.INI_FILE_PATH)

        # Define explanations for specific keys.
        # Keys here must exactly match the key names in your INI file.
        self.explanations = {
            "vpx_root_folder": "The root directory where your Visual Pinball X tables (.vpx files) are located.",
            "executable_cmd": "The path to the Visual Pinball X executable.",
            "executable_sub_cmd": "The command-line argument used to launch a table in Visual Pinball X (e.g., '-play').",
            "table_image_path": "The relative path to custom images used for table previews.",
            "table_wheel_path": "The relative path to custom images used for table wheel art.",
            "table_backglass_path": "The relative path to custom images used for table backglass displays.",
            "table_dmd_path": "The relative path to custom images used for table DMD displays.",
            "main_monitor_index": "The index of the monitor used for the main table display (0, 1, 2, etc.).",
            "main_window_width": "The width of the main table display window in pixels.",
            "main_window_height": "The height of the main table display window in pixels.",
            "wheel_image_size": "The size (width and height) of the table wheel image in pixels.",
            "wheel_image_margin": "The margin (in pixels) between the table wheel image and the edge of the window.",
            "font_name": "The name of the font used for text displays.",
            "font_size": "The size of the font used for text displays in pixels.",
            "bg_color": "The background color of the application icons (in hexadecimal format).",
            "text_color": "The color of the text displayed in the application windows.",
            "secondary_monitor_index": "The index of the monitor used for the secondary backglass/DMD display (0, 1, 2, etc.).",
            "backglass_window_width": "The width of the backglass display window in pixels.",
            "backglass_window_height": "The height of the backglass display window in pixels.",
            "backglass_image_width": "The width of the backglass image in pixels.",
            "backglass_image_height": "The height of the backglass image in pixels.",
            "dmd_width": "The width of the DMD display in pixels.",
            "dmd_height": "The height of the DMD display in pixels.",
            "fade_duration": "The duration of fade transitions in milliseconds.",
            "fade_opacity": "The opacity level during fade transitions (0.0 to 1.0)."
        }

        self.entry_widgets = {}
        self.setup_ui()

    def setup_ui(self):
        '''
        Sets up the user interface with section selection, key-value entry fields, and a save button.
        '''
        # Section selection frame
        section_frame = ttk.Frame(self.master)
        section_frame.pack(fill=tk.X, padx=10, pady=5)
        section_label = ttk.Label(section_frame, text="Select Section:")
        section_label.pack(side=tk.LEFT)
        self.section_var = tk.StringVar()
        self.section_combo = ttk.Combobox(section_frame, textvariable=self.section_var, state="readonly")
        self.section_combo['values'] = list(self.ini_data.keys())
        if self.ini_data:
            first_section = list(self.ini_data.keys())[0]
            self.section_combo.current(0)
        self.section_combo.pack(side=tk.LEFT, padx=5)
        self.section_combo.bind("<<ComboboxSelected>>", self.on_section_change)

        # Frame for key/value entries with scrolling
        self.entries_frame = ttk.Frame(self.master)
        self.entries_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.canvas = tk.Canvas(self.entries_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.entries_frame, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.inner_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create a frame to hold buttons side by side
        button_frame = ttk.Frame(self.master)
        button_frame.pack(pady=10)

        # Save button
        save_button = ttk.Button(button_frame, text="Save", command=self.save_changes)
        save_button.pack(side=tk.LEFT, padx=5)

        # Change INI button
        change_ini_button = ttk.Button(button_frame, text="Change INI", command=self.change_ini)
        change_ini_button.pack(side=tk.LEFT, padx=5)

        # Exit button
        exit_button = ttk.Button(button_frame, text="Exit", command=self.master.quit)
        exit_button.pack(side=tk.LEFT, padx=5)

        if self.ini_data:
            first_section = list(self.ini_data.keys())[0]
            self.load_section(first_section)

    def update_title(self):
        '''
        Updates the window title based on the currently selected INI file.
        '''
        self.master.title(f"INI Editor - {self.INI_FILE_PATH}")

    def change_ini(self):
        '''
        Opens a file dialog to choose a new INI file and update the UI accordingly.
        '''
        new_ini_file = filedialog.askopenfilename(
            title="Select INI File", filetypes=[("INI Files", "*.ini"), ("All Files", "*.*")]
        )
        if new_ini_file:
            self.INI_FILE_PATH = new_ini_file
            self.ini_data = read_ini_preserve_keys(self.INI_FILE_PATH)
            self.load_section(list(self.ini_data.keys())[0])  # Load the first section
            self.update_title()  # Update the window title after changing the INI file

    def on_section_change(self, event):
        '''
        Event handler for section selection change.
        '''
        section = self.section_var.get()
        self.load_section(section)

    def load_section(self, section):
        '''
        Loads the key-value pairs for the selected section and displays them in the UI.
        '''
        # Clear existing widgets
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.entry_widgets = {}

        # Load the section data
        if section not in self.ini_data:
            return
        section_data = self.ini_data[section]

        # Repack the canvas window if necessary
        self.canvas.yview_moveto(0)  # Scroll to top after section change

        # Create widgets for each key-value pair in the section
        for i, (key, value) in enumerate(section_data.items()):
            # Label for key (fixed width to avoid stretching)
            label = ttk.Label(self.inner_frame, text=key, anchor='w')  # Label for key
            label.grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)

            # Add a clickable "?" button if an explanation is provided
            if key in self.explanations:
                tooltip_label = ttk.Label(self.inner_frame, text="?", foreground="blue", cursor="question_arrow")
                tooltip_label.grid(row=i, column=1, padx=5, pady=2)
                ToolTip(tooltip_label, self.explanations[key])  # Bind tooltip to the "?" label

            # Entry field for value (increase width here for longer fields)
            entry = ttk.Entry(self.inner_frame, width=35)  # Increased width to make text field longer
            entry.grid(row=i, column=2, padx=5, pady=2, sticky='ew')  # 'ew' ensures it expands horizontally
            entry.insert(0, value)
            self.entry_widgets[key] = entry

        # Update column weights to ensure proper layout
        self.inner_frame.grid_columnconfigure(0, weight=1, minsize=150)  # Make the key column flexible
        self.inner_frame.grid_columnconfigure(1, weight=0)  # "?" column doesn't need to stretch
        self.inner_frame.grid_columnconfigure(2, weight=2, minsize=300)  # Entry column flexible but fixed min size

        # Ensure the canvas scrolls correctly after updating the section
        self.inner_frame.update_idletasks()  # Update the layout
        self.canvas.config(scrollregion=self.canvas.bbox("all"))  # Set the scroll region

    def save_changes(self):
        '''
        Saves the changes made in the UI back to the INI file.
        '''
        section = self.section_var.get()
        if section not in self.ini_data:
            messagebox.showerror("Error", f"Section '{section}' not found.")
            return
        
        # Update the INI data with the new values
        for key, entry in self.entry_widgets.items():
            self.ini_data[section][key] = entry.get()
        write_ini_preserve_keys(self.INI_FILE_PATH, self.ini_data)
        messagebox.showinfo("Success", f"Changes saved to {self.INI_FILE_PATH}")

def main():
    INI_FILE_PATH = os.path.expanduser(CONFIG_FILE)
    
    if not os.path.exists(INI_FILE_PATH):
        # Prompt user to either select a new INI or exit
        response = messagebox.askyesno("Error", f"INI file not found: {INI_FILE_PATH}\nDo you want to select a new INI file?")
        if response:  # User clicked "Yes"
            # Open the file selection dialog
            new_ini_file = filedialog.askopenfilename(
                title="Select INI File", filetypes=[("INI Files", "*.ini"), ("All Files", "*.*")]
            )
            if new_ini_file:
                INI_FILE_PATH = new_ini_file  # Update the INI_FILE_PATH with the new selected one
            else:
                return  # If no file selected, exit
        else:  # User clicked "No"
            return  # Exit the program

    # Proceed with the application if INI file is valid or updated
    root = tk.Tk()
    root.title(f"ASAP-Cabinet-FE Settings - {INI_FILE_PATH}")  # Set window title with the ini file path
    root.geometry("700x500")

    app = IniEditor(root, INI_FILE_PATH)
    root.mainloop()

if __name__ == "__main__":
    main()
