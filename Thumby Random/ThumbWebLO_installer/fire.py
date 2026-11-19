import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_PATH = os.path.join(BASE_DIR, "manifest.txt")
APP_PATH = os.path.join(BASE_DIR, "ThumbWebLO.py")
SITES_DIR = os.path.join(BASE_DIR, "Sites")

DEVICE_APP_DIR = ":Games/ThumbWebLO/"
DEVICE_SITES_DIR = ":Games/ThumbWebLO/Sites/"

def run_cmd(cmd):
    print(f"> {cmd}")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"Error executing command: {cmd}")
        sys.exit(1)

def parse_manifest():
    packs = {}
    current_pack = "Default Pack"
    packs[current_pack] = []
    
    if not os.path.exists(MANIFEST_PATH):
        print(f"Error: manifest.txt not found at {MANIFEST_PATH}")
        sys.exit(1)
        
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                current_pack = line[1:-1].strip()
                if current_pack not in packs:
                    packs[current_pack] = []
            else:
                path = line.replace("\\", "/")
                packs[current_pack].append(path)
    return packs

def main():
    print("----- ThumbWebLO PC Deployer -----")
    
    try:
        subprocess.run(["mpremote", "version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: 'mpremote' is required. Install it using: pip install mpremote")
        sys.exit(1)

    packs = parse_manifest()
    
    print("\nFound packs in manifest.txt:")
    pack_names = list(packs.keys())
    for idx, name in enumerate(pack_names):
        print(f"  [{idx+1}] {name} ({len(packs[name])} files)")
        
    choice = input("\nDeploy all packs? (y/n): ").strip().lower()
    selected_files = []
    
    if choice == 'y':
        for name in pack_names:
            selected_files.extend(packs[name])
    else:
        idxs = input("Enter pack numbers to deploy separated by commas (e.g., 1,2): ").split(',')
        for i in idxs:
            try:
                idx = int(i.strip()) - 1
                if 0 <= idx < len(pack_names):
                    selected_files.extend(packs[pack_names[idx]])
            except ValueError:
                pass

    print("\nConnecting to Thumby and preparing directories...")
    for d in [":Games", ":Games/ThumbWebLO", ":Games/ThumbWebLO/Sites"]:
        subprocess.run(f"mpremote mkdir {d}", shell=True, stderr=subprocess.DEVNULL)

    if os.path.exists(APP_PATH):
        print("\nUploading ThumbWebLO browser app...")
        run_cmd(f"mpremote cp \"{APP_PATH}\" {DEVICE_APP_DIR}ThumbWebLO.py")

    print("\nUploading selected site files...")
    for rel_path in selected_files:
        local_file = os.path.join(SITES_DIR, rel_path)
        if not os.path.exists(local_file):
            print(f"Warning: Local file not found: {local_file}")
            continue
        parts = rel_path.split('/')
        if len(parts) > 1:
            sub_path = DEVICE_SITES_DIR
            for p in parts[:-1]:
                if p:
                    sub_path += p + "/"
                    subprocess.run(f"mpremote mkdir \"{sub_path.rstrip('/')}\"", shell=True, stderr=subprocess.DEVNULL)
        
        remote_dest = DEVICE_SITES_DIR + rel_path
        run_cmd(f"mpremote cp \"{local_file}\" \"{remote_dest}\"")

    print("\n✨ Deployment complete! Made by Eri, pls donate idk its Christmas (at time of writing this)")

if __name__ == "__main__":
    main()