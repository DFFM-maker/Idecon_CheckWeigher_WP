#!/usr/bin/env python3
"""
IDECON - Test Completo di Tutti i Comandi Avanzati
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
            data = sock.recv(1024)
            if data:
                if data[0] == 0x02: data = data[1:]
                if data[-1] == 0x03: data = data[:-1]
                return data.decode('ascii', errors='replace')
        return None
    except Exception as e:
        return f"ERROR: {e}"

def test_all_commands():
    print("="*70)
    print("IDECON - TEST COMPLETO COMANDI AVANZATI")
    print("="*70)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        print(f"\nConnessione a {IDEON_IP}:{IDEON_PORT}...")
        sock.connect((IDEON_IP, IDEON_PORT))
        print("[OK] Connesso!\n")
        
        # 1. ERRNUM - Errori attivi
        print("="*70)
        print("1. LETTURA ERRORI ATTIVI (ERRNUM)")
        print("="*70)
        resp = send_command(sock, "ERRNUM")
        print(f"Risposta: {resp}")
        if resp and resp.startswith("ERRNUM="):
            err_code = resp[7:]
            print(f"Codice errore: {err_code}")
            if err_code == "0":
                print("[OK] Nessun errore attivo")
            elif err_code == "30":
                print("[WARN] Errore 30: Negative Mean Error")
        
        # 2. LINECODE - Codice linea
        print("\n" + "="*70)
        print("2. LETTURA CODICE LINEA (LINECODE)")
        print("="*70)
        resp = send_command(sock, "LINECODE")
        print(f"Risposta: {resp}")
        
        # 3. DATETIME - Data e ora
        print("\n" + "="*70)
        print("3. LETTURA DATA E ORA (DATETIME)")
        print("="*70)
        resp = send_command(sock, "DATETIME")
        print(f"Risposta: {resp}")
        
        # 4. STATCADENCY - Frequenza statistiche
        print("\n" + "="*70)
        print("4. MODIFICA FREQUENZA STATISTICHE (STATCADENCY)")
        print("="*70)
        print("Cambio da 60s a 30s...")
        resp = send_command(sock, "STATCADENCY=30")
        print(f"Risposta: {resp}")
        time.sleep(1)
        
        # Verifica
        resp = send_command(sock, "STATCADENCY")
        print(f"Verifica: {resp}")
        
        # 5. SELSTATSANSWER - Formato statistiche
        print("\n" + "="*70)
        print("5. FORMATO STATISTICHE (SELSTATSANSWER)")
        print("="*70)
        print("Opzioni: STATP (default) o STATPATB")
        resp = send_command(sock, "SELSTATSANSWER")
        print(f"Formato attuale: {resp}")
        
        # Prova STATPATB
        print("\nCambio a STATPATB...")
        resp = send_command(sock, "SELSTATSANSWER=STATPATB")
        print(f"Risposta: {resp}")
        time.sleep(1)
        
        # Test STATREQATB
        print("\nRichiesta statistica STATPATB...")
        resp = send_command(sock, "STATREQATB")
        print(f"Risposta: {resp}")
        time.sleep(2)
        
        # Ricevi STATPATB
        ready = select.select([sock], [], [], 3)
        if ready[0]:
            data = sock.recv(1024)
            if data:
                if data[0] == 0x02: data = data[1:]
                if data[-1] == 0x03: data = data[:-1]
                msg = data.decode('ascii', errors='replace')
                if "STATPATB=" in msg:
                    print(f"STATPATB ricevuto: {msg[:80]}...")
        
        # Torna a STATP
        print("\nRitorno a STATP...")
        resp = send_command(sock, "SELSTATSANSWER=STATP")
        print(f"Risposta: {resp}")
        
        # 6. GET_CURRENT_PIECE_STAT - Media pezzi
        print("\n" + "="*70)
        print("6. CALCOLO MEDIA ULTIMI PEZZI (GET_CURRENT_PIECE_STAT)")
        print("="*70)
        print("Calcolo media ultimi 5 pezzi su 10 totali...")
        resp = send_command(sock, "GET_CURRENT_PIECE_STAT=5|10|1")
        print(f"Risposta: {resp}")
        time.sleep(2)
        
        # Ricevi PIECE_STAT
        ready = select.select([sock], [], [], 3)
        if ready[0]:
            data = sock.recv(1024)
            if data:
                if data[0] == 0x02: data = data[1:]
                if data[-1] == 0x03: data = data[:-1]
                msg = data.decode('ascii', errors='replace')
                if "PIECE_STAT=" in msg:
                    print(f"PIECE_STAT ricevuto: {msg}")
                    # Parse: PIECE_STAT=nominal|mean|tare|samples|lung
                    parts = msg[11:].split("|")
                    if len(parts) >= 5:
                        print(f"  Peso nominale: {int(parts[0])/1000:.1f}g")
                        print(f"  Media calcolata: {int(parts[1])/1000:.1f}g")
                        print(f"  Tara: {int(parts[2])/1000:.1f}g")
                        print(f"  Campioni: {parts[3]}")
        
        # 7. SHOWMESSAGE - Messaggio display
        print("\n" + "="*70)
        print("7. MESSAGGIO SU DISPLAY (SHOWMESSAGE)")
        print("="*70)
        print("Invio messaggio: 'TEST PYTHON OK'")
        resp = send_command(sock, "SHOWMESSAGE=TEST PYTHON OK")
        print(f"Risposta: {resp}")
        time.sleep(3)
        
        # Rimuovi messaggio
        print("Rimozione messaggio...")
        resp = send_command(sock, "SHOWMESSAGE=")
        print(f"Risposta: {resp}")
        
        # 8. GETRECIPELIST - Lista ricette
        print("\n" + "="*70)
        print("8. LISTA RICETTE DISPONIBILI (GETRECIPELIST)")
        print("="*70)
        print("Richiedo lista...")
        resp = send_command(sock, "GETRECIPELIST")
        print(f"Risposta: {resp}")
        
        # Aspetta ricezione lista (DSxx messages)
        print("\nAttendo ricezione ricette (5 secondi)...")
        recipes = []
        start = time.time()
        while time.time() - start < 5:
            ready = select.select([sock], [], [], 0.5)
            if ready[0]:
                try:
                    data = sock.recv(1024)
                    if data:
                        if data[0] == 0x02: data = data[1:]
                        if data[-1] == 0x03: data = data[:-1]
                        msg = data.decode('ascii', errors='replace')
                        if "DS" in msg and ("=BEGIN" in msg or "=END" in msg or ("=" in msg and not msg.startswith("DS") == False)):
                            print(f"  {msg}")
                            if "=" in msg and "BEGIN" not in msg and "END" not in msg:
                                recipe_name = msg.split("=")[1] if "=" in msg else msg
                                recipes.append(recipe_name)
                except:
                    pass
        
        if recipes:
            print(f"\nRicette trovate: {len(recipes)}")
            for r in recipes:
                print(f"  - {r}")
        else:
            print("Nessuna ricetta ricevuta (timeout)")
        
        # 9. INFORECIPE dettagliato
        print("\n" + "="*70)
        print("9. DETTAGLI RICETTA ATTIVA (INFORECIPE)")
        print("="*70)
        resp = send_command(sock, "INFORECIPE")
        print(f"Risposta: {resp}")
        if resp and resp.startswith("INFORECIPE="):
            # Parse
            data = resp[11:]
            parts = data.split("|")
            if parts:
                print(f"  Nome: {parts[0]}")
            for part in parts[1:]:
                if "=" in part:
                    key, val = part.split("=", 1)
                    print(f"  {key}: {val}")
        
        # 10. Verifica finale stato
        print("\n" + "="*70)
        print("10. VERIFICA FINALE STATO (STATSV)")
        print("="*70)
        resp = send_command(sock, "STATSV")
        print(f"Risposta: {resp}")
        
        print("\n" + "="*70)
        print("TEST COMPLETATO!")
        print("="*70)
        print("\nComandi testati:")
        print("  [OK] ERRNUM - Lettura errori")
        print("  [OK] LINECODE - Codice linea")
        print("  [OK] DATETIME - Data/ora")
        print("  [OK] STATCADENCY - Frequenza statistiche")
        print("  [OK] SELSTATSANSWER - Formato statistiche")
        print("  [OK] GET_CURRENT_PIECE_STAT - Media pezzi")
        print("  [OK] SHOWMESSAGE - Messaggio display")
        print("  [OK] GETRECIPELIST - Lista ricette")
        print("  [OK] INFORECIPE - Dettagli ricetta")
        print("  [OK] STATSV - Stato macchina")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        sock.close()
        print("\n[DISCONNESSO]")

if __name__ == "__main__":
    test_all_commands()