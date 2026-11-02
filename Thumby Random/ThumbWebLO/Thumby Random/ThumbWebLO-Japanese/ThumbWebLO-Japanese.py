import thumby
import os
import time
import gc
import struct
#Build:2013:2026:EC3.1:JPY:ERI
gc.collect()
thumby.display.setFPS(30)

SITES_DIR = "/Games/ThumbWebLO-Japanese/Sites/"
FONT_FILE = "/Games/ThumbWebLO-Japanese/jpy.fnt"
MAX_RESULTS = 20

try:
    os.mkdir(SITES_DIR)
except OSError:
    pass

FONT = {}
GLYPH_PIXELS = {}

def load_font():
    global FONT, GLYPH_PIXELS
    FONT = {}
    GLYPH_PIXELS = {}
    try:
        f = open(FONT_FILE, "rb")
    except OSError:
        return
    try:
        if f.read(4) != b"KNA2":
            return
        raw = f.read(2)
        if len(raw) != 2:
            return
        count = struct.unpack("<H", raw)[0]
        for _ in range(count):
            raw = f.read(2)
            if len(raw) != 2:
                break
            code = struct.unpack("<H", raw)[0]
            data = f.read(8)
            if len(data) != 8:
                break
            FONT[code] = data
            pixels = []
            for yy in range(8):
                bits = data[yy]
                for xx in range(8):
                    if bits & (1 << xx):
                        pixels.append((xx, yy))
            GLYPH_PIXELS[code] = pixels
    finally:
        f.close()

def kana(ch):
    n = ord(ch)
    return 0x3041 <= n <= 0x3096 or 0x30A1 <= n <= 0x30FA

def draw_glyph(ch, x, y, invert=False):
    pixels = GLYPH_PIXELS.get(ord(ch))
    if pixels is None:
        return 8
    if invert:
        thumby.display.drawFilledRectangle(x, y, 8, 8, 1)
        for xx, yy in pixels:
            thumby.display.setPixel(x + xx, y + yy, 0)
    else:
        for xx, yy in pixels:
            thumby.display.setPixel(x + xx, y + yy, 1)
    return 8

def draw_text(text, x, y, width=72, invert=False):
    pos = x
    limit = x + width
    for ch in text:
        if pos + 4 > limit:
            break
        if kana(ch):
            if pos + 8 > limit:
                break
            draw_glyph(ch, pos, y, invert)
            pos += 8
        elif ch == " ":
            pos += 4
        elif ch == "\t":
            pos += 8
        elif ch == "\n":
            break
        else:
            if ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789":
                pos += 5
            else:
                pos += 5
    return pos

def fit_text(text, width=72):
    out = ""
    used = 0
    for ch in text:
        w = 8 if kana(ch) else (4 if ch == " " else 5)
        if used + w > width:
            break
        out += ch
        used += w
    return out

def safe_lines(text):
    if not isinstance(text, str):
        text = str(text)
    return text.split("\n")

def parse_site(path):
    lines = []
    links = {}
    animations = {}
    try:
        f = open(path, "r")
    except OSError:
        return lines, links, animations, False
    try:
        while True:
            raw = f.readline()
            if not raw:
                break
            raw = raw.rstrip("\r\n")
            if not raw or raw.startswith("#"):
                continue
            if raw.startswith("T:"):
                lines.append(raw[2:])
            elif raw.startswith("A:"):
                frames = raw[2:].split("|")
                if frames:
                    lines.append(frames[0])
                    animations[len(lines) - 1] = frames
            elif raw.startswith("L:"):
                if lines:
                    links[len(lines) - 1] = raw[2:]
    finally:
        f.close()
    return lines, links, animations, True

def search(query):
    q = query.lower()
    lines = ["検索結果"]
    links = {}
    try:
        entries = os.listdir(SITES_DIR)
    except OSError:
        entries = []
    count = 0
    for name in entries:
        if not name.endswith(".sit"):
            continue
        if name in ("home.sit", "index.sit"):
            continue
        if q in name.lower():
            links[len(lines)] = name
            lines.append(name)
            count += 1
            if count >= MAX_RESULTS:
                break
    if count == 0:
        return ["みつかりません", query[:8]], {}, {}
    return lines, links, {}

def directory():
    lines = ["サイト"]
    links = {}
    try:
        entries = os.listdir(SITES_DIR)
    except OSError:
        entries = []
    for name in entries:
        if name.endswith(".sit") and name not in ("home.sit", "index.sit"):
            links[len(lines)] = name
            lines.append(name)
    if len(lines) == 1:
        lines.append("サイトなし")
    return lines, links, {}

cx = 36.0
cy = 20.0
scroll_offset = 0
visible_lines = 5

history = []
current_req = None

page_lines = []
page_links = {}
page_animations = {}

kana_rows = (
    "ぁあぃいぅうぇえぉお",
    "かがきぎくぐけげこご",
    "さざしじすずせぜそぞ",
    "ただちぢっつづてでと",
    "なにぬねのはばぱひび",
    "ぴふぶぷへべぺほぼぽ",
    "まみむめもゃやゅゆょ",
    "よらりるれろゎわをん"
)

kata_rows = (
    "ァアィイゥウェエォオ",
    "カガキギクグケゲコゴ",
    "サザシジスズセゼソゾ",
    "タダチヂッツヅテデト",
    "ナニヌネノハバパヒビ",
    "ピフブプヘベペホボポ",
    "マミムメモャヤュユョ",
    "ヨラリルレロヮワヲン"
)

def controls():
    return ("←", "＿", "へ", "決", "　", "　", "　", "　", "　", "→")

KANA_CONTROLS = controls()

def keyboard_rows(mode):
    return (kana_rows if mode == 0 else kata_rows) + (KANA_CONTROLS,)

def draw_control(ch, x, y, selected):
    if selected:
        thumby.display.drawFilledRectangle(x, y - 1, 7, 9, 1)
        fg = 0
    else:
        fg = 1
    if ch == "←":
        thumby.display.drawLine(x + 5, y + 3, x + 1, y + 3, fg)
        thumby.display.drawLine(x + 1, y + 3, x + 3, y + 1, fg)
        thumby.display.drawLine(x + 1, y + 3, x + 3, y + 5, fg)
    elif ch == "→":
        thumby.display.drawLine(x + 1, y + 3, x + 5, y + 3, fg)
        thumby.display.drawLine(x + 5, y + 3, x + 3, y + 1, fg)
        thumby.display.drawLine(x + 5, y + 3, x + 3, y + 5, fg)
    elif ch == "＿":
        thumby.display.drawLine(x + 1, y + 6, x + 5, y + 6, fg)
    elif ch == "へ":
        draw_glyph("へ", x, y, selected)
    elif ch == "決":
        thumby.display.drawLine(x + 1, y + 1, x + 5, y + 1, fg)
        thumby.display.drawLine(x + 1, y + 3, x + 5, y + 3, fg)
        thumby.display.drawLine(x + 1, y + 5, x + 5, y + 5, fg)

def open_keyboard():
    search_query = ""
    kx = 0
    ky = 0
    mode = 0

    while thumby.buttonA.pressed():
        time.sleep(0.01)

    rows = keyboard_rows(mode)
    while True:
        rows = keyboard_rows(mode)
        last = len(rows) - 1

        if ky > last:
            ky = last
        if ky == last:
            start = max(0, last - 1)
        else:
            start = ky

        thumby.display.fill(0)
        title = "ひらがな" if mode == 0 else "カタカナ"
        draw_text(title, 0, 0, 32)
        draw_text(fit_text(search_query, 40), 32, 0, 40)
        thumby.display.drawLine(0, 17, 72, 17, 1)

        for screen_row in range(2):
            row = start + screen_row
            if row >= len(rows):
                continue
            y = 20 + screen_row * 10
            for x in range(10):
                selected = row == ky and x == kx
                ch = rows[row][x]
                if row == last:
                    draw_control(ch, x * 7, y, selected)
                else:
                    if selected:
                        thumby.display.drawFilledRectangle(x * 7, y - 1, 7, 9, 1)
                    draw_glyph(ch, x * 7, y, selected)

        thumby.display.update()

        if thumby.buttonU.justPressed():
            ky = max(0, ky - 1)
        elif thumby.buttonD.justPressed():
            ky = min(last, ky + 1)
        elif thumby.buttonL.justPressed():
            kx = max(0, kx - 1)
        elif thumby.buttonR.justPressed():
            kx = min(9, kx + 1)
        elif thumby.buttonA.justPressed():
            ch = rows[ky][kx]
            if ky == last:
                if kx == 0:
                    search_query = search_query[:-1]
                elif kx == 1:
                    search_query += " "
                elif kx == 2:
                    mode = 1 - mode
                    ky = 0
                    kx = 0
                elif kx == 3:
                    if search_query:
                        return search_query
            else:
                search_query += ch
        elif thumby.buttonB.justPressed():
            return ""

def load_file(rel_path):
    if not rel_path:
        return ["ファイルなし"], {}, {}
    full = rel_path if rel_path.startswith("/") else SITES_DIR + rel_path
    lines, links, animations, found = parse_site(full)
    if not found:
        return ["ファイルなし", rel_path[:8]], {}, {}
    return lines, links, animations

def go_home():
    global page_lines, page_links, page_animations, scroll_offset, current_req
    current_req = None
    scroll_offset = 0
    try:
        lines, links, anims = load_file("home.sit")
        if lines and lines[0] == "ファイルなし":
            lines, links, anims = directory()
    except Exception:
        lines, links, anims = ["ファイルなし"], {}, {}
    page_lines = lines
    page_links = links
    page_animations = anims

def load_page(kind, value):
    try:
        if kind == "FILE":
            return load_file(value)
        return search(value)
    except Exception:
        return ["読みこみ失敗"], {}, {}

def navigate(kind, value):
    global current_req, page_lines, page_links, page_animations, scroll_offset
    if current_req is not None:
        history.append(current_req)
    current_req = (kind, value)
    page_lines, page_links, page_animations = load_page(kind, value)
    scroll_offset = 0

def go_back():
    global current_req, page_lines, page_links, page_animations, scroll_offset
    if history:
        current_req = history.pop()
        page_lines, page_links, page_animations = load_page(*current_req)
        scroll_offset = 0
    else:
        go_home()

def render():
    thumby.display.fill(0)

    for i in range(visible_lines):
        idx = i + scroll_offset
        if idx >= len(page_lines):
            continue

        y = i * 8

        if idx in page_animations:
            frames = page_animations[idx]
            if frames:
                text = frames[(time.ticks_ms() // 250) % len(frames)]
            else:
                text = ""
        else:
            text = page_lines[idx]

        hover = int(cy) // 8 == i
        link = idx in page_links

        if link and hover:
            thumby.display.drawFilledRectangle(0, y, 72, 8, 1)
            draw_text(text, 0, y, 72, True)
        else:
            draw_text(text, 0, y, 72)

    if cy < 5:
        thumby.display.drawFilledRectangle(0, 0, 72, 8, 1)
        draw_text("けんさく", 20, 0, 32, True)

    if cy >= 5:
        ix = int(cx)
        iy = int(cy)
        thumby.display.drawLine(ix - 1, iy, ix + 1, iy, 1)
        thumby.display.drawLine(ix, iy - 1, ix, iy + 1, 1)
        thumby.display.setPixel(ix, iy, 0)

    thumby.display.update()

def main_loop():
    global cx, cy, scroll_offset

    load_font()
    go_home()

    frame_count = 0
    while True:
        frame_count += 1
        if frame_count >= 30:
            gc.collect()
            frame_count = 0

        if thumby.buttonU.pressed():
            cy = max(0.0, cy - 2.2)
        if thumby.buttonD.pressed():
            cy = min(39.0, cy + 2.2)
        if thumby.buttonL.pressed():
            cx = max(0.0, cx - 2.2)
        if thumby.buttonR.pressed():
            cx = min(71.0, cx + 2.2)

        if cy >= 38 and scroll_offset + visible_lines < len(page_lines):
            scroll_offset += 1
            cy = 34
        elif cy <= 1 and scroll_offset > 0:
            scroll_offset -= 1
            cy = 5

        render()

        if thumby.buttonA.justPressed():
            if cy < 5:
                query = open_keyboard()
                if query:
                    navigate("SEARCH", query)
            else:
                visible = int(cy) // 8
                actual = visible + scroll_offset
                if actual in page_links:
                    target = page_links[actual]
                    if target == "SEARCH":
                        query = open_keyboard()
                        if query:
                            navigate("SEARCH", query)
                    elif target == "HOME":
                        go_home()
                    elif target == "BACK":
                        go_back()
                    else:
                        navigate("FILE", target)
        elif thumby.buttonB.justPressed():
            go_back()

try:
    main_loop()
except Exception as e:
    thumby.display.fill(0)
    draw_text("エラー", 0, 0, 72)
    msg = str(e)
    if not msg:
        msg = "しっぱい"
    draw_text(msg[:8], 0, 8, 72)
    thumby.display.update()
    while True:
        time.sleep(0.1)
