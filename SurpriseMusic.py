import pygame
import os
import tkinter as tk
from tkinter import *
from tkinter.ttk import *

pygame.init()

# Load music files from a directory
music_dir = "music/Surprise"
songs = os.listdir(music_dir)

# Initialize variables for music player
song_index = 0
paused = False

# Function to play a song
def play_song():
    global paused
    global song_index
    pygame.mixer.music.load(os.path.join(music_dir, songs[song_index]))
    pygame.mixer.music.play()
    paused = False

# Function to go to the next song
def next_song():
    global song_index
    song_index = (song_index + 1) % len(songs)
    pygame.mixer.music.stop()
    play_song()

# Function to go to the previous song
def prev_song():
    global song_index
    song_index = (song_index - 1) % len(songs)
    pygame.mixer.music.stop()
    play_song()

# Function to pause or resume the music
def toggle_pause():
    global paused
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        pygame.mixer.music.pause()
        paused = True

# Function to stop the music player
def stop_player():
    pygame.mixer.music.stop()
    pygame.quit()
    root.destroy()

# Create a GUI window
root = tk.Tk()
root.title("Music Player")

# Add buttons for music player controls
from PIL import Image, ImageTk

image = Image.open("photo/bg1.jpg")
image = image.resize((400, 400), Image.ANTIALIAS)
photo = ImageTk.PhotoImage(image)
label = Label(root, image=photo)
label.pack()
pauseimage = PhotoImage(file = r"photo/pause.png")
playimage = PhotoImage(file = r"photo/play.png")
stopimage = PhotoImage(file = r"photo/stop.png")
backimage = PhotoImage(file = r"photo/back.png")
nextimage = PhotoImage(file = r"photo/next.png")




# Add buttons for music player controls
prev_button = tk.Button(root, text="<<", image = backimage, command=prev_song)
prev_button.pack(side=tk.LEFT)
pause_button = tk.Button(root, text="Pause",image = pauseimage, command=toggle_pause)
pause_button.pack(side=tk.LEFT)
next_button = tk.Button(root, text=">>",image = nextimage, command=next_song)
next_button.pack(side=tk.LEFT)
stop_button = tk.Button(root, text="Stop",image =stopimage, command=stop_player)
stop_button.pack(side=tk.LEFT)

# Start playing the first song
play_song()

# Run the GUI window
root.mainloop()