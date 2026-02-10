#!/usr/bin/env python3
"""
IDECON Simple Dashboard - Versione essenziale con output immediato
"""

import asyncio
import websockets
import json
import time
import select
from datetime import datetime
from idecon_client import IdeconClient, IDEON_IP, IDEON_PORT

# Stato globale
weights = []
events = []
connected_clients = set()
client = None

async def broadcast(message):
    """Invia messaggio a tutti i client connessi"""
    if connected_clients:
        await asyncio.gather(
            *[ws.send(json.dumps(message)) for ws in connected_clients],
            return_exceptions=True
        )

async def handle_websocket(websocket, path):
    """Gestione connessione WebSocket"""
    print(f"[WEB] Client connesso: {websocket.remote_address}")
    connected_clients.add(websocket)
    
    # Invia storico
    await websocket.send(json.dumps({
        'type': 'history',
        'weights': weights[-50:],
        'events': events[-20:]
    }))
    
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get('command') and client:
                success, response = client.send_command(data['command'])
                await websocket.send(json.dumps({
                    'type': 'command_response',
                    'success': success,
                    'response': response
                }))
    except:
        pass
    finally:
        connected_clients.remove(websocket)
        print(f"[WEB] Client disconnesso: {websocket.remote_address}")

async def monitor_idecon():
    """Monitoraggio bilancia"""
    global client
    
    client = IdeconClient(IDEON_IP, IDEON_PORT)
    
    print(f"[IDECON] Connessione a {IDEON_IP}:{IDEON_PORT}...")
    
    while True:
        try:
            if not client.connected:
                if client.connect():
                    print("[IDECON] Connesso!")
                    client.set_msg_filter(17)
                    print("[IDECON] MSGFILTER=17 impostato")
                else:
                    print(f"[IDECON] Connessione fallita: {client.last_error}")
                    await asyncio.sleep(5)
                    continue
            
            # Polling STATSV
            client.socket.sendall(b'\x02STATSV\x03')
            
            # Ricezione dati
            ready = select.select([client.socket], [], [], 1)
            if ready[0]:
                data = client.socket.recv(1024)
                if data:
                    # Parse
                    if data[0] == 0x02:
                        data = data[1:]
                    if data[-1] == 0x03:
                        data = data[:-1]
                    
                    msg = data.decode('ascii', errors='replace')
                    
                    if msg.startswith("WEIGHT="):
                        weight = client.parse_weight(msg)
                        if weight:
                            print(f"[PESATA] {weight.weight_g:.3f}g - Flags: {weight.get_active_flags()}")
                            
                            w_data = {
                                'type': 'weight',
                                'timestamp': datetime.now().isoformat(),
                                'weight_g': weight.weight_g,
                                'delta_g': weight.delta_g,
                                'batch_code': weight.batch_code,
                                'recipe_name': weight.recipe_name,
                                'flags': weight.get_active_flags()
                            }
                            weights.append(w_data)
                            await broadcast(w_data)
                    
                    elif msg.startswith("EVENT="):
                        event = client.parse_event(msg)
                        if event:
                            print(f"[EVENTO] {event.event_code}: {event.event_name}")
                            
                            e_data = {
                                'type': 'event',
                                'timestamp': datetime.now().isoformat(),
                                'event_code': event.event_code,
                                'event_name': event.event_name,
                                'description': event.event_description
                            }
                            events.append(e_data)
                            await broadcast(e_data)
            
            await asyncio.sleep(0.1)
            
        except Exception as e:
            print(f"[IDECON] Errore: {e}")
            client.connected = False
            await asyncio.sleep(5)

async def main():
    print("="*70)
    print("IDECON SIMPLE DASHBOARD")
    print("="*70)
    print(f"Bilancia: {IDEON_IP}:{IDEON_PORT}")
    print(f"WebSocket: ws://localhost:5002")
    print(f"HTTP: http://localhost:5002")
    print("\nApri il browser per vedere la dashboard")
    print("="*70)
    
    # Avvia server WebSocket
    server = await websockets.serve(handle_websocket, "localhost", 5002)
    
    # Avvia monitor bilancia
    asyncio.create_task(monitor_idecon())
    
    # Mantieni in esecuzione
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())