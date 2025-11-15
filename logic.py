# logic.py

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
from scipy.io import wavfile

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

def translate_text(input_box, output_box):
    input_text = input_box.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showwarning("Empty", "Please enter some text to translate.")
        return
    output_text = f"Translated version of:\n{input_text}"
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, output_text)

def play_output_audio(output_box):
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

# Recorder functions 
def audio_callback(indata, frames, time_info, status):
    global recording, paused, q
    if recording and not paused:
        q.put(indata.copy())

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
    label.config(text="Recording... 🔴", fg="red")
    q = queue.Queue()

    def _record():
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
        label.config(text="Paused", fg="orange")

def play_recording():
    global saved_files
    if saved_files:
        all_data = []
        for f in saved_files:
            fs_read, data = wavfile.read(f)
            all_data.append(data)
        all_data = np.concatenate(all_data, axis=0)
        wavfile.write(output_voice_file, fs, all_data)
        pygame.mixer.init()
        pygame.mixer.music.load(output_voice_file)
        pygame.mixer.music.play()
