import thumby
import os
import time
import gc
#Build:2013:2026:EC1.3:ETA:ERI
gc.collect()
thumby.display.setFPS(30)

SITES_DIR = "/Games/ThumbWebLO/Sites/"
INDEX_FILE = SITES_DIR + "index.sit"
MAX_RESULTS = 20

try:
    os.mkdir(SITES_DIR)
except OSError:
    pass

def _rstrip_newline(line):
    return line.rstrip("\r\n")

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
            raw = _rstrip_newline(raw)
            if not raw or raw[0] == "#":
                continue
            if raw[:2] == "T:":
                lines.append(raw[2:])
            elif raw[:2] == "A:":
                frames = raw[2:].split("|")
                lines.append(frames[0])
                animations[len(lines) - 1] = frames
            elif raw[:2] == "L:":
                idx = len(lines) - 1
                if idx >= 0:
                    links[idx] = raw[2:]
    finally:
        f.close()

    return lines, links, animations, True

def search(query):
    q = query.lower()
    lines = ["Results:"]
    links = {}

    try:
        entries = os.listdir(SITES_DIR)
    except OSError:
        entries = []

    count = 0
    for name in entries:
        if name.endswith(".sit") and name not in ("home.sit", "index.sit"):
            if q in name.lower():
                links[len(lines)] = name
                lines.append(name)
                count += 1
                if count >= MAX_RESULTS:
                    break

    if count == 0:
        return ["No results for", query[:12]], {}, {}

    return lines, links, {}

def build_directory_listing():
    lines = ["-- Sites --"]
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
        lines.append("(no sites)")
    return lines, links, {}

# cursor
cx, cy = 36.0, 20.0
scroll_offset = 0
visible_lines = 5

history = []
current_req = None

page_lines = []
page_links = {}
page_animations = {}

keyboard = (
    "qwertyuiop",
    "asdfghjkl_",
    "zxcvbnm./<",
    "http://ENT"
)

def open_keyboard():
    search_query = ""
    kx, ky = 0, 0

    while thumby.buttonA.pressed():
        time.sleep(0.01)

    while True:
        gc.collect()

        thumby.display.fill(0)
        thumby.display.drawText("SEARCH", 0, 0, 1)
        thumby.display.drawText(search_query[-12:], 0, 9, 1)
        thumby.display.drawLine(0, 17, 72, 17, 1)

        start_row = ky
        if ky == len(keyboard) - 1:
            start_row = ky - 1

        draw_y = 20
        for y_offset in range(2):
            grid_y = start_row + y_offset
            if grid_y < len(keyboard):
                for x in range(10):
                    char = keyboard[grid_y][x]

                    is_ent = (grid_y == 3 and x >= 7)
                    if grid_y == ky and ((x == kx) or (is_ent and kx >= 7)):
                        thumby.display.drawFilledRectangle(x*7, draw_y-1, 7, 9, 1)
                        thumby.display.drawText(char, x*7+1, draw_y, 0)
                    else:
                        thumby.display.drawText(char, x*7+1, draw_y, 1)
            draw_y += 10
        thumby.display.update()

        if thumby.buttonU.justPressed(): ky = max(0, ky - 1)
        elif thumby.buttonD.justPressed(): ky = min(len(keyboard)-1, ky + 1)
        elif thumby.buttonL.justPressed(): kx = max(0, kx - 1)
        elif thumby.buttonR.justPressed(): kx = min(9, kx + 1)
        elif thumby.buttonA.justPressed():
            selected = keyboard[ky][kx]
            if selected == '<': search_query = search_query[:-1]
            elif selected == '_': search_query += " "
            elif selected in ('E', 'N', 'T'):
                if len(search_query) > 0:
                    return search_query
            else:
                search_query += selected
        elif thumby.buttonB.justPressed():
            return ""

#Eri tottally watermark
def load_file(rel_path):
    full = rel_path if rel_path[:1] == "/" else SITES_DIR + rel_path
    lines, links, animations, found = parse_site(full)
    if not found: #Eri tottaly watermark
        return ["File missing:", rel_path[:12]], {}, {}
    return lines, links, animations

def go_home():
    global page_lines, page_links, page_animations, scroll_offset, current_req
    current_req = None
    scroll_offset = 0
    try:
        lines, links, anims = load_file("home.sit")
        if lines and lines[0] == "File missing:":
            lines, links, anims = build_directory_listing()
    except Exception:
        lines, links, anims = ["No files"], {}, {}
    page_lines, page_links, page_animations = lines, links, anims

def _load_page(kind, value):
    try:
        if kind == "FILE": #Eri tottally watermark
            return load_file(value)
        return search(value)
    except Exception:
        return ["No files"], {}, {}

def navigate(kind, value):
    global current_req, page_lines, page_links, page_animations, scroll_offset
    if current_req is not None:
        history.append(current_req)
    current_req = (kind, value)
    page_lines, page_links, page_animations = _load_page(kind, value)
    scroll_offset = 0

def go_back():
    global current_req, page_lines, page_links, page_animations, scroll_offset
    if history:
        current_req = history.pop()
        page_lines, page_links, page_animations = _load_page(*current_req)
        scroll_offset = 0
    else:
        go_home()

#Eri tottaly watermark
def main_loop():
    global cx, cy, scroll_offset

    go_home()

    while True:
        gc.collect()

        speed = 1.3
        if thumby.buttonU.pressed(): cy = max(0.0, cy - speed)
        if thumby.buttonD.pressed(): cy = min(39.0, cy + speed)
        if thumby.buttonL.pressed(): cx = max(0.0, cx - speed)
        if thumby.buttonR.pressed(): cx = min(71.0, cx + speed)

        if cy >= 38.0 and (scroll_offset + visible_lines) < len(page_lines):
            scroll_offset += 1
            cy = 34.0
        elif cy <= 1.0 and scroll_offset > 0:
            scroll_offset -= 1
            cy = 5.0

        # render
        thumby.display.fill(0)

        for i in range(visible_lines):
            line_idx = i + scroll_offset
            if line_idx < len(page_lines):
                y_pos = i * 8
                
                if line_idx in page_animations:
                    frames = page_animations[line_idx]
                    frame_idx = (time.ticks_ms() // 250) % len(frames)
                    text = frames[frame_idx]
                else:
                    text = page_lines[line_idx]

                is_link = line_idx in page_links
                hovering_line = (int(cy) // 8 == i)

                if is_link and hovering_line:
                    thumby.display.drawText(f">{text[:11]}", 0, y_pos, 1)
                else:
                    thumby.display.drawText(text[:12], 0, y_pos, 1)

        url_hover = (cy < 5)
        if url_hover:
            thumby.display.drawFilledRectangle(0, 0, 72, 8, 1)
            thumby.display.drawText("Search", 18, 1, 0)

        if not url_hover:
            ix, iy = int(cx), int(cy)
            thumby.display.drawLine(ix - 1, iy, ix + 1, iy, 1)
            thumby.display.drawLine(ix, iy - 1, ix, iy + 1, 1)
            thumby.display.setPixel(ix, iy, 0)

        thumby.display.update()

        if thumby.buttonA.justPressed():
            if url_hover:
                query = open_keyboard()
                if query:
                    navigate("SEARCH", query)
            else:
                clicked_visible_idx = int(cy) // 8
                clicked_actual_idx = clicked_visible_idx + scroll_offset
                if clicked_actual_idx in page_links:
                    target = page_links[clicked_actual_idx]
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

# shield
try:
    main_loop()
except Exception as e:
    thumby.display.fill(0)
    thumby.display.drawText("CRASH SHIELD", 2, 0, 1)
    msg = str(e)
    for i in range(4):
        chunk = msg[i*12:(i+1)*12]
        if not chunk:
            break
        thumby.display.drawText(chunk, 0, 8 + i*8, 1)
    thumby.display.update()
    while True:
        time.sleep(0.1)