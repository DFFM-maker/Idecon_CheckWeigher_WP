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

print("Avvio monitor (60s)...")
print("Target:", IDEON_IP + ":" + str(IDEON_PORT))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(15)

try:
    sock.connect((IDEON_IP, IDEON_PORT))
    print("Connesso!")
    
    sock.sendall(create_cmd("MSGFILTER=17"))
    print("MSGFILTER=17 inviato")
    
    # Poll STATSV continuously
    weights = []
    start = time.time()
    last_poll = 0
    
    while time.time() - start < 60:
        # Poll STATSV every 1s
        if time.time() - last_poll > 1:
            try:
                sock.sendall(create_cmd("STATSV"))
                sock.settimeout(1)
                resp = sock.recv(256)
                if resp:
                    print(f"[{time.strftime('%H:%M:%S')}] STATSV={parse(resp)[:25]}...")
            except:
                pass
            last_poll = time.time()
        
        # Check for WEIGHT data
        try:
            sock.settimeout(0.1)
            data = sock.recv(512, socket.MSG_DONTWAIT)
            if data:
                resp = parse(data)
                ts = time.strftime("%H:%M:%S")
                
                if "WEIGHT=" in resp:
                    print(f"\n!!! [{ts}] WEIGHT RICEVUTO !!!")
                    print(f"    Raw: {resp[:80]}")
                    weights.append(resp)
                    
                elif "STATP=" in resp:
                    print(f"[{ts}] STATP")
                    
                elif "NEWPIECE" in resp:
                    print(f"[{ts}] NEWPIECE")
                    
        except BlockingIOError:
            pass
        
        time.sleep(0.01)
    
    print(f"\n--- FINE TEST ---")
    print(f"Pesate ricevute: {len(weights)}")
    if weights:
        for w in weights:
            print(f"  {w[:60]}...")
    
except Exception as e:
    print(f"Errore: {e}")
finally:
    sock.close()
    print("Chiuso")