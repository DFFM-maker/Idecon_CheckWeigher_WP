#!/usr/bin/env python3
"""
Monitor Pesate IDECON - Output in tempo reale
"""

import socket
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

def main():
    print("="*60)
    print("MONITOR PESATE IDECON - TEMPO REALE")
    print("="*60)
    print("Target:", IDEON_IP + ":" + str(IDEON_PORT))
    print("Aspettando pesate...\n")
    
    weights = []
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        sock.connect((IDEON_IP, IDEON_PORT))
        print("[CONNESSO]", time.strftime("%H:%M:%S"))
        
        # MSGFILTER=17 per ricevere WEIGHT
        sock.sendall(create_cmd("MSGFILTER=17"))
        print("[CONFIG] MSGFILTER=17 inviato")
        
        while True:
            try:
                sock.settimeout(1)
                data = sock.recv(512)
                
                if data:
                    resp = parse(data)
                    ts = time.strftime("%H:%M:%S")
                    
                    if resp.startswith("WEIGHT="):
                        parts = resp.split("|")
                        if len(parts) >= 8:
                            # WEIGHT=timestamp|||batch|recipe|line|serial|weight|delta|cls
                            weight_mg = int(parts[6])
                            delta_mg = int(parts[7])
                            cls = int(parts[8]) if len(parts) > 8 else 0
                            
                            expelled = (cls & 0x100) > 0 or (cls & 0x8000) > 0
                            status = "EXPELLED" if expelled else "OK"
                            
                            print(f"[{ts}] WEIGHT: {weight_mg/1000:.1f}g (delta: {delta_mg/1000:+.1f}g) [{status}]")
                            weights.append(weight_mg)
                    
                    elif resp.startswith("STATSV="):
                        mode = resp.split("=")[1][:3] if "=" in resp else "???"
                        print(f"[{ts}] STATSV: {mode}")
                    
                    elif resp.startswith("STATP="):
                        print(f"[{ts}] STATP ricevuto")
                    
                    elif "NEWPIECE" in resp:
                        print(f"[{ts}] NEWPIECE")
                    
                    else:
                        if resp.strip():
                            print(f"[{ts}] ALTRO: {resp[:50]}")
                
            except socket.timeout:
                pass
                
    except KeyboardInterrupt:
        print("\n\nInterrotto.")
    except Exception as e:
        print(f"\nErrore: {e}")
    finally:
        sock.close()
    
    if weights:
        print(f"\n--- RIEPILOGO ({len(weights)} pesate) ---")
        print(f"Peso medio: {sum(weights)/len(weights)/1000:.1f}g")
        print(f"Min: {min(weights)/1000:.1f}g | Max: {max(weights)/1000:.1f}g")

if __name__ == "__main__":
    main()