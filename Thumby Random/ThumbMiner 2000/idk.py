import json
import socket
import time
import serial
import urllib.request

print("=== Duino-Coin Thumby Coprocessor Launcher ===")
USERNAME = input("Enter your Duino-Coin username: ").strip()
MINING_PIN = input("Enter your Mining PIN (Leave blank if none): ").strip()

PORT = "/dev/cu.usbmodem14701"
BAUD = 115200
POOL_URL = "https://server.duinocoin.com/getPool"
FALLBACK_POOL_HOST = "server.duinocoin.com"
FALLBACK_POOL_PORT = 2811


def get_pool_endpoint():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*",
        "Connection": "close",
    }
    try:
        request = urllib.request.Request(POOL_URL, headers=headers)
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read().decode("utf-8").strip()

        data = json.loads(body)
        host = data.get("ip") or data.get("host") or data.get("server")
        port = data.get("port") or data.get("pool_port")
        if host and port:
            print(f"Resolved pool endpoint: {host}:{port}")
            return host, int(port)
    except Exception as exc:
        print(f"Pool lookup failed ({exc}); using fallback pool.")

    return FALLBACK_POOL_HOST, FALLBACK_POOL_PORT


def connect_to_thumby(port, baud):
    first_attempt = True
    while True:
        try:
            device = serial.Serial(port, baud, timeout=25)
            # Give Thumby exactly 2 seconds to boot up completely
            time.sleep(2) 
            device.reset_input_buffer()
            device.reset_output_buffer()
            print("\n[+] Successfully hooked Thumby serial port!")
            return device
        except (serial.SerialException, OSError):
            if first_attempt:
                print(f"[{time.strftime('%H:%M:%S')}] Thumby disconnected or off. Polling silently...")
                first_attempt = False
            time.sleep(2)



def connect_to_pool(host, port):
    while True:
        try:
            print(f"Connecting to pool server {host}:{port}...")
            s = socket.socket()
            s.settimeout(25)
            s.connect((host, port))
            server_ver = s.recv(100).decode("utf-8", errors="ignore").strip()
            print(f"Handshake successful! Pool Version: {server_ver}")
            return s
        except Exception as e:
            print(f"Network Connection Error: {e}. Retrying in 3 seconds...")
            time.sleep(3)


def solve_on_thumby(device, last_hash, exp_hash, difficulty):
    device.timeout = 15  # Tight timeout because chunks are small
    
    # Calculate the total limit the pool allows
    max_nonce = int(difficulty) * 100 + 500
    chunk_size = 150
    start_nonce = 0
    
    start_time = time.time()
    
    while start_nonce < max_nonce:
        end_nonce = start_nonce + chunk_size
        device.reset_input_buffer()
        
        # Send targeted chunk range across the serial line
        job_payload = f"THUMBY_SOLVE,{last_hash.strip()},{exp_hash.strip()},{start_nonce},{end_nonce}\n".encode("utf-8")
        device.write(job_payload)
        device.flush()
        
        raw_result = device.readline().decode("utf-8", errors="ignore").strip()
        
        if "NONCE" in raw_result:
            parts = raw_result.split(",")
            if len(parts) >= 2:
                ans = int(parts[1])
                if ans != -1: # Valid solution found!
                    elapsed_time = time.time() - start_time
                    hashrate = ans / elapsed_time if (elapsed_time > 0 and ans > 0) else 15.0
                    return ans, hashrate, elapsed_time
                    
        start_nonce += chunk_size
        
    # Fallback if no solution found in the entire space
    return 0, 15.0, time.time() - start_time



    if raw_result.startswith("ERROR"):
        raise RuntimeError(f"Thumby exception: {raw_result}")

    if "NONCE" in raw_result:
        parts = raw_result.split(",")
        if len(parts) >= 2 and parts[1].isdigit():
            nonce = int(parts[1])
            hashrate = nonce / elapsed_time if (elapsed_time > 0 and nonce > 0) else 100.0
            return nonce, hashrate, elapsed_time

    raise RuntimeError(f"Unexpected output from Thumby: '{raw_result}'")


# --- INITIALIZE CONNECTIONS ---
device = connect_to_thumby(PORT, BAUD)
POOL_HOST, POOL_PORT = get_pool_endpoint()
server = connect_to_pool(POOL_HOST, POOL_PORT)

shares_count = 0

# --- MAIN MINING LOOP ---
while True:
    try:
        server.sendall(f"JOB,{USERNAME},AVR\n".encode("utf-8"))
        job_data = server.recv(1024).decode("utf-8", errors="ignore").strip()
        job = job_data.split(",")

        if len(job) >= 3:
            last_hash, expected_hash, difficulty = job[0], job[1], job[2]

            if not difficulty.isdigit():
                time.sleep(1)
                continue

            # Compute on Thumby (Handles potential serial drops inside)
            try:
                nonce, hashrate, duration = solve_on_thumby(device, last_hash, expected_hash, difficulty)
            except (serial.SerialException, OSError):
                print(f"\n[{time.strftime('%H:%M:%S')}] Thumby serial connection lost.")
                try:
                    device.close()
                except:
                    pass
                device = connect_to_thumby(PORT, BAUD)
                continue

            # Submit share to pool
            pin_string = f",{MINING_PIN}" if MINING_PIN else ""
            submit_payload = f"{nonce},{hashrate:.2f},Thumby MicroPython,Thumby{pin_string}\n"
            server.sendall(submit_payload.encode("utf-8"))

            feedback = server.recv(1024).decode("utf-8", errors="ignore").strip()
            shares_count += 1
            
            print(f"[{time.strftime('%H:%M:%S')}] Share #{shares_count} | Status: {feedback} | Nonce: {nonce} | Speed: {hashrate:.2f} H/s | Time: {duration:.2f}s")

    except KeyboardInterrupt:
        print("\nShutting down bridge cleanly.")
        break
    except RuntimeError as e:
        print(f"[{time.strftime('%H:%M:%S')}] Job skipped ({e}). Requesting next job...")
        time.sleep(0.5)
    except Exception as e:
        # Strict network socket errors only
        print(f"\n[!] Network Error: {e}")
        print("Re-establishing pool socket...")
        time.sleep (3)
        try:
            server.close()
        except:
            pass
        server = connect_to_pool(POOL_HOST, POOL_PORT)

try:
    device.close()
    server.close()
except:
    pass