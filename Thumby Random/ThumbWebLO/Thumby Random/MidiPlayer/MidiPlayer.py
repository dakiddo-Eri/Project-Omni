# MidiPlayer — Thumby polysynth MIDI player
# ONLY compatible with .mid or .midi files
# Put .mid files in /Games/MidiPlayer/songs/ (Song name)
# Credits and thanks to transistortester for midi.py and polysynth.py
# Made by Eri
# Some songs may have "clicking" notes using the program
# Name your files 10 characters or less to avoid cut off
from sys import path as syspath
syspath.insert(0, "/Games/MidiPlayer")

import thumby
import os
import time

SONGS_DIR = "/Games/MidiPlayer/songs/"
VISIBLE   = 4
CHANNELS  = 6


def strip(filename, cap=None):
    n = filename
    for ext in (".midi", ".MIDI", ".mid", ".MID"):
        if n.endswith(ext):
            n = n[:-len(ext)]
            break
    return n if cap is None else n[:cap]

def scan():
    try:
        return sorted([f for f in os.listdir(SONGS_DIR)
                       if f.lower().endswith(".mid")
                       or f.lower().endswith(".midi")])
    except Exception:
        return []

def msg(a, b="", c=""):
    thumby.display.fill(0)
    thumby.display.drawText(a, 0,  4, 1)
    thumby.display.drawText(b, 0, 16, 1)
    thumby.display.drawText(c, 0, 28, 1)
    thumby.display.update()

def oct_str(t):
    o = t // 12
    return ("+" if o >= 0 else "") + str(o) + "oct"


def draw_browse(songs, cur, scroll, tr):
    thumby.display.fill(0)
    for i in range(VISIBLE):
        idx = scroll + i
        if idx >= len(songs):
            break
        label = (">" if idx == cur else " ") + strip(songs[idx], 11)
        thumby.display.drawText(label, 0, i * 8, 1)
    thumby.display.drawText("A:Ply " + oct_str(tr), 0, 32, 1)
    thumby.display.update()

def draw_playing(name, idx, total, tr):
    thumby.display.fill(0)
    thumby.display.drawText(">PLAYING<", 6, 0, 1)
    thumby.display.drawText(strip(name, 12), 0, 12, 1)
    thumby.display.drawText(oct_str(tr) + " L/R", 0, 24, 1)
    thumby.display.drawText(str(idx+1)+"/"+str(total)+" B:Stp", 0, 32, 1)
    thumby.display.update()


_fh         = None
_play_start = 0

def play(idx, songs, tr):
    global _fh, _play_start
    polysynth.stop()
    try:
        if _fh is not None:
            _fh.close()
    except OSError:
        pass  # already closed, safe to ignore
    _fh = open(SONGS_DIR + songs[idx], "rb")
    polysynth.enabled(CHANNELS)
    polysynth.playstream(midi.loadstream(_fh), transpose=tr)
    _play_start = time.ticks_ms()

def stop():
    global _fh
    polysynth.stop()
    try:
        if _fh is not None:
            _fh.close()
            _fh = None
    except OSError:
        _fh = None


try:
    import polysynth
    import midi
except Exception as e:
    msg("Import fail", str(e)[:12], str(e)[12:24])
    time.sleep(5)
    raise SystemExit

songs = scan()
if not songs:
    msg("No songs!", "Add .mid files", "to /songs/")
    time.sleep(5)
    raise SystemExit

polysynth.configure()


BROWSE      = 0
PLAYING     = 1
state       = BROWSE
cursor      = 0
scroll      = 0
playing_idx = 0
transpose   = 0
dirty       = True


try:
    while True:

        if state == BROWSE:
            if thumby.buttonU.justPressed():
                if cursor > 0:
                    cursor -= 1
                    if cursor < scroll: scroll = cursor
                    dirty = True

            if thumby.buttonD.justPressed():
                if cursor < len(songs) - 1:
                    cursor += 1
                    if cursor >= scroll + VISIBLE: scroll = cursor - VISIBLE + 1
                    dirty = True

            if thumby.buttonL.justPressed():
                transpose -= 12
                dirty = True

            if thumby.buttonR.justPressed():
                transpose += 12
                dirty = True

            if thumby.buttonA.justPressed():
                try:
                    play(cursor, songs, transpose)
                    playing_idx = cursor
                    state = PLAYING
                    dirty = True
                except Exception as e:
                    msg("Play error", str(e)[:12])
                    time.sleep(2)
                    dirty = True

        elif state == PLAYING:
            if thumby.buttonB.justPressed():
                stop()
                state = BROWSE
                dirty = True

            if thumby.buttonL.justPressed():
                transpose -= 12
                try:
                    play(playing_idx, songs, transpose)
                    dirty = True
                except Exception as e:
                    msg("Play error", str(e)[:12])
                    time.sleep(2)
                    dirty = True

            if thumby.buttonR.justPressed():
                transpose += 12
                try:
                    play(playing_idx, songs, transpose)
                    dirty = True
                except Exception as e:
                    msg("Play error", str(e)[:12])
                    time.sleep(2)
                    dirty = True

            elapsed = time.ticks_diff(time.ticks_ms(), _play_start)
            if not polysynth.playing and elapsed > 2000:
                playing_idx = (playing_idx + 1) % len(songs)
                cursor = playing_idx
                if cursor < scroll or cursor >= scroll + VISIBLE:
                    scroll = max(0, cursor - VISIBLE // 2)
                try:
                    play(playing_idx, songs, transpose)
                    dirty = True
                except Exception as e:
                    msg("Play error", str(e)[:12])
                    time.sleep(2)
                    stop()
                    state = BROWSE
                    dirty = True

        if dirty:
            if state == BROWSE:
                draw_browse(songs, cursor, scroll, transpose)
            elif state == PLAYING:
                draw_playing(songs[playing_idx], playing_idx, len(songs), transpose)
            dirty = False

        time.sleep_ms(10)
        thumby.display.update()

except Exception as e:
    msg("Crash", str(e)[:12], str(e)[12:24])
    time.sleep(3)

finally:
    stop()