# ui.py

import tkinter as tk    # - tkinter: Python’s standard GUI library. Imported as tk for shorthand.
from tkinter import ttk # - ttk: The themed widgets module (provides modern-looking widgets like Combobox).
import logic

root = tk.Tk()
#root.title("Speech & Text Translator")
root.title("Text Translator")
root.geometry("1000x600")
root.configure(bg="#0A1A3D")

# ---- Container ----
container = tk.Frame(root, bg="#142859", width=900, height=520)
container.place(relx=0.5, rely=0.5, anchor="center")

# ---- Title ----
# "Speech & Text Translator"
title_text = "Text Translator"
title = tk.Label(container, text = title_text,
                 font=("Segoe UI", 24, "bold"), fg="white", bg="#142859")
title.pack(pady=15)

# ---- Combobox style (Increase dropdown popup list font) ----
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TCombobox",
    font=("Segoe UI", 15),             # text inside combobox
    padding=6
)

# Dropdown LIST items style
style.configure(
    "TCombobox.popup",
    font=("Segoe UI", 15)
)

# Extra trick to enlarge popup list
root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 16))

# ---- Language Selectors ----
langs = ["Garhwali"]

lang_frame = tk.Frame(container, bg="#142859")
lang_frame.pack(pady=10)

src = ttk.Combobox(lang_frame, values=langs, state="readonly",
                   font=("Segoe UI", 18), width=20)
src.set("Garhwali")
src.pack(side="left", padx=20)

swap = tk.Label(lang_frame, text="⇄", font=("Segoe UI", 32),
                bg="#142859", fg="white")
swap.pack(side="left", padx=25)

tgt = ttk.Combobox(lang_frame, values=["Hindi", "English"], state="readonly",
                   font=("Segoe UI", 18), width=20)
tgt.set("Hindi")
tgt.pack(side="left", padx=20)

# ---- Text Boxes ----
text_frame = tk.Frame(container, bg="#142859")
text_frame.pack(pady=10)

input_box = tk.Text(text_frame, width=40, height=12,
                    font=("Segoe UI", 14))
# Insert default text
def clear_placeholder(event):
    if input_box.get("1.0", "end-1c") == placeholder:
        input_box.delete("1.0", "end")
        input_box.config(fg="black")   # switch to normal text color

def add_placeholder(event):
    if input_box.get("1.0", "end-1c").strip() == "":
        input_box.insert("1.0", placeholder)
        input_box.config(fg="grey")    # placeholder color

placeholder = "Enter text here..."
input_box.insert("1.0", "Enter text here...")

# Bind focus events
input_box.bind("<FocusIn>", clear_placeholder)
input_box.bind("<FocusOut>", add_placeholder)

output_box = tk.Text(text_frame, width=40, height=12,
                     font=("Segoe UI", 14))

'''
    - Text: Multi-line text widgets.
    - input_box: For user input.
    - output_box: For translated output.
'''
# -------------------------------------------------------------------------------------------------

input_box.pack(side="left", padx=20)
output_box.pack(side="left", padx=20)

# ---- Buttons ----
btn_frame = tk.Frame(container, bg="#142859")
btn_frame.pack(pady=20)

def btn(text, cmd, color):
    return tk.Button(
        btn_frame,
        text=text,
        command=cmd,
        font=("Segoe UI", 14, "bold"),
        bg=color,
        fg="white",
        padx=5,
        pady=6,
        relief="raised",
        bd=4
    )
'''
    - Helper function to create styled buttons:
    - text: Button label.
    - cmd: Function to run when clicked.
    - color: Background color.
'''
# -------------------------------------------------------------------------------------------------

record_label = tk.Label(container, text="", bg="#142859", fg="white",
                        font=("Segoe UI", 14))
record_label.pack(pady=5)

'''
- Label to show recording status (currently empty).

'''
# -------------------------------buttons--------------------------------------------------
# btn("🎤 Record", lambda: logic.start_recording(record_label, True), "#5A67D8").pack(side="left", padx=10)
# btn("⏸ Pause", lambda: logic.pause_recording(record_label), "#EC7063").pack(side="left", padx=10)
# btn("▶ Play", logic.play_recording, "#5DADE2").pack(side="left", padx=10)
# btn("📁 File", logic.upload_audio_or_video, "#F4D03F").pack(side="left", padx=10)
btn("Translate", lambda: logic.translate_text(input_box, output_box), "#E91E63").pack(side="left", padx=10)
# btn("🔊", lambda: logic.play_output_audio(output_box), "#1ABC9C").pack(side="left", padx=10)
# -------------------------------------------------------------------------------------------------
root.mainloop()
'''
    - Starts Tkinter’s event loop.
    - Keeps the window open and responsive until closed.
'''


