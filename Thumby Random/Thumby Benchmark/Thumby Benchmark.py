# ============================================================
#  ThumbyBenchmark.py  --  Original Thumby Performance Suite
#  Target  : Original Thumby (RP2040, 72x40 mono OLED)
#  Runtime : ~5 minutes  |  Dual-core  |  Version 5.3 (polished)
#
#  CRASH-RESISTANCE DESIGN
#  ========================
#  Every phase is wrapped in try/except so one bad phase
#  never kills the whole benchmark -- it records 0 and moves on.
#
#  The memory/GC phase has been replaced with a pure GC timing
#  test: it calls gc.collect() in a tight loop and counts how
#  many GC cycles complete per second. This allocates NOTHING
#  inside the hot loop, making it impossible to OOM.
#
#  machine.freq() returns None on Thumby firmware, so it is
#  never called. CPU speed is hardcoded as CPU_MHZ = 125.
#
#  All integer counters that could grow beyond 255 in inner
#  loops have been eliminated. All display text is pre-checked
#  to fit within 72 pixels (12 chars x 6px/char).
#
#  FIXES IN v5.3
#  ==============
#  1. thumbyAudio.audio.play() corrected API path
#  2. safe() error handler case-matched to actual phase names
#  3. _thread launch wrapped for core1-in-use resilience
#  4. gc.collect() between every phase to prevent OOM
#  5. Fanfare audio wrapped to prevent crash before results
#  6. Animated workbench splash screen added
#  7. Removed overlapping nav text from results page
#  8. Controls text repositioned above bench animation
#  9. Smooth 20-second looping melody on splash screen
#
#  HOW TO USE
#  Upload to /Games/ThumbyBenchmark/ThumbyBenchmark.py
#  Press A on the ready screen to begin.
# ============================================================

import thumbyGraphics
import thumbyButton
import thumbyAudio
import utime
import math
import gc

# machine.freq() returns None on Thumby -- never call it.
CPU_MHZ = 125

# -- Display shorthand --
d    = thumbyGraphics.display
W, H = 72, 40

# -- Timing constants --
TOTAL_MS   = 5 * 60 * 1000
NUM_PHASES = 7
PHASE_MS   = TOTAL_MS // NUM_PHASES  # ~42 857 ms each

PHASE_NAMES = [
    "INT MATH",
    "FLOAT MATH",
    "FPS DRAW",
    "PIXEL FILL",
    "TEXT RENDER",
    "SHAPES",
    "GC TIMING",
]

# -- Run-varied seed (changes every run) --
_SEED = utime.ticks_us() & 0xFFFF

# -- Dual-core shared memory --
# Layout (little-endian uint32 at each 4-byte slot):
#   byte  0 : run flag  -- Core 0 sets 1 before launch, 0 to stop
#   byte  1 : done flag -- Core 1 sets 1 when finished
#   bytes 4-7  : Core 1 integer ops count
#   bytes 8-11 : Core 1 float   ops count
#  bytes 12-15 : Core 1 integer elapsed ms
#  bytes 16-19 : Core 1 float   elapsed ms
_shared = bytearray(20)


def _pack32(buf, offset, value):
    v = int(value) & 0xFFFFFFFF
    buf[offset]     =  v        & 0xFF
    buf[offset + 1] = (v >>  8) & 0xFF
    buf[offset + 2] = (v >> 16) & 0xFF
    buf[offset + 3] = (v >> 24) & 0xFF


def _unpack32(buf, offset):
    return (buf[offset]
            | (buf[offset + 1] <<  8)
            | (buf[offset + 2] << 16)
            | (buf[offset + 3] << 24))


# ============================================================
#  CORE 1 WORKER -- never touches display or any Thumby API
# ============================================================
def _core1_worker(shared, seed):
    half_ms = TOTAL_MS // 2

    # -- Integer math --
    int_ops = 0
    a = (seed ^ 0xBEEF) & 0xFFFF
    b = (seed & 0x0F) | 1
    t0 = utime.ticks_ms()
    dl = utime.ticks_add(t0, half_ms)

    while shared[0] == 1 and utime.ticks_diff(dl, utime.ticks_ms()) > 0:
        a = (a + b) & 0xFF
        a = (a ^ b) & 0xFF
        a = (a | b) & 0xFF
        a = (a & b) & 0xFF
        b = (b + 1) & 0x0F
        b = b | 1
        int_ops += 6

    int_ms = utime.ticks_diff(utime.ticks_ms(), t0)

    # -- Float math --
    flt_ops = 0
    fx = float((seed & 0xFF) or 1) * 0.01 + 1.0
    t0 = utime.ticks_ms()
    dl = utime.ticks_add(t0, half_ms)

    while shared[0] == 1 and utime.ticks_diff(dl, utime.ticks_ms()) > 0:
        fx = fx + 0.001
        fx = fx * 1.0001
        fx = fx / 1.0001
        fx = math.sin(fx) + math.cos(fx)
        fx = math.sqrt(abs(fx) + 0.001)
        fx = fx ** 1.5
        fx = math.log(abs(fx) + 0.001)
        fx = math.exp(min(fx, 5.0))
        fx = math.atan2(fx, 1.0)
        if fx > 1e6 or fx < -1e6 or fx != fx:
            fx = 1.0
        flt_ops += 9

    flt_ms = utime.ticks_diff(utime.ticks_ms(), t0)

    _pack32(shared,  4, int_ops)
    _pack32(shared,  8, flt_ops)
    _pack32(shared, 12, int_ms)
    _pack32(shared, 16, flt_ms)
    shared[1] = 1


# ============================================================
#  UI HELPERS
# ============================================================

def _c1():
    return "C1:RUN" if _shared[1] == 0 else "C1:DONE"


def _bar(elapsed_ms, total_ms):
    filled = int(70 * min(elapsed_ms, total_ms) // total_ms)
    d.drawLine(1, 33, 70, 33, 1)
    if filled > 0:
        d.drawLine(1, 33, 1 + filled, 33, 1)


def show_splash():
    # Smooth looping melody (~20s). (freq_hz, duration_in_frames)
    # C major pentatonic: C4=262 D4=294 E4=330 G4=392 A4=440 C5=523 D5=587
    # 0 freq = rest.  Each frame = ~80ms.  Total = 250 frames = 20s.
    melody = [
        (262, 6), (330, 6), (392, 6), (440, 8), (0, 3),
        (392, 5), (330, 5), (262, 8), (0, 3),
        (294, 5), (392, 5), (440, 6), (523, 8), (0, 3),
        (440, 5), (392, 5), (330, 8), (0, 3),
        (392, 5), (523, 6), (587, 6), (523, 8), (0, 3),
        (440, 5), (392, 6), (330, 5), (262, 8), (0, 3),
        (330, 6), (392, 6), (440, 8), (0, 3),
        (523, 6), (440, 5), (392, 6), (330, 8), (0, 3),
        (294, 5), (330, 6), (392, 8), (0, 3),
        (330, 5), (294, 5), (262, 10), (0, 4),
    ]
    mel_len = len(melody)
    note_idx = 0
    note_rem = melody[0][1]
    frame = 0
    while True:
        d.fill(0)

        # -- Workbench surface (double thick) --
        d.drawLine(4, 27, 67, 27, 1)
        d.drawLine(4, 28, 67, 28, 1)
        # Left leg
        d.drawLine(8, 29, 8, 39, 1)
        d.drawLine(9, 29, 9, 39, 1)
        # Right leg
        d.drawLine(62, 29, 62, 39, 1)
        d.drawLine(63, 29, 63, 39, 1)
        # Cross brace
        d.drawLine(9, 34, 62, 34, 1)

        # -- Workpiece on bench --
        d.drawFilledRectangle(30, 24, 12, 3, 1)

        # -- Hammer animation (16-frame cycle) --
        cyc = frame % 16
        if cyc < 8:
            hy = 15 + cyc
        else:
            hy = 23 - (cyc - 8)

        # Hammer head
        d.drawFilledRectangle(33, hy - 2, 6, 3, 1)
        # Handle (angled)
        d.drawLine(39, hy - 1, 45, hy - 7, 1)
        d.drawLine(39, hy, 45, hy - 6, 1)

        # -- Sparks on impact --
        if cyc > 5 and cyc < 10:
            sp = frame % 7
            sdx = [-4, -2, 3, 5, -5, 2, 6]
            sdy = [-1, -3, -2, -1, -3, -4, -2]
            for i in range(3):
                sx = 36 + sdx[(i + sp) % 7]
                sy = 23 + sdy[(i + sp) % 7]
                if 0 <= sx < W and 0 <= sy < H:
                    d.setPixel(sx, sy, 1)

        # -- Title text --
        d.drawText("THUMBY", 18, 0, 1)
        d.drawText("BENCHMARK", 9, 9, 1)

        # -- Controls (above bench, no overlap) --
        d.drawText("A=GO  B=NO", 6, 17, 1)

        d.update()
        frame += 1

        # Check buttons before delay
        if thumbyButton.buttonA.justPressed():
            try:
                thumbyAudio.audio.stop()
            except Exception:
                pass
            return True
        if thumbyButton.buttonB.justPressed():
            try:
                thumbyAudio.audio.stop()
            except Exception:
                pass
            return False

        # Play melody note (non-blocking PWM tone)
        freq = melody[note_idx][0]
        if freq > 0:
            thumbyAudio.audio.play(freq, 85)
        utime.sleep_ms(80)

        # Advance melody
        note_rem -= 1
        if note_rem <= 0:
            note_idx = (note_idx + 1) % mel_len
            note_rem = melody[note_idx][1]


def check_power():
    d.fill(0)
    d.drawText("READY?",      0, 0,  1)
    d.drawText("125MHz",      0, 10, 1)
    d.drawText("DUAL CORE",   0, 20, 1)
    d.drawText("A=YES  B=NO", 0, 30, 1)
    d.update()
    while True:
        utime.sleep_ms(80)
        if thumbyButton.buttonA.justPressed():
            return True
        if thumbyButton.buttonB.justPressed():
            return False


def countdown():
    for i in (3, 2, 1):
        d.fill(0)
        d.drawText("STARTING", 0, 8,  1)
        d.drawText("IN " + str(i), 0, 20, 1)
        d.update()
        utime.sleep_ms(1000)


def phase_card(num, name):
    d.fill(0)
    d.drawText("PHASE " + str(num) + "/" + str(NUM_PHASES), 0, 0,  1)
    d.drawText(name,      0, 12, 1)
    d.drawText(_c1(),     0, 24, 1)
    d.update()
    utime.sleep_ms(1200)


def show_results(pages):
    idx   = 0
    total = len(pages)
    while True:
        title, lines = pages[idx]
        d.fill(0)
        d.drawText(title, 0, 0, 1)
        d.drawLine(0, 9, 71, 9, 1)
        for i in range(len(lines)):
            d.drawText(lines[i], 0, 11 + i * 10, 1)
        d.update()
        utime.sleep_ms(120)
        a = thumbyButton.buttonA.justPressed()
        b = thumbyButton.buttonB.justPressed()
        if a and b:
            break
        if a:
            idx = (idx + 1) % total
            utime.sleep_ms(150)
        elif b:
            idx = (idx - 1) % total
            utime.sleep_ms(150)


# ============================================================
#  PHASE FUNCTIONS
#  Each returns (score_value, elapsed_s).
#  All wrapped in try/except in main() -- a crash returns (0, 1).
# ============================================================

def bench_integer_math(duration_ms, seed):
    ops  = 0
    a = seed & 0xFF
    b = (seed >> 4) & 0x0F
    b = b | 1

    start    = utime.ticks_ms()
    deadline = utime.ticks_add(start, duration_ms)

    while utime.ticks_diff(deadline, utime.ticks_ms()) > 0:
        a = (a + b) & 0xFF
        a = (a ^ b) & 0xFF
        a = (a | b) & 0xFF
        a = (a & b) | 1
        a = (a << 1) & 0xFF
        a = (a >> 1) & 0xFF
        a = a % 97
        b = (b + 1) & 0x0F
        b = b | 1
        ops += 9

        if ops % 90000 == 0:
            elapsed = utime.ticks_diff(utime.ticks_ms(), start)
            d.fill(0)
            d.drawText("INT MATH", 0, 0,  1)
            d.drawText(str(ops // 1000) + "K ops", 0, 12, 1)
            d.drawText(_c1(), 0, 24, 1)
            _bar(elapsed, duration_ms)
            d.update()

    elapsed_s = utime.ticks_diff(utime.ticks_ms(), start) / 1000.0
    return ops, elapsed_s


def bench_float_math(duration_ms, seed):
    ops  = 0
    x    = float((seed & 0xFF) or 1) * 0.01 + 0.5

    start    = utime.ticks_ms()
    deadline = utime.ticks_add(start, duration_ms)

    while utime.ticks_diff(deadline, utime.ticks_ms()) > 0:
        x = x + 0.001
        x = x * 1.0001
        x = x / 1.0001
        x = math.sin(x) + math.cos(x)
        x = math.sqrt(abs(x) + 0.001)
        x = x ** 1.5
        x = math.log(abs(x) + 0.001)
        x = math.exp(min(x, 5.0))
        x = math.atan2(x, 1.0)
        if x > 1e6 or x < -1e6 or x != x:
            x = 1.0
        ops += 9

        if ops % 9000 == 0:
            elapsed = utime.ticks_diff(utime.ticks_ms(), start)
            d.fill(0)
            d.drawText("FLOAT C0", 0, 0,  1)
            d.drawText(str(ops // 1000) + "K ops", 0, 12, 1)
            d.drawText(_c1(), 0, 24, 1)
            _bar(elapsed, duration_ms)
            d.update()

    elapsed_s = utime.ticks_diff(utime.ticks_ms(), start) / 1000.0
    return ops, elapsed_s


def bench_fps(duration_ms):
    frames   = 0
    bx, by   = 0, 0
    dx, dy   = 1, 1

    start    = utime.ticks_ms()
    deadline = utime.ticks_add(start, duration_ms)

    while utime.ticks_diff(deadline, utime.ticks_ms()) > 0:
        d.fill(0)
        bx = (bx + dx) % W
        by = (by + dy) % H
        if bx == 0 or bx == W - 1:
            dx = -dx
        if by == 0 or by == H - 1:
            dy = -dy
        d.drawFilledRectangle(bx, by, 4, 4, 1)
        for px in range(0, W, 4):
            py = int(8 + math.sin(px * 0.2 + frames * 0.05) * 6)
            if 0 <= py < H:
                d.setPixel(px, py, 1)
        d.drawText(str(frames % 1000), 0, H - 8, 1)
        d.update()
        frames += 1

    elapsed_s = utime.ticks_diff(utime.ticks_ms(), start) / 1000.0
    fps = frames / elapsed_s if elapsed_s > 0.0 else 0.0
    return frames, elapsed_s, fps


def bench_pixel_fill(duration_ms):
    passes   = 0
    color    = 1

    start    = utime.ticks_ms()
    deadline = utime.ticks_add(start, duration_ms)

    while utime.ticks_diff(deadline, utime.ticks_ms()) > 0:
        py = 0
        while py < H:
            px = 0
            while px < W:
                d.setPixel(px, py, color)
                px += 1
            py += 1
        d.update()
        color = color ^ 1
        passes += 1

        if passes % 5 == 0:
            elapsed = utime.ticks_diff(utime.ticks_ms(), start)
            d.fill(0)
            d.drawText("PIX FILL", 0, 0,  1)
            d.drawText(str(passes) + " pass", 0, 12, 1)
            _bar(elapsed, duration_ms)
            d.update()

    elapsed_s = utime.ticks_diff(utime.ticks_ms(), start) / 1000.0
    return passes, elapsed_s


def bench_text_render(duration_ms):
    cycles   = 0
    labels   = ["THUMBY", "BENCH", "DUAL CORE", "CYCLE:"]

    start    = utime.ticks_ms()
    deadline = utime.ticks_add(start, duration_ms)

    while utime.ticks_diff(deadline, utime.ticks_ms()) > 0:
        d.fill(0)
        d.drawText(labels[0], 0, 0,  1)
        d.drawText(labels[1], 0, 10, 1)
        d.drawText(labels[2], 0, 20, 1)
        d.drawText(str(cycles % 1000), 0, 30, 1)
        d.update()
        cycles += 1

    elapsed_s = utime.ticks_diff(utime.ticks_ms(), start) / 1000.0
    return cycles, elapsed_s


def bench_shapes(duration_ms, seed):
    frames = 0
    phase  = seed & 0x3F

    start    = utime.ticks_ms()
    deadline = utime.ticks_add(start, duration_ms)

    while utime.ticks_diff(deadline, utime.ticks_ms()) > 0:
        d.fill(0)

        cx = (frames + phase) % W
        cy = (frames + phase) % H
        d.drawLine(0, 0, cx, cy, 1)
        d.drawLine(W - 1, 0, W - 1 - cx, cy, 1)

        pulse = frames % 10
        rx = pulse * 3
        ry = pulse * 2
        rw = W - rx * 2
        rh = H - ry * 2
        if rw >= 2 and rh >= 2:
            d.drawFilledRectangle(rx, ry, rw, rh, 1)
            if rw >= 6 and rh >= 6:
                d.drawFilledRectangle(rx + 2, ry + 2, rw - 4, rh - 4, 0)

        ew = ((frames * 3) % (W - 4)) + 4
        eh = ((frames * 2) % (H - 4)) + 4
        d.drawRectangle((W - ew) // 2, (H - eh) // 2, ew, eh, 1)

        d.update()
        frames += 1

        if frames % 40 == 0:
            elapsed = utime.ticks_diff(utime.ticks_ms(), start)
            d.fill(0)
            d.drawText("SHAPES", 0, 0,  1)
            d.drawText(_c1(), 0, 12, 1)
            _bar(elapsed, duration_ms)
            d.update()

    elapsed_s = utime.ticks_diff(utime.ticks_ms(), start) / 1000.0
    fps = frames / elapsed_s if elapsed_s > 0.0 else 0.0
    return frames, elapsed_s, fps


def bench_gc(duration_ms):
    gc_calls = 0

    d.fill(0)
    d.drawText("GC TIMING", 0, 0,  1)
    d.drawText("RUNNING...", 0, 12, 1)
    d.drawText(_c1(), 0, 24, 1)
    d.update()

    start    = utime.ticks_ms()
    deadline = utime.ticks_add(start, duration_ms)

    while utime.ticks_diff(deadline, utime.ticks_ms()) > 0:
        gc.collect()
        gc_calls += 1

    elapsed_ms = utime.ticks_diff(utime.ticks_ms(), start)
    elapsed_s  = elapsed_ms / 1000.0

    gc.collect()
    return gc_calls, elapsed_s


# ============================================================
#  MAIN
# ============================================================
def main():
    import _thread

    # -- Splash --
    if not show_splash():
        return

    # -- Ready check --
    if not check_power():
        d.fill(0)
        d.drawText("CANCELLED", 0, 16, 1)
        d.update()
        return

    countdown()

    # -- Launch Core 1 --
    _shared[0] = 1
    _shared[1] = 0
    # FIX #3: Wrap thread launch -- handles "core1 in use" from prior crash
    try:
        _thread.start_new_thread(_core1_worker, (_shared, _SEED))
    except Exception:
        _shared[0] = 0
        _shared[1] = 1  # mark done so _c1() shows C1:DONE
    utime.sleep_ms(50)

    run_start = utime.ticks_ms()

    # -- Helper: safely run a phase --
    def safe(fn, args, name):
        try:
            return fn(*args)
        except Exception:
            d.fill(0)
            d.drawText("ERR:" + name, 0, 16, 1)
            d.update()
            utime.sleep_ms(800)
            # FIX #2: Match actual name strings passed by callers
            return (0, 0, 0.0) if name in ("FPS", "SHP") else (0, 1.0)

    # -- Phase 1: Integer Math --
    gc.collect()  # FIX #4
    phase_card(1, PHASE_NAMES[0])
    r1 = safe(bench_integer_math, (PHASE_MS, _SEED), "INT")
    int_ops, int_s = r1[0], r1[1]
    int_per_s = int(int_ops / int_s) if int_s > 0.0 else 0

    # -- Phase 2: Float Math --
    gc.collect()
    phase_card(2, PHASE_NAMES[1])
    r2 = safe(bench_float_math, (PHASE_MS, _SEED), "FLT")
    flt_ops, flt_s = r2[0], r2[1]
    flt_per_s = int(flt_ops / flt_s) if flt_s > 0.0 else 0

    # -- Phase 3: FPS Draw --
    gc.collect()
    phase_card(3, PHASE_NAMES[2])
    r3 = safe(bench_fps, (PHASE_MS,), "FPS")
    frames, fps_s, fps_val = r3[0], r3[1], r3[2]

    # -- Phase 4: Pixel Fill --
    gc.collect()
    phase_card(4, PHASE_NAMES[3])
    r4 = safe(bench_pixel_fill, (PHASE_MS,), "PIX")
    fill_p, fill_s = r4[0], r4[1]
    px_per_s = int(fill_p * W * H / fill_s) if fill_s > 0.0 else 0

    # -- Phase 5: Text Render --
    gc.collect()
    phase_card(5, PHASE_NAMES[4])
    r5 = safe(bench_text_render, (PHASE_MS,), "TXT")
    txt_cyc, txt_s = r5[0], r5[1]
    txt_per_s = int(txt_cyc / txt_s) if txt_s > 0.0 else 0

    # -- Phase 6: Shapes --
    gc.collect()
    phase_card(6, PHASE_NAMES[5])
    r6 = safe(bench_shapes, (PHASE_MS, _SEED), "SHP")
    sh_frm, sh_s, sh_fps = r6[0], r6[1], r6[2]

    # -- Stop Core 1 BEFORE GC phase --
    _shared[0] = 0
    ws = utime.ticks_ms()
    while _shared[1] == 0:
        if utime.ticks_diff(utime.ticks_ms(), ws) > 3000:
            break
        utime.sleep_ms(5)

    # Unpack Core 1 results
    c1_int_ops = _unpack32(_shared,  4)
    c1_flt_ops = _unpack32(_shared,  8)
    c1_int_ms  = _unpack32(_shared, 12)
    c1_flt_ms  = _unpack32(_shared, 16)

    c1_int_s   = c1_int_ms / 1000.0
    c1_flt_s   = c1_flt_ms / 1000.0
    c1_int_ps  = int(c1_int_ops / c1_int_s) if c1_int_s > 0.0 else 0
    c1_flt_ps  = int(c1_flt_ops / c1_flt_s) if c1_flt_s > 0.0 else 0

    gc.collect()

    # -- Phase 7: GC Timing (Core 1 stopped) --
    phase_card(7, PHASE_NAMES[6])
    r7 = safe(bench_gc, (PHASE_MS,), "GC")
    gc_calls, gc_s = r7[0], r7[1]
    gc_per_s = int(gc_calls / gc_s) if gc_s > 0.0 else 0

    total_s = utime.ticks_diff(utime.ticks_ms(), run_start) / 1000.0

    # -- Scoring --
    S_INT   = int_per_s   // 4000
    S_FLT   = flt_per_s   // 80
    S_FPS   = int(fps_val) * 5
    S_PIX   = px_per_s    // 4000
    S_TXT   = txt_per_s   * 3
    S_SHP   = int(sh_fps)  * 5
    S_GC    = gc_per_s    // 5
    S_C1INT = c1_int_ps   // 4000
    S_C1FLT = c1_flt_ps   // 80
    TOTAL   = (S_INT + S_FLT + S_FPS + S_PIX + S_TXT
             + S_SHP + S_GC + S_C1INT + S_C1FLT)

    # -- Fanfare (FIX #5: wrapped to protect results display) --
    try:
        for freq in (523, 659, 784, 1047):
            thumbyAudio.audio.play(freq, 120)  # FIX #1: correct API path
            utime.sleep_ms(140)
    except Exception:
        pass

    # -- Results pages --
    pages = [
        ("SUMMARY", [
            "SCR:" + str(TOTAL),
            str(int(total_s)) + "s",
            str(CPU_MHZ) + "MHz 2CORE",
        ]),
        ("C0:INT", [
            str(int_ops // 1000) + "K ops",
            str(int_per_s) + "/s",
            "Scr:" + str(S_INT),
        ]),
        ("C0:FLOAT", [
            str(flt_ops // 1000) + "K ops",
            str(flt_per_s) + "/s",
            "Scr:" + str(S_FLT),
        ]),
        ("C0:FPS", [
            str(frames) + " frm",
            str(int(fps_val * 10) // 10) + " FPS",
            "Scr:" + str(S_FPS),
        ]),
        ("C0:PIX", [
            str(fill_p) + " pass",
            str(px_per_s) + " px/s",
            "Scr:" + str(S_PIX),
        ]),
        ("C0:TEXT", [
            str(txt_cyc) + " cyc",
            str(txt_per_s) + "/s",
            "Scr:" + str(S_TXT),
        ]),
        ("C0:SHAPES", [
            str(sh_frm) + " frm",
            str(int(sh_fps)) + " FPS",
            "Scr:" + str(S_SHP),
        ]),
        ("GC TIMING", [
            str(gc_calls) + " calls",
            str(gc_per_s) + "/s",
            "Scr:" + str(S_GC),
        ]),
        ("C1:INT", [
            str(c1_int_ops // 1000) + "K ops",
            str(c1_int_ps) + "/s",
            "Scr:" + str(S_C1INT),
        ]),
        ("C1:FLOAT", [
            str(c1_flt_ops // 1000) + "K ops",
            str(c1_flt_ps) + "/s",
            "Scr:" + str(S_C1FLT),
        ]),
    ]

    show_results(pages)

    # -- Done screen --
    d.fill(0)
    d.drawText("DONE!", 0, 16, 1)
    d.update()


# ============================================================
#  ENTRY POINT
# ============================================================
main()