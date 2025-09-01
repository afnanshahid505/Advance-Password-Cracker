import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk 
import webbrowser
import os

# Functions for button actions
def wordlist():
    messagebox.showinfo("wordlist", "wordlist coming soon...")

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
