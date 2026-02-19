#!/usr/bin/env python3
"""
Test Simulazione PLC - Timing realistici per identificare G_System_Error
"""

import socket
import time
import sys

IDEON_IP = '172.16.224.210'
IDEON_PORT = 50000

# Timing realistici PLC NJ
PLC_CYCLE_TIME_MS = 2      # Task ciclico ogni 2ms
PLC_TIMEOUT_RX = 100       # Timeout ricezione 100ms
PLC_TIMEOUT_CONNECT = 5000 # Timeout connessione 5s

def create_idecon_command(command: str) -> bytes:
    return b'\x02' + command.encode('ascii') + b'\x03'

def parse_response(data: bytes) -> str:
    if data and len(data) >= 2:
        if data[0] == 0x02:
            data = data[1:]
        if data[-1] == 0x03:
            data = data[:-1]
    return data.decode('ascii', errors='replace')

def simulate_plc_behavior():
    """Simula comportamento PLC NJ"""
    print("="*60)
    print("SIMULAZIONE COMPORTAMENTO PLC NJ")
    print("="*60)
    print(f"PLC Cycle Time: {PLC_CYCLE_TIME_MS}ms")
    print(f"PLC RX Timeout: {PLC_TIMEOUT_RX}ms")
    print()
    
    errors = []
    connection_lost = 0
    rx_timeouts = 0
    parse_errors = 0
    weights_received = 0
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(PLC_TIMEOUT_CONNECT)
    
    try:
        # Simula ENABLE
        print("[ENABLE] Connessione...")
        sock.connect((IDEON_IP, IDEON_PORT))
        print("    OK")
        
        # Invia MSGFILTER
        sock.sendall(create_idecon_command("MSGFILTER=17"))
        response = sock.recv(512)
        print(f"    MSGFILTER set: {parse_response(response)}")
        
        # Simula polling loop
        print(f"\n[RUN] Polling per 60 secondi...")
        print("-"*60)
        
        cycle_count = 0
        start_time = time.time()
        poll_interval = 0.5  # Polling STATSV ogni 500ms
        
        last_poll_time = 0
        last_weight_time = 0
        
        while time.time() - start_time < 60:
            cycle_start = time.perf_counter()
            
            current_time = time.time()
            
            # Polling STATSV ogni 500ms
            if current_time - last_poll_time >= poll_interval:
                try:
                    sock.settimeout(PLC_TIMEOUT_RX)
                    sock.sendall(create_idecon_command("STATSV"))
                    response = sock.recv(512)
                    resp_str = parse_response(response)
                    
                    if resp_str.startswith("STATSV="):
                        mode = resp_str.split("=")[1][:3]
                        print(f"    [{cycle_count}] STATSV={mode}")
                    else:
                        parse_errors += 1
                        
                except socket.timeout:
                    rx_timeouts += 1
                    errors.append(f"RX_TIMEOUT at cycle {cycle_count}")
                except Exception as e:
                    errors.append(f"ERROR at cycle {cycle_count}: {e}")
                    connection_lost += 1
                    break
                
                last_poll_time = current_time
            
            # Ricezione dati (non-blocking in realta, ma qui simuliamo)
            try:
                sock.settimeout(0.01)  # 10ms timeout
                data = sock.recv(512, socket.MSG_DONTWAIT)
                if data:
                    resp_str = parse_response(data)
                    if resp_str.startswith("WEIGHT="):
                        weights_received += 1
                        parts = resp_str.split("|")
                        if len(parts) >= 7:
                            weight = parts[6] if len(parts) > 6 else "?"
                            print(f"    [WEIGHT] {weight}g")
                    elif resp_str.startswith("STATP="):
                        print(f"    [STATP] Received")
            except BlockingIOError:
                pass
            except Exception as e:
                pass
            
            cycle_count += 1
            
            # Simula ciclo PLC
            cycle_time = (time.perf_counter() - cycle_start) * 1000
            sleep_time = max(0, PLC_CYCLE_TIME_MS - cycle_time) / 1000
            time.sleep(sleep_time)
        
        print("-"*60)
        
    except socket.timeout:
        print("TIMEOUT connessione")
        connection_lost += 1
    except Exception as e:
        print(f"ERRORE: {e}")
        errors.append(str(e))
    finally:
        sock.close()
    
    # Riepilogo errori
    print(f"\n{'='*60}")
    print("RIEPILOGO SIMULAZIONE")
    print(f"{'='*60}")
    print(f"Durata test: 60s")
    print(f"Cicli eseguiti: {cycle_count}")
    print(f"Pesate ricevute: {weights_received}")
    print(f"RX Timeouts: {rx_timeouts}")
    print(f"Parse Errors: {parse_errors}")
    print(f"Connection Lost: {connection_lost}")
    
    if errors:
        print(f"\nErrori ({len(errors)}):")
        for e in errors[:10]:
            print(f"  - {e}")
    
    # Raccomandazioni
    print(f"\n{'='*60}")
    print("ANALISI")
    print(f"{'='*60}")
    
    if rx_timeouts > 10:
        print(f"PROBLEMA: {rx_timeouts} timeout di ricezione")
        print("  - Aumentare timeout RX nel PLC (attuale: {PLC_TIMEOUT_RX}ms)")
        print("  - Verificare carico CPU PLC")
        print("  - Verificare priorità task")
    elif connection_lost > 0:
        print(f"PROBLEMA: {connection_lost} connessioni perse")
        print("  - Verificare cavo di rete")
        print("  - Verificare impostazioni firewall")
    elif weights_received == 0:
        print("ATTENZIONE: Nessuna pesata ricevuta")
        print("  - Verificare che la bilancia sia in RUN")
        print("  - Verificare MSGFILTER (attuale: 17 = WEIGHT + risposte)")
    else:
        print("TEST OK - Connessione stabile")
        print("  - Il problema potrebbe essere nel codice PLC")
        print("  - Verificare parsing risposte")
        print("  - Verificare gestione errori in FB_IDECON_Client")

def quick_weight_monitor():
    """Monitor pesate in tempo reale"""
    print("="*60)
    print("MONITOR PESATE (Ctrl+C per uscire)")
    print("="*60)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        sock.connect((IDEON_IP, IDEON_PORT))
        print("Connesso. In attesa pesate...\n")
        
        # Configura MSGFILTER per ricevere WEIGHT
        sock.sendall(create_idecon_command("MSGFILTER=17"))
        
        weights = []
        start = time.time()
        
        while True:
            try:
                data = sock.recv(512)
                if data:
                    resp = parse_response(data)
                    if resp.startswith("WEIGHT="):
                        parts = resp.split("|")
                        if len(parts) >= 8:
                            ts = parts[0].replace("WEIGHT=", "")
                            weight = parts[6]
                            delta = parts[7]
                            cls = parts[8]
                            
                            weight_val = int(weight)
                            delta_val = int(delta)
                            
                            # Classificazione
                            expelled = (int(cls) & 0x100) > 0 or (int(cls) & 0x8000) > 0
                            status = "EXPELLED" if expelled else "OK"
                            
                            now = time.strftime("%H:%M:%S")
                            print(f"[{now}] {weight}g (delta: {delta_val:+d}g) [{status}]")
                            
                            weights.append(weight_val)
                            
            except BlockingIOError:
                pass
                
    except KeyboardInterrupt:
        print("\n\nInterrotto.")
    except Exception as e:
        print(f"\nErrore: {e}")
    finally:
        sock.close()
        
    if weights:
        print(f"\nStatistiche ({len(weights)} pesate):")
        print(f"  Media: {sum(weights)/len(weights):.1f}g")
        print(f"  Min: {min(weights)}g")
        print(f"  Max: {max(weights)}g")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        quick_weight_monitor()
    else:
        simulate_plc_behavior()