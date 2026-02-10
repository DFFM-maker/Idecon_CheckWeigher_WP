#!/usr/bin/env python3
import socket
import time
import sys

IDEON_IP = '172.16.224.210'
IDEON_PORT = 50000

def create_cmd(cmd):
    return b'\x02' + cmd.encode('ascii') + b'\x03'

def parse(data):
    if data and len(data) >= 2:
        if data[0] == 0x02:
            data = data[1:]
        if data[-1] == 0x03:
            data = data[:-1]
    return data.decode('ascii', errors='replace')

print("Avvio monitor...")
print("Target:", IDEON_IP + ":" + str(IDEON_PORT))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)

try:
    sock.connect((IDEON_IP, IDEON_PORT))
    print("Connesso!")
    
    sock.sendall(create_cmd("MSGFILTER=17"))
    print("MSGFILTER inviato")
    
    weights = []
    start = time.time()
    
    while time.time() - start < 30:
        try:
            sock.settimeout(1)
            data = sock.recv(512)
            
            if data:
                resp = parse(data)
                ts = time.strftime("%H:%M:%S")
                print(f"[{ts}] {resp[:80]}")
                
                if resp.startswith("WEIGHT="):
                    parts = resp.split("|")
                    if len(parts) >= 8:
                        w = int(parts[6])
                        d = int(parts[7])
                        print(f"  -> PESO: {w/1000:.1f}g ({d:+d})")
                        weights.append(w)
                        
        except socket.timeout:
            pass
    
    print(f"\nTotale pesate: {len(weights)}")
    
except Exception as e:
    print(f"Errore: {e}")
finally:
    sock.close()
    print("Chiuso")