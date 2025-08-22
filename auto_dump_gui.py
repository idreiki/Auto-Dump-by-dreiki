import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import subprocess
import os
import zipfile
import tempfile
import shutil
from pathlib import Path
import sys

class AutoDumpGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Dump - by dreiki (pyinstaller only)")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        self.selected_file = None
        self.temp_dir = None
        self.selected_pyc = None
        self.extracted_dir = None
        self.pyinstxtractor_path = Path(__file__).parent / "pyinstxtractor-ng.exe"
        self.pylingual_path = Path(__file__).parent / "pylingual-main"
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(main_frame, text="Auto Dump Tool", 
                              font=('Arial', 24, 'bold'), 
                              fg='#ffffff', bg='#2b2b2b')
        title_label.pack(pady=(0, 20))
        
        subtitle_label = tk.Label(main_frame, text="by dreiki (pyinstaller only)", 
                                 font=('Arial', 12), 
                                 fg='#cccccc', bg='#2b2b2b')
        subtitle_label.pack(pady=(0, 30))
        
        self.file_frame = tk.Frame(main_frame, bg='#3c3c3c', relief=tk.RAISED, bd=2)
        self.file_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.drop_label = tk.Label(self.file_frame, text="Drag & Drop EXE file here or click to select", 
                             font=('Arial', 14), 
                             fg='#ffffff', bg='#3c3c3c',
                             height=4)
        self.drop_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.drop_label.bind("<Button-1>", self.select_file)
        
        self.file_frame.drop_target_register(DND_FILES)
        self.file_frame.dnd_bind('<<Drop>>', self.on_drop)
        
        self.file_label = tk.Label(main_frame, text="No file selected", 
                                  font=('Arial', 10), 
                                  fg='#cccccc', bg='#2b2b2b')
        self.file_label.pack(pady=(0, 20))
        
        self.go_button = tk.Button(main_frame, text="GO DUMP", 
                                  font=('Arial', 16, 'bold'),
                                  bg='#4CAF50', fg='white',
                                  height=2, width=15,
                                  command=self.start_dump,
                                  state=tk.DISABLED)
        self.go_button.pack(pady=(0, 20))
        
        log_frame = tk.Frame(main_frame, bg='#2b2b2b')
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        log_label = tk.Label(log_frame, text="Process Log:", 
                            font=('Arial', 12, 'bold'), 
                            fg='#ffffff', bg='#2b2b2b')
        log_label.pack(anchor=tk.W)
        
        self.log_text = tk.Text(log_frame, bg='#1e1e1e', fg='#00ff00', 
                               font=('Consolas', 10),
                               wrap=tk.WORD, state=tk.DISABLED)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def select_file(self, event=None):
        file_path = filedialog.askopenfilename(
            title="Select EXE file",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=f"Selected: {os.path.basename(file_path)}")
            self.go_button.config(state=tk.NORMAL)
            
    def on_drop(self, event):
        files = event.data.split()
        if files and files[0].endswith('.exe'):
            self.selected_file = files[0]
            self.file_label.config(text=f"Selected: {os.path.basename(files[0])}")
            self.go_button.config(state=tk.NORMAL)
            
    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
        
    def start_dump(self):
        if not self.selected_file:
            messagebox.showerror("Error", "Please select an EXE file first")
            return
            
        self.go_button.config(state=tk.DISABLED)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.dump_process)
        thread.daemon = True
        thread.start()
        
    def dump_process(self):
        try:
            self.log_message("=== Starting Auto Dump Process ===")
            self.log_message(f"Target file: {self.selected_file}")
            
            self.temp_dir = tempfile.mkdtemp(prefix="autodump_")
            self.log_message(f"Working directory: {self.temp_dir}")
            
            if not self.run_pyinstxtractor():
                return
                
            if not self.extract_archive():
                return
                
            if not self.select_main_script():
                return
                
            if not self.run_pylingual():
                return
                
            self.log_message("=== Process completed successfully! ===")
            messagebox.showinfo("Success", "Decompilation completed! Check the output file next to the executable.")
            
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
            messagebox.showerror("Error", f"Process failed: {str(e)}")
        finally:
            self.go_button.config(state=tk.NORMAL)
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                
    def run_pyinstxtractor(self):
        self.log_message("\n--- Running PyInstaller Extractor ---")
        
        if not self.pyinstxtractor_path.exists():
            self.log_message("ERROR: pyinstxtractor-ng.exe not found!")
            return False
            
        cmd = [str(self.pyinstxtractor_path), self.selected_file]
        self.log_message(f"Command: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     text=True, cwd=self.temp_dir)
            
            for line in process.stdout:
                self.log_message(line.strip())
                
            process.wait()
            
            if process.returncode == 0:
                self.log_message("PyInstaller extraction completed successfully!")
                return True
            else:
                self.log_message(f"PyInstaller extraction failed with code {process.returncode}")
                return False
                
        except Exception as e:
            self.log_message(f"ERROR running pyinstxtractor: {str(e)}")
            return False
            
    def extract_archive(self):
        self.log_message("\n--- Extracting Archive ---")
        
        extracted_dir = None
        for item in os.listdir(self.temp_dir):
            item_path = os.path.join(self.temp_dir, item)
            if os.path.isdir(item_path) and item.endswith('_extracted'):
                extracted_dir = item_path
                break
                
        if not extracted_dir:
            self.log_message("ERROR: No extracted directory found!")
            return False
            
        self.log_message(f"Found extracted directory: {extracted_dir}")
        self.extracted_dir = extracted_dir
        return True
        
    def select_main_script(self):
        self.log_message("\n--- Selecting Main Script ---")
        
        pyc_files = []
        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                if file.endswith('.pyc'):
                    pyc_files.append(os.path.join(root, file))
                    
        if not pyc_files:
            self.log_message("ERROR: No .pyc files found in extracted directory!")
            return False
            
        self.log_message(f"Found {len(pyc_files)} .pyc files:")
        for i, pyc_file in enumerate(pyc_files):
            self.log_message(f"  {i+1}. {os.path.basename(pyc_file)}")
            
        selection_window = tk.Toplevel(self.root)
        selection_window.title("Select Main Script")
        selection_window.geometry("600x400")
        selection_window.configure(bg='#2b2b2b')
        selection_window.grab_set()
        selection_window.transient(self.root)
        
        tk.Label(selection_window, text="Select the main .pyc file to decompile:", 
                font=('Arial', 12), fg='#ffffff', bg='#2b2b2b').pack(pady=10)
        
        listbox = tk.Listbox(selection_window, bg='#1e1e1e', fg='#ffffff', 
                           font=('Consolas', 10), selectmode=tk.SINGLE)
        
        for pyc_file in pyc_files:
            listbox.insert(tk.END, os.path.basename(pyc_file))
            
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        selected_index = [None]
        
        def on_select():
            selection = listbox.curselection()
            if selection:
                selected_index[0] = selection[0]
            selection_window.destroy()
            
        def on_double_click(event):
            on_select()
            
        listbox.bind('<Double-Button-1>', on_double_click)
        
        button_frame = tk.Frame(selection_window, bg='#2b2b2b')
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Select", command=on_select,
                 bg='#4CAF50', fg='white', font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Cancel", command=selection_window.destroy,
                 bg='#f44336', fg='white', font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
        
        selection_window.wait_window()
        
        if selected_index[0] is not None:
            self.selected_pyc = pyc_files[selected_index[0]]
            self.log_message(f"Selected: {os.path.basename(self.selected_pyc)}")
            return True
        else:
            self.log_message("ERROR: No .pyc file selected!")
            return False
            
    def run_pylingual(self):
        self.log_message("\n--- Running Pylingual Decompiler ---")
        
        if not self.pylingual_path.exists():
            self.log_message("ERROR: pylingual directory not found!")
            return False
            
        output_file = Path(self.selected_file).parent / f"decompiled_{Path(self.selected_pyc).stem}.py"
        
        python_exe = sys.executable
        main_script = self.pylingual_path / "pylingual" / "main.py"
        
        if not main_script.exists():
            self.log_message(f"ERROR: main.py not found at {main_script}")
            return False
        
        env = os.environ.copy()
        env['PYTHONPATH'] = str(self.pylingual_path) + os.pathsep + env.get('PYTHONPATH', '')
        
        cmd = [python_exe, "-c", f"""
import sys
sys.path.insert(0, r'{self.pylingual_path}')
from pylingual.main import main
sys.argv = ['pylingual', r'{self.selected_pyc}', '-o', r'{output_file.parent}']
main()
"""]
        self.log_message(f"Command: {' '.join(cmd)}")
        self.log_message(f"Working directory: {self.pylingual_path}")
        self.log_message(f"PYTHONPATH: {env['PYTHONPATH']}")
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     text=True, encoding='utf-8', errors='replace',
                                     cwd=str(self.pylingual_path), env=env)
            
            for line in process.stdout:
                self.log_message(line.strip())
                
            process.wait()
            
            if process.returncode == 0:
                self.log_message(f"Decompilation completed! Output saved to: {output_file}")
                return True
            else:
                self.log_message(f"Pylingual decompilation failed with code {process.returncode}")
                return False
                
        except Exception as e:
            self.log_message(f"ERROR running pylingual: {str(e)}")
            return False

def main():
    root = TkinterDnD.Tk()
    app = AutoDumpGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
