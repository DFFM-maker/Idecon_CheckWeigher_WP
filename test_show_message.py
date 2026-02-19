#!/usr/bin/env python3
"""
IDECON - Messaggio Display con Lotto/Ordine Attivo
"""

import socket
import select
import time
from idecon_client import IDEON_IP, IDEON_PORT

def create_cmd(cmd):
    return b'\x02' + cmd.encode('ascii') + b'\x03'

def send_command(sock, cmd, timeout=5):
    try:
        sock.sendall(create_cmd(cmd))
        sock.settimeout(timeout)
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            data = sock.recv(512)
            if data:
                if data[0] == 0x02: data = data[1:]
                if data[-1] == 0x03: data = data[:-1]
                return data.decode('ascii', errors='replace')
        return None
    except Exception as e:
        return f"ERROR: {e}"

def parse_batchinfo(msg):
    """Parsa BATCHINFO per estrarre ordine e batch"""
    if not msg.startswith("BATCHINFO="):
        return None, None
    
    data = msg[10:]  # Rimuovi BATCHINFO=
    parts = data.split("|")
    
    if len(parts) >= 5:
        return parts[2], parts[1]  # order, batch
    return None, None

def main():
    print("="*70)
    print("IDECON - MESSAGGIO DISPLAY LOTTO/ORDINE")
    print("="*70)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        print(f"\nConnessione a {IDEON_IP}:{IDEON_PORT}...")
        sock.connect((IDEON_IP, IDEON_PORT))
        print("[OK] Connesso!\n")
        
        # 1. Leggi info batch
        print("Lettura info batch...")
        resp = send_command(sock, "BATCHINFO")
        print(f"Risposta: {resp}\n")
        
        order, batch = parse_batchinfo(resp)
        
        if order and batch:
            print(f"Ordine attivo: {order}")
            print(f"Batch attivo: {batch}\n")
            
            # Crea messaggio
            message = f"Lotto/Ordine Attivo: {order} / {batch} in produzione"
            print(f"Messaggio da inviare:")
            print(f"  '{message}'")
            print(f"  (Lunghezza: {len(message)} caratteri)\n")
            
            # Invia messaggio
            print("Invio messaggio al display...")
            cmd = f"SHOWMESSAGE={message}"
            resp = send_command(sock, cmd)
            print(f"Risposta: {resp}\n")
            
            # Attendi 10 secondi
            print("Messaggio visualizzato per 10 secondi...")
            for i in range(10, 0, -1):
                print(f"\r  [{i}s]", end="", flush=True)
                time.sleep(1)
            print("\r  [0s]\n")
            
            # Rimuovi messaggio
            print("Rimozione messaggio...")
            resp = send_command(sock, "SHOWMESSAGE=")
            print(f"Risposta: {resp}\n")
            
            print("[OK] Messaggio completato!")
            
        else:
            print("[WARN] Impossibile leggere ordine/batch")
            print("Invio messaggio generico...")
            
            message = "Lotto/Ordine Attivo: In attesa dati"
            resp = send_command(sock, f"SHOWMESSAGE={message}")
            print(f"Risposta: {resp}")
            
            time.sleep(5)
            
            send_command(sock, "SHOWMESSAGE=")
            print("[OK] Messaggio rimosso")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        sock.close()
        print("\n[DISCONNESSO]")

if __name__ == "__main__":
    main()