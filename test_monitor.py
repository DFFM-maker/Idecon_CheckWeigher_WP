#!/usr/bin/env python3
import socket
import select
import time

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

print("="*70)
print("MONITOR IDECON - IN ATTESA PESATE")
print("="*70)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)

try:
    sock.connect((IDEON_IP, IDEON_PORT))
    print("[CONNESSO]")
    
    sock.sendall(create_cmd("MSGFILTER=17"))
    print("[CONFIG] MSGFILTER=17")
    print("Aspettando pesate (30s)...\n")
    
    weights = []
    last_poll_time = 0
    
    for sec in range(30, 0, -1):
        ts = time.strftime("%H:%M:%S")
        
        # Poll STATSV ogni 3 secondi (una volta sola)
        if sec % 3 == 0 and last_poll_time != sec:
            try:
                sock.sendall(create_cmd("STATSV"))
                sock.settimeout(0.5)
                resp = sock.recv(256)
                if resp:
                    print(f"[{ts}] STATSV={parse(resp)[:20]}...")
            except:
                pass
            last_poll_time = sec
        
        # Check dati in arrivo
        ready = select.select([sock], [], [], 0.5)
        if ready[0]:
            try:
                data = sock.recv(512)
                if data:
                    resp = parse(data)
                    
                    if "WEIGHT=" in resp:
                        print("\n" + "="*70)
                        print(f"PESATA RICEVUTA [{ts}]")
                        print("="*70)
                        print(f"Raw: {resp}")
                        
                        # Parse campi
                        parts = resp[7:].split("|")
                        print(f"\n[PRODUZIONE]")
                        print(f"  Timestamp:  {parts[0]}")
                        print(f"  Order:      '{parts[1]}'")
                        print(f"  Batch:      '{parts[2]}'")
                        print(f"  Recipe:     '{parts[3]}'")
                        print(f"  Line:       '{parts[4]}'")
                        print(f"  Serial:     '{parts[5]}'")
                        print(f"\n[PESO]")
                        print(f"  Weight:     {parts[6]} mg = {int(parts[6])/1000:.3f} g")
                        print(f"  Delta:      {parts[7]} mg = {int(parts[7])/1000:+.3f} g")
                        print(f"  Flags:      {parts[8] if len(parts) > 8 else 'N/A'}")
                        
                        weights.append(resp)
                        
                    elif "NEWPIECE" in resp:
                        print(f"[{ts}] NEWPIECE (diff peso)")
                    
                    elif "STATP=" in resp:
                        print(f"[{ts}] STATP - statistiche batch")
            except:
                pass
        
        print(f"  [{sec}s] In attesa...", end="\r")
    
    print("\n" + "="*70)
    print(f"RIEPILOGO - {len(weights)} PESATE RICEVUTE")
    print("="*70)
    
    if weights:
        for i, w in enumerate(weights, 1):
            parts = w[7:].split("|")
            print(f"{i}. {parts[6]}mg ({int(parts[7]):+d}mg) - Batch: '{parts[2]}' - Recipe: '{parts[3]}'")
    
except Exception as e:
    print(f"\nErrore: {e}")
finally:
    sock.close()
    print("\n[CHUSO]")