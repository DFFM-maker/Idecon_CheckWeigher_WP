#!/usr/bin/env python3
"""
Simulazione Errore 30 - Negative Mean Error
Test gestione allarme bilancia
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

def parse_event(msg):
    """Parsa messaggio EVENT"""
    if not msg.startswith("EVENT="):
        return None
    
    data = msg[6:]
    parts = data.split("|")
    
    if len(parts) >= 8:
        event_code_str = parts[6].replace("Cod.", "").strip()
        try:
            event_code = int(event_code_str)
            return {
                'timestamp': parts[0],
                'event_code': event_code,
                'description': parts[7],
                'raw': msg
            }
        except:
            pass
    return None

def main():
    print("="*70)
    print("SIMULAZIONE ERRORE 30 - NEGATIVE MEAN ERROR")
    print("="*70)
    print("\nQuesto test monitora l'arrivo dell'errore 30")
    print("e verifica la gestione con RESETERRORI\n")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        print(f"Connessione a {IDEON_IP}:{IDEON_PORT}...")
        sock.connect((IDEON_IP, IDEON_PORT))
        print("[OK] Connesso!\n")
        
        # Imposta filtro per ricevere errori ed eventi
        print("Configurazione MSGFILTER (errori + eventi + pesi)...")
        resp = send_command(sock, "MSGFILTER=23")  # Bit 0+1+2+4 = 1+2+4+16 = 23
        print(f"Risposta: {resp}\n")
        
        error_30_detected = False
        weight_count = 0
        weights = []
        
        print("="*70)
        print("MONITORAGGIO (120 secondi)")
        print("="*70)
        print("Aspettando errori 30 o pesate...")
        print("(Invia prodotti leggeri < 224g per simulare errore)\n")
        
        start_time = time.time()
        last_poll = 0
        
        while time.time() - start_time < 120:
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
                        
                        # Controlla EVENT
                        if msg.startswith("EVENT="):
                            event = parse_event(msg)
                            if event:
                                print(f"\n[{ts}] EVENTO #{event['event_code']}")
                                print(f"  Descrizione: {event['description']}")
                                print(f"  Raw: {event['raw'][:80]}")
                                
                                if event['event_code'] == 30:
                                    print(f"\n  ⚠️  ERRORE 30 RILEVATO!")
                                    print(f"  Negative Mean Error - Il peso medio è sotto il nominale")
                                    error_30_detected = True
                                    
                                    # Prova a resettare
                                    print(f"\n  Tentativo RESETERRORI...")
                                    resp = send_command(sock, "RESETERRORI")
                                    print(f"  Risposta: {resp}")
                                    time.sleep(2)
                                    
                                    # Verifica stato dopo reset
                                    resp = send_command(sock, "STATSV")
                                    print(f"  Stato dopo reset: {resp}")
                        
                        # Controlla ERRORI
                        elif msg.startswith("ERRNUM="):
                            err_code = msg[7:]
                            print(f"\n[{ts}] ERRNUM: Codice errore attivo = {err_code}")
                        
                        # Controlla WEIGHT
                        elif msg.startswith("WEIGHT="):
                            weight_count += 1
                            # Estrai peso
                            parts = msg[7:].split("|")
                            if len(parts) >= 8:
                                weight_mg = int(parts[6])
                                weight_g = weight_mg / 1000.0
                                delta_mg = int(parts[7])
                                weights.append(weight_g)
                                
                                # Calcola media
                                if len(weights) > 0:
                                    avg = sum(weights) / len(weights)
                                    status = "⚠️ SOTTO" if avg < 224 else "✅ OK"
                                    
                                    print(f"[{ts}] Peso #{weight_count}: {weight_g:.1f}g | Media: {avg:.1f}g {status}", end="\r")
                        
                        # Altri messaggi
                        elif not msg.startswith("STATSV") and not msg.startswith("MSGFILTER"):
                            if len(msg.strip()) > 0:
                                print(f"[{ts}] {msg[:60]}")
                                
                except Exception as e:
                    pass
            
            time.sleep(0.1)
        
        # Riepilogo
        print("\n\n" + "="*70)
        print("RIEPILOGO")
        print("="*70)
        print(f"Pesi ricevuti: {weight_count}")
        if weights:
            avg = sum(weights) / len(weights)
            print(f"Peso medio: {avg:.2f}g (nominale: 224g)")
            print(f"Errore medio: {avg - 224:.2f}g")
        print(f"Errore 30 rilevato: {'SÌ' if error_30_detected else 'NO'}")
        
        if not error_30_detected:
            print("\n⚠️  Nessun errore 30 ricevuto.")
            print("Possibili cause:")
            print("  - Non sono state fatte abbastanza pesate sotto il nominale")
            print("  - Il 'Negative mean error delay time' è troppo lungo")
            print("  - L'opzione è disabilitata nella configurazione")
        
    except KeyboardInterrupt:
        print("\n\n[Interrotto dall'utente]")
    except Exception as e:
        print(f"\n[ERROR] {e}")
    finally:
        sock.close()
        print("\n[DISCONNESSO]")

if __name__ == "__main__":
    main()