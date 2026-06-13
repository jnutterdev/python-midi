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

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_to_name(note):
    return f"{NOTE_NAMES[note % 12]}{(note // 12) - 1}"


def update_notes_display():
    if notes_label:
        if active_notes:
            names = sorted([note_to_name(n) for n in active_notes])
            notes_label.config(text="  ".join(names))
        else:
            notes_label.config(text="— none —")


current_octave = 0
current_velocity = 80
active_notes = set()
port = None
octave_label = None
velocity_label = None
channel_label = None
notes_label = None
velocity_var = None
sustain_on = False


def update_labels():
    if octave_label:
        octave_label.config(text=f"{current_octave:+d}")
    if velocity_label:
        velocity_label.config(text=str(current_velocity))
    if velocity_var:
        velocity_var.set(current_velocity)


def octave_shift(event):
    global current_octave
    if event.char == "z":
        current_octave = max(-4, current_octave - 1)
    elif event.char == "x":
        current_octave = min(4, current_octave + 1)
    update_labels()


def velocity_shift(event):
    global current_velocity
    if event.char == "c":
        current_velocity = max(0, current_velocity - 1)
    elif event.char == "v":
        current_velocity = min(127, current_velocity + 1)
    update_labels()


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
    update_notes_display()


def on_release(event):
    note = get_note(event)
    if note and note in active_notes:
        if not sustain_on:
            active_notes.discard(note)
            port.send(mido.Message("note_off", channel=0, note=note, velocity=0))
        update_notes_display()


with mido.open_output("IAC Driver Bus 1") as port:
    root = tk.Tk()
    root.title("MIDI Controller")
    root.geometry("520x400")
    root.configure(bg="#1a1b26")
    root.resizable(False, False)

    # Tokyo Night colors
    BG = "#1a1b26"
    PANEL = "#1f2335"
    BORDER = "#3b4261"
    FG = "#c0caf5"
    COMMENT = "#565f89"
    CYAN = "#7dcfff"
    BLUE = "#7aa2f7"
    MAGENTA = "#bb9af7"

    # Fonts
    MONO = ("Courier New", 11)
    MONO_LG = ("Courier New", 24, "bold")
    MONO_SM = ("Courier New", 9)

    # Stat cards frame
    cards_frame = tk.Frame(root, bg=BG)
    cards_frame.pack(padx=16, pady=(16, 8), fill="x")

    # Active notes panel
    notes_frame = tk.Frame(root, bg=PANEL, padx=12, pady=10)
    notes_frame.pack(padx=16, pady=(0, 8), fill="x")
    tk.Label(notes_frame, text="ACTIVE NOTES", bg=PANEL, fg=COMMENT, font=MONO_SM).pack(
        anchor="w"
    )
    notes_label = tk.Label(
        notes_frame, text="— none —", bg=PANEL, fg=MAGENTA, font=MONO
    )
    notes_label.pack(anchor="w", pady=(4, 0))

    # Velocity slider panel
    slider_frame = tk.Frame(root, bg=PANEL, padx=12, pady=10)
    slider_frame.pack(padx=16, pady=(0, 8), fill="x")
    tk.Label(slider_frame, text="VELOCITY", bg=PANEL, fg=COMMENT, font=MONO_SM).pack(
        anchor="w"
    )

    velocity_var = tk.IntVar(value=current_velocity)

    # Buttons
    buttons_frame = tk.Frame(root, bg=BG)
    buttons_frame.pack(padx=16, pady=(0, 16), fill="x")

    def panic():
        for note in list(active_notes):
            port.send(mido.Message("note_off", channel=0, note=note, velocity=0))
        active_notes.clear()
        update_notes_display()

    def toggle_sustain():
        global sustain_on
        sustain_on = not sustain_on
        if not sustain_on:
            for note in list(active_notes):
                port.send(mido.Message("note_off", channel=0, note=note, velocity=0))
            active_notes.clear()
            update_notes_display()
        sustain_btn.config(
            text="SUSTAIN: ON" if sustain_on else "SUSTAIN: OFF",
            fg=CYAN if sustain_on else COMMENT,
        )

    panic_btn = tk.Button(
        buttons_frame,
        text="PANIC — ALL NOTES OFF",
        command=panic,
        bg=PANEL,
        fg=COMMENT,
        font=MONO_SM,
        relief="flat",
        activebackground=PANEL,
        activeforeground="#f7768e",
        cursor="hand2",
        pady=8,
    )
    panic_btn.pack(side="left", expand=True, fill="x", padx=(0, 8))

    sustain_btn = tk.Button(
        buttons_frame,
        text="SUSTAIN: OFF",
        command=toggle_sustain,
        bg=PANEL,
        fg=COMMENT,
        font=MONO_SM,
        relief="flat",
        activebackground=PANEL,
        activeforeground=CYAN,
        cursor="hand2",
        pady=8,
    )
    sustain_btn.pack(side="left", expand=True, fill="x")

    def on_slider_change(val):
        global current_velocity
        current_velocity = int(val)
        update_labels()

    slider = tk.Scale(
        slider_frame,
        from_=0,
        to=127,
        orient="horizontal",
        variable=velocity_var,
        command=on_slider_change,
        bg=PANEL,
        fg=FG,
        troughcolor=BORDER,
        activebackground=BLUE,
        highlightthickness=0,
        sliderrelief="flat",
        bd=0,
        showvalue=False,
    )
    slider.pack(fill="x", pady=(4, 0))

    def make_stat_card(parent, label, value, color):
        frame = tk.Frame(parent, bg=PANEL, padx=12, pady=10)
        frame.pack(side="left", expand=True, fill="x", padx=(0, 8))
        tk.Label(frame, text=label.upper(), bg=PANEL, fg=COMMENT, font=MONO_SM).pack(
            anchor="w"
        )
        val_label = tk.Label(frame, text=value, bg=PANEL, fg=color, font=MONO_LG)
        val_label.pack(anchor="w")
        return val_label

    octave_label = make_stat_card(cards_frame, "Octave", "+0", CYAN)
    velocity_label = make_stat_card(cards_frame, "Velocity", "80", BLUE)
    channel_label = make_stat_card(cards_frame, "Channel", "1", MAGENTA)

    root.bind("<KeyPress>", on_press)
    root.bind("<KeyRelease>", on_release)
    root.mainloop()
