import tkinter as tk

import mido

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
port = None


def octave_shift(event):
    global current_octave
    if event.char == "z":
        current_octave = max(-4, current_octave - 1)
    elif event.char == "x":
        current_octave = min(4, current_octave + 1)


def velocity_shift(event):
    global current_velocity
    if event.char == "c":
        current_velocity = max(0, current_velocity - 1)
    elif event.char == "v":
        current_velocity = min(127, current_velocity + 1)


def get_note(event):
    note = KEY_MAP.get(event.char)
    if note is not None:
        return note + 12 * current_octave
    return None


def on_press(event):
    octave_shift(event)
    velocity_shift(event)
    note = get_note(event)
    if note and note not in active_notes:
        active_notes.add(note)
        port.send(
            mido.Message("note_on", channel=0, note=note, velocity=current_velocity)
        )


def on_release(event):
    note = get_note(event)
    if note and note in active_notes:
        active_notes.discard(note)
        port.send(mido.Message("note_off", channel=0, note=note, velocity=0))


with mido.open_output("IAC Driver Bus 1") as port:
    root = tk.Tk()
    root.title("MIDI Controller")
    root.geometry("400x300")
    tk.Label(root, text="MIDI Controller").pack(pady=20)
    root.bind("<KeyPress>", on_press)
    root.bind("<KeyRelease>", on_release)
    root.mainloop()
