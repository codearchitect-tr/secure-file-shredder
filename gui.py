"""
Modern GUI for Secure File Shredder
Built with CustomTkinter for modern appearance
"""

import customtkinter as ctk
from tkinter import filedialog
import threading
from pathlib import Path
from datetime import datetime
import os

from core.shredder_engine import ShredderEngine, FreeSpaceShredder


class ModernShredderGUI:
    def __init__(self):
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("🔥 Secure File Shredder - Military Grade")
        self.root.geometry("900x700")
        
        # Initialize engine
        self.engine = ShredderEngine(progress_callback=self.update_progress)
        self.free_space_engine = FreeSpaceShredder(progress_callback=self.update_progress)
        
        # File list
        self.files_to_shred = []
        self.is_shredding = False
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the user interface"""
        
        # ==================== HEADER ====================
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🔥 SECURE FILE SHREDDER",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Military-Grade Data Destruction | Unrecoverable Deletion",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        subtitle_label.pack()
        
        # ==================== METHOD SELECTION ====================
        method_frame = ctk.CTkFrame(self.root)
        method_frame.pack(fill="x", padx=20, pady=10)
        
        method_label = ctk.CTkLabel(
            method_frame,
            text="Shredding Method:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        method_label.pack(side="left", padx=10)
        
        self.method_var = ctk.StringVar(value="dod")
        
        methods = [
            ("DoD 5220.22-M (3 passes) ⭐", "dod"),
            ("Gutmann (35 passes) 🔥", "gutmann"),
            ("Random 7-Pass", "random_7"),
            ("Simple Random (1 pass)", "simple")
        ]
        
        for text, value in methods:
            radio = ctk.CTkRadioButton(
                method_frame,
                text=text,
                variable=self.method_var,
                value=value,
                font=ctk.CTkFont(size=12)
            )
            radio.pack(side="left", padx=10)
        
        # ==================== FILE SELECTION ====================
        file_frame = ctk.CTkFrame(self.root)
        file_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        add_files_btn = ctk.CTkButton(
            button_frame,
            text="➕ Add Files",
            command=self.add_files,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        add_files_btn.pack(side="left", padx=5)
        
        add_folder_btn = ctk.CTkButton(
            button_frame,
            text="📁 Add Folder",
            command=self.add_folder,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        add_folder_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear List",
            command=self.clear_list,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="gray40",
            hover_color="gray30"
        )
        clear_btn.pack(side="left", padx=5)
        
        # File count
        self.file_count_label = ctk.CTkLabel(
            button_frame,
            text="Files: 0 | Total: 0 bytes",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.file_count_label.pack(side="right", padx=10)
        
        # File list (scrollable)
        self.file_listbox = ctk.CTkTextbox(
            file_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="none"
        )
        self.file_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ==================== PROGRESS ====================
        progress_frame = ctk.CTkFrame(self.root)
        progress_frame.pack(fill="x", padx=20, pady=10)
        
        self.status_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to shred",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.status_label.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=400,
            height=20
        )
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="0%",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.progress_label.pack()
        
        # ==================== SHRED BUTTON ====================
        self.shred_button = ctk.CTkButton(
            self.root,
            text="🔥 SHRED FILES (PERMANENT DELETION)",
            command=self.start_shredding,
            font=ctk.CTkFont(size=18, weight="bold"),
            height=60,
            fg_color="#DC2626",
            hover_color="#991B1B"
        )
        self.shred_button.pack(fill="x", padx=20, pady=10)
        
        # ==================== OPTIONS ====================
        options_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        options_frame.pack(fill="x", padx=20, pady=5)
        
        self.verify_var = ctk.BooleanVar(value=True)
        verify_check = ctk.CTkCheckBox(
            options_frame,
            text="Verify deletion",
            variable=self.verify_var,
            font=ctk.CTkFont(size=12)
        )
        verify_check.pack(side="left", padx=10)
        
        # ==================== FOOTER ====================
        footer_label = ctk.CTkLabel(
            self.root,
            text="⚠️ WARNING: Shredded files CANNOT be recovered. This is PERMANENT.",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#DC2626"
        )
        footer_label.pack(pady=10)
        
    def add_files(self):
        """Add files to shred list"""
        files = filedialog.askopenfilenames(
            title="Select files to shred",
            filetypes=[("All files", "*.*")]
        )
        
        for file in files:
            if file not in self.files_to_shred:
                self.files_to_shred.append(file)
        
        self.update_file_list()
    
    def add_folder(self):
        """Add all files in folder to shred list"""
        folder = filedialog.askdirectory(title="Select folder to shred")
        
        if folder:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in self.files_to_shred:
                        self.files_to_shred.append(file_path)
        
        self.update_file_list()
    
    def clear_list(self):
        """Clear file list"""
        self.files_to_shred = []
        self.update_file_list()
    
    def update_file_list(self):
        """Update the file listbox"""
        self.file_listbox.delete("1.0", "end")
        
        total_size = 0
        
        for i, file_path in enumerate(self.files_to_shred, 1):
            try:
                size = os.path.getsize(file_path)
                total_size += size
                size_str = self.format_size(size)
                
                self.file_listbox.insert("end", f"{i}. {file_path} ({size_str})\n")
            except:
                self.file_listbox.insert("end", f"{i}. {file_path} (Error reading size)\n")
        
        # Update count label
        count = len(self.files_to_shred)
        self.file_count_label.configure(
            text=f"Files: {count} | Total: {self.format_size(total_size)}"
        )
    
    def format_size(self, bytes_size):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"
    
    def update_progress(self, progress):
        """Update progress bar"""
        self.progress_bar.set(progress / 100)
        self.progress_label.configure(text=f"{progress}%")
        self.root.update_idletasks()
    
    def start_shredding(self):
        """Start shredding process"""
        if self.is_shredding:
            return
        
        if not self.files_to_shred:
            self.show_warning("No files selected!")
            return
        
        # Confirmation dialog
        confirm = ctk.CTkInputDialog(
            text="Type 'DELETE' to confirm permanent file destruction:",
            title="⚠️ CONFIRM DELETION"
        )
        
        if confirm.get_input() != "DELETE":
            return
        
        self.is_shredding = True
        self.shred_button.configure(state="disabled", text="🔥 SHREDDING IN PROGRESS...")
        
        # Run in thread
        thread = threading.Thread(target=self.shred_files_thread)
        thread.daemon = True
        thread.start()
    
    def shred_files_thread(self):
        """Shred files in background thread"""
        method = self.method_var.get()
        verify = self.verify_var.get()
        
        total_files = len(self.files_to_shred)
        shredded = 0
        failed = 0
        
        results = []
        
        for i, file_path in enumerate(self.files_to_shred, 1):
            self.status_label.configure(
                text=f"Shredding {i}/{total_files}: {Path(file_path).name}"
            )
            
            result = self.engine.shred_file(file_path, method=method, verify=verify)
            results.append(result)
            
            if result['success']:
                shredded += 1
            else:
                failed += 1
        
        # Complete
        self.is_shredding = False
        self.files_to_shred = []
        
        self.root.after(0, lambda: self.shredding_complete(shredded, failed, results))
    
    def shredding_complete(self, shredded, failed, results):
        """Handle shredding completion"""
        self.update_file_list()
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        self.shred_button.configure(
            state="normal",
            text="🔥 SHRED FILES (PERMANENT DELETION)"
        )
        
        # Show results
        message = f"✅ Shredding Complete!\n\n"
        message += f"Successfully shredded: {shredded}\n"
        message += f"Failed: {failed}\n\n"
        
        if shredded > 0:
            message += "Files have been PERMANENTLY deleted and cannot be recovered."
        
        self.show_info("Shredding Complete", message)
        
        self.status_label.configure(text="Ready to shred")
    
    def show_warning(self, message):
        """Show warning dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Warning")
        dialog.geometry("400x150")
        
        label = ctk.CTkLabel(dialog, text=message, font=ctk.CTkFont(size=14))
        label.pack(pady=20)
        
        button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy)
        button.pack(pady=10)
    
    def show_info(self, title, message):
        """Show info dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x300")
        
        label = ctk.CTkLabel(
            dialog,
            text=message,
            font=ctk.CTkFont(size=13),
            justify="left"
        )
        label.pack(pady=20, padx=20)
        
        button = ctk.CTkButton(
            dialog,
            text="OK",
            command=dialog.destroy,
            height=40
        )
        button.pack(pady=10)
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
