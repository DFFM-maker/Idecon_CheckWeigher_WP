#!/usr/bin/env python3
"""
Test Completo Dati IDECON - Tutti i campi dal manuale
"""

import socket
import select
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

def parse_weight(resp):
    """Parse WEIGHT message - tutti i campi"""
    if not resp.startswith("WEIGHT="):
        return None
    
    data = resp[7:]
    parts = data.split("|")
    
    result = {}
    
    try:
        result['timestamp'] = parts[0] if len(parts) > 0 else ""
        result['order'] = parts[1] if len(parts) > 1 else ""
        result['batch'] = parts[2] if len(parts) > 2 else ""
        result['recipe'] = parts[3] if len(parts) > 3 else ""
        result['line'] = parts[4] if len(parts) > 4 else ""
        result['serial'] = parts[5] if len(parts) > 5 else ""
        result['weight_mg'] = int(parts[6]) if len(parts) > 6 and parts[6] else 0
        result['delta_mg'] = int(parts[7]) if len(parts) > 7 and parts[7] else 0
        result['classification'] = parts[8] if len(parts) > 8 else ""
        result['extra'] = parts[9:] if len(parts) > 9 else []
    except (IndexError, ValueError) as e:
        result['error'] = str(e)
        result['raw'] = resp
    
    return result

def classification_bits(cls_str):
    """Decode classification bits - secondo manuale"""
    if not cls_str:
        return {}
    
    try:
        cls = int(cls_str) if cls_str.isdigit() else int(cls_str, 16)
    except:
        return {'raw': cls_str}
    
    return {
        'Bit0_UnderMin': bool(cls & 0x0001),
        'Bit1_OverMax': bool(cls & 0x0002),
        'Bit2_NearMin': bool(cls & 0x0004),
        'Bit3_NearMax': bool(cls & 0x0008),
        'Bit4_ManualCheck': bool(cls & 0x0010),
        'Bit5_Empty': bool(cls & 0x0020),
        'Bit6_OverMax2': bool(cls & 0x0040),
        'Bit7_UnderMax2': bool(cls & 0x0080),
        'Bit8_Expelled': bool(cls & 0x0100),
        'Bit9_Accepted': bool(cls & 0x0200),
        'Bit10_SpecialAccept': bool(cls & 0x0400),
        'Bit11_ManualEject': bool(cls & 0x0800),
        'Bit12': bool(cls & 0x1000),
        'Bit13': bool(cls & 0x2000),
        'Bit14': bool(cls & 0x4000),
        'Bit15_ConsensEject': bool(cls & 0x8000),
    }

def print_weight_data(w):
    """Stampa tutti i dati pesata formattati"""
    print(f"\n{'='*70}")
    print("CAMPI PRODUZIONE")
    print('='*70)
    print(f"  Timestamp:      {w['timestamp']}")
    print(f"  Order:          '{w['order']}'")
    print(f"  Batch:          '{w['batch']}'")
    print(f"  Recipe:         '{w['recipe']}'")
    print(f"  Line:           '{w['line']}'")
    print(f"  Serial:         '{w['serial']}'")
    
    print(f"\n{'='*70}")
    print("PESO E DELTA")
    print('='*70)
    print(f"  LastWeight_mg:  {w['weight_mg']} mg")
    print(f"  Peso (g):       {w['weight_mg']/1000:.3f} g")
    print(f"  Delta (mg):     {w['delta_mg']} mg")
    print(f"  Delta (g):      {w['delta_mg']/1000:+.3f} g")
    
    if w['classification']:
        print(f"\n{'='*70}")
        print("CLASSIFICAZIONE (LastWeightFlags)")
        print('='*70)
        print(f"  Valore esadecimale: 0x{w['classification'].upper()}")
        bits = classification_bits(w['classification'])
        active = [(k,v) for k,v in bits.items() if v]
        for bit, val in active:
            print(f"  {bit}: {val}")
    
    if w['extra']:
        print(f"\n{'='*70}")
        print(f"CAMPI EXTRA ({len(w['extra'])})")
        print('='*70)
        for i, e in enumerate(w['extra']):
            print(f"  [{i+9}]: '{e}'")

def main():
    print("="*70)
    print("TEST COMPLETO DATI IDECON")
    print("="*70)
    print(f"Target: {IDEON_IP}:{IDEON_PORT}")
    print("Aspettando pesate (60s)...\n")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        sock.connect((IDEON_IP, IDEON_PORT))
        print("[CONNESSO]")
        
        sock.sendall(create_cmd("MSGFILTER=17"))
        print("[CONFIG] MSGFILTER=17\n")
        
        weights = []
        start = time.time()
        poll_interval = 3
        
        while time.time() - start < 60:
            ts = time.strftime("%H:%M:%S")
            
            # Poll STATSV
            if time.time() - start > poll_interval and int(time.time()) % poll_interval == 0:
                try:
                    sock.sendall(create_cmd("STATSV"))
                    print(f"[{ts}] Poll STATSV")
                except:
                    pass
            
            # Check dati
            ready = select.select([sock], [], [], 0.1)
            if ready[0]:
                try:
                    data = sock.recv(512)
                    if data:
                        resp = parse(data)
                        
                        if "WEIGHT=" in resp:
                            w = parse_weight(resp)
                            if w and 'error' not in w:
                                print_weight_data(w)
                                weights.append(w)
                            else:
                                print(f"[ERRORE Parsing] {w.get('error', 'unknown')}")
                                
                        elif "NEWPIECE" in resp:
                            print(f"[{ts}] NEWPIECE (differenza peso)")
                        
                        elif resp.strip() and resp != "MSGFILTER=17" and not resp.startswith("STATSV="):
                            print(f"[{ts}] {resp[:60]}")
                            
                except:
                    pass
            
            time.sleep(0.01)
        
        # Riepilogo
        print("\n" + "="*70)
        print("RIEPILOGO BATCH")
        print("="*70)
        
        if weights:
            # Global batch stats
            total = len(weights)
            weight_vals = [w['weight_mg'] for w in weights]
            delta_vals = [w['delta_mg'] for w in weights]
            
            # Classificazione
            accepted = 0
            rejected_under = 0
            rejected_over = 0
            expelled = 0
            
            for w in weights:
                bits = classification_bits(w['classification'])
                if bits.get('Bit9_Accepted', False):
                    accepted += 1
                if bits.get('Bit0_UnderMin', False):
                    rejected_under += 1
                if bits.get('Bit1_OverMax', False):
                    rejected_over += 1
                if bits.get('Bit8_Expelled', False) or bits.get('Bit15_ConsensEject', False):
                    expelled += 1
            
            print(f"\n[PRODUZIONE]")
            print(f"  MotorRunning:   2 (operativo)")
            print(f"  SerialNumber:   '{weights[0]['serial']}'")
            print(f"  LineCode:       '{weights[0]['line']}'")
            print(f"  Recipe:         '{weights[0]['recipe']}'")
            print(f"  BatchCode:      '{weights[0]['batch']}'")
            print(f"  ProductionOrder:'{weights[0]['order']}'")
            
            print(f"\n[GLOBAL BATCH - g*]")
            print(f"  gTotalPieces:          {total}")
            print(f"  gTotalPiecesApproved:  {accepted}")
            print(f"  gTotalPiecesOK:        {accepted}")
            print(f"  gTotalPieces-:         {rejected_under}")
            print(f"  gTotalPieces+:         {rejected_over}")
            print(f"  gAverageWeight:        {sum(weight_vals)/len(weight_vals)/1000:.3f} g")
            print(f"  gMeanError:            {sum(delta_vals)/len(delta_vals)/1000:+.3f} g")
            
            # Deviazione standard
            mean = sum(weight_vals) / len(weight_vals)
            variance = sum((x - mean)**2 for x in weight_vals) / len(weight_vals)
            std_dev = variance ** 0.5
            print(f"  gStandardDeviation:    {std_dev:.0f} mg")
            
            print(f"\n[ULTIMA PESATA]")
            last = weights[-1]
            print(f"  LastWeight_mg:      {last['weight_mg']}")
            print(f"  LastWeightFlags:    0x{last['classification'].upper() if last['classification'] else '0'}")
            print(f"  BatchOpened:        1 (aperto)")
        
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sock.close()
        print("\n[CHUSO]")

if __name__ == "__main__":
    main()