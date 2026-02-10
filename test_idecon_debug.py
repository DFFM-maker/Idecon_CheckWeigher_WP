#!/usr/bin/env python3
"""
Test Connessione Bilancia IDECON - Versione Debug
Diagnostica completa per identificare problemi di comunicazione
"""

import socket
import time
import sys
import subprocess

# Fix output encoding for Windows
try:
    subprocess.run(['chcp', '65001'], capture_output=True)
except:
    pass

IDEON_IP = '172.16.224.210'
IDEON_PORT = 50000
TIMEOUT = 3.0

def create_idecon_command(command: str) -> bytes:
    return b'\x02' + command.encode('ascii') + b'\x03'

def parse_response(data: bytes) -> str:
    if len(data) < 2:
        return data.decode('ascii', errors='replace')
    if data[0] == 0x02:
        data = data[1:]
    if data[-1] == 0x03:
        data = data[:-1]
    return data.decode('ascii', errors='replace')

def measure_latency(sock, command: str, iterations: int = 5) -> list:
    """Misura latenza di risposta"""
    latencies = []
    
    for i in range(iterations):
        start = time.perf_counter()
        sock.sendall(create_idecon_command(command))
        
        sock.settimeout(TIMEOUT)
        try:
            response = b''
            while True:
                chunk = sock.recv(256)
                if not chunk:
                    break
                response += chunk
                if len(response) > 10:
                    break
        except socket.timeout:
            latencies.append(None)
            continue
            
        end = time.perf_counter()
        latency_ms = (end - start) * 1000
        latencies.append(latency_ms)
        time.sleep(0.1)
    
    return latencies

def test_command_sequence(sock, commands: list) -> dict:
    """Testa sequenza di comandi"""
    results = {}
    
    for cmd in commands:
        results[cmd] = {'success': False, 'response': '', 'time_ms': 0}
        
        try:
            start = time.perf_counter()
            sock.sendall(create_idecon_command(cmd))
            
            sock.settimeout(TIMEOUT)
            response = sock.recv(512)
            end = time.perf_counter()
            
            if response:
                results[cmd]['success'] = True
                results[cmd]['response'] = parse_response(response)
                results[cmd]['time_ms'] = round((end - start) * 1000, 2)
                
        except socket.timeout:
            results[cmd]['error'] = 'TIMEOUT'
        except Exception as e:
            results[cmd]['error'] = str(e)
    
    return results

def test_reconnection(stability_seconds: int = 10):
    """Test stabilita connessione"""
    print(f"\n{'-'*60}")
    print(f"TEST STABILITA' ({stability_seconds}s)")
    print(f"{'-'*60}")
    
    errors = []
    start_time = time.time()
    
    while time.time() - start_time < stability_seconds:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        
        try:
            sock.connect((IDEON_IP, IDEON_PORT))
            sock.sendall(create_idecon_command("STATSV"))
            response = sock.recv(512)
            
            if response and parse_response(response).startswith("STATSV="):
                pass
            else:
                errors.append(f"Risposta non valida: {response}")
                
        except socket.timeout:
            errors.append("TIMEOUT")
        except ConnectionRefusedError:
            errors.append("CONNECTION_REFUSED")
        except Exception as e:
            errors.append(f"ERRORE: {e}")
        finally:
            sock.close()
        
        time.sleep(0.5)
    
    print(f"Test completato. Errori: {len(errors)}")
    if errors:
        print("Errori rilevati:")
        for e in errors[:10]:
            print(f"  - {e}")
    
    return len(errors)

def main():
    print(f"{'='*60}")
    print("TEST DIAGNOSTICO BILANCIA IDECON")
    print(f"{'='*60}")
    print(f"Target: {IDEON_IP}:{IDEON_PORT}")
    print(f"Timeout: {TIMEOUT}s")
    print()
    
    commands_to_test = [
        'STATSV',
        'STATREQ',
        'WEIGHT?',
        'MSGFILTER=17',
    ]
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    
    try:
        # 1. Connessione
        print("[1] Connessione...")
        sock.connect((IDEON_IP, IDEON_PORT))
        print("    OK")
        
        # 2. Test comandi
        print(f"\n[2] Test sequenza comandi ({len(commands_to_test)} comandi)...")
        results = test_command_sequence(sock, commands_to_test)
        
        print()
        for cmd, res in results.items():
            status = "OK" if res['success'] else "FAIL"
            print(f"  [{status}] {cmd}: {res.get('response', res.get('error', 'N/A'))} ({res.get('time_ms', 'N/A')}ms)")
        
        # 3. Latenza STATSV
        print(f"\n[3] Misurazione latenza STATSV...")
        latencies = measure_latency(sock, "STATSV", 5)
        valid = [l for l in latencies if l is not None]
        if valid:
            print(f"  Media: {sum(valid)/len(valid):.2f}ms")
            print(f"  Min: {min(valid):.2f}ms")
            print(f"  Max: {max(valid):.2f}ms")
        
        # 4. Loop ricezione
        print(f"\n[4] Loop ricezione (30s) - in attesa pesate automatiche...")
        sock.setblocking(False)
        data_count = 0
        last_data = time.time()
        
        for i in range(30):
            time.sleep(1)
            try:
                data = sock.recv(512)
                if data:
                    data_count += 1
                    last_data = time.time()
                    print(f"    [{i+1}s] RX: {parse_response(data)}")
            except BlockingIOError:
                pass
        
        if data_count == 0:
            print("    Nessuna pesata automatica ricevuta")
        print(f"    Totale messaggi: {data_count}")
        
        # 5. Test stabilita
        test_reconnection(5)
        
        # Riepilogo
        print(f"\n{'='*60}")
        print("RIEPILOGO")
        print(f"{'='*60}")
        
        success_cmds = sum(1 for r in results.values() if r['success'])
        print(f"Comandi riusciti: {success_cmds}/{len(commands_to_test)}")
        print(f"Pesate ricevute: {data_count}")
        
        if success_cmds == len(commands_to_test):
            print("\n[OK] COMUNICAZIONE BASICA OK")
            print("Il problema potrebbe essere:")
            print("  - Timeout nel PLC (troppo breve)")
            print("  - Carico CPU sul PLC")
            print("  - Task ciclico troppo lento")
            print("  - Errori durante parsing/statistics update")
        else:
            print("\n[FAIL] PROBLEMI DI COMUNICAZIONE")
        
    except Exception as e:
        print(f"\nERRORE: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()