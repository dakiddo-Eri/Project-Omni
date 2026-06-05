# MidiPlayer — Thumby polysynth MIDI player
# Put .mid files in /Games/MidiPlayer/songs/
# Requires polysynth.py + midi.py (transistortester/thumby-polysynth)

from sys import path as syspath
syspath.insert(0, "/Games/MidiPlayer")

import thumby
import os
import time

SONGS_DIR    = "/Games/MidiPlayer/songs/"
VISIBLE      = 4      # song rows on screen
CHANNELS     = 6      # polyphonic channels (max 7, fewer = louder)
SCROLL_DELAY = 1500   # ms before marquee starts after cursor lands
SCROLL_SPEED = 280    # ms per character advance

# ── helpers ───────────────────────────────────────────────────────────────────

def strip(filename, cap=None):
    """Strip extension; optionally cap length."""
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
    except:
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

# ── marquee ───────────────────────────────────────────────────────────────────

def marquee(name, moved_at, width=11):
    """
    Returns the visible slice of `name` for a scrolling marquee.
    - `moved_at`: ticks_ms() when cursor arrived on this row.
    - Holds still for SCROLL_DELAY ms, then advances one char per SCROLL_SPEED ms.
    - Wraps with a 2-space gap so the start reappears from the right.
    """
    if len(name) <= width:
        return name.ljust(width)              # short name: no scroll needed

    padded = name + "  "                      # 2-space gap before wrap
    plen   = len(padded)
    elapsed = time.ticks_diff(time.ticks_ms(), moved_at)

    if elapsed < SCROLL_DELAY:
        char_off = 0                          # hold at start during pause
    else:
        char_off = (elapsed - SCROLL_DELAY) // SCROLL_SPEED % plen

    # Build visible slice, wrapping around
    return "".join(padded[(char_off + i) % plen] for i in range(width))

# ── draw ──────────────────────────────────────────────────────────────────────

def draw_browse(songs, cur, scroll, tr, moved_at):
    thumby.display.fill(0)
    for i in range(VISIBLE):
        idx = scroll + i
        if idx >= len(songs):
            break
        sel  = (idx == cur)
        name = strip(songs[idx])              # full name, no cap
        if sel:
            label = ">" + marquee(name, moved_at)
        else:
            label = " " + name[:11]
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

# ── audio ─────────────────────────────────────────────────────────────────────

_fh         = None
_play_start = 0

def play(idx, songs, tr):
    global _fh, _play_start
    polysynth.stop()
    try:    _fh.close()
    except: pass
    _fh = open(SONGS_DIR + songs[idx], "rb")
    polysynth.enabled(CHANNELS)
    polysynth.playstream(midi.loadstream(_fh), transpose=tr)
    _play_start = time.ticks_ms()

def stop():
    global _fh
    polysynth.stop()
    try:    _fh.close(); _fh = None
    except: pass

# ── boot ──────────────────────────────────────────────────────────────────────

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

# ── state ─────────────────────────────────────────────────────────────────────

BROWSE      = 0
PLAYING     = 1
state       = BROWSE
cursor      = 0
scroll      = 0
playing_idx = 0
transpose   = 0
dirty       = True
moved_at    = time.ticks_ms()   # when cursor last landed on current row

# ── main loop ─────────────────────────────────────────────────────────────────

while True:

    if state == BROWSE:
        if thumby.buttonU.justPressed():
            if cursor > 0:
                cursor -= 1
                if cursor < scroll: scroll = cursor
                moved_at = time.ticks_ms()    # reset marquee
                dirty = True

        if thumby.buttonD.justPressed():
            if cursor < len(songs) - 1:
                cursor += 1
                if cursor >= scroll + VISIBLE: scroll = cursor - VISIBLE + 1
                moved_at = time.ticks_ms()    # reset marquee
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
            try:    play(playing_idx, songs, transpose); dirty = True
            except: pass

        if thumby.buttonR.justPressed():
            transpose += 12
            try:    play(playing_idx, songs, transpose); dirty = True
            except: pass

        elapsed = time.ticks_diff(time.ticks_ms(), _play_start)
        if not polysynth.playing and elapsed > 2000:
            playing_idx = (playing_idx + 1) % len(songs)
            cursor = playing_idx
            if cursor < scroll or cursor >= scroll + VISIBLE:
                scroll = max(0, cursor - VISIBLE // 2)
            moved_at = time.ticks_ms()
            try:
                play(playing_idx, songs, transpose)
                dirty = True
            except Exception as e:
                msg("Play error", str(e)[:12])
                time.sleep(2)
                stop()
                state = BROWSE
                dirty = True

    # browse redraws every tick when selected name needs scrolling
    cur_name = strip(songs[cursor]) if songs else ""
    needs_scroll = state == BROWSE and len(cur_name) > 11

    if dirty or needs_scroll:
        if state == BROWSE:
            draw_browse(songs, cursor, scroll, transpose, moved_at)
        elif state == PLAYING:
            draw_playing(songs[playing_idx], playing_idx, len(songs), transpose)
        dirty = False

    time.sleep_ms(10)
    thumby.display.update()
