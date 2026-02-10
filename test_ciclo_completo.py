#!/usr/bin/env python3
"""
IDECON - Ciclo Completo: Invio campi, Avvio, 60s pesate, Chiusura, Reset
"""

import socket
import select
import time
from datetime import datetime
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
    print("IDECON - CICLO COMPLETO PRODUZIONE")
    print("="*70)
    
    # NUOVI CAMPI
    config = {
        'production_order': 'ORDINE_TEST_001',
        'batch_code': 'LOTTO_001', 
        'extra_field_1': 'TURNO_1',
        'extra_field_2': 'OPERATORE_MARIO'
    }
    
    print("\n" + "="*70)
    print("FASE 1: INVIO NUOVI CAMPI BATCH")
    print("="*70)
    print("\nCampi da inviare:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        # CONNESSIONE
        print(f"\nConnessione a {IDEON_IP}:{IDEON_PORT}...")
        sock.connect((IDEON_IP, IDEON_PORT))
        print("[OK] Connesso!")
        
        # INVIO CAMPI
        print("\nInvio campi batch...")
        for field, value in [
            ('PRODUCTIONORDER', config['production_order']),
            ('BATCHCODE', config['batch_code']),
            ('EXTRAFIELD1', config['extra_field_1']),
            ('EXTRAFIELD2', config['extra_field_2'])
        ]:
            cmd = f"BATCHMODIFY={field}|{value}"
            print(f"  {cmd}")
            resp = send_command(sock, cmd)
            print(f"    -> {resp}")
            time.sleep(0.5)
        
        # VERIFICA
        print("\nVerifica campi:")
        resp = send_command(sock, "BATCHINFO")
        print(f"  {resp}")
        
        # AVVIO PRODUZIONE
        print("\n" + "="*70)
        print("FASE 2: AVVIO PRODUZIONE")
        print("="*70)
        
        print("\nSTOP...")
        send_command(sock, "STOP")
        time.sleep(1)
        
        print("BATCHSTART...")
        resp = send_command(sock, "BATCHSTART")
        print(f"  -> {resp}")
        time.sleep(2)
        
        print("START (avvio nastri)...")
        resp = send_command(sock, "START")
        print(f"  -> {resp}")
        time.sleep(3)
        
        # VERIFICA STATO
        resp = send_command(sock, "STATSV")
        print(f"\nStato: {resp}")
        
        # FASE 3: MONITORAGGIO 60 SECONDI
        print("\n" + "="*70)
        print("FASE 3: MONITORAGGIO PESATE (60 secondi)")
        print("="*70)
        print("Fai le pesate ora!\n")
        
        weights = []
        start_time = time.time()
        last_poll = 0
        
        while time.time() - start_time < 60:
            elapsed = int(time.time() - start_time)
            remaining = 60 - elapsed
            
            # Polling STATSV ogni 5s
            if time.time() - last_poll >= 5:
                try:
                    sock.sendall(create_cmd("STATSV"))
                except:
                    pass
                last_poll = time.time()
            
            # Ricezione dati
            ready = select.select([sock], [], [], 0.5)
            if ready[0]:
                try:
                    data = sock.recv(1024)
                    if data:
                        if data[0] == 0x02: data = data[1:]
                        if data[-1] == 0x03: data = data[:-1]
                        
                        msg = data.decode('ascii', errors='replace')
                        ts = datetime.now().strftime("%H:%M:%S")
                        
                        if msg.startswith("WEIGHT="):
                            parts = msg[7:].split("|")
                            if len(parts) >= 8:
                                weight_g = int(parts[6]) / 1000.0
                                delta_g = int(parts[7]) / 1000.0
                                weights.append({'w': weight_g, 'd': delta_g, 't': ts})
                                print(f"[{ts}] Peso: {weight_g:.3f}g ({delta_g:+.1f}g) - Total: {len(weights)}")
                        elif "EVENT=" in msg:
                            print(f"[{ts}] EVENT: {msg[:60]}...")
                        
                except:
                    pass
            
            print(f"\r  [{remaining}s] In attesa...", end="", flush=True)
            time.sleep(0.1)
        
        # FASE 4: CHIUSURA E VERIFICA
        print("\n\n" + "="*70)
        print("FASE 4: CHIUSURA BATCH E VERIFICA")
        print("="*70)
        
        print("\nSTOP produzione...")
        resp = send_command(sock, "STOP")
        print(f"  -> {resp}")
        time.sleep(2)
        
        print("BATCHSTOP (chiusura lotto)...")
        resp = send_command(sock, "BATCHSTOP")
        print(f"  -> {resp}")
        time.sleep(2)
        
        # STATISTICHE
        print("\nSTATISTICHE PESATE:")
        print(f"  Totale pesi: {len(weights)}")
        if weights:
            w_vals = [w['w'] for w in weights]
            print(f"  Media: {sum(w_vals)/len(w_vals):.2f}g")
            print(f"  Min: {min(w_vals):.2f}g")
            print(f"  Max: {max(w_vals):.2f}g")
            print(f"\n  Dettaglio:")
            for i, w in enumerate(weights[-10:], 1):
                print(f"    {i}. {w['t']} - {w['w']:.3f}g ({w['d']:+.1f}g)")
        
        # FASE 5: RESET STATISTICHE
        print("\n" + "="*70)
        print("FASE 5: RESET STATISTICHE")
        print("="*70)
        
        print("\nDISABLESTATS...")
        resp = send_command(sock, "DISABLESTATS")
        print(f"  -> {resp}")
        time.sleep(1)
        
        print("ENABLESTATS...")
        resp = send_command(sock, "ENABLESTATS")
        print(f"  -> {resp}")
        time.sleep(1)
        
        print("\nNuovo BATCHSTART (reset totale)...")
        resp = send_command(sock, "BATCHSTART")
        print(f"  -> {resp}")
        
        print("\nVerifica finale:")
        resp = send_command(sock, "STATSV")
        print(f"  STATSV: {resp}")
        
        print("\n" + "="*70)
        print("CICLO COMPLETATO!")
        print("="*70)
        print(f"Pesate: {len(weights)}")
        print("Statistiche resettate!")
        
    except KeyboardInterrupt:
        print("\n[Interrotto]")
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        sock.close()
        print("\n[DISCONNESSO]")

if __name__ == "__main__":
    main()