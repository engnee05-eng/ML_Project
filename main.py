import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gtts import gTTS
import pygame
import threading
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from PIL import Image, ImageTk
import os
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import queue
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.io import wavfile  # make sure this import is at the top

# --- Temp storage ---
TEMP_DIR = os.path.join(os.getcwd(), "temp_voice")
os.makedirs(TEMP_DIR, exist_ok=True)
output_voice_file = os.path.join(TEMP_DIR, "user_voice.wav")

# --- Global variables ---
recording = False
paused = False
q = None
fs = 44100
record_start_time = None
recorded_frames = []
saved_files = []

# --- Helper functions ---
def convert_to_wav(file_path, output_dir=None):
    ext = os.path.splitext(file_path)[1].lower()
    if output_dir is None:
        output_dir = os.getcwd()
    output_wav = os.path.join(output_dir, "converted.wav")
    try:
        if ext in [".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"]:
            clip = AudioFileClip(file_path)
            clip.write_audiofile(output_wav, logger=None)
        elif ext in [".mp4", ".mkv", ".avi", ".mov"]:
            clip = VideoFileClip(file_path)
            clip.audio.write_audiofile(output_wav, logger=None)
        else:
            messagebox.showerror("Unsupported", f"Unsupported file type: {ext}")
            return None
        return output_wav
    except Exception as e:
        messagebox.showerror("Conversion Error", str(e))
        return None

def translate_text():
    input_text = input_box.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showwarning("Empty", "Please enter some text to translate.")
        return
    output_text = f"Translated version of:\n{input_text}"
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, output_text)

def play_output_audio():
    text = output_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showinfo("No Output", "No text to play.")
        return
    try:
        tts = gTTS(text=text, lang='en')
        output_file = os.path.join(TEMP_DIR, "output.mp3")
        tts.save(output_file)
        pygame.mixer.init()
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
    except Exception as e:
        messagebox.showerror("Audio Error", str(e))

def upload_audio_or_video():
    file_path = filedialog.askopenfilename(
        title="Select Audio or Video File",
        filetypes=[("Media Files", "*.wav *.mp3 *.m4a *.flac *.aac *.ogg *.mp4 *.avi *.mkv *.mov")]
    )
    if file_path:
        converted = convert_to_wav(file_path, output_dir=os.getcwd())
        if converted:
            messagebox.showinfo("Converted", f"File converted to:\n{converted}")
        else:
            messagebox.showerror("Error", "Conversion failed.")

def upload_image():
    file_path = filedialog.askopenfilename(
        title="Select Image File",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif *.webp *.tiff")]
    )
    if file_path:
        try:
            img = Image.open(file_path)
            img.thumbnail((150, 150))
            img_tk = ImageTk.PhotoImage(img)
            img_label.configure(image=img_tk)
            img_label.image = img_tk
        except Exception as e:
            messagebox.showerror("Image Error", str(e))

# --- Voice recorder functions ---
def audio_callback(indata, frames, time_info, status):
    if recording and not paused:
        q.put(indata.copy())
        update_waveform(indata)

def update_waveform(data):
    if data.size > 0:
        waveform_line.set_ydata(data.flatten()[:waveform_length])
        canvas.draw()

def update_timer(label):
    if recording and record_start_time and not paused:
        elapsed = int(time.time() - record_start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        label.config(text=f"Recording... 🔴 {minutes:02d}:{seconds:02d}", fg="red")
        label.after(500, lambda: update_timer(label))

def start_recording(label, new_recording=False):
    global recording, paused, q, record_start_time, recorded_frames, saved_files
    if recording:
        return
    if new_recording:
        recorded_frames = []
        saved_files = []

    recording = True
    paused = False
    record_start_time = time.time()
    label.config(text="Recording... 🔴 00:00", fg="red")
    q = queue.Queue()
    update_timer(label)

    def _record():
        global recording, recorded_frames, saved_files
        with sd.InputStream(samplerate=fs, channels=1, callback=audio_callback):
            while recording:
                sd.sleep(100)
        frames = []
        while not q.empty():
            frames.append(q.get())
        if frames:
            recorded_frames.extend(frames)
            all_data = np.concatenate(frames, axis=0)
            temp_file = os.path.join(TEMP_DIR, f"segment_{len(saved_files)+1}.wav")
            write(temp_file, fs, (all_data * 32767).astype(np.int16))
            saved_files.append(temp_file)

    threading.Thread(target=_record, daemon=True).start()

def pause_recording(label):
    global recording
    if recording:
        recording = False
        # Save frames on pause
        if recorded_frames:
            all_data = np.concatenate(recorded_frames, axis=0)
            write(output_voice_file, fs, (all_data * 32767).astype(np.int16))
        label.config(text="Paused", fg="orange")

def resume_recording(label):
    global paused, recording
    if not recording:
        start_recording(label, new_recording=False)

def toggle_recording(label):
    global recording, paused
    if not recording:
        start_recording(label, new_recording=True)
    elif recording:
        pause_recording(label)
    else:
        resume_recording(label)

def play_recording():
    if saved_files:
        # Merge all segments
        all_data = []
        for f in saved_files:
            fs_read, data = wavfile.read(f)
            all_data.append(data)
        all_data = np.concatenate(all_data, axis=0)

        # Stop pygame before writing
        try:
            pygame.mixer.quit()
        except:
            pass

        # Save merged file
        wavfile.write(output_voice_file, fs, all_data)

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(output_voice_file)
            pygame.mixer.music.play()
        except Exception as e:
            messagebox.showerror("Play Error", str(e))
    else:
        messagebox.showinfo("No Recording", "No recorded audio found.")

# --- GUI setup ---
root = tk.Tk()
root.title("Speech & Text Translator")
root.geometry("950x550")
root.configure(bg="#B3E5FC")

container = tk.Frame(root, bg="white", bd=2, relief="groove")
container.place(relx=0.5, rely=0.5, anchor="center", width=900, height=500)

style = ttk.Style()
style.theme_use('default')  # ensures the style changes work
style.configure("TCombobox", font=("Arial", 16))
style.map('TCombobox', selectbackground=[('readonly', 'white')], fieldbackground=[('readonly', 'white')])
style.configure('TCombobox.Listbox', font=('Arial', 16))  # <-- this increases dropdown text font


# Language selectors
lang_frame = tk.Frame(container, bg="white")
lang_frame.pack(pady=10)

lang_options = ["Garhwali","English", "Hindi"]
src_lang = ttk.Combobox(lang_frame, values=lang_options, width=20, font=("Arial", 14), state='readonly')
src_lang.set("Hindi")
src_lang.pack(side="left", padx=20, pady=20)

swap_icon = tk.Label(lang_frame, text="⇄", font=("Arial", 30,"bold"), bg="white")
swap_icon.pack(side="left", padx=15)

tgt_lang = ttk.Combobox(lang_frame, values=lang_options, width=20, font=("Arial", 14), state='readonly')
tgt_lang.set("Garhwali")
tgt_lang.pack(side="left", padx=15, pady=5)

# Text boxes
text_frame = tk.Frame(container, bg="white")
text_frame.pack(pady=10)

input_frame = tk.Frame(text_frame, bd=2, relief="groove", bg="white")
input_frame.pack(side="left", padx=10)
input_box = tk.Text(input_frame, height=15, width=35, font=("Arial", 12), bd=0, padx=5, pady=5)
input_box.pack()

output_frame = tk.Frame(text_frame, bd=2, relief="groove", bg="white")
output_frame.pack(side="left", padx=10)
output_box = tk.Text(output_frame, height=15, width=35, font=("Arial", 12), bd=0, padx=5, pady=5)
output_box.pack()

# Buttons
icon_frame = tk.Frame(container, bg="white")
icon_frame.pack(pady=10)

button_padx = 5
button_pady = 2
button_spacing = 10

record_label = tk.Label(icon_frame, text="🎤 Record", font=("Arial", 12), bg="white",
                        relief="raised", padx=button_padx, pady=button_pady)
record_label.pack(side="left", padx=button_spacing)
record_label.bind("<Button-1>", lambda e: toggle_recording(record_label))

play_btn_canvas = tk.Canvas(icon_frame, width=60, height=20, bg="white", bd=2, relief="raised", highlightthickness=0)
play_btn_canvas.pack(side="left", padx=0, pady=0)
play_btn_canvas.create_text(30, 10, text="▶️", font=("Arial", 18), fill="black")
play_btn_canvas.create_text(40, 10, text="Play", font=("Arial", 12, "bold"), fill="black")
play_btn_canvas.bind("<Button-1>", lambda e: play_recording())

file_icon = tk.Button(icon_frame, text="📁 File", font=("Arial", 12, "bold"),
            fg="black", bg="#FFEB3B", activebackground="#FFEB3B", relief="raised",
            padx=button_padx, pady=button_pady, command=upload_audio_or_video)
file_icon.pack(side="left", padx=button_spacing)

translate_btn = tk.Button(icon_frame, text="Translate", bg="#E91E63", fg="white", font=("Arial", 12, "bold"),
                          padx=button_padx, pady=button_pady, command=translate_text)
translate_btn.pack(side="left", padx=button_spacing)

sound_icon = tk.Button(icon_frame, text="🔊", font=("Arial", 12),
                       padx=button_padx, pady=button_pady, command=play_output_audio)
sound_icon.pack(side="left", padx=button_spacing)

settings_icon = tk.Label(icon_frame, text="⚙️", font=("Arial", 12), bg="white")
settings_icon.pack(side="left", padx=button_spacing)

img_label = tk.Label(container, bg="white")
img_label.pack(pady=5)

# Waveform
waveform_length = 1024
fig = Figure(figsize=(8,1.2), dpi=100)
ax = fig.add_subplot(111)
ax.set_ylim(-0.5, 0.5)
ax.set_xlim(0, waveform_length)
ax.axis('off')
waveform_line, = ax.plot(np.zeros(waveform_length), color="green")
canvas = FigureCanvasTkAgg(fig, master=container)
canvas.get_tk_widget().pack(pady=10)

root.mainloop()
