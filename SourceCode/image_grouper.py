import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
import shutil
from pathlib import Path
import random
import time
import json
import threading
from queue import Queue, Empty

class ImageGrouper:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Image Grouper")
        self.window.geometry("800x600")  # Larger window
        self.window.configure(bg='#f0f0f0')  # Light gray background
        
        self.moved_files = []  # For undo functionality
        self.config_file = "session_config.json"
        self.processing = False  # Flag to prevent multiple operations
        
        # Path variables
        self.pool_path = tk.StringVar()
        self.horizontal_path = tk.StringVar()
        self.vertical_path = tk.StringVar()
        
        # Progress variables
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        # Message queue for thread communication
        self.msg_queue = Queue()
        
        # Load last session
        self._load_session()
        self._create_ui()
        
        # Save session when window closes
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Start message checking
        self._check_messages()
    
    def _load_session(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.pool_path.set(config.get('pool', ''))
                    self.horizontal_path.set(config.get('horizontal', ''))
                    self.vertical_path.set(config.get('vertical', ''))
        except Exception as e:
            print(f"Error loading session: {e}")
    
    def _save_session(self):
        try:
            config = {
                'pool': self.pool_path.get(),
                'horizontal': self.horizontal_path.get(),
                'vertical': self.vertical_path.get()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def _on_closing(self):
        self._save_session()
        self.window.destroy()
    
    def _create_ui(self):
        # Main container with padding
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Image Grouper",
            font=('Helvetica', 24, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        title_label.pack(pady=(0, 20))
        
        # Folder selection frame
        folder_frame = tk.LabelFrame(
            main_frame,
            text="Folder Selection",
            font=('Helvetica', 12),
            bg='#f0f0f0',
            fg='#333333',
            padx=15,
            pady=15
        )
        folder_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Pool folder
        self._create_folder_row(folder_frame, "Pool Folder:", self.pool_path, 0)
        # Horizontal folder
        self._create_folder_row(folder_frame, "Horizontal Folder:", self.horizontal_path, 1)
        # Vertical folder
        self._create_folder_row(folder_frame, "Vertical Folder:", self.vertical_path, 2)
        
        # Progress frame
        progress_frame = tk.LabelFrame(
            main_frame,
            text="Progress",
            font=('Helvetica', 12),
            bg='#f0f0f0',
            fg='#333333',
            padx=15,
            pady=15
        )
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Progress bar with custom style
        style = ttk.Style()
        style.theme_use('default')  # Use default theme for consistent look
        style.configure(
            "Custom.Horizontal.TProgressbar",
            troughcolor='#e0e0e0',
            background='#4CAF50',
            bordercolor='#999999',
            lightcolor='#4CAF50',
            darkcolor='#4CAF50',
            thickness=25
        )
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            style="Custom.Horizontal.TProgressbar",
            length=300
        )
        self.progress_bar.pack(fill=tk.X, pady=(5, 10))
        
        # Status label with more visible styling
        status_label = tk.Label(
            progress_frame,
            textvariable=self.status_var,
            font=('Helvetica', 10, 'bold'),  # Made bold
            bg='#f0f0f0',
            fg='#333333'  # Darker color for better visibility
        )
        status_label.pack()
        
        # Action buttons frame
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        # Action buttons with improved styling
        self._create_button(button_frame, "Group Images", self._start_group_images, '#4CAF50')  # Green
        self._create_button(button_frame, "Undo Last Operation", self._start_undo, '#2196F3')  # Blue
        self._create_button(button_frame, "Generate Test Images", self._start_generate_test, '#FF9800')  # Orange
    
    def _create_folder_row(self, parent, label_text, path_var, row):
        frame = tk.Frame(parent, bg='#f0f0f0')
        frame.pack(fill=tk.X, pady=5)
        
        label = tk.Label(
            frame,
            text=label_text,
            font=('Helvetica', 10),
            bg='#f0f0f0',
            fg='#333333',
            width=15,
            anchor='w'
        )
        label.pack(side=tk.LEFT)
        
        entry = tk.Entry(
            frame,
            textvariable=path_var,
            font=('Helvetica', 10),
            width=50,
            bg='white',
            relief=tk.SOLID
        )
        entry.pack(side=tk.LEFT, padx=5)
        
        browse_btn = tk.Button(
            frame,
            text="Browse",
            command=lambda: self._browse_folder(path_var),
            font=('Helvetica', 10),
            bg='#e0e0e0',
            relief=tk.RAISED,
            padx=10
        )
        browse_btn.pack(side=tk.LEFT)
    
    def _create_button(self, parent, text, command, color):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Helvetica', 12, 'bold'),
            bg=color,
            fg='white',
            relief=tk.RAISED,
            padx=20,
            pady=10
        )
        btn.pack(side=tk.LEFT, padx=10)
        
        # Hover effects
        btn.bind('<Enter>', lambda e: btn.configure(bg=self._adjust_color(color, 1.1)))
        btn.bind('<Leave>', lambda e: btn.configure(bg=color))
    
    def _adjust_color(self, color, factor):
        """Adjust color brightness for hover effect"""
        # Convert hex to RGB
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Adjust brightness
        r = min(int(r * factor), 255)
        g = min(int(g * factor), 255)
        b = min(int(b * factor), 255)
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _update_progress(self, value, status):
        """Helper method to update progress and status"""
        self.progress_var.set(value)
        self.status_var.set(status)
        self.progress_bar.update()
        self.window.update_idletasks()
    
    def _check_messages(self):
        """Check for messages from worker threads"""
        try:
            # Process all available messages
            while True:
                try:
                    msg = self.msg_queue.get_nowait()
                    msg_type = msg.get('type')
                    
                    if msg_type == 'progress':
                        self._update_progress(msg['value'], msg['status'])
                    elif msg_type == 'error':
                        messagebox.showerror("Error", msg['message'])
                        self._update_progress(0, "Error occurred")
                    elif msg_type == 'warning':
                        messagebox.showwarning("Warning", msg['message'])
                    elif msg_type == 'info':
                        messagebox.showinfo("Info", msg['message'])
                    elif msg_type == 'done':
                        self.processing = False
                        self._update_progress(0, "Ready")
                except Empty:
                    break
        finally:
            # Schedule the next check
            self.window.after(10, self._check_messages)  # Check even more frequently (10ms)
    
    def _start_group_images(self):
        if self.processing:
            messagebox.showwarning("Warning", "Operation in progress. Please wait.")
            return
        self.processing = True
        threading.Thread(target=self.group_images, daemon=True).start()
    
    def _start_undo(self):
        if self.processing:
            messagebox.showwarning("Warning", "Operation in progress. Please wait.")
            return
        self.processing = True
        threading.Thread(target=self.undo_last_operation, daemon=True).start()
    
    def _start_generate_test(self):
        if self.processing:
            messagebox.showwarning("Warning", "Operation in progress. Please wait.")
            return
        self.processing = True
        threading.Thread(target=self.generate_test_images, daemon=True).start()
    
    def _browse_folder(self, path_var):
        folder = filedialog.askdirectory()
        if folder:
            path_var.set(folder)
    
    def _safe_file_operation(self, src, dst, operation='move'):
        max_retries = 3
        retry_delay = 0.5  # seconds
        
        for attempt in range(max_retries):
            try:
                if operation == 'move':
                    # Try to force close any open handles to the file
                    if os.path.exists(dst):
                        try:
                            os.remove(dst)
                        except:
                            pass
                    
                    # Copy first, then delete original
                    shutil.copy2(src, dst)
                    try:
                        os.remove(src)
                    except:
                        # If we can't delete the original, delete the copy and fail
                        os.remove(dst)
                        raise
                    return True
                else:  # remove
                    os.remove(src)
                    return True
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                print(f"Error in file operation: {str(e)}")
                return False
        return False
    
    def group_images(self):
        pool = self.pool_path.get()
        horizontal = self.horizontal_path.get()
        vertical = self.vertical_path.get()
        
        if not all([pool, horizontal, vertical]):
            self.msg_queue.put({'type': 'error', 'message': "Please select all folders"})
            self.msg_queue.put({'type': 'done'})
            return
        
        self.moved_files.clear()
        errors = []
        
        # Count total files for progress
        image_files = [f for f in os.listdir(pool) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        total_files = len(image_files)
        
        if total_files == 0:
            self.msg_queue.put({'type': 'warning', 'message': "No image files found in Pool folder"})
            self.msg_queue.put({'type': 'done'})
            return
        
        # Process files in batches for better performance
        batch_size = 10  # Process 10 files before updating UI
        
        for i, file in enumerate(image_files, 1):
            try:
                img_path = os.path.join(pool, file)
                img = None
                try:
                    img = Image.open(img_path)
                    width, height = img.size
                    target_dir = horizontal if width > height else vertical
                    target_path = os.path.join(target_dir, file)
                finally:
                    if img:
                        img.close()
                
                if self._safe_file_operation(img_path, target_path, 'move'):
                    self.moved_files.append((target_path, img_path))
                else:
                    errors.append(f"Could not move {file}")
                
                # Update progress in batches
                if i % batch_size == 0 or i == total_files:
                    progress = (i / total_files) * 100
                    self.msg_queue.put({
                        'type': 'progress',
                        'value': progress,
                        'status': f"Processing: {i}/{total_files} files"
                    })
                
            except Exception as e:
                errors.append(f"Error processing {file}: {str(e)}")
        
        if errors:
            self.msg_queue.put({'type': 'warning', 'message': "\n".join(errors)})
        else:
            self.msg_queue.put({'type': 'info', 'message': "Images grouped successfully!"})
        
        self.msg_queue.put({'type': 'done'})
    
    def undo_last_operation(self):
        if not self.moved_files:
            self.msg_queue.put({'type': 'info', 'message': "Nothing to undo"})
            self.msg_queue.put({'type': 'done'})
            return
        
        errors = []
        successful_undos = []
        total_files = len(self.moved_files)
        batch_size = 10
        
        for i, (current_path, original_path) in enumerate(self.moved_files, 1):
            try:
                if self._safe_file_operation(current_path, original_path, 'move'):
                    successful_undos.append((current_path, original_path))
                else:
                    errors.append(f"Could not move back {os.path.basename(current_path)}")
                
                if i % batch_size == 0 or i == total_files:
                    progress = (i / total_files) * 100
                    self.msg_queue.put({
                        'type': 'progress',
                        'value': progress,
                        'status': f"Undoing: {i}/{total_files} files"
                    })
                
            except Exception as e:
                errors.append(f"Error undoing move for {os.path.basename(current_path)}: {str(e)}")
        
        # Only remove successfully undone operations from the list
        self.moved_files = [op for op in self.moved_files if op not in successful_undos]
        
        if errors:
            self.msg_queue.put({'type': 'warning', 'message': "\n".join(errors)})
        else:
            self.msg_queue.put({'type': 'info', 'message': "Undo completed successfully!"})
        
        self.msg_queue.put({'type': 'done'})
    
    def generate_test_images(self):
        pool_dir = self.pool_path.get()
        if not pool_dir:
            self.msg_queue.put({'type': 'error', 'message': "Please select Pool folder first"})
            self.msg_queue.put({'type': 'done'})
            return
        
        total_images = 10
        batch_size = 2  # Generate images in batches
        
        for i in range(total_images):
            if i < 5:
                img = Image.new('RGB', (800, 600), color='white')
            else:
                img = Image.new('RGB', (600, 800), color='white')
            
            img_path = os.path.join(pool_dir, f"test_image_{i+1}.png")
            img.save(img_path)
            
            # Update progress in batches
            if (i + 1) % batch_size == 0 or i == total_images - 1:
                progress = ((i + 1) / total_images) * 100
                self.msg_queue.put({
                    'type': 'progress',
                    'value': progress,
                    'status': f"Generating: {i+1}/{total_images} images"
                })
        
        self.msg_queue.put({'type': 'info', 'message': "Test images generated in Pool folder!"})
        self.msg_queue.put({'type': 'done'})
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ImageGrouper()
    app.run() 