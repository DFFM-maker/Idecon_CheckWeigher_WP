#!/usr/bin/env python3
"""
Analyzer Dati Pesate - Simulazione comportamento PLC
Identifica possibili cause di G_System_Error
"""

import socket
import time
from collections import deque

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

class PLCSimulator:
    """Simula comportamento PLC NJ con diagnostica"""
    
    def __init__(self):
        self.errors = {
            'connect_error': 0,
            'send_error': 0,
            'recv_error': 0,
            'timeout': 0,
            'parse_error': 0,
            'data_valid_error': 0,
        }
        self.weights = []
        self.weight_timestamps = []
        self.connection_lost_events = []
        self.last_weight_time = 0
        self.weight_gap_warnings = []
        
    def simulate_cycle(self, cycle_data: dict):
        """Simula un ciclo PLC e rileva errori"""
        # Simulazione timeout (se nessun dato per > 200ms)
        time_since_last = time.time() - self.last_weight_time
        if time_since_last > 0.2:
            if cycle_data.get('has_data', False):
                self.last_weight_time = time.time()
            else:
                self.errors['timeout'] += 1
                if len(self.weights) > 0:
                    self.weight_gap_warnings.append(time_since_last)
        
        # Errore connessione
        if not cycle_data.get('connected', True):
            self.errors['connect_error'] += 1
            self.connection_lost_events.append(time.time())
        
        # Errore parsing
        if cycle_data.get('parse_error', False):
            self.errors['parse_error'] += 1
        
        # Peso non valido
        if cycle_data.get('weight_valid', True) == False:
            self.errors['data_valid_error'] += 1

def analyze_weights(raw_data):
    """Analizza dati pesate per simulazione"""
    weights = []
    for entry in raw_data:
        if 'WEIGHT=' in entry:
            parts = entry.split('|')
            if len(parts) >= 8:
                w = int(parts[6])  # peso in mg
                d = int(parts[7])  # delta
                cls = int(parts[8]) if len(parts) > 8 else 0
                ts = entry.split('|')[0].replace('WEIGHT=', '')
                weights.append({'weight_mg': w, 'delta': d, 'cls': cls, 'ts': ts})
    return weights

def main():
    print("="*70)
    print("ANALYZER DATI PESATE - SIMULAZIONE PLC")
    print("="*70)
    
    # Dati reali dalle pesate
    raw_data = [
        "WEIGHT=2026.02.10 13:08:31:466|||225g|codeline|ID 02792|212300|-11700|540|",
        "WEIGHT=2026.02.10 13:08:58:564|||225g|codeline|ID 02792|221200|-2800|10480|NEWPIECEDIFF=-0000028NEWPIECE=+0002212",
        "WEIGHT=2026.02.10 13:09:02:295|||225g|codeline|ID 02792|215500|-8500|10480|",
        "WEIGHT=2026.02.10 13:09:06:840|||225g|codeline|ID 02792|224700|700|20480|",
        "WEIGHT=2026.02.10 13:09:09:930|||225g|codeline|ID 02792|220300|-3700|10480|",
        "WEIGHT=2026.02.10 13:09:12:701|||225g|codeline|ID 02792|224900|900|20480|",
    ]
    
    weights = analyze_weights(raw_data)
    
    print(f"\nDATI PESATE ({len(weights)} pesi):")
    print("-"*70)
    print(f"{'Timestamp':<25} {'Peso(mg)':<10} {'Peso(g)':<10} {'Delta(g)':<10} {'Class':<8} {'Status'}")
    print("-"*70)
    
    for w in weights:
        status = "EXPELLED" if (w['cls'] & 0x100) > 0 or (w['cls'] & 0x8000) > 0 else "OK"
        print(f"{w['ts']:<25} {w['weight_mg']:<10} {w['weight_mg']/1000:<10.1f} {w['delta']/1000:+<10.1f} {w['cls']:<8} {status}")
    
    # Calcolo statistiche
    weight_vals = [w['weight_mg'] for w in weights]
    avg = sum(weight_vals) / len(weight_vals)
    min_w = min(weight_vals)
    max_w = max(weight_vals)
    
    print("\n" + "="*70)
    print("STATISTICHE")
    print("="*70)
    print(f"Media: {avg:.0f}mg ({avg/1000:.1f}g)")
    print(f"Min: {min_w}mg ({min_w/1000:.1f}g)")
    print(f"Max: {max_w}mg ({max_w/1000:.1f}g)")
    print(f"Range: {max_w - min_w}mg ({max_w - min_w}mg / 1000 = {(max_w - min_w)/1000:.1f}g)")
    print(f"Dev.std: {((sum((x-avg)**2 for x in weight_vals)/len(weight_vals))**0.5):.0f}mg")
    
    # Calcolo KPI per DT_Idecon_BatchStats
    accepted = sum(1 for w in weights if w['delta'] >= -5000 and w['delta'] <= 5000)  # +/- 5g tolleranza
    rejected_under = sum(1 for w in weights if w['delta'] < -5000)
    rejected_over = sum(1 for w in weights if w['delta'] > 5000)
    total = len(weights)
    
    print("\n" + "="*70)
    print("KPI BATCH (simulati)")
    print("="*70)
    print(f"TotalProducts: {total}")
    print(f"AcceptedProducts: {accepted} (tolleranza +/-5g)")
    print(f"RejectedUnderweight: {rejected_under}")
    print(f"RejectedOverweight: {rejected_over}")
    print(f"Yield%: {(accepted/total)*100:.1f}%")
    print(f"TotalWeight_kg: {sum(weight_vals)/1000/1000:.3f}kg")
    print(f"AverageWeight_g: {avg/1000:.1f}g")
    
    # Test connessione real-time
    print("\n" + "="*70)
    print("TEST CONNESSIONE REAL-TIME (30s)")
    print("="*70)
    
    plc = PLCSimulator()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        sock.connect((IDEON_IP, IDEON_PORT))
        print("Connesso!")
        
        # Invia MSGFILTER
        sock.sendall(create_idecon_command("MSGFILTER=17"))
        print("MSGFILTER=17 inviato")
        
        # Loop 30s
        start = time.time()
        last_statsv = 0
        weights_received = []
        
        while time.time() - start < 30:
            # Polling STATSV ogni 2s
            if time.time() - last_statsv > 2:
                try:
                    sock.settimeout(1)
                    sock.sendall(create_idecon_command("STATSV"))
                    resp = sock.recv(256)
                    print(f"[{time.strftime('%H:%M:%S')}] STATSV={parse_response(resp)[:20]}...")
                except socket.timeout:
                    plc.errors['timeout'] += 1
                    print(f"[{time.strftime('%H:%M:%S')}] Timeout STATSV")
                last_statsv = time.time()
            
            # Ricezione dati
            try:
                sock.settimeout(0.1)
                data = sock.recv(512, socket.MSG_DONTWAIT)
                if data:
                    resp = parse_response(data)
                    if resp.startswith("WEIGHT="):
                        parts = resp.split('|')
                        w = int(parts[6])
                        d = int(parts[7])
                        print(f"[{time.strftime('%H:%M:%S')}] WEIGHT: {w}mg ({d:+d})")
                        weights_received.append(w)
                        plc.last_weight_time = time.time()
            except BlockingIOError:
                pass
            
            time.sleep(0.01)
        
        print(f"\nRicevute {len(weights_received)} pesate aggiuntive")
        
    except Exception as e:
        print(f"Errore: {e}")
    finally:
        sock.close()
    
    # Riepilogo errori
    print("\n" + "="*70)
    print("RIEPILOGO ERRORI SIMULAZIONE")
    print("="*70)
    for err, count in plc.errors.items():
        if count > 0:
            print(f"  {err}: {count}")
    
    if all(v == 0 for v in plc.errors.values()):
        print("  Nessun errore rilevato!")

if __name__ == "__main__":
    main()