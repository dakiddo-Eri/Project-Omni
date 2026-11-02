import thumby
import sys
import ubinascii
import time
import gc

display_on = True
shares_mined = 0

# Global pre-allocated buffers to prevent heap allocation pauses and crashes
W = [0] * 80
padded = bytearray(64)

def update_display(status_text):
    if not display_on:
        return
    thumby.display.fill(0)
    thumby.display.drawText("Duino-Coin", 10, 0, 1)
    thumby.display.drawText("Verified Native", 0, 10, 1)
    thumby.display.drawText(status_text, 0, 25, 1)
    thumby.display.drawText(f"Shares:{shares_mined}", 0, 35, 1)
    thumby.display.update()

# Isolated compression engine function to bypass the native bytecode compiler size limit
@micropython.native
def sha1_compress_block(pad_buf):
    global W
    h0, h1, h2, h3, h4 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0
    
    for j in range(16):
        o = j * 4
        W[j] = (pad_buf[o] << 24) | (pad_buf[o+1] << 16) | (pad_buf[o+2] << 8) | pad_buf[o+3]
        
    for j in range(16, 80):
        x = W[j-3] ^ W[j-8] ^ W[j-14] ^ W[j-16]
        W[j] = ((x << 1) | (x >> 31)) & 0xFFFFFFFF
        
    a, b, c, d, e = h0, h1, h2, h3, h4
    
    for j in range(80):
        if j < 20:
            f = (b & c) | ((~b) & d)
            k = 0x5A827999
        elif j < 40:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif j < 60:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6
            
        temp_word = (((a << 5) | (a >> 27)) + f + e + k + W[j]) & 0xFFFFFFFF
        e = d
        d = c
        c = ((b << 30) | (b >> 2)) & 0xFFFFFFFF
        b = a
        a = temp_word
        
    return (
        ((h0 + a) & 0xFFFFFFFF).to_bytes(4, 'big') +
        ((h1 + b) & 0xFFFFFFFF).to_bytes(4, 'big') +
        ((h2 + c) & 0xFFFFFFFF).to_bytes(4, 'big') +
        ((h3 + d) & 0xFFFFFFFF).to_bytes(4, 'big') +
        ((h4 + e) & 0xFFFFFFFF).to_bytes(4, 'big')
    )

@micropython.native
def mine_duco(last_hash, exp_hash, difficulty):
    global padded
    base_bytes = last_hash.strip().encode('ascii')
    expected_hex = exp_hash.strip().lower().encode('ascii')
    max_nonce = int(difficulty.strip()) * 100 + 1
    base_len = len(base_bytes)
    
    buf = bytearray(base_bytes + b'0' * 12)
    hexlify = ubinascii.hexlify
    
    for nonce in range(max_nonce):
        temp = nonce
        idx = len(buf) - 1
        
        if temp == 0:
            buf[base_len] = 48
            current_len = base_len + 1
        else:
            while temp > 0:
                buf[idx] = 48 + (temp % 10)
                temp //= 10
                idx -= 1
            num_len = (len(buf) - 1) - idx
            start_pos = idx + 1
            buf[base_len : base_len + num_len] = buf[start_pos : start_pos + num_len]
            current_len = base_len + num_len

        # Zero out our fixed padded array safely using an explicit index range loop
        for j in range(64):
            padded[j] = 0
            
        # Copy current working text string over
        padded[0:current_len] = buf[0:current_len]
        padded[current_len] = 0x80 # Standard SHA-1 bit termination marker
        
        # Inject our calculated bit length tracking integer directly into the final block positions
        bit_len = current_len * 8
        padded[60] = (bit_len >> 24) & 0xFF
        padded[61] = (bit_len >> 16) & 0xFF
        padded[62] = (bit_len >> 8) & 0xFF
        padded[63] = bit_len & 0xFF
        
        res_bytes = sha1_compress_block(padded)
        
        if hexlify(res_bytes) == expected_hex:
            return nonce
            
    return 0

update_display("Waiting PC...")

while True:
    try:
        line = sys.stdin.readline()
        if not line:
            time.sleep_ms(10)
            continue
            
        line = line.strip()
        if line.startswith("THUMBY_SOLVE"):
            parts = line.split(",")
            if len(parts) >= 4:
                update_display("Mining...")
                
                # Explicit argument parsing positions
                nonce = mine_duco(parts[1], parts[2], parts[3])
                if nonce > 0:
                    shares_mined += 1
                
                sys.stdout.write(f"NONCE,{nonce}\n")
                sys.stdout.flush()
                
                update_display("Waiting...")
                gc.collect()
    except Exception as e:
        sys.stdout.write(f"ERROR,{e}\n")
        sys.stdout.flush()
        time.sleep_ms(100)
