import tkinter as tk
from tkinter import  filedialog, messagebox, Toplevel, Text, Scrollbar,scrolledtext
from PIL import Image, ImageTk 
import webbrowser
import os
import hashlib

# Functions for button actions
def wordlist():


    attack_window = tk.Toplevel()
    attack_window.title("Wordlist Attack")
    attack_window.geometry("700x500")

    hash_file_path = tk.StringVar()
    wordlist_file_path = tk.StringVar()

    # Browse for hash file
    def browse_hash_file():
        file_path = filedialog.askopenfilename(title="Select Hash File")
        if file_path:
            hash_file_path.set(file_path)

    # Browse for wordlist file
    def browse_wordlist_file():
        file_path = filedialog.askopenfilename(title="Select Wordlist File")
        if file_path:
            wordlist_file_path.set(file_path)

    # Results box (create BEFORE crack_passwords so it’s visible there)
    results_box = scrolledtext.ScrolledText(attack_window, width=70, height=15)
    results_box.pack(pady=10)

    # Password cracking logic
    def crack_passwords():
        hash_path = hash_file_path.get()
        wordlist_path = wordlist_file_path.get()

        if not os.path.exists(hash_path) or not os.path.exists(wordlist_path):
            messagebox.showerror("Error", "Please select valid files.")
            return

        try:
            with open(hash_path, 'r', encoding='utf-8', errors='ignore') as f:
                hashes = [line.strip() for line in f.readlines()]
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                wordlist = [line.strip() for line in f.readlines()]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read files: {e}")
            return

        results_box.delete(1.0, tk.END)
        results_box.insert(tk.END, "Starting password cracking...\n\n")

        cracked = 0
        for hash_line in hashes:
            found = False
            for word in wordlist:
                if hashlib.md5(word.encode()).hexdigest() == hash_line:
                    results_box.insert(tk.END, f"Found: {word} for MD5 hash: {hash_line}\n")
                    found = True
                    cracked += 1
                    break
                elif hashlib.sha1(word.encode()).hexdigest() == hash_line:
                    results_box.insert(tk.END, f"Found: {word} for SHA1 hash: {hash_line}\n")
                    found = True
                    cracked += 1
                    break
                elif hashlib.sha256(word.encode()).hexdigest() == hash_line:
                    results_box.insert(tk.END, f"Found: {word} for SHA256 hash: {hash_line}\n")
                    found = True
                    cracked += 1
                    break
            if not found:
                results_box.insert(tk.END, f"No match found for hash: {hash_line}\n")

        results_box.insert(tk.END, f"\nPassword cracking completed.\n")
        results_box.insert(tk.END, f"Cracked passwords: {cracked}\n")
        results_box.insert(tk.END, f"Passwords not found: {len(hashes) - cracked}\n")

    # Layout
    tk.Label(attack_window, text="Hash File:").pack()
    tk.Entry(attack_window, textvariable=hash_file_path, width=60).pack()
    tk.Button(attack_window, text="Browse", command=browse_hash_file).pack(pady=5)

    tk.Label(attack_window, text="Wordlist File:").pack()
    tk.Entry(attack_window, textvariable=wordlist_file_path, width=60).pack()
    tk.Button(attack_window, text="Browse", command=browse_wordlist_file).pack(pady=5)

    # Start button (AFTER defining crack_passwords)
    tk.Button(attack_window, text="Start Cracking", bg="steelblue", fg="white",
              command=crack_passwords).pack(pady=10)

    



def rainbow():
    messagebox.showinfo("rainbow attack", "rainbow attack coming soon...")

def about_tool():
    
    file_path = os.path.join(os.getcwd(), "about.html")
    webbrowser.open_new_tab('file://' + os.path.realpath(file_path))

  
    
    
    
    

# Main window
root = tk.Tk()
root.title("🔐 Advanced Password cracker")
root.geometry("400x300")
#background image
bg_image = Image.open("images/background.jpg")  
bg_image = bg_image.resize((1500, 1400))    
bg_photo = ImageTk.PhotoImage(bg_image)

# Create background label
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Heading
label = tk.Label(root, text="Advanced Password cracker", font=("Arial", 16, "bold"))
label.pack(pady=20)

# Buttons
btn_abttool = tk.Button(root, text="Project Info", font=("Arial", 12), width=15, command=about_tool)
btn_abttool.pack(pady=30)

btn_wordlist = tk.Button(root, text="wordlist attack", font=("Arial", 12), width=25, command=wordlist)
btn_wordlist.pack(pady=(150,0))

btn_rainbow = tk.Button(root, text="Rainbow table attack", font=("Arial", 12), width=25, command=rainbow)
btn_rainbow.pack(pady=10)

# Run the app
root.mainloop()
