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
import itertools
import string
import requests #type: ignore
from io import BytesIO
import queue
import binascii

# ---------------- Utility Functions ----------------
def hash_md5(password):
    """Original helper kept for reference (not used by safe pages)."""
    return hashlib.md5(password.encode()).hexdigest()

# NOTE: the original passlib nthash-based hash_ntlm was replaced below in pages;
# we won't perform NTLM cracking in the safe pages.

# ---------------- Main App ----------------
class HashCrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Password Cracking Tool")
        self.root.geometry("1000x700")

        # === Download image from URL ===
        url = "https://media.istockphoto.com/id/1412282189/photo/lock-network-technology-concept.jpg?s=612x612&w=0&k=20&c=hripuxLs9pS_7Ln6YWQR-Ow2_-BU5RdQ4vOY8s1q1iQ="
        response = requests.get(url)
        img_data = BytesIO(response.content)

        # === Load and resize background image ===
        self.bg_image = Image.open(img_data)
        self.bg_image = self.bg_image.resize((1000, 700), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # === Set as background ===
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # === Transparent label ===
        tk.Label(
            self.root,
            text=" Advanced Password Cracking Tool ",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#000000",
        ).pack(pady=20)

        buttons = [
            ("Wi-Fi Cracker", "#1abc9c", self.open_wifi_page),
            ("NTLM Cracker", "#3498db", self.open_ntlm_page),
            ("MD5 Cracker", "#f39c12", self.open_md5_page),
            ("Rainbow Attack", "#9b59b6", self.open_rainbow_page),
        ]

        for text, color, command in buttons:
            tk.Button(
                self.root, text=text, font=("Arial", 14, "bold"),
                width=30, bg=color, fg="white", command=command
            ).pack(pady=10)

    def open_wifi_page(self):
        WiFiPage(self.root)

    def open_ntlm_page(self):
        NTLMPage(self.root)

    def open_md5_page(self):
        MD5Page(self.root)

    def open_rainbow_page(self):
        RainbowPage(self.root)

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

from passlib.hash import nthash  # type: ignore
class NTLMPage:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("NTLM Hash Cracker - Super Fast")
        self.window.geometry("700x550")
        self.window.config(bg="#3498db")

        tk.Label(
            self.window, text="NTLM Hash Cracker",
            font=("Arial", 16, "bold"), fg="white", bg="#3498db"
        ).pack(pady=10)

        self.output = ScrolledText(self.window, wrap=tk.WORD, height=20, width=80)
        self.output.pack(pady=10)

        self.targets_path = None
        self.wordlist_path = None
        self.stop_flag = {"stop": False}  # Stop signal

        # File selection buttons
        btn_frame = tk.Frame(self.window, bg="#3498db")
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Upload Targets File", bg="#2980b9", fg="white",
                  command=self.upload_targets, width=20).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Choose Wordlist", bg="#8e44ad", fg="white",
                  command=self.choose_wordlist, width=20).grid(row=0, column=1, padx=5)

        # Start and Stop buttons side by side
        run_frame = tk.Frame(self.window, bg="#3498db")
        run_frame.pack(pady=5)
        tk.Button(run_frame, text="Start Check", bg="#e67e22", fg="white",
                  command=self.start_check, width=20).grid(row=0, column=0, padx=5)
        tk.Button(run_frame, text="Stop Check", bg="#e74c3c", fg="white",
                  command=self.stop_check, width=20).grid(row=0, column=1, padx=5)

        # Back button centered below Start/Stop
        back_frame = tk.Frame(self.window, bg="#3498db")
        back_frame.pack(pady=5)
        tk.Button(back_frame, text="Back", bg="#34495e", fg="white",
                  command=self.close, width=20).pack()

        tk.Button(self.window, text="Clear Output", bg="#c0392b", fg="white",
                  command=lambda: self.output.delete(1.0, tk.END)).pack(pady=5)

    def log(self, message):
        self.output.insert(tk.END, message + "\n")
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

    def start_check(self):
        if not self.targets_path or not self.wordlist_path:
            messagebox.showwarning("Missing Input", "Please upload both targets file and wordlist.")
            return
        self.stop_flag["stop"] = False
        threading.Thread(target=self.fast_ntlm_check, daemon=True).start()

    def stop_check(self):
        self.stop_flag["stop"] = True
        self.log("[!] Stop signal sent. Cracking will terminate shortly...")

    def fast_ntlm_check(self):
        try:
            self.log("Starting NTLM hash check (super fast mode)...")

            if not os.path.exists(self.targets_path) or not os.path.exists(self.wordlist_path):
                self.log("[-] Error: One of the files does not exist.")
                return

            with open(self.targets_path, "r", encoding="utf-8", errors="ignore") as f:
                targets = {line.strip().lower() for line in f if line.strip()}

            matches = {}
            checked = 0

            with open(self.wordlist_path, "r", encoding="utf-8", errors="ignore") as wf:
                for line in wf:
                    if self.stop_flag["stop"]:
                        self.log("[!] Cracking stopped by user.")
                        break

                    password = line.strip()
                    if not password:
                        continue

                    checked += 1
                    candidate_hash = nthash.hash(password).lower()

                    if candidate_hash in targets:
                        matches[candidate_hash] = password

                    if checked % 50000 == 0:
                        self.log(f"[*] Candidates checked: {checked}")

            self.log(f"Total targets: {len(targets)}")
            self.log(f"Candidates checked: {checked}")

            if matches:
                self.log(f"[+] Matches found ({len(matches)}):")
                for h, pwd in matches.items():
                    self.log(f"    {pwd} -> {h}")
            else:
                self.log("[-] No matches found.")

        except Exception as e:
            self.log(f"[!] Error occurred: {str(e)}")

    def close(self):
        self.stop_flag["stop"] = True
        self.window.destroy()
        
# ---------------- MD5 Page ----------------

class MD5Page:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("MD5 Cracker (Safe Mode)")
        self.window.geometry("700x500")
        self.window.config(bg="#7f8c8d")

        tk.Label(
            self.window, text="MD5 — Safe Check",
            font=("Arial", 16, "bold"), fg="white", bg="#7f8c8d"
        ).pack(pady=10)

        self.output = ScrolledText(self.window, wrap=tk.WORD, height=15, width=80)
        self.output.pack(pady=10)

        self.hash_file_path = None
        self.wordlist_path = None
        self.stop_flag = False  # For stopping the cracking loop

        button_frame = tk.Frame(self.window, bg="#7f8c8d")
        button_frame.pack(pady=5)

        tk.Button(
            button_frame, text="Upload Targets File", bg="#f39c12", fg="white",
            command=self.upload_md5_hash, width=20
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_frame, text="Choose Wordlist", bg="#8e44ad", fg="white",
            command=self.choose_wordlist, width=20
        ).grid(row=0, column=1, padx=5)

        # Row for Start and Stop buttons
        action_frame = tk.Frame(self.window, bg="#7f8c8d")
        action_frame.pack(pady=5)

        tk.Button(
            action_frame, text="Start Check", bg="#e67e22", fg="white",
            command=self.start_cracking, width=20
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            action_frame, text="Stop Check", bg="#e74c3c", fg="white",
            command=self.stop_cracking, width=20
        ).grid(row=0, column=1, padx=10)

        tk.Button(
            self.window, text="Clear Output", bg="#c0392b", fg="white",
            command=lambda: self.output.delete(1.0, tk.END)
        ).pack(pady=5)

        tk.Button(
            self.window, text="Back", bg="#34495e", fg="white",
            command=self.close
        ).pack(pady=5)

    def log(self, message):
        self.output.insert(tk.END, message + "\n")
        self.output.see(tk.END)
        self.output.update()

    def upload_md5_hash(self):
        self.hash_file_path = filedialog.askopenfilename(
            title="Select Targets File",
            filetypes=[("Text Files", "*.txt")]
        )
        if self.hash_file_path:
            self.log(f"[*] Targets file loaded: {self.hash_file_path}")

    def choose_wordlist(self):
        self.wordlist_path = filedialog.askopenfilename(
            title="Select Wordlist File",
            filetypes=[("Text Files", "*.txt")]
        )
        if self.wordlist_path:
            self.log(f"[*] Wordlist loaded: {self.wordlist_path}")

    def start_cracking(self):
        if not self.hash_file_path or not self.wordlist_path:
            messagebox.showwarning("Missing Input", "Please upload both targets file and wordlist.")
            return
        self.stop_flag = False
        threading.Thread(
            target=self.safe_md5_check,
            args=(self.hash_file_path, self.wordlist_path),
            daemon=True
        ).start()

    def stop_cracking(self):
        self.stop_flag = True
        self.log("[*] Stopping the cracking process...")

    def safe_md5_check(self, targets_file, wordlist_file):
        self.log("Starting MD5 cracking...\n")

        # Load target hashes
        with open(targets_file, "r", encoding="utf-8", errors="ignore") as tf:
            targets = {line.strip().lower() for line in tf if line.strip()}

        matches = []
        total_checked = 0

        with open(wordlist_file, "r", encoding="utf-8", errors="ignore") as wf:
            for line in wf:
                if self.stop_flag:
                    self.log("[*] Cracking stopped by user.")
                    return

                candidate = line.strip()
                if not candidate:
                    continue

                # Hash candidate with MD5
                candidate_hash = hashlib.md5(candidate.encode()).hexdigest()
                total_checked += 1

                if candidate_hash in targets:
                    self.log(f"[+] Match Found: {candidate} -> {candidate_hash}")
                    matches.append((candidate, candidate_hash))

        self.log(f"\nTotal targets: {len(targets)}")
        self.log(f"Total candidates checked: {total_checked}")
        if matches:
            self.log(f"[+] {len(matches)} matches found:")
            for password, hsh in matches:
                self.log(f"    {password} -> {hsh}")
        else:
            self.log("[-] No matches found.")

    def close(self):
        self.window.destroy()

# ---------------- Rainbow  ----------------
class RainbowPage:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Rainbow Table Attack (Safe Mode)")
        self.window.geometry("700x500")
        self.window.config(bg="#8e44ad")

        tk.Label(self.window, text="Rainbow Table (Safe) — JSON key matching",
                 font=("Arial", 16, "bold"), fg="white", bg="#8e44ad").pack(pady=10)

        self.output = scrolledtext.ScrolledText(self.window, wrap=tk.WORD, height=15, width=80)
        self.output.pack(pady=10)

        # Buttons
        tk.Button(self.window, text="Upload Rainbow JSON", bg="#9b59b6", fg="white",
                  command=self.upload_rainbow_json).pack(pady=5)
        tk.Button(self.window, text="Upload Wordlist", bg="#2980b9", fg="white",
                  command=self.upload_wordlist).pack(pady=5)

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

        self.rainbow_data = None
        self.wordlist_file = None
        self.json_path = None

        self.attack_thread = None
        self.stop_flag = threading.Event()

    def log(self, msg):
        self.output.insert(tk.END, msg + "\n")
        self.output.see(tk.END)

    def upload_rainbow_json(self):
        file_path = filedialog.askopenfilename(
            title="Select Rainbow JSON File", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    self.rainbow_data = json.load(f)
                self.json_path = file_path
                self.log("[*] Rainbow JSON loaded successfully.")
            except Exception as e:
                messagebox.showerror("JSON Error", f"Failed to load JSON: {e}")

    def upload_wordlist(self):
        self.wordlist_file = filedialog.askopenfilename(
            title="Select Wordlist File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if self.wordlist_file:
            self.log("[*] Wordlist loaded successfully.")
            self.start_btn.config(state="normal")

    def start_attack(self):
        if not self.rainbow_data:
            self.log("[!] Please load a Rainbow JSON first.")
            return
        if not self.wordlist_file:
            self.log("[!] Please load a Wordlist file first.")
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
        self.log("Starting Rainbow JSON key matching (safe)...")
        try:
            rainbow_keys = {str(k).strip() for k in self.rainbow_data.keys()}
        except Exception:
            rainbow_keys = set()

        matches = []
        total_checked = 0

        with open(self.wordlist_file, "r", encoding="utf-8", errors="ignore") as wf:
            for line in wf:
                if self.stop_flag.is_set():
                    self.log("[!] Attack stopped by user.")
                    break
                candidate = line.strip()
                if not candidate:
                    continue
                total_checked += 1
                if candidate in rainbow_keys:
                    matches.append(candidate)

                if total_checked % 50000 == 0:
                    self.log(f"[*] Checked {total_checked} candidates...")

        self.log(f"JSON keys: {len(rainbow_keys)}")
        self.log(f"Candidates checked: {total_checked}")
        if matches:
            self.log(f"[+] Matches found ({len(matches)}):")
            for m in matches:
                self.log(f"    {m}")
        else:
            self.log("[-] No matches found in rainbow attack.")

        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def close(self):
        self.stop_flag.set()
        self.window.destroy()

# ---------------- Run App ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = HashCrackerApp(root)
    root.mainloop()
