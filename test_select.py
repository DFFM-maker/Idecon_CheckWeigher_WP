#!/usr/bin/env python3
import socket
import select
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

print("="*60)
print("MONITOR IDECON - 60 secondi")
print("="*60)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)

try:
    sock.connect((IDEON_IP, IDEON_PORT))
    print("Connesso!")
    
    sock.sendall(create_cmd("MSGFILTER=17"))
    print("MSGFILTER=17")
    
    weights = []
    start = time.time()
    last_poll = 0
    
    while time.time() - start < 60:
        current = time.time()
        ts = time.strftime("%H:%M:%S")
        
        # Poll STATSV ogni 2s
        if current - last_poll > 2:
            try:
                sock.sendall(create_cmd("STATSV"))
                ready = select.select([sock], [], [], 1)
                if ready[0]:
                    resp = sock.recv(256)
                    if resp:
                        print(f"[{ts}] STATSV")
            except:
                print(f"[{ts}] STATSV timeout")
            last_poll = current
        
        # Check dati in arrivo
        ready = select.select([sock], [], [], 0.1)
        if ready[0]:
            try:
                data = sock.recv(512)
                if data:
                    resp = parse(data)
                    
                    if "WEIGHT=" in resp:
                        print(f"\n[{ts}] *** WEIGHT ***")
                        print(f"    {resp[:70]}")
                        weights.append(resp)
                        
                    elif "NEWPIECE" in resp:
                        print(f"[{ts}] NEWPIECE")
                        
                    elif "STATP=" in resp:
                        print(f"[{ts}] STATP")
                        
                    elif resp.strip() and resp != "MSGFILTER=17":
                        print(f"[{ts}] {resp[:40]}")
            except:
                pass
        
        time.sleep(0.01)
    
    print("\n" + "="*60)
    print(f"PESATE RICEVUTE: {len(weights)}")
    if weights:
        for w in weights:
            parts = w.split("|")
            if len(parts) >= 8:
                print(f"  {parts[6]}mg")
    
except Exception as e:
    print(f"Errore: {e}")
finally:
    sock.close()
    print("\nChiuso")