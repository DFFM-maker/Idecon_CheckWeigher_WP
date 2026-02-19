#!/usr/bin/env python3
"""
Dashboard + Ciclo Completo - Versione integrata
"""

import asyncio
import websockets
import json
import time
import threading
import select
import socket
from datetime import datetime
from idecon_client import IDEON_IP, IDEON_PORT

# Stato
weights = []
events = []
connected_clients = set()
production_active = False
batch_info = {}

async def broadcast(message):
    if connected_clients:
        await asyncio.gather(
            *[ws.send(json.dumps(message)) for ws in connected_clients],
            return_exceptions=True
        )

async def handle_ws(websocket, path):
    global production_active, batch_info
    connected_clients.add(websocket)
    
    # Invia storico
    await websocket.send(json.dumps({
        'type': 'history',
        'weights': weights[-50:],
        'events': events[-20:],
        'batch': batch_info
    }))
    
    try:
        async for msg in websocket:
            pass
    except:
        pass
    finally:
        connected_clients.remove(websocket)

async def start_server():
    print("[WEB] Dashboard su http://localhost:5050")
    server = await websockets.serve(handle_ws, "localhost", 5050)
    await asyncio.Future()

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
    except:
        return None

def ciclo_produzione():
    global weights, events, production_active, batch_info
    
    print("\n" + "="*70)
    print("CICLO PRODUZIONE")
    print("="*70)
    
    config = {
        'production_order': 'ORDINE_TEST_001',
        'batch_code': 'LOTTO_001', 
        'extra_field_1': 'TURNO_1',
        'extra_field_2': 'OPERATORE_MARIO'
    }
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        print("Connessione...")
        sock.connect((IDEON_IP, IDEON_PORT))
        print("[OK] Connesso!")
        
        # INVIO CAMPI
        print("\nInvio campi batch...")
        for field, value in [
            ('PRODUCTIONORDER', config['production_order']),
            ('BATCHCODE', config['batch_code']),
            ('EXTRAFIELD1', config['extra_field_1']),
            ('EXTRAFIELD2', config['extra_field_2'])
        ]:
            send_command(sock, f"BATCHMODIFY={field}|{value}")
            time.sleep(0.3)
        
        # Leggi batch info
        resp = send_command(sock, "BATCHINFO")
        if resp:
            parts = resp[9:].split("|") if resp.startswith("BATCHINFO=") else []
            if len(parts) >= 5:
                batch_info = {
                    'recipe': parts[0],
                    'batch': parts[1],
                    'order': parts[2],
                    'extra1': parts[3],
                    'extra2': parts[4]
                }
                asyncio.run(broadcast({'type': 'batch', 'data': batch_info}))
        
        # AVVIO
        print("\nAvvio produzione...")
        send_command(sock, "STOP")
        time.sleep(1)
        send_command(sock, "BATCHSTART")
        time.sleep(2)
        send_command(sock, "START")
        time.sleep(3)
        
        production_active = True
        
        # MONITORAGGIO 60s
        print("\nMonitoraggio 60 secondi...")
        print("Fai le pesate ora!\n")
        
        start = time.time()
        last_poll = 0
        
        while time.time() - start < 60:
            if time.time() - last_poll >= 5:
                try:
                    sock.sendall(create_cmd("STATSV"))
                except:
                    pass
                last_poll = time.time()
            
            ready = select.select([sock], [], [], 0.5)
            if ready[0]:
                try:
                    data = sock.recv(1024)
                    if data:
                        if data[0] == 0x02: data = data[1:]
                        if data[-1] == 0x03: data = data[:-1]
                        
                        msg = data.decode('ascii', errors='replace')
                        
                        if msg.startswith("WEIGHT="):
                            parts = msg[7:].split("|")
                            if len(parts) >= 8:
                                w_data = {
                                    'timestamp': datetime.now().isoformat(),
                                    'weight_g': int(parts[6]) / 1000.0,
                                    'delta_g': int(parts[7]) / 1000.0,
                                    'batch_code': parts[2] if len(parts) > 2 else '',
                                    'recipe_name': parts[3] if len(parts) > 3 else ''
                                }
                                weights.append(w_data)
                                print(f"Peso: {w_data['weight_g']:.3f}g - Total: {len(weights)}")
                                asyncio.run(broadcast({'type': 'weight', 'weight': w_data, 'total': len(weights)}))
                        
                        elif "EVENT=" in msg:
                            events.append({'timestamp': datetime.now().isoformat(), 'msg': msg[:50]})
                            asyncio.run(broadcast({'type': 'event', 'event': msg[:50]}))
                        
                except:
                    pass
            
            remaining = 60 - int(time.time() - start)
            print(f"\r  [{remaining}s]", end="", flush=True)
            time.sleep(0.1)
        
        # CHIUSURA
        print("\n\nChiusura batch...")
        send_command(sock, "STOP")
        time.sleep(2)
        send_command(sock, "BATCHSTOP")
        time.sleep(2)
        
        # STATISTICHE
        print(f"\nTotale pesate: {len(weights)}")
        if weights:
            w_vals = [w['weight_g'] for w in weights]
            print(f"Media: {sum(w_vals)/len(w_vals):.2f}g")
            print(f"Min: {min(w_vals):.2f}g | Max: {max(w_vals):.2f}g")
        
        # RESET
        print("\nReset statistiche...")
        send_command(sock, "DISABLESTATS")
        time.sleep(1)
        send_command(sock, "ENABLESTATS")
        time.sleep(1)
        send_command(sock, "BATCHSTART")
        
        print("\nCICLO COMPLETATO!")
        
    except Exception as e:
        print(f"\nErrore: {e}")
    finally:
        sock.close()
        production_active = False

def main():
    print("="*70)
    print("IDECON - DASHBOARD + CICLO PRODUZIONE")
    print("="*70)
    print("\nDashboard: http://localhost:5050")
    print("Inizio tra 3 secondi...\n")
    time.sleep(3)
    
    # Avvia server WebSocket in thread
    server_thread = threading.Thread(target=lambda: asyncio.run(start_server()))
    server_thread.daemon = True
    server_thread.start()
    
    time.sleep(2)
    
    # Esegui ciclo produzione
    ciclo_produzione()
    
    print("\nFINITO. Premi Ctrl+C per chiudere.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nChiusura...")

if __name__ == "__main__":
    main()