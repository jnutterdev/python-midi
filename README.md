# Using Python to control Midi

Using python to control midi via a typing keyboard. This is more for practice, so nothing serious.

- Home row keys are the whole notes (white keys) on a piano, A though K.
- W, E, T, Y, U are the sharps/flats (black keys) on a piano.
- Z, X decreases or increases the octave
- C, V decreases or increases the velocity (default 80)

Dependencies:

- Python 3.14.4
- pynput
- mido

To install packages required:

- Run `python -m pip install -r requirements.txt`

Make sure midi can be received:

- On Mac, open up Audio Midi Setup > Window > Show Midi Studio > IAC Driver
- Click "Device is online"

Should work with most VSTs, you'll just want to be sure to set the active Midi input to "IAC Driver" as well.
