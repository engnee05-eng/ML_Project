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

def translate_text(input_box, output_box):
    input_text = input_box.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showwarning("Empty", "Please enter some text to translate.")
        return
    output_text = f"Translated version of:\n{input_text}"
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, output_text)
