import itertools
import string
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

wordlist = []

# --- Brute-force generator ---
def generate_passwords(length):
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    for password in itertools.product(characters, repeat=length):
        yield ''.join(password)

def preview_generated():
    try:
        length = int(entry_length.get())
        if length <= 0:
            messagebox.showerror("Invalid Input", "Password length must be greater than 0.")
            return

        output_box.delete(1.0, tk.END)
        output_box.insert(tk.END, f"Preview of first 50 generated combinations (length {length}):\n\n")
        for idx, pwd in enumerate(generate_passwords(length), start=1):
            output_box.insert(tk.END, f"{idx}. {pwd}\n")
            if idx >= 50:
                output_box.insert(tk.END, "\n... and more.\n")
                break
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

def save_generated():
    try:
        length = int(entry_length.get())
        if length <= 0:
            messagebox.showerror("Invalid Input", "Password length must be greater than 0.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text Files", "*.txt")])
        if not save_path:
            return

        output_box.delete(1.0, tk.END)
        output_box.insert(tk.END, f"Saving all generated combinations to {save_path}...\n")
        root.update()

        with open(save_path, "w", encoding="utf-8") as file:
            for count, pwd in enumerate(generate_passwords(length), start=1):
                file.write(pwd + "\n")
                if count % 100000 == 0:
                    output_box.delete(1.0, tk.END)
                    output_box.insert(tk.END, f"Saved {count:,} combinations so far...\n")
                    root.update()

        messagebox.showinfo("Success", f"All generated passwords saved to {save_path}")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")

# --- Wordlist Loader ---
def load_wordlist():
    global wordlist
    file_path = filedialog.askopenfilename(title="Select Password Wordlist",
                                           filetypes=[("Text Files", "*.txt")])
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                wordlist = [line.strip() for line in file if line.strip()]
            messagebox.showinfo("Success", f"Loaded {len(wordlist):,} passwords from file.")
            preview_wordlist()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")

def preview_wordlist():
    output_box.delete(1.0, tk.END)
    if wordlist:
        output_box.insert(tk.END, "Preview of first 50 passwords from wordlist:\n\n")
        for idx, pwd in enumerate(wordlist[:50], start=1):
            output_box.insert(tk.END, f"{idx}. {pwd}\n")
        if len(wordlist) > 50:
            output_box.insert(tk.END, "\n... and more.\n")
    else:
        output_box.insert(tk.END, "No wordlist loaded yet.\n")

def save_wordlist():
    if not wordlist:
        messagebox.showerror("Error", "No wordlist loaded yet.")
        return

    save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt")])
    if not save_path:
        return

    try:
        with open(save_path, "w", encoding="utf-8") as file:
            for pwd in wordlist:
                file.write(pwd + "\n")
        messagebox.showinfo("Success", f"Saved {len(wordlist):,} passwords to {save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Could not save file: {e}")

# --- Wi-Fi Scanner ---
def scan_wifi():
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, "Scanning for available Wi-Fi networks...\n\n")
    try:
        result = subprocess.run(["netsh", "wlan", "show", "network", "mode=bssid"],
                                capture_output=True, text=True, shell=True)
        networks = result.stdout.strip()
        if networks:
            output_box.insert(tk.END, networks)
        else:
            output_box.insert(tk.END, "No networks found. Check your Wi-Fi adapter.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to scan networks: {e}")

# --- GUI Setup ---
root = tk.Tk()
root.title("Brute-force Generator & Wordlist Loader with Wi-Fi Scanner")
root.geometry("700x700")
root.resizable(False, False)

# Brute-force Generator Frame
frame_generate = tk.LabelFrame(root, text="Brute-force Generator", padx=10, pady=10)
frame_generate.pack(fill="x", padx=10, pady=5)

tk.Label(frame_generate, text="Enter Password Length:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5)
entry_length = tk.Entry(frame_generate, font=("Arial", 12), width=10, justify="center")
entry_length.grid(row=0, column=1, padx=5, pady=5)

tk.Button(frame_generate, text="Preview", font=("Arial", 12), command=preview_generated).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame_generate, text="Save All to File", font=("Arial", 12), command=save_generated).grid(row=1, column=1, padx=5, pady=5)

# Wordlist Loader Frame
frame_wordlist = tk.LabelFrame(root, text="Wordlist Loader", padx=10, pady=10)
frame_wordlist.pack(fill="x", padx=10, pady=5)

tk.Button(frame_wordlist, text="Load Wordlist", font=("Arial", 12), command=load_wordlist).grid(row=0, column=0, padx=5, pady=5)
tk.Button(frame_wordlist, text="Preview Wordlist", font=("Arial", 12), command=preview_wordlist).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_wordlist, text="Save Wordlist", font=("Arial", 12), command=save_wordlist).grid(row=0, column=2, padx=5, pady=5)

# Wi-Fi Scanner Frame
frame_wifi = tk.LabelFrame(root, text="Wi-Fi Scanner", padx=10, pady=10)
frame_wifi.pack(fill="x", padx=10, pady=5)

tk.Button(frame_wifi, text="Scan Wi-Fi Networks", font=("Arial", 12), command=scan_wifi).pack(padx=5, pady=5)

# Output Box
output_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=25, font=("Courier", 10))
output_box.pack(pady=10)

root.mainloop()
