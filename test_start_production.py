#!/usr/bin/env python3
"""
IDECON - Invio campi e avvio produzione
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
    print("IDECON - CONFIGURAZIONE E AVVIO PRODUZIONE")
    print("="*70)
    
    # Configurazione da inviare
    config = {
        'recipe': '225g',
        'production_order': 'ORDINE_001',
        'batch_code': 'BATCH_001', 
        'extra_field_1': 'Linea_A',
        'extra_field_2': 'Turno_Mattina'
    }
    
    print("\nConfigurazione da inviare:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        print(f"\nConnessione a {IDEON_IP}:{IDEON_PORT}...")
        sock.connect((IDEON_IP, IDEON_PORT))
        print("[OK] Connesso!\n")
        
        # 1. STOP (se in produzione)
        print("="*70)
        print("1. STOP MACCHINA (se attiva)")
        print("="*70)
        resp = send_command(sock, "STOP")
        print(f"Risposta: {resp}")
        time.sleep(2)
        
        # 2. Imposta campi batch (usa ricetta già attiva)
        print("\n" + "="*70)
        print("3. IMPOSTA CAMPI BATCH")
        print("="*70)
        
        # Production Order
        cmd = f"BATCHMODIFY=PRODUCTIONORDER|{config['production_order']}"
        print(f"Invio: {cmd}")
        resp = send_command(sock, cmd)
        print(f"Risposta: {resp}")
        time.sleep(0.5)
        
        # Batch Code (attenzione: potrebbe essere chiamato BATCHCODE)
        cmd = f"BATCHMODIFY=BATCHCODE|{config['batch_code']}"
        print(f"Invio: {cmd}")
        resp = send_command(sock, cmd)
        print(f"Risposta: {resp}")
        time.sleep(0.5)
        
        # Extra Field 1
        cmd = f"BATCHMODIFY=EXTRAFIELD1|{config['extra_field_1']}"
        print(f"Invio: {cmd}")
        resp = send_command(sock, cmd)
        print(f"Risposta: {resp}")
        time.sleep(0.5)
        
        # Extra Field 2
        cmd = f"BATCHMODIFY=EXTRAFIELD2|{config['extra_field_2']}"
        print(f"Invio: {cmd}")
        resp = send_command(sock, cmd)
        print(f"Risposta: {resp}")
        time.sleep(0.5)
        
        # 4. Verifica configurazione
        print("\n" + "="*70)
        print("4. VERIFICA CONFIGURAZIONE")
        print("="*70)
        resp = send_command(sock, "BATCHINFO")
        print(f"BATCHINFO: {resp}")
        time.sleep(1)
        
        # 5. Apri batch
        print("\n" + "="*70)
        print("5. APERTURA BATCH")
        print("="*70)
        resp = send_command(sock, "BATCHSTART")
        print(f"Risposta: {resp}")
        time.sleep(2)
        
        # 6. Avvia produzione
        print("\n" + "="*70)
        print("6. AVVIO PRODUZIONE")
        print("="*70)
        print("Attenzione: I nastri inizieranno a muoversi!")
        print("Avvio tra 3 secondi...")
        time.sleep(3)
        
        resp = send_command(sock, "START")
        print(f"Risposta: {resp}")
        time.sleep(3)
        
        # 7. Verifica stato
        print("\n" + "="*70)
        print("7. VERIFICA STATO")
        print("="*70)
        resp = send_command(sock, "STATSV")
        print(f"STATSV: {resp}")
        
        if resp and resp.startswith("STATSV="):
            code = resp[7:]
            print(f"\nStato:")
            print(f"  - Motore: {'IN MOTO' if code[0] == '2' else 'Fermo'}")
            print(f"  - Produzione: {'ON' if code[1] == '1' else 'OFF'}")
            print(f"  - Batch: {'APERTO' if code[4] == '1' else 'Chiuso'}")
        
        print("\n" + "="*70)
        print("PRODUZIONE AVVIATA!")
        print("="*70)
        print("La bilancia è in funzione.")
        print("Puoi passare i prodotti sulla pesatrice.")
        print("\nPer fermare, usa il comando: STOP")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        sock.close()
        print("\n[DISCONNESSO]")

if __name__ == "__main__":
    main()