from threading import currentThread

import mido
from pynput import keyboard

KEY_MAP = {
    "a": 60,  # C4
    "s": 62,  # D4
    "d": 64,  # E4
    "f": 65,  # F4
    "g": 67,  # G4
    "h": 69,  # A4
    "j": 71,  # B4
    "k": 72,  # C5
}

current_octave = 0
active_notes = set()


def octave_shift(key):
    global current_octave

    if key.char == "z":
        current_octave -= 1
    elif key.char == "x":
        current_octave += 1


def get_note(key):
    try:
        note = KEY_MAP.get(key.char)
        if note is not None:
            return note + 12 * current_octave
    except AttributeError:
        return None


def on_press(key):
    octave_shift(key)
    note = get_note(key)

    if note and note not in active_notes:
        active_notes.add(note)
        port.send(mido.Message("note_on", channel=0, note=note, velocity=80))


def on_release(key):
    note = get_note(key)
    if note and note in active_notes:
        active_notes.discard(note)
        port.send(mido.Message("note_off", channel=0, note=note, velocity=0))


with mido.open_output("IAC Driver Bus 1") as port:  # type: ignore
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
