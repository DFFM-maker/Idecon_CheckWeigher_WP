#!/usr/bin/env python3
"""
Test IDECON: Lettura Campi Batch (Solo lettura)
"""

import socket
import select
from idecon_client import IDEON_IP, IDEON_PORT

def create_cmd(cmd):
    """Crea comando IDECON con STX/ETX"""
    return b'\x02' + cmd.encode('ascii') + b'\x03'

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
        print(f"Errore: {e}")
        return None

def parse_batchinfo(msg):
    """Parsa risposta BATCHINFO"""
    if not msg.startswith("BATCHINFO="):
        return None
    
    data = msg[10:]  # Rimuovi BATCHINFO=
    parts = data.split("|")
    
    return {
        'operator': parts[0] if len(parts) > 0 else "",
        'production_code': parts[1] if len(parts) > 1 else "",
        'production_order': parts[2] if len(parts) > 2 else "",
        'extra_field_1': parts[3] if len(parts) > 3 else "",
        'extra_field_2': parts[4] if len(parts) > 4 else "",
        'batch_type': parts[5] if len(parts) > 5 else "",
        'legislation': parts[6] if len(parts) > 6 else "",
    }

def parse_inforecipe(msg):
    """Parsa risposta INFORECIPE"""
    if not msg.startswith("INFORECIPE="):
        return None
    
    data = msg[11:]
    parts = data.split("|")
    
    info = {'recipe_name': parts[0] if parts else ""}
    
    for part in parts[1:]:
        if "prod.code=" in part:
            info['product_code'] = part.split("=")[1] if "=" in part else ""
        elif "weight=" in part:
            info['weight'] = part.split("=")[1] if "=" in part else ""
    
    return info

def main():
    print("="*70)
    print("LETTURA CAMPI BATCH IDECON")
    print("="*70)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        print(f"\nConnessione a {IDEON_IP}:{IDEON_PORT}...")
        sock.connect((IDEON_IP, IDEON_PORT))
        print("[OK] Connesso!\n")
        
        # 1. STATSV
        print("1. STATO MACCHINA (STATSV)")
        print("-"*70)
        resp = send_command(sock, "STATSV")
        if resp:
            print(f"   Risposta: {resp}")
            if resp.startswith("STATSV="):
                code = resp[7:]
                print(f"   Status: {code}")
                print(f"   - Motore: {'Operativo' if code[0] == '2' else 'Fermo'}")
                print(f"   - Produzione: {'ON' if code[1] == '1' else 'OFF'}")
                print(f"   - Batch: {'Aperto' if code[4] == '1' else 'Chiuso'}")
        
        # 2. INFORECIPE
        print("\n2. RICETTA ATTIVA (INFORECIPE)")
        print("-"*70)
        resp = send_command(sock, "INFORECIPE")
        if resp:
            print(f"   Risposta: {resp}")
            info = parse_inforecipe(resp)
            if info:
                print(f"   - Recipe Name:     {info.get('recipe_name', 'N/A')}")
                print(f"   - Product Code:    {info.get('product_code', 'N/A')}")
                print(f"   - Nominal Weight:  {info.get('weight', 'N/A')} g")
        
        # 3. BATCHINFO - CAMPI CHE HAI INSERITO
        print("\n3. CAMPI BATCH (BATCHINFO)")
        print("-"*70)
        resp = send_command(sock, "BATCHINFO")
        if resp:
            print(f"   Raw: {resp}\n")
            batch = parse_batchinfo(resp)
            if batch:
                print("   CAMPI CHE HAI INSERITO:")
                print(f"   - Recipe Name:      '{batch['operator']}'")
                print(f"   - Production Code:  '{batch['production_code']}'")
                print(f"   - Production Order: '{batch['production_order']}'")
                print(f"   - Extra Field 1:    '{batch['extra_field_1']}'")
                print(f"   - Extra Field 2:    '{batch['extra_field_2']}'")
                print(f"\n   CONFIGURAZIONE:")
                print(f"   - Batch Type:       {batch['batch_type']}")
                print(f"   - Legislation:      {batch['legislation']}")
        
        print("\n" + "="*70)
        print("LETTURA COMPLETATA")
        print("="*70)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        sock.close()
        print("\n[DISCONNESSO]")

if __name__ == "__main__":
    main()