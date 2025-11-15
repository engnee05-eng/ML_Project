# ui.py

import tkinter as tk
from tkinter import ttk
import logic

root = tk.Tk()
root.title("Speech & Text Translator")
root.geometry("1000x600")
root.configure(bg="#0A1A3D")

# ---- Container ----
container = tk.Frame(root, bg="#142859", width=900, height=520)
container.place(relx=0.5, rely=0.5, anchor="center")

# ---- Title ----
title = tk.Label(container, text="Speech & Text Translator",
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
langs = ["Hindi", "English", "Garhwali"]

lang_frame = tk.Frame(container, bg="#142859")
lang_frame.pack(pady=10)

src = ttk.Combobox(lang_frame, values=langs, state="readonly",
                   font=("Segoe UI", 18), width=20)
src.set("Hindi")
src.pack(side="left", padx=20)

swap = tk.Label(lang_frame, text="⇄", font=("Segoe UI", 32),
                bg="#142859", fg="white")
swap.pack(side="left", padx=25)

tgt = ttk.Combobox(lang_frame, values=langs, state="readonly",
                   font=("Segoe UI", 18), width=20)
tgt.set("Garhwali")
tgt.pack(side="left", padx=20)

# ---- Text Boxes ----
text_frame = tk.Frame(container, bg="#142859")
text_frame.pack(pady=10)

input_box = tk.Text(text_frame, width=40, height=12,
                    font=("Segoe UI", 14))
output_box = tk.Text(text_frame, width=40, height=12,
                     font=("Segoe UI", 14))

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

record_label = tk.Label(container, text="", bg="#142859", fg="white",
                        font=("Segoe UI", 14))
record_label.pack(pady=5)

btn("🎤 Record", lambda: logic.start_recording(record_label, True), "#5A67D8").pack(side="left", padx=10)
btn("⏸ Pause", lambda: logic.pause_recording(record_label), "#EC7063").pack(side="left", padx=10)
btn("▶ Play", logic.play_recording, "#5DADE2").pack(side="left", padx=10)
#btn("📁 File", logic.upload_audio_or_video, "#F4D03F").pack(side="left", padx=10)
btn("Translate", lambda: logic.translate_text(input_box, output_box), "#E91E63").pack(side="left", padx=10)
btn("🔊", lambda: logic.play_output_audio(output_box), "#1ABC9C").pack(side="left", padx=10)

root.mainloop()
