import serial
import time
import glob
import requests
from bs4 import BeautifulSoup
import textwrap
import re
from urllib.parse import urljoin

MANUAL_PORT = '/dev/cu.usbmodem14301' #!!!put your port here!!!
BAUD_RATE = 115200

def find_thumby_port():
    ports = glob.glob('/dev/cu.usbmodem*')
    return ports[0] if ports else MANUAL_PORT

def process_search(query):
    """Fetches search engine results formatted strictly as lightweight text structures."""
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        titles = soup.find_all('a', class_='result__url', limit=5)
        snippets = soup.find_all('a', class_='result__snippet', limit=5)
        
        out = [
            "T:=== RESULTS ===",
            "T:-------------"
        ]
        
        for i in range(min(len(titles), len(snippets))):
            raw_title = titles[i].get_text(strip=True)[:24]
            desc = snippets[i].get_text(strip=True)[:45]
            
            link = titles[i].get('href', '')
            if "uddg=" in link:
                link = link.split('uddg=')[1].split('&')[0]
                link = requests.utils.unquote(link)
                
            out.append(f"T:🔗 {raw_title}")
            out.append(f"L:{link}") # Associate link with title line
            
            for line in textwrap.wrap(desc, width=12):
                out.append(f"T:{line}")
            out.append("T:-------------")
            
        return out
    except Exception as e:
        return [f"T:Search Error", f"T:{str(e)[:12]}"]

def process_webpage(url):
    """Scrapes raw web page text and nested hyperlinks sequentially."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for junk in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form', 'button', 'svg', 'img', 'iframe']):
            junk.decompose()
            
        out = ["T:BROWSER"]
        
        line_count = 0
        max_lines = 150
        
        body = soup.body if soup.body else soup
        
        for element in body.find_all(['p', 'h1', 'h2', 'h3', 'a']):
            if line_count >= max_lines:
                break
                
            text = element.get_text(strip=True)
            if not text or len(text) < 2:
                continue
                
            if element.name == 'a':
                href = element.get('href', '')
                if href:
                    resolved_url = urljoin(url, href)
                    if resolved_url.startswith('http'):
                        wrapped = textwrap.wrap(f"LNK:{text}", width=12)
                        for w_line in wrapped:
                            out.append(f"T:{w_line}")
                            out.append(f"L:{resolved_url}") # Map link data
                            line_count += 1
            else:
                wrapped = textwrap.wrap(text, width=12)
                for w_line in wrapped:
                    out.append(f"T:{w_line}")
                    line_count += 1
                    
        if len(out) <= 1:
            out.append("T:No text found.")
            
        return out[:max_lines]
    except Exception as e:
        return [f"T:Web Error", f"T:{str(e)[:12]}"]

#bridge
ser = None
while True:
    if ser is None:
        target_port = find_thumby_port()
        print(f"🔌 Listening for Thumby text terminal on {target_port}...")
        try:
            ser = serial.Serial(target_port, BAUD_RATE, timeout=0.1)
            print("✅ Web Link Established!")
        except Exception:
            time.sleep(1)
            continue

    try:
        if ser.in_waiting > 0:
            raw_req = ser.readline().decode('utf-8', errors='ignore').strip()
            if raw_req:
                print(f"📡 Request Received: {raw_req}")
                
                payload_lines = []
                if raw_req.startswith("SEARCH:"):
                    payload_lines = process_search(raw_req[7:])
                elif raw_req.startswith("GET:"):
                    payload_lines = process_webpage(raw_req[4:])
                
                if payload_lines:
                    ser.write(b"RESET\n")
                    time.sleep(0.01)
                    
                    for payload_line in payload_lines:
                        ser.write((payload_line + "\n").encode('utf-8'))
                        time.sleep(0.01)
                    print("✅ Page updated.")
                    
    except (serial.SerialException, OSError):
        print("❌ Interface dropped. Reconnecting...")
        if ser:
            try: ser.close()
            except: pass
        ser = None
        time.sleep(1)