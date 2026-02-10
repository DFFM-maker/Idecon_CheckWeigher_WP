#!/usr/bin/env python3
"""
Test IDECON: Reset Statistiche
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

def main():
    print("="*70)
    print("RESET STATISTICHE IDECON")
    print("="*70)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        print(f"\nConnessione a {IDEON_IP}:{IDEON_PORT}...")
        sock.connect((IDEON_IP, IDEON_PORT))
        print("[OK] Connesso!\n")
        
        # Stato prima
        print("STATO PRIMA DEL RESET")
        print("-"*70)
        resp = send_command(sock, "STATSV")
        print(f"STATSV: {resp}")
        
        resp = send_command(sock, "STATREQ")
        print(f"STATREQ: {resp}")
        time.sleep(2)
        
        # Ricevi STATP
        ready = select.select([sock], [], [], 3)
        if ready[0]:
            data = sock.recv(1024)
            if data:
                if data[0] == 0x02: data = data[1:]
                if data[-1] == 0x03: data = data[:-1]
                msg = data.decode('ascii', errors='replace')
                if "STATP=" in msg:
                    print(f"STATP (prima): {msg[:80]}...")
        
        # METODO 1: DISABLESTATS + ENABLESTATS
        print("\n" + "="*70)
        print("METODO 1: Toggle Statistiche")
        print("="*70)
        
        print("1. Disabilito statistiche...")
        resp = send_command(sock, "DISABLESTATS")
        print(f"   DISABLESTATS: {resp}")
        time.sleep(2)
        
        print("2. Riabilito statistiche...")
        resp = send_command(sock, "ENABLESTATS")
        print(f"   ENABLESTATS: {resp}")
        time.sleep(2)
        
        # METODO 2: BATCHSTOP + BATCHSTART
        print("\n" + "="*70)
        print("METODO 2: Reset Batch")
        print("="*70)
        
        # Verifica se batch aperto
        resp = send_command(sock, "STATSV")
        if resp and resp.startswith("STATSV="):
            batch_open = resp[7:][4] == '1'  # Pos 4: 1=aperto
            print(f"Stato batch: {'APERTO' if batch_open else 'CHIUSO'}")
            
            if batch_open:
                print("Chiudo batch (BATCHSTOP)...")
                resp = send_command(sock, "BATCHSTOP")
                print(f"   BATCHSTOP: {resp}")
                time.sleep(3)
        
        print("Apro nuovo batch (BATCHSTART)...")
        resp = send_command(sock, "BATCHSTART")
        print(f"   BATCHSTART: {resp}")
        time.sleep(3)
        
        # Verifica dopo
        print("\n" + "="*70)
        print("VERIFICA DOPO RESET")
        print("="*70)
        
        resp = send_command(sock, "STATSV")
        print(f"STATSV: {resp}")
        
        resp = send_command(sock, "BATCHINFO")
        print(f"BATCHINFO: {resp}")
        
        print("\n" + "="*70)
        print("RESET COMPLETATO")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        sock.close()
        print("\n[DISCONNESSO]")

if __name__ == "__main__":
    main()