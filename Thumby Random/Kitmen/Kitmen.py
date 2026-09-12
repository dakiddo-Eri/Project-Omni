#Designed by Eri & Co California
# =========================
# PART 1 — CORE / MAP / PLAYER / SPRITES / KITMEN / BATTLE STATE
# =========================

import thumby
import time
import random

thumby.display.setFPS(30)

# -------------------------
# CONSTANTS / BUTTONS
# -------------------------
TILE = 8
SCREEN_W = 72
SCREEN_H = 40

BTN_A = thumby.buttonA
BTN_B = thumby.buttonB
BTN_U = thumby.buttonU
BTN_D = thumby.buttonD
BTN_L = thumby.buttonL
BTN_R = thumby.buttonR

def update_buttons():
    BTN_A.update(); BTN_B.update()
    BTN_U.update(); BTN_D.update()
    BTN_L.update(); BTN_R.update()

def clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)

def make_sprite(rows):
    return bytearray(rows)

def blit8(sprite, x, y):
    thumby.display.blit(sprite, x, y, 8, 8, 0, 0, 0)

# -------------------------
# PLAYER SPRITES
# -------------------------
PLAYER_IDLE = make_sprite([
    0b00111100,
    0b01111110,
    0b11100111,
    0b11100111,
    0b11111111,
    0b10111101,
    0b00111100,
    0b00100100
])

PLAYER_BLINK = make_sprite([
    0b00111100,
    0b01111110,
    0b11111111,
    0b11111111,
    0b11111111,
    0b10111101,
    0b00111100,
    0b00100100
])

PLAYER_WALK1 = make_sprite([
    0b00111100,
    0b01111110,
    0b11100111,
    0b11100111,
    0b11111111,
    0b11101111,
    0b00111100,
    0b00100100
])

PLAYER_WALK2 = make_sprite([
    0b00111100,
    0b01111110,
    0b11100111,
    0b11100111,
    0b11111111,
    0b10111101,
    0b00111100,
    0b00100100
])

# -------------------------
# GAME STATE
# -------------------------
GAME_STATE = "intro"
MENU_STATE = "none"   # "none", "main", "items", "book", "save", "items_select"
menu_index = 0
book_scroll = 0
last_encounter_time = -20000

intro_index = 0
intro_mode = "main"   # "main" or "confirm"
starter_index = 0

# Eviler global state
evilers_defeated = 0

# -------------------------
# MAP
# -------------------------
MAP_W = 64
MAP_H = 64
MAP_DATA = bytearray(MAP_W * MAP_H)

for i in range(MAP_W * MAP_H):
    MAP_DATA[i] = 1

random.seed(12345)
for y in range(MAP_H):
    for x in range(MAP_W):
        if (x // 8 + y // 8) % 2 == 0:
            MAP_DATA[y*MAP_W + x] = 3

for _ in range(40):
    cx = random.randint(0, MAP_W-1)
    cy = random.randint(0, MAP_H-1)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            tx = cx + dx
            ty = cy + dy
            if 0 <= tx < MAP_W and 0 <= ty < MAP_H:
                if dx*dx + dy*dy <= 9:
                    MAP_DATA[ty*MAP_W + tx] = 2

def get_tile(tx, ty):
    if tx < 0 or ty < 0 or tx >= MAP_W or ty >= MAP_H:
        return 0
    return MAP_DATA[ty * MAP_W + tx]

# -------------------------
# PLAYER + CAMERA
# -------------------------
player = {
    "x": TILE * 10,
    "y": TILE * 10,
    "walk_frame": 0,
    "walk_timer": 0,
    "blink_timer": 0,
    "blink_state": "open",
}

camera = {"x": 0, "y": 0}

def update_camera():
    camera["x"] = clamp(player["x"] + 4 - SCREEN_W//2, 0, MAP_W*TILE - SCREEN_W)
    camera["y"] = clamp(player["y"] + 4 - SCREEN_H//2, 0, MAP_H*TILE - SCREEN_H)

# -------------------------
# EVILER BLOCKS
# -------------------------
eviler_blocks = [
    {"x": 20, "y": 20},
    {"x": 40, "y": 10},
    {"x": 55, "y": 30},
]

def respawn_eviler_block(i):
    while True:
        nx = random.randint(0, MAP_W-1)
        ny = random.randint(0, MAP_H-1)
        overlap = False
        for j, b in enumerate(eviler_blocks):
            if j != i and b["x"] == nx and b["y"] == ny:
                overlap = True
                break
        if not overlap:
            eviler_blocks[i]["x"] = nx
            eviler_blocks[i]["y"] = ny
            return

def draw_eviler_blocks():
    for b in eviler_blocks:
        sx = b["x"]*TILE - camera["x"]
        sy = b["y"]*TILE - camera["y"]
        if 0 <= sx < SCREEN_W and 0 <= sy < SCREEN_H:
            thumby.display.drawFilledRectangle(sx, sy, TILE, TILE, 1)

def check_eviler_trigger():
    px = player["x"] // TILE
    py = player["y"] // TILE
    for i, b in enumerate(eviler_blocks):
        if b["x"] == px and b["y"] == py:
            return i
    return -1

# -------------------------
# WORLD RENDER
# -------------------------
def draw_tile(t, sx, sy):
    if t == 1:  # grass
        thumby.display.drawRectangle(sx, sy, TILE, TILE, 1)
    elif t == 2:  # tall grass
        thumby.display.drawRectangle(sx, sy, TILE, TILE, 1)
        thumby.display.drawFilledRectangle(sx+1, sy+1, 1, 1, 1)
        thumby.display.drawFilledRectangle(sx+3, sy+2, 1, 1, 1)
        thumby.display.drawFilledRectangle(sx+5, sy+1, 1, 1, 1)
    elif t == 3:  # path
        for yy in range(0, TILE, 2):
            for xx in range(0, TILE, 2):
                thumby.display.drawFilledRectangle(sx+xx, sy+yy, 1, 1, 1)

def draw_world():
    thumby.display.fill(0)
    update_camera()

    left = camera["x"] // TILE
    top = camera["y"] // TILE

    for ty in range(top, top + 8):
        for tx in range(left, left + 12):
            t = get_tile(tx, ty)
            draw_tile(t, tx*TILE - camera["x"], ty*TILE - camera["y"])

    draw_eviler_blocks()

    if player["blink_state"] == "closed":
        sprite = PLAYER_BLINK
    elif player["walk_timer"] > 0:
        sprite = PLAYER_WALK1 if player["walk_frame"] == 0 else PLAYER_WALK2
    else:
        sprite = PLAYER_IDLE

    blit8(sprite, player["x"] - camera["x"], player["y"] - camera["y"])
    thumby.display.update()

def update_blink():
    player["blink_timer"] += 1
    if player["blink_state"] == "open":
        if player["blink_timer"] > random.randint(60, 120):
            player["blink_state"] = "closed"
            player["blink_timer"] = 0
    else:
        if player["blink_timer"] > 6:
            player["blink_state"] = "open"
            player["blink_timer"] = 0

# -------------------------
# KITMEN SPRITES (16x16)
# -------------------------
# Mankey - small monkey-ish
KIT_MA = bytearray([
0b00000111,0b00000000,
0b00011111,0b10000000,
0b00111111,0b11000000,
0b00111011,0b11000000,
0b01110111,0b11100000,
0b01111111,0b11100000,
0b11111111,0b11110000,
0b11101111,0b01110000,
0b11101111,0b01110000,
0b11111111,0b11110000,
0b01111111,0b11100000,
0b01110111,0b11100000,
0b00111011,0b11000000,
0b00111111,0b11000000,
0b00011111,0b10000000,
0b00000111,0b00000000
])

# Banna - chunky banana tank
KIT_BA = bytearray([
0b00000011,0b00000000,
0b00000111,0b10000000,
0b00001111,0b11000000,
0b00011111,0b11100000,
0b00111111,0b11110000,
0b01111111,0b11111000,
0b01111111,0b11111000,
0b11111111,0b11111100,
0b11111111,0b11111100,
0b11111111,0b11111100,
0b01111111,0b11111000,
0b01111111,0b11111000,
0b00111111,0b11110000,
0b00011111,0b11100000,
0b00001111,0b11000000,
0b00000111,0b10000000
])

# Choopick - bird-ish
KIT_CH = bytearray([
0b00000011,0b11000000,
0b00001111,0b11110000,
0b00011111,0b11111000,
0b00111100,0b00111100,
0b01111011,0b10111110,
0b01110111,0b11011110,
0b11101111,0b11101111,
0b11111111,0b11111111,
0b11111111,0b11111111,
0b11111111,0b11111111,
0b11101111,0b11101111,
0b01110111,0b11011110,
0b01111011,0b10111110,
0b00111100,0b00111100,
0b00011111,0b11111000,
0b00001111,0b11110000
])

# Block - square tank
KIT_BL = bytearray([
0b00111111,0b11111000,
0b01111111,0b11111100,
0b01111111,0b11111100,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b01111111,0b11111100,
0b01111111,0b11111100,
0b00111111,0b11111000,
0b00011111,0b11110000
])

# Rock - rounder tank
KIT_RO = bytearray([
0b00000111,0b11000000,
0b00011111,0b11110000,
0b00111111,0b11111000,
0b01111111,0b11111100,
0b01111111,0b11111100,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b01111111,0b11111100,
0b01111111,0b11111100,
0b00111111,0b11111000,
0b00011111,0b11110000,
0b00000111,0b11000000
])

# Admin - spooky-ish
KIT_AD = bytearray([
0b00000111,0b11000000,
0b00011111,0b11110000,
0b00111111,0b11111000,
0b01111111,0b11111100,
0b01100111,0b11100100,
0b11100111,0b11100110,
0b11100111,0b11100110,
0b11100111,0b11100110,
0b11100111,0b11100110,
0b11100111,0b11100110,
0b11100111,0b11100110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b01111111,0b11111100,
0b00111111,0b11111000,
0b00011111,0b11110000
])

# Grass - leafy blob
KIT_GR = bytearray([
0b00000111,0b00000000,
0b00001111,0b10000000,
0b00011111,0b11000000,
0b00111111,0b11100000,
0b01111111,0b11110000,
0b01101111,0b10110000,
0b11111111,0b11111000,
0b11101111,0b10111000,
0b11111111,0b11111000,
0b11101111,0b10111000,
0b11111111,0b11111000,
0b01111111,0b11110000,
0b00111111,0b11100000,
0b00011111,0b11000000,
0b00001111,0b10000000,
0b00000111,0b00000000
])

# Python - snake-ish
KIT_PY = bytearray([
0b00000011,0b11000000,
0b00001111,0b11110000,
0b00011111,0b11111000,
0b00111100,0b00111100,
0b01111000,0b00011110,
0b01110011,0b11001110,
0b11100111,0b11100111,
0b11100111,0b11100111,
0b11100111,0b11100111,
0b11100111,0b11100111,
0b11100111,0b11100111,
0b01110011,0b11001110,
0b01111000,0b00011110,
0b00111100,0b00111100,
0b00011111,0b11111000,
0b00001111,0b11110000
])

# Micropython - tiny dodgy blob
KIT_MP = bytearray([
0b00000000,0b00000000,
0b00000111,0b00000000,
0b00001111,0b10000000,
0b00011111,0b11000000,
0b00111111,0b11100000,
0b00111111,0b11100000,
0b01111111,0b11110000,
0b01111111,0b11110000,
0b01111111,0b11110000,
0b01111111,0b11110000,
0b00111111,0b11100000,
0b00111111,0b11100000,
0b00011111,0b11000000,
0b00001111,0b10000000,
0b00000111,0b00000000,
0b00000000,0b00000000
])

# Doggy - small dog
KIT_DO = bytearray([
0b00001111,0b00000000,
0b00011111,0b10000000,
0b00111111,0b11000000,
0b00111011,0b11000000,
0b01110111,0b11100000,
0b01110111,0b11100000,
0b11111111,0b11110000,
0b11111111,0b11110000,
0b11111111,0b11110000,
0b11111111,0b11110000,
0b01110111,0b11100000,
0b01110111,0b11100000,
0b00111011,0b11000000,
0b00111111,0b11000000,
0b00011111,0b10000000,
0b00001111,0b00000000
])

# Meme - weird bat blob
KIT_ME = bytearray([
0b00000000,0b00000000,
0b00011000,0b00110000,
0b00111100,0b01111000,
0b01111110,0b11111100,
0b11100111,0b11100110,
0b11100111,0b11100110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11111111,0b11111110,
0b11100111,0b11100110,
0b11100111,0b11100110,
0b01111110,0b11111100,
0b00111100,0b01111000,
0b00011000,0b00110000,
0b00000000,0b00000000
])

# Eri - big cat tank
KIT_ER = bytearray([
0b00011100,0b00111000,
0b00111110,0b01111100,
0b01111111,0b11111110,
0b01100111,0b11100110,
0b11100111,0b11100111,
0b11111111,0b11111111,
0b11111111,0b11111111,
0b11111111,0b11111111,
0b11111111,0b11111111,
0b11111111,0b11111111,
0b11100111,0b11100111,
0b11100111,0b11100111,
0b01100111,0b11100110,
0b01111111,0b11111110,
0b00111110,0b01111100,
0b00011100,0b00111000
])

# -------------------------
# KITMEN DATA / WILD TABLE
# -------------------------
kitmen_data = [
    {"name":"Mankey",   "max_hp":16, "atk":7, "def":3, "catch_rate":60,
     "dodge":0,  "sprite":KIT_MA, "special":"double_hit"},
    {"name":"Banna",    "max_hp":28, "atk":8, "def":6, "catch_rate":80,
     "dodge":0,  "sprite":KIT_BA, "special":None},
    {"name":"Choopick", "max_hp":20, "atk":5, "def":4, "catch_rate":65,
     "dodge":0,  "sprite":KIT_CH, "special":None},
    {"name":"Block",    "max_hp":30, "atk":3, "def":7, "catch_rate":55,
     "dodge":0,  "sprite":KIT_BL, "special":None},
    {"name":"Rock",     "max_hp":32, "atk":3, "def":8, "catch_rate":55,
     "dodge":0,  "sprite":KIT_RO, "special":None},
    {"name":"Admin",    "max_hp":22, "atk":9, "def":5, "catch_rate":45,
     "dodge":0,  "sprite":KIT_AD, "special":None},
    {"name":"Grass",    "max_hp":16, "atk":6, "def":3, "catch_rate":60,
     "dodge":30, "sprite":KIT_GR, "special":None},
    {"name":"Python",   "max_hp":20, "atk":9, "def":4, "catch_rate":45,
     "dodge":50, "sprite":KIT_PY, "special":None},
    {"name":"Micropy",  "max_hp":14, "atk":4, "def":3, "catch_rate":55,
     "dodge":80, "sprite":KIT_MP, "special":None},
    {"name":"Doggy",    "max_hp":10, "atk":1, "def":2, "catch_rate":90,
     "dodge":10, "sprite":KIT_DO, "special":"catch_only"},
    {"name":"Meme",     "max_hp":40, "atk":4, "def":6, "catch_rate":40,
     "dodge":10, "sprite":KIT_ME, "special":None},
    {"name":"Eri",      "max_hp":60, "atk":5, "def":8, "catch_rate":30,
     "dodge":20, "sprite":KIT_ER, "special":None},
]

KITMEN_COUNT = len(kitmen_data)

WILD_TABLE = (
    [0]*6 +   # Mankey mid
    [1]*6 +   # Banna mid
    [2]*10 +  # Choopick high
    [3]*10 +  # Block high
    [4]*10 +  # Rock high
    [5]*3 +   # Admin small
    [6]*6 +   # Grass mid
    [7]*3 +   # Python small
    [8]*3 +   # Micropy small
    [9]*1 +   # Doggy microscopic
    [10]*1 +  # Meme rare
    [11]*1    # Eri ultra rare
)

# -------------------------
# INVENTORY / CAUGHT
# -------------------------
inventory = {
    "Rocks": 20,
    "Heals": 3
}

caught_flags = [0] * KITMEN_COUNT
caught_counts = [0] * KITMEN_COUNT

# -------------------------
# BATTLE STATE
# -------------------------
battle = {
    "wild_id": 0,
    "wild_hp": 0,
    "player_id": 0,
    "player_hp": 30,
    "menu_index": 0,
    "message": "",
    "message_timer": 0,
    "end_after": None,
    "eviler": False,
    "eviler_index": -1
}
# =========================
# PART 2 — SAVE / INTRO / STARTER / ENCOUNTERS / MOVEMENT
# =========================

# -------------------------
# SAVE / LOAD
# -------------------------
def save_game():
    data = {
        "x": player["x"],
        "y": player["y"],
        "caught_flags": caught_flags,
        "caught_counts": caught_counts,
        "rocks": inventory["Rocks"],
        "heals": inventory["Heals"],
        "starter": battle["player_id"],
        "evilers_defeated": evilers_defeated
    }
    try:
        with open("/Games/KitmenSave.txt", "w") as f:
            f.write(str(data))
    except:
        pass

def load_game():
    global caught_flags, caught_counts, evilers_defeated
    try:
        with open("/Games/KitmenSave.txt", "r") as f:
            data = eval(f.read())
            player["x"] = data["x"]
            player["y"] = data["y"]
            cf = data.get("caught_flags", [0]*KITMEN_COUNT)
            cc = data.get("caught_counts", [0]*KITMEN_COUNT)
            caught_flags = list(cf) + [0]*(KITMEN_COUNT-len(cf))
            caught_counts = list(cc) + [0]*(KITMEN_COUNT-len(cc))
            inventory["Rocks"] = data.get("rocks", 20)
            inventory["Heals"] = data.get("heals", 3)
            battle["player_id"] = data.get("starter", 0)
            battle["player_hp"] = kitmen_data[battle["player_id"]]["max_hp"]
            evilers_defeated = data.get("evilers_defeated", 0)
    except:
        new_game()

def new_game():
    global caught_flags, caught_counts, GAME_STATE, evilers_defeated
    player["x"] = TILE * 10
    player["y"] = TILE * 10
    caught_flags = [0] * KITMEN_COUNT
    caught_counts = [0] * KITMEN_COUNT
    inventory["Rocks"] = 20
    inventory["Heals"] = 3
    evilers_defeated = 0
    GAME_STATE = "starter"

# -------------------------
# INTRO
# -------------------------
def draw_intro():
    thumby.display.fill(0)
    thumby.display.drawText("KITMEN", 18, 4, 1)

    if intro_mode == "main":
        options = ["Load", "New Game"]
        for i, opt in enumerate(options):
            prefix = "> " if i == intro_index else "  "
            thumby.display.drawText(prefix + opt, 10, 18 + i*10, 1)
    else:
        thumby.display.drawText("New Game?", 10, 16, 1)
        thumby.display.drawText("A=Yes B=No", 6, 26, 1)

    thumby.display.update()

def update_intro():
    global intro_index, GAME_STATE, intro_mode

    update_buttons()

    if intro_mode == "main":
        if BTN_U.justPressed():
            intro_index = (intro_index - 1) % 2
        elif BTN_D.justPressed():
            intro_index = (intro_index + 1) % 2

        if BTN_A.justPressed():
            if intro_index == 0:
                load_game()
                GAME_STATE = "overworld"
            else:
                intro_mode = "confirm"
    else:
        if BTN_A.justPressed():
            new_game()
        elif BTN_B.justPressed():
            intro_mode = "main"

# -------------------------
# STARTER SELECTION
# -------------------------
def draw_starter():
    thumby.display.fill(0)
    thumby.display.drawText("Choose Kitmen", 0, 0, 1)

    starters = [0, 1, 2]
    y = 12
    for i, idx in enumerate(starters):
        name = kitmen_data[idx]["name"]
        prefix = "> " if i == starter_index else "  "
        thumby.display.drawText(prefix + name, 5, y, 1)
        y += 10

    thumby.display.update()

def update_starter():
    global starter_index, GAME_STATE

    update_buttons()

    if BTN_U.justPressed():
        starter_index = (starter_index - 1) % 3
    elif BTN_D.justPressed():
        starter_index = (starter_index + 1) % 3

    if BTN_A.justPressed():
        starters = [0, 1, 2]
        chosen = starters[starter_index]
        battle["player_id"] = chosen
        battle["player_hp"] = kitmen_data[chosen]["max_hp"]
        # starter is considered "owned"
        caught_flags[chosen] = 1
        caught_counts[chosen] += 1
        GAME_STATE = "overworld"

# -------------------------
# ENCOUNTERS
# -------------------------
def start_wild_encounter():
    global GAME_STATE

    battle["eviler"] = False
    battle["eviler_index"] = -1

    battle["wild_id"] = random.choice(WILD_TABLE)
    wild = kitmen_data[battle["wild_id"]]
    battle["wild_hp"] = wild["max_hp"]

    for _ in range(3):
        thumby.display.fill(1)
        thumby.display.update()
        time.sleep(0.05)
        thumby.display.fill(0)
        thumby.display.update()
        time.sleep(0.05)

    battle["menu_index"] = 0
    battle["message"] = "Wild " + wild["name"]
    battle["message_timer"] = 40
    battle["end_after"] = None

    GAME_STATE = "battle"

def start_eviler_encounter(ev_index):
    global GAME_STATE

    battle["eviler"] = True
    battle["eviler_index"] = ev_index

    # Eviler uses Eri as base but scaled
    base = kitmen_data[11]
    scale = 1 + evilers_defeated
    battle["wild_id"] = 11
    battle["wild_hp"] = base["max_hp"] + 10 * evilers_defeated

    for _ in range(3):
        thumby.display.fill(1)
        thumby.display.update()
        time.sleep(0.05)
        thumby.display.fill(0)
        thumby.display.update()
        time.sleep(0.05)

    battle["menu_index"] = 0
    battle["message"] = "Eviler Eri"
    battle["message_timer"] = 40
    battle["end_after"] = None

    GAME_STATE = "battle"

# -------------------------
# MOVEMENT
# -------------------------
def try_move(dx, dy):
    global last_encounter_time

    nx = player["x"] + dx*TILE
    ny = player["y"] + dy*TILE

    tx = nx // TILE
    ty = ny // TILE

    tile = get_tile(tx, ty)

    if tile != 0:
        player["x"] = nx
        player["y"] = ny
        player["walk_frame"] ^= 1
        player["walk_timer"] = 6

        # Eviler trigger
        ev_index = check_eviler_trigger()
        if ev_index != -1:
            start_eviler_encounter(ev_index)
            return

        # Wild encounter in tall grass
        if tile == 2:
            if time.ticks_ms() - last_encounter_time > 20000:
                if random.randint(1, 12) == 1:
                    start_wild_encounter()

def update_player():
    update_buttons()

    if BTN_U.justPressed():   try_move(0, -1)
    elif BTN_D.justPressed(): try_move(0, 1)
    elif BTN_L.justPressed(): try_move(-1, 0)
    elif BTN_R.justPressed(): try_move(1, 0)

    if BTN_B.justPressed():
        global GAME_STATE, MENU_STATE, menu_index
        GAME_STATE = "menu"
        MENU_STATE = "main"
        menu_index = 0

    if player["walk_timer"] > 0:
        player["walk_timer"] -= 1

    update_blink()
# =========================
# PART 3 — BATTLE HELPERS / LOGIC / RENDER (PATCHED)
# =========================

# -------------------------
# BATTLE HELPERS
# -------------------------
def draw_hp_bar(x, y, cur, maxhp, width=40):
    if maxhp <= 0:
        return
    if cur < 0:
        cur = 0
    ratio = cur * width // maxhp
    thumby.display.drawRectangle(x, y, width, 3, 1)
    if ratio > 2:
        thumby.display.drawFilledRectangle(x+1, y+1, ratio-2, 1, 1)

def damage(attacker, defender):
    base = attacker["atk"] - defender["def"]//2
    if base < 1:
        base = 1

    # crit
    if random.randint(1, 10) == 1:
        base *= 2

    # ±25% variation
    var = base // 4
    if var > 0:
        base = base + random.randint(-var, var)
        if base < 1:
            base = 1

    return base

def attempt_capture():
    wild = kitmen_data[battle["wild_id"]]
    hp = battle["wild_hp"]
    maxhp = wild["max_hp"]
    rate = wild["catch_rate"]

    chance = rate + (maxhp - hp) * 2
    if chance > 95:
        chance = 95

    return random.randint(1, 100) <= chance

def wild_attack():
    wild = kitmen_data[battle["wild_id"]]
    player_mon = kitmen_data[battle["player_id"]]

    if wild.get("special") == "catch_only":
        return "Too cute"

    dmg = damage(wild, player_mon)
    battle["player_hp"] -= dmg

    if battle["player_hp"] <= 0:
        battle["player_hp"] = 0
        return "You fainted"

    return "Hit you " + str(dmg)

def player_hit_wild():
    wild = kitmen_data[battle["wild_id"]]
    player_mon = kitmen_data[battle["player_id"]]

    if random.randint(1, 100) <= wild["dodge"]:
        return "Dodged!"

    dmg = damage(player_mon, wild)

    if player_mon.get("special") == "double_hit":
        dmg += damage(player_mon, wild)

    battle["wild_hp"] -= dmg

    if battle["wild_hp"] <= 0:
        battle["wild_hp"] = 0
        return "Fainted!"

    return "Hit " + str(dmg)

# -------------------------
# BATTLE LOGIC (PATCHED)
# -------------------------
def update_battle():
    update_buttons()

    # -------------------------
    # MESSAGE MODE (patched)
    # -------------------------
    if battle["message_timer"] > 0:
        # A skips message
        if BTN_A.justPressed():
            battle["message_timer"] = 0
        else:
            battle["message_timer"] -= 1

        # If timer hits 0 AND end_after exists → exit immediately
        if battle["message_timer"] == 0 and battle["end_after"]:
            f = battle["end_after"]
            battle["end_after"] = None
            f()
        return

    # -------------------------
    # HEAL (B)
    # -------------------------
    if BTN_B.justPressed():
        maxhp = kitmen_data[battle["player_id"]]["max_hp"]
        if inventory["Heals"] > 0 and battle["player_hp"] < maxhp:
            battle["player_hp"] = maxhp
            inventory["Heals"] -= 1
            battle["message"] = "Healed!"
            battle["message_timer"] = 30
        else:
            battle["message"] = "No heals"
            battle["message_timer"] = 20
        return

    # -------------------------
    # MENU NAVIGATION
    # -------------------------
    if BTN_L.justPressed():
        battle["menu_index"] = (battle["menu_index"] - 1) % 3
    elif BTN_R.justPressed():
        battle["menu_index"] = (battle["menu_index"] + 1) % 3

    # -------------------------
    # MENU ACTIONS
    # -------------------------
    if BTN_A.justPressed():
        choice = battle["menu_index"]
        wild = kitmen_data[battle["wild_id"]]
        player_mon = kitmen_data[battle["player_id"]]

        # -------------------------
        # FIGHT
        # -------------------------
        if choice == 0:
            msg = player_hit_wild()
            battle["message"] = msg
            battle["message_timer"] = 30

            if msg == "Fainted!":
                def end_after():
                    global GAME_STATE, last_encounter_time, evilers_defeated
                    GAME_STATE = "overworld"
                    last_encounter_time = time.ticks_ms()

                    if battle["eviler"] and battle["eviler_index"] >= 0:
                        evilers_defeated += 1
                        respawn_eviler_block(battle["eviler_index"])

                battle["end_after"] = end_after
                return

            # Wild counterattack
            reply = wild_attack()
            battle["message"] = reply
            battle["message_timer"] = 30

            if reply == "You fainted":
                def end_after():
                    global GAME_STATE, last_encounter_time
                    GAME_STATE = "overworld"
                    last_encounter_time = time.ticks_ms()
                    battle["player_hp"] = kitmen_data[battle["player_id"]]["max_hp"]
                battle["end_after"] = end_after

        # -------------------------
        # CATCH
        # -------------------------
        elif choice == 1:
            if battle["eviler"]:
                battle["message"] = "Can't catch"
                battle["message_timer"] = 30
                return

            if inventory["Rocks"] <= 0:
                battle["message"] = "No Rocks"
                battle["message_timer"] = 20
                return

            inventory["Rocks"] -= 1

            if attempt_capture():
                caught_flags[battle["wild_id"]] = 1
                caught_counts[battle["wild_id"]] += 1
                inventory["Rocks"] += 5
                inventory["Heals"] += 2

                battle["message"] = "Caught!"
                battle["message_timer"] = 40

                def end_after():
                    global GAME_STATE, last_encounter_time
                    GAME_STATE = "overworld"
                    last_encounter_time = time.ticks_ms()

                battle["end_after"] = end_after
                return

            # Failed catch → wild hits back
            battle["message"] = "Broke free!"
            battle["message_timer"] = 30

            reply = wild_attack()
            battle["message"] = reply
            battle["message_timer"] = 30

            if reply == "You fainted":
                def end_after():
                    global GAME_STATE, last_encounter_time
                    GAME_STATE = "overworld"
                    last_encounter_time = time.ticks_ms()
                    battle["player_hp"] = kitmen_data[battle["player_id"]]["max_hp"]
                battle["end_after"] = end_after

        # -------------------------
        # RUN
        # -------------------------
        elif choice == 2:
            if battle["eviler"]:
                battle["message"] = "Can't run!"
                battle["message_timer"] = 30
                reply = wild_attack()
                battle["message"] = reply
                battle["message_timer"] = 30

                if reply == "You fainted":
                    def end_after():
                        global GAME_STATE, last_encounter_time
                        GAME_STATE = "overworld"
                        last_encounter_time = time.ticks_ms()
                        battle["player_hp"] = kitmen_data[battle["player_id"]]["max_hp"]
                    battle["end_after"] = end_after
                return

            # Normal run
            if random.randint(1, 3) != 1:
                battle["message"] = "Escaped!"
                battle["message_timer"] = 30

                def end_after():
                    global GAME_STATE, last_encounter_time
                    GAME_STATE = "overworld"
                    last_encounter_time = time.ticks_ms()

                battle["end_after"] = end_after
                return

            # Failed run
            battle["message"] = "Can't run!"
            battle["message_timer"] = 30

            reply = wild_attack()
            battle["message"] = reply
            battle["message_timer"] = 30

            if reply == "You fainted":
                def end_after():
                    global GAME_STATE, last_encounter_time
                    GAME_STATE = "overworld"
                    last_encounter_time = time.ticks_ms()
                    battle["player_hp"] = kitmen_data[battle["player_id"]]["max_hp"]
                battle["end_after"] = end_after

# -------------------------
# BATTLE RENDER
# -------------------------
def draw_battle_menu():
    options = ["F", "C", "R"]
    base_x = 6
    spacing = 18
    y = 32

    for i, opt in enumerate(options):
        x = base_x + i * spacing
        if i == battle["menu_index"]:
            thumby.display.drawText("[" + opt + "]", x, y, 1)
        else:
            thumby.display.drawText(" " + opt + " ", x, y, 1)

def draw_battle_screen():
    thumby.display.fill(0)

    wild = kitmen_data[battle["wild_id"]]
    player_mon = kitmen_data[battle["player_id"]]

    title = "Eviler " + wild["name"] if battle["eviler"] else "Wild " + wild["name"]
    thumby.display.drawText(title, 0, 0, 1)

    maxhp = wild["max_hp"] + (10 * evilers_defeated if battle["eviler"] else 0)
    draw_hp_bar(0, 10, battle["wild_hp"], maxhp, 40)
    thumby.display.blit(wild["sprite"], 50, 2, 16, 16, 0, 0, 0)

    thumby.display.drawText(player_mon["name"], 0, 20, 1)
    draw_hp_bar(0, 30, battle["player_hp"], player_mon["max_hp"], 40)
    thumby.display.blit(player_mon["sprite"], 50, 22, 16, 16, 0, 0, 0)

    draw_battle_menu()

    if battle["message_timer"] > 0 and battle["message"]:
        thumby.display.drawFilledRectangle(0, 14, SCREEN_W, 10, 0)
        thumby.display.drawText(battle["message"], 1, 15, 1)

    thumby.display.update()

# =========================
# PART 4 — MENUS / ITEMS+SELECTION / BOOK / MAIN LOOP (PATCHED)
# =========================

# -------------------------
# ITEMS MENU (with Select Kitmen >)
# -------------------------
def draw_items_menu():
    thumby.display.fill(0)
    thumby.display.drawText("Items:", 0, 0, 1)

    y = 12
    thumby.display.drawText("Rocks: " + str(inventory["Rocks"]), 0, y, 1); y += 10
    thumby.display.drawText("Heals: " + str(inventory["Heals"]), 0, y, 1); y += 10

    thumby.display.drawText("Select Kitmen >", 0, y, 1)

    thumby.display.update()

def update_items_menu():
    global MENU_STATE

    update_buttons()

    # A = open selection menu
    if BTN_A.justPressed():
        MENU_STATE = "items_select"
        return

    # B = back
    if BTN_B.justPressed():
        MENU_STATE = "main"
        return

# -------------------------
# SELECTION MENU (3 visible, centered scroll)
# -------------------------
selection_index = 0
selection_scroll = 0
selection_mode = "list"   # "list" or "detail"

def get_selectable_ids():
    ids = []
    for i in range(KITMEN_COUNT):
        if caught_flags[i] == 1 or i == battle["player_id"]:
            ids.append(i)
    return ids

def draw_selection_list():
    thumby.display.fill(0)
    thumby.display.drawText("Select Kitmen:", 0, 0, 1)

    ids = get_selectable_ids()
    total = len(ids)

    for i in range(3):
        idx = selection_scroll + i
        if idx >= total:
            break

        kid = ids[idx]
        name = kitmen_data[kid]["name"]

        prefix = "> " if idx == selection_index else "  "
        thumby.display.drawText(prefix + name, 5, 12 + i*10, 1)

    thumby.display.update()

def draw_selection_detail():
    thumby.display.fill(0)

    ids = get_selectable_ids()
    kid = ids[selection_index]
    k = kitmen_data[kid]

    thumby.display.drawText(k["name"], 0, 0, 1)
    thumby.display.drawText("HP " + str(k["max_hp"]), 0, 10, 1)
    thumby.display.drawText("ATK " + str(k["atk"]), 0, 18, 1)
    thumby.display.drawText("DEF " + str(k["def"]), 0, 26, 1)
    thumby.display.drawText("DOD " + str(k["dodge"]), 0, 34, 1)

    thumby.display.drawText("A=Equip B=Back", 0, 40-8, 1)
    thumby.display.update()

def update_selection_menu():
    global selection_index, selection_scroll, selection_mode, MENU_STATE

    update_buttons()

    ids = get_selectable_ids()
    total = len(ids)

    if selection_mode == "list":
        # Move cursor
        if BTN_U.justPressed():
            if selection_index > 0:
                selection_index -= 1
                if selection_index < selection_scroll + 1 and selection_scroll > 0:
                    selection_scroll -= 1

        elif BTN_D.justPressed():
            if selection_index < total - 1:
                selection_index += 1
                if selection_index > selection_scroll + 1 and selection_scroll < total - 3:
                    selection_scroll += 1

        # A = open detail
        if BTN_A.justPressed():
            selection_mode = "detail"

        # B = back to items
        if BTN_B.justPressed():
            MENU_STATE = "items"
            selection_mode = "list"
            return

    else:  # detail mode
        if BTN_A.justPressed():
            chosen = ids[selection_index]
            battle["player_id"] = chosen
            battle["player_hp"] = kitmen_data[chosen]["max_hp"]
            selection_mode = "list"
            MENU_STATE = "items"
            return

        if BTN_B.justPressed():
            selection_mode = "list"
            return

# -------------------------
# BOOK MENU (Eviler now inside list)
# -------------------------
def draw_book_menu():
    thumby.display.fill(0)
    caught_total = sum(caught_counts)
    thumby.display.drawText("Kitdex " + str(caught_total) + "/" + str(KITMEN_COUNT+1), 0, 0, 1)

    # 4 visible entries
    for i in range(4):
        idx = book_scroll + i

        # Normal Kitmen entries
        if idx < KITMEN_COUNT:
            name = kitmen_data[idx]["name"]
            thumby.display.drawText(name, 10, 10 + i*8, 1)

            if caught_flags[idx] == 1:
                thumby.display.drawFilledRectangle(0, 10 + i*8, 6, 6, 1)
            else:
                thumby.display.drawRectangle(0, 10 + i*8, 6, 6, 1)

            thumby.display.drawText(str(caught_counts[idx]), 60, 10 + i*8, 1)

        # Eviler entry (after Eri)
        elif idx == KITMEN_COUNT:
            thumby.display.drawText("Eviler", 10, 10 + i*8, 1)
            thumby.display.drawText(str(evilers_defeated), 60, 10 + i*8, 1)

    thumby.display.update()

def update_book_menu():
    global book_scroll, MENU_STATE

    update_buttons()

    max_scroll = (KITMEN_COUNT + 1) - 4

    if BTN_U.justPressed():
        book_scroll = max(0, book_scroll - 1)
    elif BTN_D.justPressed():
        book_scroll = min(max_scroll, book_scroll + 1)

    if BTN_B.justPressed():
        MENU_STATE = "main"

# -------------------------
# SAVE MENU
# -------------------------
def draw_save_menu():
    thumby.display.fill(0)
    thumby.display.drawText("Saving...", 5, 10, 1)
    thumby.display.update()
    save_game()
    thumby.display.fill(0)
    thumby.display.drawText("Saved!", 15, 15, 1)
    thumby.display.drawText("A/B to exit", 5, 25, 1)
    thumby.display.update()

def update_save_menu():
    global MENU_STATE
    update_buttons()
    if BTN_A.justPressed() or BTN_B.justPressed():
        MENU_STATE = "main"

# -------------------------
# MAIN MENU
# -------------------------
def draw_main_menu():
    thumby.display.fill(0)
    options = ["Items", "Book", "Save"]
    y = 10
    for i, opt in enumerate(options):
        prefix = "> " if i == menu_index else "  "
        thumby.display.drawText(prefix + opt, 5, y, 1)
        y += 10
    thumby.display.update()

def update_main_menu():
    global menu_index, MENU_STATE, GAME_STATE

    update_buttons()

    if BTN_U.justPressed():
        menu_index = (menu_index - 1) % 3
    elif BTN_D.justPressed():
        menu_index = (menu_index + 1) % 3

    if BTN_A.justPressed():
        if menu_index == 0:
            MENU_STATE = "items"
        elif menu_index == 1:
            MENU_STATE = "book"
        elif menu_index == 2:
            MENU_STATE = "save"

    if BTN_B.justPressed():
        GAME_STATE = "overworld"
        MENU_STATE = "none"

# -------------------------
# MENU ROUTER
# -------------------------
def update_menu():
    if MENU_STATE == "main":
        update_main_menu()
    elif MENU_STATE == "items":
        update_items_menu()
    elif MENU_STATE == "items_select":
        update_selection_menu()
    elif MENU_STATE == "book":
        update_book_menu()
    elif MENU_STATE == "save":
        update_save_menu()

def draw_menu():
    if MENU_STATE == "main":
        draw_main_menu()
    elif MENU_STATE == "items":
        draw_items_menu()
    elif MENU_STATE == "items_select":
        if selection_mode == "list":
            draw_selection_list()
        else:
            draw_selection_detail()
    elif MENU_STATE == "book":
        draw_book_menu()
    elif MENU_STATE == "save":
        draw_save_menu()

# -------------------------
# MAIN LOOP
# -------------------------
def main():
    global GAME_STATE, last_encounter_time

    GAME_STATE = "intro"
    battle["player_id"] = 0
    battle["player_hp"] = kitmen_data[0]["max_hp"]
    battle["end_after"] = None
    last_encounter_time = time.ticks_ms() - 20000

    while True:
        if GAME_STATE == "intro":
            update_intro()
            draw_intro()

        elif GAME_STATE == "starter":
            update_starter()
            draw_starter()

        elif GAME_STATE == "overworld":
            update_player()
            draw_world()

        elif GAME_STATE == "battle":
            update_battle()
            draw_battle_screen()

        elif GAME_STATE == "menu":
            update_menu()
            draw_menu()

        time.sleep(0.03)

main()

