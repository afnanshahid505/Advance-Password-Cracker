# Password Generating along with Security-Level
import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib
import time
import threading

# Simulated Wi-Fi password
TARGET_PASSWORD = "password"
TARGET_HASH = hashlib.sha256(TARGET_PASSWORD.encode()).hexdigest()

# Function to perform brute force
def brute_force(wordlist_file, result_label):
    start_time = time.time()
    attempts = 0
    found = False

    try:
        with open(wordlist_file, "r", encoding="utf-8") as file:
            for line in file:
                guess = line.strip()
                attempts += 1
                guess_hash = hashlib.sha256(guess.encode()).hexdigest()

                if guess_hash == TARGET_HASH:
                    elapsed = time.time() - start_time
                    result_label.config(
                        text=f"[+] Password cracked!\nPassword: {guess}\nAttempts: {attempts}\nTime: {elapsed:.2f}s",
                        fg="green"
                    )
                    found = True
                    break

        if not found:
            result_label.config(text="[-] Password not found in wordlist.", fg="red")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to open file dialog and start cracking
def start_bruteforce(result_label):
    wordlist_file = filedialog.askopenfilename(title="Select Wordlist File", filetypes=[("Text files", "*.txt")])
    if wordlist_file:
        result_label.config(text="Brute forcing... please wait.", fg="blue")
        # Run in a separate thread so GUI doesn't freeze
        thread = threading.Thread(target=brute_force, args=(wordlist_file, result_label))
        thread.start()

# GUI Setup
def main():
    root = tk.Tk()
    root.title("Wi-Fi Brute Force Simulation")
    root.geometry("500x300")

    tk.Label(root, text="Wi-Fi Brute Force Simulation (Educational)", font=("Arial", 14, "bold")).pack(pady=10)

    result_label = tk.Label(root, text="Select a wordlist to start.", font=("Arial", 12))
    result_label.pack(pady=20)

    tk.Button(root, text="Upload Wordlist & Start", command=lambda: start_bruteforce(result_label),
              font=("Arial", 12), bg="black", fg="white").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
