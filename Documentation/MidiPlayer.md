# MidiPlayer

> Reference: Thumby Random/MidiPlayer/MidiPlayer.py

MidiPlayer is a Thumby application for browsing and playing MIDI files from a folder on the device. It combines file scanning, playback state management, and transposition controls in a compact UI.

## Purpose

The app allows users to select a song from a list of .mid or .midi files and play it through a synthesizer engine built using polysynth and MIDI parsing helpers.

## Key components

- scan(): reads the songs directory and finds valid MIDI files
- draw_browse(): shows a list of available tracks
- play(): opens a MIDI file and begins playback using the synth engine
- stop(): ends active playback safely
- transpose controls: adjust playback pitch without changing the file itself

## Audio / runtime behavior

The main script imports midi.py and polysynth.py, then configures the synthesizer before entering the loop. Playback is updated continuously and automatically advances to the next song if the current track finishes. Obviously, the audio sucks because of the Thumby's speaker so that is no suprise, it is still good though for just you wanting to hear the melodies.

> The tool is designed to be straightforward and resilient: it displays a proper error screen if imports fail or a song cannot be played.

> The files itself also has to be instrumental as the Thumby can not play lyrics/voices.

## Notes

This is one of the more utility-oriented applications in the repo. It is focused on music playback and file management, giving the Thumby a basic audio-library experience without requiring a full desktop system. 
