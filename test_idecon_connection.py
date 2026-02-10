#!/usr/bin/env python3
"""
Test Connessione Bilancia IDECON
IP: 172.16.224.210 | Port: 50000
Protocollo: STX + [comando] + ETX (byte values 0x02 e 0x03)
"""

import socket
import time
import sys

# Configurazione
IDEON_IP = '172.16.224.210'
IDEON_PORT = 50000
TIMEOUT = 5.0

def create_idecon_command(command: str) -> bytes:
    """Costruisce comando protocollo IDECON (STX + cmd + ETX)"""
    return b'\x02' + command.encode('ascii') + b'\x03'

def parse_response(data: bytes) -> str:
    """Parsa risposta rimuovendo STX/ETX e convertendo in stringa"""
    if len(data) < 2:
        return data.decode('ascii', errors='replace')
    
    # Rimuovi STX (0x02) e ETX (0x03)
    if data[0] == 0x02:
        data = data[1:]
    if data[-1] == 0x03:
        data = data[:-1]
    
    return data.decode('ascii', errors='replace')

def test_connection():
    """Test completo connessione bilancia"""
    print(f"{'='*60}")
    print(f"TEST CONNESSIONE BILANCIA IDECON")
    print(f"{'='*60}")
    print(f"Target: {IDEON_IP}:{IDEON_PORT}")
    print()
    
    sock = None
    try:
        # 1. Creazione socket
        print("[1] Creazione socket TCP...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        print("    OK - Socket creato")
        
        # 2. Connessione
        print(f"[2] Connessione a {IDEON_IP}:{IDEON_PORT}...")
        sock.connect((IDEON_IP, IDEON_PORT))
        print("    OK - Connesso!")
        
        connected_time = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"    Timestamp: {connected_time}")
        
        # 3. Invia STATSV (stato macchina)
        print("[3] Invio comando STATSV...")
        statsv_cmd = create_idecon_command("STATSV")
        sock.sendall(statsv_cmd)
        print(f"    TX ({len(statsv_cmd)} bytes): {statsv_cmd.hex().upper()}")
        
        # 4. Ricevi risposta STATSV
        print("[4] Attesa risposta STATSV...")
        response = sock.recv(512)
        if response:
            response_str = parse_response(response)
            print(f"    RX ({len(response)} bytes): {response.hex().upper()}")
            print(f"    Parsed: {response_str}")
        else:
            print("    Nessuna risposta ricevuta")
            
        # 5. Invia STATREQ (richiesta statistiche)
        print()
        print("[5] Invio comando STATREQ (statistiche)...")
        statreq_cmd = create_idecon_command("STATREQ")
        sock.sendall(statreq_cmd)
        print(f"    TX ({len(statreq_cmd)} bytes): {statreq_cmd.hex().upper()}")
        
        # 6. Ricevi risposta STATP
        print("[6] Attesa risposta STATP...")
        response = sock.recv(512)
        if response:
            response_str = parse_response(response)
            print(f"    RX ({len(response)} bytes): {response.hex().upper()}")
            print(f"    Parsed: {response_str}")
        else:
            print("    Nessuna risposta ricevuta")
            
        # 7. Test Keep-alive (attendiamo eventuali pesate automatiche)
        print()
        print("[7] Attesa 2s per eventuali pesate automatiche...")
        time.sleep(2)
        
        # Prova a ricevere dati extra
        sock.setblocking(False)
        try:
            extra_data = sock.recv(512)
            if extra_data:
                print(f"    RX aggiuntivo ({len(extra_data)} bytes): {extra_data.hex().upper()}")
                extra_str = parse_response(extra_data)
                print(f"    Parsed: {extra_str}")
        except BlockingIOError:
            print("    Nessun dato aggiuntivo")
        
        print()
        print("="*60)
        print("TEST COMPLETATO CON SUCCESSO!")
        print("="*60)
        return True
        
    except socket.timeout:
        print(f"\nERRORE: Timeout connessione ({TIMEOUT}s)")
        return False
    except socket.error as e:
        print(f"\nERRORE Socket: {e}")
        return False
    except Exception as e:
        print(f"\nERRORE: {e}")
        return False
    finally:
        if sock:
            sock.close()
            print("\nSocket chiuso")

def quick_test():
    """Test rapido singolo comando"""
    print("QUICK TEST - Invio solo comando STATSV")
    print("-" * 40)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIMEOUT)
    
    try:
        sock.connect((IDEON_IP, IDEON_PORT))
        print(f"Connesso a {IDEON_IP}:{IDEON_PORT}")
        
        # Invia STATSV
        cmd = b'\x02STATSV\x03'
        sock.sendall(cmd)
        print(f"Inviato: {cmd.hex()}")
        
        # Ricevi
        data = sock.recv(512)
        if data:
            print(f"Ricevuto: {data.hex()}")
            print(f"Risposta: {parse_response(data)}")
        else:
            print("Nessuna risposta")
            
    except Exception as e:
        print(f"Errore: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        quick_test()
    else:
        test_connection()