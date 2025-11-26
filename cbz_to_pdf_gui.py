
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import os
from pathlib import Path

from cbz_to_pdf import convert_single_cbz_to_pdf, combine_cbz_to_pdf

class CbzToPdfConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CBZ to PDF Converter")
        self.root.geometry("500x300")

        # --- Input Directory ---
        self.input_dir_label = tk.Label(root, text="Input Directory:")
        self.input_dir_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.input_dir_var = tk.StringVar()
        self.input_dir_entry = tk.Entry(root, textvariable=self.input_dir_var, width=50)
        self.input_dir_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.input_browse_button = tk.Button(root, text="Browse...", command=self.browse_input_dir)
        self.input_browse_button.grid(row=0, column=2, padx=10, pady=10)

        # --- Output Directory ---
        self.output_dir_label = tk.Label(root, text="Output Directory:")
        self.output_dir_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = tk.Entry(root, textvariable=self.output_dir_var, width=50)
        self.output_dir_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.output_browse_button = tk.Button(root, text="Browse...", command=self.browse_output_dir)
        self.output_browse_button.grid(row=1, column=2, padx=10, pady=5)

        # --- Combine Checkbox ---
        self.combine_var = tk.BooleanVar()
        self.combine_check = tk.Checkbutton(root, text="Combine into a single PDF", variable=self.combine_var, command=self.toggle_combine)
        self.combine_check.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # --- Output Filename (for combined) ---
        self.output_file_label = tk.Label(root, text="Output Filename:")
        self.output_file_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.output_file_var = tk.StringVar()
        self.output_file_entry = tk.Entry(root, textvariable=self.output_file_var, width=50, state="disabled")
        self.output_file_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # --- Convert Button ---
        self.convert_button = tk.Button(root, text="Convert", command=self.start_conversion_thread)
        self.convert_button.grid(row=4, column=1, padx=10, pady=20)

        # --- Progress Bar ---
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        # --- Status Label ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = tk.Label(root, textvariable=self.status_var)
        self.status_label.grid(row=6, column=0, columnspan=3, padx=10, pady=5, sticky="w")

        self.root.grid_columnconfigure(1, weight=1)

    def browse_input_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir_var.set(directory)

    def browse_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)
            
    def toggle_combine(self):
        if self.combine_var.get():
            self.output_file_entry.config(state="normal")
            self.output_dir_entry.config(state="disabled")
            self.output_dir_label.config(text="Output Directory:")
        else:
            self.output_file_entry.config(state="disabled")
            self.output_dir_entry.config(state="normal")
            self.output_dir_label.config(text="Output Directory:")


    def start_conversion_thread(self):
        self.convert_button.config(state="disabled")
        self.progress["value"] = 0
        self.status_var.set("Starting conversion...")
        
        conversion_thread = threading.Thread(target=self.run_conversion)
        conversion_thread.start()

    def run_conversion(self):
        input_path = self.input_dir_var.get()
        output_path = self.output_dir_var.get()
        combine = self.combine_var.get()
        output_file = self.output_file_var.get()

        if not input_path:
            self.root.after(0, self.update_status, "Error: Input directory not selected.", True)
            return
        
        if not output_path:
            self.root.after(0, self.update_status, "Error: Output directory not selected.", True)
            return
            
        if combine:
            if not output_file:
                self.root.after(0, self.update_status, "Error: Output filename not specified.", True)
                return
            
            # Enforce .pdf extension
            if not output_file.lower().endswith(".pdf"):
                output_file += ".pdf"
                self.output_file_var.set(output_file) # Update the GUI field
                 
            cbz_files = [f for f in os.listdir(input_path) if f.lower().endswith('.cbz')]
            full_cbz_paths = [str(Path(input_path) / f) for f in cbz_files]
            
            output_file_path = Path(output_path) / output_file
            
            self.progress["maximum"] = len(full_cbz_paths)
            
            for processed_count in combine_cbz_to_pdf(full_cbz_paths, str(output_file_path)):
                self.root.after(0, self.progress.config, {"value": processed_count})
                self.root.after(0, self.update_status, f"Combining file {processed_count} of {len(full_cbz_paths)}...")

            self.root.after(0, self.update_status, "Combined PDF created successfully!", True)

        else:
            cbz_files = [f for f in os.listdir(input_path) if f.lower().endswith('.cbz')]
            total_files = len(cbz_files)
            self.progress["maximum"] = total_files
            
            for i, filename in enumerate(cbz_files):
                cbz_file_path = Path(input_path) / filename
                self.root.after(0, self.update_status, f"Converting {filename}...")
                convert_single_cbz_to_pdf(cbz_file_path, output_path)
                self.root.after(0, self.progress.config, {"value": i + 1})

            self.root.after(0, self.update_status, "Conversion complete!", True)

    def update_status(self, message, reenable_button=False):
        self.status_var.set(message)
        if reenable_button:
            self.convert_button.config(state="normal")
        if "Error" in message:
             messagebox.showerror("Error", message)
             self.convert_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = CbzToPdfConverterApp(root)
    root.mainloop()
