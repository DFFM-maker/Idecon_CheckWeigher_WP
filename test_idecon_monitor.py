#!/usr/bin/env python3
"""
Monitor Pesate IDECON - Pronti per 6 pesate
"""

import socket
import time
import sys
import threading

IDEON_IP = '172.16.224.210'
IDEON_PORT = 50000

def create_idecon_command(command: str) -> bytes:
    return b'\x02' + command.encode('ascii') + b'\x03'

def parse_response(data: bytes) -> str:
    if data and len(data) >= 2:
        if data[0] == 0x02:
            data = data[1:]
        if data[-1] == 0x03:
            data = data[:-1]
    return data.decode('ascii', errors='replace')

def connect_and_monitor(stop_event):
    """Connessione e monitor in thread separato"""
    weights = []
    reconnect_count = 0
    
    while not stop_event.is_set():
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        try:
            print(f"[{time.strftime('%H:%M:%S')}] Connessione...")
            sock.connect((IDEON_IP, IDEON_PORT))
            print(f"[{time.strftime('%H:%M:%S')}] Connesso!")
            
            # Configura MSGFILTER
            sock.sendall(create_idecon_command("MSGFILTER=17"))
            reconnect_count = 0
            
            weights = []
            start_time = time.time()
            
            while not stop_event.is_set() and (time.time() - start_time) < 180:
                try:
                    sock.settimeout(1)
                    data = sock.recv(512)
                    
                    if data:
                        resp = parse_response(data)
                        print(f"[{time.strftime('%H:%M:%S')}] RX: {resp}")
                        
                        if resp.startswith("WEIGHT="):
                            parts = resp.split("|")
                            if len(parts) >= 8:
                                weight = parts[6]
                                delta = parts[7]
                                cls = parts[8]
                                
                                w = int(weight)
                                d = int(delta)
                                
                                expelled = (int(cls) & 0x100) > 0 or (int(cls) & 0x8000) > 0
                                status = "EXPELLED" if expelled else "OK"
                                
                                print(f"  -> PESO: {w}g (delta: {d:+d}) [{status}]")
                                weights.append(w)
                                
                except socket.timeout:
                    pass
                except Exception as e:
                    print(f"Errore: {e}")
                    break
            
        except socket.timeout:
            print(f"[{time.strftime('%H:%M:%S')}] Timeout - riconnessione...")
            reconnect_count += 1
        except ConnectionRefusedError:
            print(f"[{time.strftime('%H:%M:%S')}] Connessione rifiutata")
            time.sleep(1)
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Errore: {e}")
            time.sleep(1)
        finally:
            sock.close()
        
        if reconnect_count > 5:
            print("Troppi tentativi falliti. Aspetto...")
            time.sleep(5)
            reconnect_count = 0
    
    return weights

def main():
    print("="*60)
    print("MONITOR PESATE IDECON - PRONTO")
    print("="*60)
    print("Target: 172.16.224.210:50000")
    print("In attesa di 6 pesate...")
    print("Ctrl+C per uscire")
    print("="*60)
    
    weights = []
    stop_event = threading.Event()
    
    try:
        weights = connect_and_monitor(stop_event)
    except KeyboardInterrupt:
        print("\nInterrotto.")
        stop_event.set()
    
    if weights:
        print("\n" + "="*60)
        print(f"PESATE RICEVUTE: {len(weights)}")
        print("="*60)
        print(f"Pesi: {weights}")
        print(f"Media: {sum(weights)/len(weights):.1f}g")
        print(f"Min: {min(weights)}g")
        print(f"Max: {max(weights)}g")

if __name__ == "__main__":
    main()