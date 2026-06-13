import threading
import tkinter as tk

import mido
from pynput import keyboard

KEY_MAP = {
    "a": 60,  # C4
    "w": 61,  # C#4/Db4
    "s": 62,  # D4
    "e": 63,  # D#4/Eb4
    "d": 64,  # E4
    "f": 65,  # F4
    "t": 66,  # F#4/Gb4
    "g": 67,  # G4
    "y": 68,  # G#4/Ab4
    "h": 69,  # A4
    "u": 70,  # A#4/Bb4
    "j": 71,  # B4
    "k": 72,  # C5
}

current_octave = 0
current_velocity = 80
active_notes = set()


def octave_shift(key):
    global current_octave
    try:
        if key.char == "z":
            current_octave = max(-4, current_octave - 1)
        elif key.char == "x":
            current_octave = min(4, current_octave + 1)
    except AttributeError:
        pass


def velocity_shift(key):
    global current_velocity
    try:
        if key.char == "c":
            current_velocity = max(0, current_velocity - 1)
        elif key.char == "v":
            current_velocity = min(127, current_velocity + 1)
    except AttributeError:
        return None


def get_note(key):
    try:
        note = KEY_MAP.get(key.char)
        if note is not None:
            return note + 12 * current_octave
    except AttributeError:
        return None


def on_press(key):
    octave_shift(key)
    velocity_shift(key)
    note = get_note(key)

    if note and note not in active_notes:
        active_notes.add(note)
        port.send(
            mido.Message("note_on", channel=0, note=note, velocity=current_velocity)
        )


def on_release(key):
    note = get_note(key)
    if note and note in active_notes:
        active_notes.discard(note)
        port.send(mido.Message("note_off", channel=0, note=note, velocity=0))


def launch_ui():
    root = tk.Tk()
    root.title("MIDI Controller")
    root.geometry("400x300")
    tk.Label(root, text="MIDI Controller").pack(pady=20)
    root.mainloop()


ui_thread = threading.Thread(target=launch_ui, daemon=True)
ui_thread.start()


with mido.open_output("IAC Driver Bus 1") as port:  # type: ignore
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
