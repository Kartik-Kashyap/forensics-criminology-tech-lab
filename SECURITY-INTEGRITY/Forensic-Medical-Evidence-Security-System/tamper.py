import os
import random
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class HackerTamperTool:
    def __init__(self, root):
        self.root = root
        self.root.title("EVIDENCE_CORRUPTOR_V1.0")
        self.root.geometry("600x450")
        self.root.configure(bg="#000000")

        # --- STYLES ---
        self.bg_color = "#000000"
        self.text_color = "#00FF41"  # Matrix Green
        self.accent_color = "#FF3333" # Red for danger/tamper
        self.font_main = ("Consolas", 10)
        self.font_header = ("Consolas", 16, "bold")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", thickness=20, troughcolor=self.bg_color, background=self.text_color)
        
        # --- HEADER ---
        header_frame = tk.Frame(root, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=20)
        
        lbl_title = tk.Label(header_frame, text="[ SYSTEM INTEGRITY COMPROMISER ]", 
                             font=self.font_header, fg=self.text_color, bg=self.bg_color)
        lbl_title.pack()
        
        lbl_subtitle = tk.Label(header_frame, text="Authorized Personnel Only // Top Secret", 
                                font=("Consolas", 8), fg="#555555", bg=self.bg_color)
        lbl_subtitle.pack()

        # --- FILE SELECTION ---
        self.lbl_file = tk.Label(root, text="NO TARGET SELECTED", font=self.font_main, 
                                 fg="#555555", bg=self.bg_color)
        self.lbl_file.pack(pady=(20, 5))

        btn_select = tk.Button(root, text="> SELECT TARGET FILE <", command=self.select_file,
                               font=self.font_main, bg="#111111", fg=self.text_color,
                               activebackground=self.text_color, activeforeground=self.bg_color,
                               relief="flat", borderwidth=1, padx=20, pady=5)
        btn_select.pack()

        # --- LOG CONSOLE ---
        self.log_text = tk.Text(root, height=8, width=60, bg="#0a0a0a", fg=self.text_color,
                                font=("Consolas", 9), relief="flat", borderwidth=0)
        self.log_text.pack(pady=20, padx=20)
        self.log_text.insert(tk.END, "> SYSTEM READY...\n")
        self.log_text.config(state=tk.DISABLED)

        # --- ACTION BUTTON ---
        self.btn_tamper = tk.Button(root, text="[ INITIATE DATA CORRUPTION ]", command=self.start_tamper_thread,
                                    font=("Consolas", 12, "bold"), bg="#330000", fg=self.accent_color,
                                    activebackground=self.accent_color, activeforeground="white",
                                    relief="flat", state=tk.DISABLED)
        self.btn_tamper.pack(pady=10, fill=tk.X, padx=50)

        # --- PROGRESS BAR ---
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10, padx=50, fill=tk.X)

        self.target_path = None

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        for char in msg:
            self.log_text.insert(tk.END, char)
            self.log_text.update()
            time.sleep(0.005) # Typing effect
        self.log_text.insert(tk.END, "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def select_file(self):
        path = filedialog.askopenfilename(title="Select File to Tamper", filetypes=[("Encrypted Bin", "*.bin"), ("All Files", "*.*")])
        if path:
            self.target_path = path
            self.lbl_file.config(text=f"TARGET: {os.path.basename(path)}", fg=self.accent_color)
            self.btn_tamper.config(state=tk.NORMAL, bg="#550000")
            self.log(f"> Target acquired: {path}")
            self.log("> Analyze... SIZE: " + str(os.path.getsize(path)) + " bytes")

    def start_tamper_thread(self):
        threading.Thread(target=self.run_tamper).start()

    def run_tamper(self):
        self.btn_tamper.config(state=tk.DISABLED)
        self.log("> INITIATING ATTACK SEQUENCE...")
        
        # Simulate "hacking" progress
        for i in range(101):
            time.sleep(random.uniform(0.01, 0.03))
            self.progress['value'] = i
            self.root.update_idletasks()
        
        try:
            with open(self.target_path, "rb") as f:
                data = bytearray(f.read())
            
            # The attack: Flip a bit in the middle
            target_idx = len(data) // 2
            original_byte = data[target_idx]
            new_byte = original_byte ^ 0xFF
            data[target_idx] = new_byte
            
            with open(self.target_path, "wb") as f:
                f.write(data)
                
            self.log(f"> BYTE {target_idx} COMPROMISED")
            self.log(f"> HEX CHANGE: {hex(original_byte)} -> {hex(new_byte)}")
            self.log("> INTEGRITY CHECKSUM INVALIDATED.")
            self.log("> ATTACK SUCCESSFUL.")
            
            messagebox.showwarning("SYSTEM COMPROMISED", "The file has been successfully tampered with.")
            
        except Exception as e:
            self.log(f"> ERROR: {e}")
        
        self.btn_tamper.config(state=tk.NORMAL)
        self.progress['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = HackerTamperTool(root)
    root.mainloop()