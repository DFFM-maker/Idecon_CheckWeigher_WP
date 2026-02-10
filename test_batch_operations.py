#!/usr/bin/env python3
"""
Test IDECON: Lettura Batch Info e Reset Statistiche
"""

import socket
import select
import time
from idecon_client import IdeconClient, create_cmd, parse_response, IDEON_IP, IDEON_PORT

def send_command(sock, cmd, timeout=5):
    """Invia comando e attendi risposta"""
    try:
        sock.sendall(create_cmd(cmd))
        sock.settimeout(timeout)
        
        ready = select.select([sock], [], [], timeout)
        if ready[0]:
            data = sock.recv(512)
            if data:
                if data[0] == 0x02:
                    data = data[1:]
                if data[-1] == 0x03:
                    data = data[:-1]
                return data.decode('ascii', errors='replace')
        return None
    except Exception as e:
        print(f"Errore comando {cmd}: {e}")
        return None

def parse_batchinfo(msg):
    """Parsa risposta BATCHINFO"""
    if not msg.startswith("BATCHINFO="):
        return None
    
    # BATCHINFO=operator|prod_code|prod_order|extra1|extra2|batch_type|legislation|end_type|end_value|split_end_type|split_end_value|time_option|time|print_option|
    data = msg[10:]  # Rimuovi BATCHINFO=
    parts = data.split("|")
    
    return {
        'operator': parts[0] if len(parts) > 0 else "",
        'production_code': parts[1] if len(parts) > 1 else "",
        'production_order': parts[2] if len(parts) > 2 else "",
        'extra_field_1': parts[3] if len(parts) > 3 else "",
        'extra_field_2': parts[4] if len(parts) > 4 else "",
        'batch_type': parts[5] if len(parts) > 5 else "",  # GLOBAL, SPLIT
        'legislation': parts[6] if len(parts) > 6 else "",  # NOT_SELECTED, GLOBAL, SPLIT, DISABLED
        'end_type': parts[7] if len(parts) > 7 else "",     # NOT_SELECTED, PIECES, MINUTES, MANUAL
        'end_value': parts[8] if len(parts) > 8 else "",
        'split_end_type': parts[9] if len(parts) > 9 else "",
        'split_end_value': parts[10] if len(parts) > 10 else "",
        'time_option': parts[11] if len(parts) > 11 else "",  # ENABLED, DISABLED
        'time': parts[12] if len(parts) > 12 else "",
        'print_option': parts[13] if len(parts) > 13 else ""  # MANUAL, AUTOMATIC
    }

def parse_inforecipe(msg):
    """Parsa risposta INFORECIPE"""
    if not msg.startswith("INFORECIPE="):
        return None
    
    # INFORECIPE=recipe|prod.code=xxx|weight=xxx|tare=xxx|lim-=xxx|lim+=xxx|lim--=xxx|lim++=xxx|
    data = msg[11:]
    
    info = {'raw': data}
    
    # Estrai valori
    parts = data.split("|")
    if parts:
        info['recipe_name'] = parts[0]
    
    for part in parts[1:]:
        if "prod.code=" in part:
            info['product_code'] = part.split("=")[1] if "=" in part else ""
        elif "weight=" in part:
            info['weight'] = part.split("=")[1] if "=" in part else ""
        elif "tare=" in part:
            info['tare'] = part.split("=")[1] if "=" in part else ""
        elif "lim-=" in part:
            info['limit_minus'] = part.split("=")[1] if "=" in part else ""
        elif "lim+=" in part:
            info['limit_plus'] = part.split("=")[1] if "=" in part else ""
    
    return info

def test_batch_operations():
    """Test operazioni batch"""
    print("="*70)
    print("TEST IDECON - Batch Info e Reset Statistiche")
    print("="*70)
    
    # Connessione
    print(f"\nConnessione a {IDEON_IP}:{IDEON_PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        sock.connect((IDEON_IP, IDEON_PORT))
        print("[OK] Connesso!")
        
        # 1. STATSV - Stato attuale
        print("\n" + "="*70)
        print("1. STATO ATTUALE")
        print("="*70)
        resp = send_command(sock, "STATSV")
        if resp:
            print(f"Risposta: {resp}")
            if resp.startswith("STATSV="):
                status_code = resp[7:]
                print(f"  Status Code: {status_code}")
                print(f"  Motor: {'OPERATIONAL' if status_code[0] == '2' else 'STOPPED'}")
                print(f"  Production: {'ON' if status_code[1] == '1' else 'OFF'}")
                print(f"  Errors: {'YES' if status_code[2] == '1' else 'NO'}")
                print(f"  Batch Open: {'YES' if status_code[4] == '0' else 'NO'}")  # Pos 4: batch (0=chiuso)
        
        # 2. INFORECIPE - Informazioni ricetta
        print("\n" + "="*70)
        print("2. INFO RICETTA")
        print("="*70)
        resp = send_command(sock, "INFORECIPE")
        if resp:
            print(f"Risposta: {resp}")
            info = parse_inforecipe(resp)
            if info:
                print(f"  Recipe Name: {info.get('recipe_name', 'N/A')}")
                print(f"  Product Code: {info.get('product_code', 'N/A')}")
                print(f"  Nominal Weight: {info.get('weight', 'N/A')}")
                print(f"  Tare: {info.get('tare', 'N/A')}")
                print(f"  Limit -: {info.get('limit_minus', 'N/A')}")
                print(f"  Limit +: {info.get('limit_plus', 'N/A')}")
        
        # 3. BATCHINFO - Informazioni batch
        print("\n" + "="*70)
        print("3. INFO BATCH (Campi che hai inserito)")
        print("="*70)
        resp = send_command(sock, "BATCHINFO")
        if resp:
            print(f"Risposta raw: {resp}")
            batch = parse_batchinfo(resp)
            if batch:
                print(f"\n  CAMPI BATCH:")
                print(f"  - Operator:           '{batch['operator']}'")
                print(f"  - Production Code:    '{batch['production_code']}'")
                print(f"  - Production Order:   '{batch['production_order']}'")
                print(f"  - Extra Field 1:      '{batch['extra_field_1']}'")
                print(f"  - Extra Field 2:      '{batch['extra_field_2']}'")
                print(f"\n  CONFIGURAZIONE:")
                print(f"  - Batch Type:         {batch['batch_type']}")
                print(f"  - Legislation:        {batch['legislation']}")
                print(f"  - End Type:           {batch['end_type']}")
                print(f"  - End Value:          {batch['end_value']}")
                print(f"  - Time Option:        {batch['time_option']}")
                print(f"  - Print Option:       {batch['print_option']}")
        
        # 4. Prova a modificare batch (BATCHMODIFY)
        print("\n" + "="*70)
        print("4. MODIFICA BATCH (Test BATCHMODIFY)")
        print("="*70)
        
        # Modifica production order
        print("\nTentativo modifica Production Order...")
        resp = send_command(sock, "BATCHMODIFY=PRODUCTIONORDER|TEST_ORD_001")
        print(f"Risposta: {resp}")
        
        # Modifica extra field 1
        print("\nTentativo modifica Extra Field 1...")
        resp = send_command(sock, "BATCHMODIFY=EXTRAFIELD1|Testo Extra 1")
        print(f"Risposta: {resp}")
        
        # 5. Reset statistiche
        print("\n" + "="*70)
        print("5. RESET STATISTICHE")
        print("="*70)
        
        # Opzione A: DISABLESTATS + ENABLESTATS
        print("\nOpzione A: Disabilita e riabilita statistiche...")
        resp = send_command(sock, "DISABLESTATS")
        print(f"  DISABLESTATS: {resp}")
        time.sleep(1)
        resp = send_command(sock, "ENABLESTATS")
        print(f"  ENABLESTATS: {resp}")
        
        # Opzione B: BATCHSTOP + BATCHSTART (reset completo)
        print("\nOpzione B: Chiudi e riapri batch (reset totale)...")
        
        # Leggi stato prima
        resp = send_command(sock, "STATSV")
        if resp and resp.startswith("STATSV="):
            batch_open = resp[7:][4] == '0'  # Pos 4: 0=chiuso, 1=aperto
            print(f"  Stato batch attuale: {'APERTO' if batch_open else 'CHIUSO'}")
            
            if batch_open:
                print("  Chiusura batch (BATCHSTOP)...")
                resp = send_command(sock, "BATCHSTOP")
                print(f"  BATCHSTOP: {resp}")
                time.sleep(2)
            
            print("  Apertura nuovo batch (BATCHSTART)...")
            resp = send_command(sock, "BATCHSTART")
            print(f"  BATCHSTART: {resp}")
        
        # 6. Verifica stato dopo reset
        print("\n" + "="*70)
        print("6. VERIFICA POST-RESET")
        print("="*70)
        time.sleep(2)
        
        resp = send_command(sock, "STATSV")
        if resp:
            print(f"STATSV: {resp}")
        
        resp = send_command(sock, "BATCHINFO")
        if resp:
            print(f"BATCHINFO: {resp}")
        
        print("\n" + "="*70)
        print("TEST COMPLETATO")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        sock.close()
        print("\n[DISCONNESSO]")

if __name__ == "__main__":
    test_batch_operations()