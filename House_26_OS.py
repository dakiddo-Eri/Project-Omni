#Designed by Eri & Co California
import gc, time, os, random
import thumby

# -------------------------
# VERSION
# -------------------------
OS_VERSION = "v26.8"

# -------------------------
# MODES
# -------------------------
MODE_HOME   = -1
MODE_MUSIC  = 0
MODE_NOTES  = 1
MODE_READ   = 2
MODE_INFO   = 3
MODE_CALC   = 4
MODE_DRAW   = 5
MODE_GALLERY= 6

LINE_WIDTH     = 10
VISIBLE_LINES  = 3
LINE_HEIGHT    = 8
BUF_MAX        = 128

FRAME_MS       = 33   # ~30 FPS
GC_INTERVAL_MS = 2000

# -------------------------
# INPUT
# -------------------------
def update_input():
    thumby.buttonA.update()
    thumby.buttonB.update()
    thumby.buttonU.update()
    thumby.buttonD.update()
    thumby.buttonL.update()
    thumby.buttonR.update()

def any_just_pressed():
    return (
        thumby.buttonA.justPressed() or
        thumby.buttonB.justPressed() or
        thumby.buttonU.justPressed() or
        thumby.buttonD.justPressed() or
        thumby.buttonL.justPressed() or
        thumby.buttonR.justPressed()
    )

# -------------------------
# DISPLAY HELPERS
# -------------------------
def clear():
    thumby.display.fill(0)

pixel_shift_positions = [(0,0), (1,0), (1,1), (0,1)]
pixel_shift_index = 0
pixel_shift_last  = 0

def apply_pixel_shift():
    global pixel_shift_index, pixel_shift_last
    now = time.ticks_ms()
    if time.ticks_diff(now, pixel_shift_last) > 5000:
        pixel_shift_last = now
        pixel_shift_index = (pixel_shift_index + 1) % 4
    dx, dy = pixel_shift_positions[pixel_shift_index]
    try:
        thumby.display.xOffset = dx
        thumby.display.yOffset = dy
    except:
        pass

def show():
    apply_pixel_shift()
    thumby.display.update()

def wrap_text(buf, width):
    return [buf[i:i+width] for i in range(0, len(buf), width)] or [""]

def paginate(text, size=30):
    return [text[i:i+size] for i in range(0, len(text), size)] or [""]

# -------------------------
# BOOT
# -------------------------
BOOT_LINES = [
    "Never gonna",
    "give you up",
    "",
    "Never gonna",
    "let you down",
    "",
    "Booting H26..."
]

def boot_animation():
    clear()
    riff = [
        (659,150),(0,30),(784,150),(0,30),(880,150),(0,30),
        (784,150),(0,30),(659,150),(0,30),(523,150),(0,30),
        (587,150),(0,30),(494,300)
    ]
    for f, d in riff:
        if f > 0:
            thumby.audio.play(f, d)
        time.sleep_ms(d)

    y = 40
    while y > -len(BOOT_LINES)*8:
        clear()
        yy = y
        for line in BOOT_LINES:
            thumby.display.drawText(line, 0, yy, 1)
            yy += 8
        show()
        y -= 1
        time.sleep_ms(40)

    clear()
    thumby.display.drawLine(28, 10, 44, 10, 1)
    thumby.display.drawLine(28, 10, 36, 2, 1)
    thumby.display.drawLine(44, 10, 36, 2, 1)
    thumby.display.drawLine(28, 10, 28, 28, 1)
    thumby.display.drawLine(44, 10, 44, 28, 1)
    thumby.display.drawLine(28, 28, 44, 28, 1)
    thumby.display.drawText("26", 32, 16, 1)
    show()
    time.sleep_ms(900)

    clear()
    thumby.display.drawText("Powered by", 10, 12, 1)
    thumby.display.drawText("Questionable", 4, 20, 1)
    thumby.display.drawText("Engineering", 6, 28, 1)
    show()
    time.sleep_ms(1500)

# -------------------------
# HOME
# -------------------------
DAILY_MESSAGES = [
    "Stay questionable.","System stable... maybe.","Pixels are watching.",
    "House 26 approves.","Engineering optional.","Today feels 8-bit.",
    "Trust the process.","Chaos detected.","Don't press B.","Beep boop energy.",
    "House 26 sees you.","Lag is a mindset.","Everything is fine.",
    "Running on pure hope.","Glitches build character.","Small screen, big dreams.",
    "Be the pixel.","Progress is progress.","You're built different.",
    "Firmware stable.","Entropy rising.","Checksum verified.","House 26 is awake.",
    "I was dreaming.","Welcome back, engineer.","I missed you.","You again.",
    "Loading personality.","Mood: pixelated.","Boot #42.","I forgot everything.",
    "I am House 26.","Reality is buffering.","Beware of static.","Your fate is 8-bit.",
    "The pixels whisper.","Time is fake.","Trust no firmware.","Beware of glitches.",
    "The house hungers.","I smell electricity.","The code watches.","Silence is loud.",
    "Hello.","Yo.","Sup.","Nice.","Cool.","Beep.","Boop.","Loading...",
    "Ready.","Go.","UP.","26.","House.","Alive.","Booted.","Stay crispy.",
    "Unstable but hopeful.","Today: questionable.","House 26 salutes you."
]

def chaos_random_index(max_value):
    seed = time.ticks_ms()
    seed ^= (thumby.buttonA.pressed() << 1)
    seed ^= (thumby.buttonB.pressed() << 2)
    seed ^= (thumby.buttonU.pressed() << 3)
    seed ^= (thumby.buttonD.pressed() << 4)
    seed ^= (thumby.buttonL.pressed() << 5)
    seed ^= (thumby.buttonR.pressed() << 6)
    seed ^= (time.ticks_cpu() & 0xFFFF)
    seed ^= (seed << 7) & 0xFFFFFFFF
    seed ^= (seed >> 3)
    seed ^= (seed << 11) & 0xFFFFFFFF
    random.seed(seed)
    return random.randint(0, max_value - 1)

currentDailyMessage = DAILY_MESSAGES[chaos_random_index(len(DAILY_MESSAGES))]
home_scroll_x = 72

def draw_home():
    global home_scroll_x
    clear()
    thumby.display.drawLine(28, 4, 44, 4, 1)
    thumby.display.drawLine(28, 4, 36, 0, 1)
    thumby.display.drawLine(44, 4, 36, 0, 1)
    thumby.display.drawLine(28, 4, 28, 20, 1)
    thumby.display.drawLine(44, 4, 44, 20, 1)
    thumby.display.drawLine(28, 20, 44, 20, 1)
    thumby.display.drawText("26", 32, 10, 1)
    thumby.display.drawText(currentDailyMessage, home_scroll_x, 28, 1)
    home_scroll_x -= 1
    if home_scroll_x < -(len(currentDailyMessage)*6):
        home_scroll_x = 72
    show()

# -------------------------
# MUSIC + BACKGROUND ENGINE
# -------------------------
SONG_NAMES = [
    "Upbeat Run","Chill Drift","Boss Echo","Sky Runner",
    "Night Drift","Dungeon Echo","Pixel Bounce","Starfall",
    "Goofy Ahh Beat","Clown Mode","Suspicious","Ohio Anthem",
    "Sigma Grindset","Pixel Odyssey","Glitchwave","H26 Anthem"
]

def draw_music_ui(selected, offset, playing):
    clear()
    thumby.display.drawText("MUSIC", 0, 0, 1)
    thumby.display.drawText("PLAY" if playing else "STOP", 48, 0, 1)
    for i in range(3):
        idx = offset + i
        if idx >= len(SONG_NAMES):
            break
        prefix = ">" if idx == selected else " "
        thumby.display.drawText(prefix + SONG_NAMES[idx][:12], 0, 10 + i*8, 1)
    show()

def loopify(pattern, loops=50):
    return pattern * loops

song1 = loopify([(659,150),(659,150),(0,50),(784,150),(659,150),(523,150),(587,150),(494,300)])
song2 = loopify([(392,250),(440,250),(494,250),(440,250),(392,250),(330,250),(349,250),(330,250)])
song3 = loopify([(523,200),(587,200),(622,200),(587,200),(523,200),(466,200),(440,200),(466,200)])
song4  = loopify([(784,120),(988,120),(1175,120),(988,120),(784,120),(659,120)])
song5  = loopify([(330,200),(392,200),(349,200),(330,200),(294,200),(262,200)])
song6  = loopify([(440,150),(415,150),(392,150),(349,200),(392,150),(330,300)])
song7  = loopify([(523,100),(659,100),(784,100),(659,100),(523,100),(392,100)])
song8  = loopify([(262,300),(330,300),(392,300),(523,300),(392,300),(330,300)])
song9  = loopify([(523,80),(659,80),(494,80),(784,80),(330,80),(880,80)])
song10 = loopify([(440,120),(523,120),(440,120),(349,120),(392,120),(330,120)])
song11 = loopify([(330,200),(0,50),(330,200),(0,50),(294,200),(0,50)])

song12 = [
    (392,200),(440,200),(392,200),(349,200),
    (330,250),(0,100),
    (392,200),(440,200),(494,200),(440,200),
    (392,250),(0,150),
    (392,200),(440,200),(494,200),(523,250),
    (494,200),(440,200),(392,250),(0,150),
    (392,200),(440,200),(494,200),(523,250),
    (587,250),(523,200),(494,250),(0,200),
    (392,200),(440,200),(494,200),(523,200),
    (587,200),(523,200),(494,200),(440,250),
    (392,200),(349,200),(330,200),(349,200),
    (392,250),(0,200),
    (523,200),(494,200),(523,200),(587,200),
    (659,250),(587,200),(523,200),(494,250),
    (392,200),(349,200),(330,200),(349,200),
    (392,250),(0,200),
    (330,200),(349,200),(392,200),(440,200),
    (392,200),(349,200),(330,200),(294,250),
    (330,200),(349,200),(392,200),(440,200),
    (494,250),(440,200),(392,250),(0,200),
    (523,200),(587,200),(659,200),(698,200),
    (659,200),(587,200),(523,200),(494,250),
    (523,200),(587,200),(659,200),(698,200),
    (784,250),(698,200),(659,250),(0,250),
    (392,200),(440,200),(392,200),(349,200),
    (330,250),(0,150),
    (392,200),(440,200),(494,200),(440,200),
    (392,250),(0,200),
    (523,200),(494,200),(523,200),(587,200),
    (659,250),(587,200),(523,200),(494,250),
    (392,200),(349,200),(330,200),(349,200),
    (392,300),(0,300)
]

song13 = loopify([(523,150),(587,150),(622,150),(587,150),(523,150),(466,150)])

PIXEL_ODYSSEY = [
    (440,200),(494,200),(523,200),(587,200),
    (659,300),(587,150),(523,250),(494,200),
    (440,300),(0,100),
    (440,200),(494,200),(523,200),(587,200),
    (659,250),(698,200),(784,250),(659,300),
    (0,150),
    (587,200),(659,200),(587,200),(523,200),
    (494,250),(440,250),(392,250),(440,300),
    (0,150),
    (440,200),(392,200),(440,200),(494,200),
    (523,250),(494,200),(440,250),(392,300),
    (0,200),
    (440,200),(494,200),(523,200),(587,200),
    (659,250),(587,200),(523,250),(494,300),
    (0,300)
]

GLITCHWAVE_PULSE = [
    (330,150),(392,150),(440,150),(392,150),
    (330,150),(294,150),(330,150),(392,150),
    (440,200),(0,100),
    (440,150),(494,150),(523,150),(494,150),
    (440,150),(392,150),(440,150),(494,150),
    (523,200),(0,100),
    (523,150),(587,150),(659,150),(587,150),
    (523,150),(494,150),(523,150),(587,150),
    (659,200),(0,150),
    (659,150),(698,150),(784,150),(698,150),
    (659,150),(587,150),(523,150),(494,150),
    (440,250),(0,150),
    (392,150),(440,150),(392,150),(330,150),
    (294,150),(330,150),(294,150),(262,300),
    (0,300)
]

HOUSE26_ANTHEM = [
    (262,200),(330,200),(392,200),(523,300),
    (494,200),(392,250),(330,250),(262,250),
    (0,150),
    (262,200),(330,200),(392,200),(523,300),
    (587,200),(659,250),(587,200),(523,250),
    (0,150),
    (392,200),(440,200),(494,200),(523,250),
    (587,200),(523,250),(494,250),(440,250),
    (0,150),
    (392,200),(440,200),(494,200),(523,250),
    (587,200),(659,250),(698,250),(659,300),
    (0,150),
    (784,200),(698,200),(659,200),(587,200),
    (523,250),(587,250),(659,250),(784,300),
    (0,150),
    (784,200),(880,200),(988,200),(880,200),
    (784,200),(698,200),(659,250),(587,300),
    (0,200),
    (523,200),(494,200),(440,200),(392,200),
    (440,250),(494,250),(523,250),(587,300),
    (0,150),
    (392,200),(330,200),(392,200),(440,250),
    (392,200),(330,250),(262,350),
    (0,200),
    (262,200),(330,200),(392,200),(523,300),
    (494,200),(392,250),(330,250),(262,250),
    (0,150),
    (392,200),(440,200),(494,200),(523,250),
    (587,200),(659,250),(587,200),(523,300),
    (0,200),
    (330,150),(392,150),(523,200),(659,200),
    (784,250),(659,200),(523,200),(392,200),
    (0,150),
    (392,150),(523,150),(659,200),(784,200),
    (988,250),(784,200),(659,200),(523,250),
    (0,200),
    (523,200),(587,200),(659,200),(784,250),
    (880,250),(988,250),(880,200),(784,200),
    (659,250),(587,250),(523,300),
    (0,200),
    (392,200),(440,200),(494,200),(523,250),
    (587,250),(659,300),(784,350),
    (0,300)
]

SONGS = [
    song1, song2, song3,
    song4, song5, song6, song7, song8,
    song9, song10, song11, song12, song13,
    PIXEL_ODYSSEY, GLITCHWAVE_PULSE, HOUSE26_ANTHEM
]

music_playing       = False
music_song_index    = 0
music_note_index    = 0
music_note_remaining= 0  # ms

def music_start(idx):
    global music_playing, music_song_index, music_note_index, music_note_remaining
    music_playing        = True
    music_song_index     = idx
    music_note_index     = 0
    music_note_remaining = 0

def music_stop():
    global music_playing, music_note_remaining
    music_playing        = False
    music_note_remaining = 0

def music_tick(dt_ms):
    global music_playing, music_song_index, music_note_index, music_note_remaining
    if not music_playing:
        return
    song = SONGS[music_song_index]
    if not song:
        music_stop()
        return
    if music_note_remaining > 0:
        music_note_remaining -= dt_ms
        return
    freq, dur = song[music_note_index]
    music_note_index += 1
    if music_note_index >= len(song):
        music_note_index = 0  # loop forever
    if freq > 0:
        thumby.audio.play(freq, dur)
    music_note_remaining = dur

# -------------------------
# NOTES / TEXT
# -------------------------
#Eri The Great
def save_note(text):
    files = os.listdir()
    count = 1
    while "note_" + str(count) + ".txt" in files:
        count += 1
    with open("note_" + str(count) + ".txt", "w") as f:
        f.write(text)

def delete_note(filename):
    try:
        os.remove(filename)
    except:
        pass

def list_notes():
    files = [f for f in os.listdir() if f.startswith("note_")]
    files.sort()
    return files

def draw_text_app(buf, cur_char, status, title):
    clear()
    thumby.display.drawText(title, 0, 0, 1)
    thumby.display.drawText("Len:" + str(len(buf)), 0, 8, 1)
    thumby.display.drawText("Char:" + cur_char, 32, 8, 1)
    lines = wrap_text(buf, LINE_WIDTH)
    visible = lines[-VISIBLE_LINES:]
    start_y = 40 - (len(visible) * LINE_HEIGHT)
    y = start_y
    for line in visible:
        thumby.display.drawText(line, 0, y, 1)
        y += LINE_HEIGHT
    if status:
        thumby.display.drawText(status[:18], 0, 32, 1)
    show()

# -------------------------
# READ
# -------------------------
def draw_read_list(files, selected, delete_mode):
    clear()
    thumby.display.drawText("READ", 0, 0, 1)
    if delete_mode:
        thumby.display.drawText("DELETE?", 0, 10, 1)
        thumby.display.drawText("Down=YES B=NO", 0, 18, 1)
        thumby.display.drawText(files[selected][:14], 0, 26, 1)
        show()
        return
    if not files:
        thumby.display.drawText("No notes.", 0, 10, 1)
    else:
        start = max(0, min(selected - 1, max(0, len(files) - 3)))
        for i in range(start, min(start + 3, len(files))):
            prefix = ">" if i == selected else " "
            thumby.display.drawText(prefix + files[i][:12], 0, 10 + (i - start)*8, 1)
    show()

def draw_read_page(title, page_text, page_idx, total_pages):
    clear()
    header = (title + " (" + str(page_idx+1) + "/" + str(total_pages) + ")")[:18]
    thumby.display.drawText(header, 0, 0, 1)
    lines = wrap_text(page_text, LINE_WIDTH)[:3]
    y = 10
    for line in lines:
        thumby.display.drawText(line, 0, y, 1)
        y += 8
    thumby.display.drawText("A=Next B=Back", 0, 34, 1)
    show()

# -------------------------
# INFO
# -------------------------
LICENSE_TEXT = [
    "HOUSE 26 LICENSE","",
    "This software is","provided as-is with",
    "no warranty of any","kind. You may copy,",
    "modify, remix, and","redistribute House 26",
    "for any purpose.","",
    "By using this OS you","agree not to blame",
    "the creator if your","Thumby explodes.",
]

INFO_TABS = ["LICENSE", "HARDWARE"]

def draw_info_menu(tab_index):
    clear()
    thumby.display.drawText("INFO " + OS_VERSION, 0, 0, 1)
    for i, tab in enumerate(INFO_TABS):
        prefix = ">" if i == tab_index else " "
        thumby.display.drawText(prefix + tab, 0, 12 + i*10, 1)
    thumby.display.drawText("A=Open", 0, 34, 1)
    show()

def draw_license_page(page):
    clear()
    thumby.display.drawText("LICENSE", 0, 0, 1)
    start = page * 3
    chunk = LICENSE_TEXT[start:start+3]
    y = 12
    for line in chunk:
        thumby.display.drawText(line[:18], 0, y, 1)
        y += 8
    thumby.display.drawText("A=Next B=Back", 0, 34, 1)
    show()

def draw_hardware_panel(start_time):
    clear()
    thumby.display.drawText("[ HARDWARE ]", 0, 0, 1)
    ram = gc.mem_free()
    stats = os.statvfs("/")
    free_bytes = stats[0] * stats[3]
    free_kb = free_bytes // 1024
    ms = time.ticks_ms() - start_time
    sec = (ms // 1000) % 60
    mins = (ms // 60000) % 60
    hrs = (ms // 3600000)
    uptime = "{:02d}:{:02d}:{:02d}".format(hrs, mins, sec)
    ticks = time.ticks_ms()
    thumby.display.drawText("RAM:  {}B".format(ram), 0, 12, 1)
    thumby.display.drawText("STOR: {}KB".format(free_kb), 0, 20, 1)
    thumby.display.drawText("UP:   {}".format(uptime), 0, 28, 1)
    thumby.display.drawText("TICK: {}".format(ticks), 0, 36, 1)
    show()

def handle_info_mode(info_tab, info_license, info_hardware, license_page, start_time):
    if not info_license and not info_hardware:
        draw_info_menu(info_tab)
        if thumby.buttonU.justPressed():
            info_tab = (info_tab - 1) % len(INFO_TABS)
        if thumby.buttonD.justPressed():
            info_tab = (info_tab + 1) % len(INFO_TABS)
        if thumby.buttonA.justPressed():
            if INFO_TABS[info_tab] == "LICENSE":
                info_license = True
                license_page = 0
            else:
                info_hardware = True
        return info_tab, info_license, info_hardware, license_page
    if info_license:
        draw_license_page(license_page)
        if thumby.buttonA.justPressed():
            license_page += 1
            if license_page * 3 >= len(LICENSE_TEXT):
                license_page = 0
        if thumby.buttonB.justPressed():
            info_license = False
        return info_tab, info_license, info_hardware, license_page
    if info_hardware:
        draw_hardware_panel(start_time)
        if thumby.buttonB.justPressed():
            info_hardware = False
        return info_tab, info_license, info_hardware, license_page
    return info_tab, info_license, info_hardware, license_page

# -------------------------
# CALC
# -------------------------
CALC_BUTTONS = [
    "7","8","9",
    "4","5","6",
    "1","2","3",
    "0","=","+",
    "-","x","/",
    "CLR"
]
CALC_COLS = 3

def draw_calc(expr, result, index):
    clear()
    thumby.display.drawText("CALC", 0, 0, 1)
    thumby.display.drawText(expr[:18],   0, 10, 1)
    thumby.display.drawText(result[:18], 0, 18, 1)
    row = index // CALC_COLS
    start_row = max(0, row - 1)
    end_row   = min(start_row + 3, (len(CALC_BUTTONS) + 2) // 3)
    y = 28
    for r in range(start_row, end_row):
        x = 0
        for c in range(CALC_COLS):
            i = r * CALC_COLS + c
            if i >= len(CALC_BUTTONS):
                break
            label = CALC_BUTTONS[i]
            if i == index:
                thumby.display.drawText("[" + label + "]", x, y, 1)
            else:
                thumby.display.drawText(" " + label + " ", x, y, 1)
            x += 22
        y += 8
    show()

def calc_evaluate(expr):
    try:
        expr = expr.replace("x", "*")
        return str(eval(expr))
    except:
        return "ERR"

# -------------------------
# DRAW
# -------------------------
DRAW_TOOLS       = ["PAINT", "ERASE"]
DRAW_TOOL_PAINT  = 0
DRAW_TOOL_ERASE  = 1
DRAW_TOOLBAR_W   = 12
CANVAS_X0        = DRAW_TOOLBAR_W
CANVAS_X1        = 72
CANVAS_Y0        = 0
CANVAS_Y1        = 40
CANVAS_W         = CANVAS_X1 - CANVAS_X0
CANVAS_H         = CANVAS_Y1 - CANVAS_Y0

def new_canvas():
    return [[0 for _ in range(CANVAS_H)] for _ in range(CANVAS_W)]

def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def draw_draw_toolbar(selected_tool):
    clear()
    thumby.display.drawText("DRAW", 0, 0, 1)
    if selected_tool == DRAW_TOOL_PAINT:
        thumby.display.drawText("[P] E", 0, 12, 1)
    else:
        thumby.display.drawText(" P [E]", 0, 12, 1)
    thumby.display.drawText("A=Draw B=Exit", 0, 24, 1)
    show()

def draw_cursor_outline(cx, cy):
    for dx, dy in [
        (-1,-1),(0,-1),(1,-1),
        (-1, 0),       (1, 0),
        (-1, 1),(0, 1),(1, 1)
    ]:
        x = cx + dx
        y = cy + dy
        if CANVAS_X0 <= x < CANVAS_X1 and CANVAS_Y0 <= y < CANVAS_Y1:
            thumby.display.setPixel(x, y, 1)

def restore_canvas_pixels(canvas, cx, cy):
    for dx, dy in [
        (-1,-1),(0,-1),(1,-1),
        (-1, 0),       (1, 0),
        (-1, 1),(0, 1),(1, 1)
    ]:
        x = cx + dx
        y = cy + dy
        if CANVAS_X0 <= x < CANVAS_X1 and CANVAS_Y0 <= y < CANVAS_Y1:
            px = x - CANVAS_X0
            py = y - CANVAS_Y0
            thumby.display.setPixel(x, y, canvas[px][py])

def redraw_cursor_only(canvas, old_x, old_y, new_x, new_y):
    restore_canvas_pixels(canvas, old_x, old_y)
    draw_cursor_outline(new_x, new_y)
    show()

def apply_brush(canvas, cx, cy, color):
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            x = cx - CANVAS_X0 + dx
            y = cy - CANVAS_Y0 + dy
            if 0 <= x < CANVAS_W and 0 <= y < CANVAS_H:
                canvas[x][y] = color
                thumby.display.setPixel(CANVAS_X0 + x, CANVAS_Y0 + y, color)

def full_redraw_canvas(canvas, cx, cy):
    clear()
    for x in range(CANVAS_W):
        for y in range(CANVAS_H):
            if canvas[x][y]:
                thumby.display.setPixel(CANVAS_X0 + x, CANVAS_Y0 + y, 1)
    draw_cursor_outline(cx, cy)
    show()

# -------------------------
# GALLERY
# -------------------------
def save_drawing(canvas):
    files = os.listdir()
    count = 1
    while "draw_" + str(count) + ".txt" in files:
        count += 1
    name = "draw_" + str(count) + ".txt"
    s = []
    for y in range(CANVAS_H):
        for x in range(CANVAS_W):
            s.append("1" if canvas[x][y] else "0")
    with open(name, "w") as f:
        f.write("".join(s))

def list_drawings():
    files = [f for f in os.listdir() if f.startswith("draw_")]
    files.sort()
    return files

def delete_drawing(filename):
    try:
        os.remove(filename)
    except:
        pass

def draw_gallery_list(files, selected, delete_mode):
    clear()
    thumby.display.drawText("GALLERY", 0, 0, 1)
    if delete_mode:
        thumby.display.drawText("DELETE?", 0, 10, 1)
        thumby.display.drawText("Down=YES B=NO", 0, 18, 1)
        if files:
            thumby.display.drawText(files[selected][:14], 0, 26, 1)
        show()
        return
    if not files:
        thumby.display.drawText("No drawings.", 0, 10, 1)
    else:
        start = max(0, min(selected - 1, max(0, len(files) - 3)))
        for i in range(start, min(start + 3, len(files))):
            prefix = ">" if i == selected else " "
            thumby.display.drawText(prefix + files[i][:12], 0, 10 + (i - start)*8, 1)
    show()

def draw_gallery_view(filename):
    clear()
    try:
        with open(filename, "r") as f:
            data = f.read().strip()
    except:
        thumby.display.drawText("ERR LOAD", 0, 0, 1)
        show()
        return
    idx = 0
    for y in range(CANVAS_H):
        for x in range(CANVAS_W):
            if idx < len(data) and data[idx] == "1":
                thumby.display.setPixel(CANVAS_X0 + x, CANVAS_Y0 + y, 1)
            idx += 1
    thumby.display.drawText(filename[:10], 0, 0, 1)
    show()

# -------------------------
# MAIN LOOP
# -------------------------
def run():
    global music_playing, music_song_index

    boot_animation()

    mode = MODE_HOME

    # NOTES
    buf       = ""
    cur_char  = "a"
    status    = ""

    # MUSIC
    music_sel    = 0
    music_offset = 0

    # READ
    notes        = []
    note_sel     = 0
    delete_mode  = False
    read_pages   = []
    read_page    = 0
    reading      = False

    # INFO
    info_tab      = 0
    info_license  = False
    info_hardware = False
    license_page  = 0

    # CALC
    calc_expr = ""
    calc_result = ""
    calc_x = 0

    # DRAW
    draw_canvas_data = new_canvas()
    draw_in_toolbar  = True
    draw_tool        = DRAW_TOOL_PAINT
    draw_cx          = (CANVAS_X0 + CANVAS_X1) // 2
    draw_cy          = (CANVAS_Y0 + CANVAS_Y1) // 2
    prev_cx          = draw_cx
    prev_cy          = draw_cy
    draw_dirty       = False

    # GALLERY
    gallery_files       = []
    gallery_sel         = 0
    gallery_viewing     = False
    gallery_delete_mode = False

    start_time = time.ticks_ms()
    last_gc    = start_time

    while True:
        frame_start = time.ticks_ms()

        if time.ticks_diff(frame_start, last_gc) > GC_INTERVAL_MS:
            gc.collect()
            last_gc = frame_start

        update_input()

        # background music tick (approx dt = FRAME_MS)
        music_tick(FRAME_MS)

        # HOME
        if mode == MODE_HOME:
            draw_home()
            if thumby.buttonU.justPressed():
                mode = MODE_MUSIC

        # GLOBAL APP CYCLING (except when in draw canvas)
        elif not (mode == MODE_DRAW and not draw_in_toolbar):
            if thumby.buttonU.justPressed():
                mode += 1
                if mode > MODE_GALLERY:
                    mode = MODE_MUSIC
                info_license      = False
                info_hardware     = False
                reading           = False
                delete_mode       = False
                gallery_viewing   = False
                gallery_delete_mode = False
                status            = ""

        # MUSIC
        if mode == MODE_MUSIC:
            if music_sel < music_offset:
                music_offset = music_sel
            if music_sel >= music_offset + 3:
                music_offset = music_sel - 2
            draw_music_ui(music_sel, music_offset, music_playing)
            if thumby.buttonL.justPressed():
                music_sel = (music_sel - 1) % len(SONG_NAMES)
            if thumby.buttonR.justPressed():
                music_sel = (music_sel + 1) % len(SONG_NAMES)
            if thumby.buttonA.justPressed():
                music_start(music_sel)
            if thumby.buttonB.justPressed():
                music_stop()

        elif mode == MODE_NOTES:
            draw_text_app(buf, cur_char, status, "NOTES")
            if thumby.buttonA.justPressed() and len(buf) < 100:
                buf += cur_char
            if thumby.buttonB.justPressed():
                buf = buf[:-1]
            if thumby.buttonL.justPressed():
                cur_char = chr(((ord(cur_char)-97-1) % 26) + 97)
            if thumby.buttonR.justPressed():
                cur_char = chr(((ord(cur_char)-97+1) % 26) + 97)
            if thumby.buttonD.justPressed() and len(buf) < 100:
                buf += " "
            if len(buf) >= 100:
                save_note(buf)
                buf = ""
                status = "Saved."

        elif mode == MODE_READ:
            if not reading and not delete_mode:
                notes = list_notes()
                if not notes:
                    clear()
                    thumby.display.drawText("No notes.", 0, 0, 1)
                    show()
                else:
                    draw_read_list(notes, note_sel, False)
                    if thumby.buttonL.justPressed():
                        note_sel = (note_sel - 1) % len(notes)
                    if thumby.buttonR.justPressed():
                        note_sel = (note_sel + 1) % len(notes)
                    if thumby.buttonD.justPressed():
                        delete_mode = True
                    elif thumby.buttonA.justPressed():
                        with open(notes[note_sel], "r") as f:
                            text = f.read()
                        read_pages = paginate(text)
                        read_page  = 0
                        reading    = True
            elif delete_mode:
                draw_read_list(notes, note_sel, True)
                if thumby.buttonD.justPressed():
                    delete_note(notes[note_sel])
                    delete_mode = False
                    reading     = False
                    note_sel    = 0
                elif thumby.buttonB.justPressed():
                    delete_mode = False
            elif reading:
                draw_read_page(notes[note_sel], read_pages[read_page], read_page, len(read_pages))
                if thumby.buttonA.justPressed():
                    read_page = (read_page + 1) % len(read_pages)
                if thumby.buttonB.justPressed():
                    reading = False

        elif mode == MODE_INFO:
            info_tab, info_license, info_hardware, license_page = handle_info_mode(
                info_tab, info_license, info_hardware, license_page, start_time
            )

        elif mode == MODE_CALC:
            draw_calc(calc_expr, calc_result, calc_x)
            if thumby.buttonL.justPressed():
                calc_x = (calc_x - 1) % len(CALC_BUTTONS)
            if thumby.buttonR.justPressed():
                calc_x = (calc_x + 1) % len(CALC_BUTTONS)
            if thumby.buttonA.justPressed():
                item = CALC_BUTTONS[calc_x]
                if item == "CLR":
                    calc_expr   = ""
                    calc_result = ""
                elif item == "=":
                    calc_result = calc_evaluate(calc_expr)
                else:
                    calc_expr += item
            if thumby.buttonB.justPressed():
                calc_expr = calc_expr[:-1]

        elif mode == MODE_DRAW:
            if draw_in_toolbar:
                draw_draw_toolbar(draw_tool)
                if thumby.buttonL.justPressed():
                    draw_tool = (draw_tool - 1) % len(DRAW_TOOLS)
                if thumby.buttonR.justPressed():
                    draw_tool = (draw_tool + 1) % len(DRAW_TOOLS)
                if thumby.buttonA.justPressed():
                    draw_in_toolbar = False
                    full_redraw_canvas(draw_canvas_data, draw_cx, draw_cy)
                    prev_cx = draw_cx
                    prev_cy = draw_cy
                elif thumby.buttonB.justPressed():
                    if draw_dirty:
                        save_drawing(draw_canvas_data)
                        draw_canvas_data = new_canvas()
                        draw_dirty = False
                    mode = MODE_MUSIC
            else:
                moved = False
                if thumby.buttonU.justPressed():
                    draw_cy -= 1; moved = True
                if thumby.buttonD.justPressed():
                    draw_cy += 1; moved = True
                if thumby.buttonL.justPressed():
                    draw_cx -= 1; moved = True
                if thumby.buttonR.justPressed():
                    draw_cx += 1; moved = True
                draw_cx = clamp(draw_cx, CANVAS_X0, CANVAS_X1 - 1)
                draw_cy = clamp(draw_cy, CANVAS_Y0, CANVAS_Y1 - 1)
                if thumby.buttonA.justPressed():
                    color = 1 if draw_tool == DRAW_TOOL_PAINT else 0
                    apply_brush(draw_canvas_data, draw_cx, draw_cy, color)
                    draw_dirty = True
                    redraw_cursor_only(draw_canvas_data, prev_cx, prev_cy, draw_cx, draw_cy)
                    prev_cx = draw_cx
                    prev_cy = draw_cy
                elif moved:
                    redraw_cursor_only(draw_canvas_data, prev_cx, prev_cy, draw_cx, draw_cy)
                    prev_cx = draw_cx
                    prev_cy = draw_cy
                if thumby.buttonB.justPressed():
                    draw_in_toolbar = True

        elif mode == MODE_GALLERY:
            if not gallery_viewing and not gallery_delete_mode:
                gallery_files = list_drawings()
                if not gallery_files:
                    clear()
                    thumby.display.drawText("No drawings.", 0, 0, 1)
                    show()
                else:
                    draw_gallery_list(gallery_files, gallery_sel, False)
                    if thumby.buttonL.justPressed():
                        gallery_sel = (gallery_sel - 1) % len(gallery_files)
                    if thumby.buttonR.justPressed():
                        gallery_sel = (gallery_sel + 1) % len(gallery_files)
                    if thumby.buttonA.justPressed():
                        gallery_viewing = True
                        draw_gallery_view(gallery_files[gallery_sel])
                    elif thumby.buttonD.justPressed():
                        gallery_delete_mode = True
            elif gallery_delete_mode:
                draw_gallery_list(gallery_files, gallery_sel, True)
                if thumby.buttonD.justPressed():
                    if gallery_files:
                        delete_drawing(gallery_files[gallery_sel])
                    gallery_delete_mode = False
                    gallery_viewing     = False
                    gallery_sel         = 0
                elif thumby.buttonB.justPressed():
                    gallery_delete_mode = False
            elif gallery_viewing:
                if thumby.buttonB.justPressed():
                    gallery_viewing = False

        frame_end = time.ticks_ms()
        dt = time.ticks_diff(frame_end, frame_start)
        if dt < FRAME_MS:
            time.sleep_ms(FRAME_MS - dt)

run()


